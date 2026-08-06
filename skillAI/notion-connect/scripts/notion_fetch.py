#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Notion READ-ONLY fetch (REST API, stdlib-only).

Token: --token hoặc env NOTION_TOKEN (integration token ntn_... — KHÔNG ghi vào file).
Lệnh:
  search "<query>"            tìm page/database theo từ khoá
  page <page_id>              tải 1 page (kèm block con, đệ quy) ra markdown
  db <database_id>            query database, xuất bảng markdown
Tuỳ chọn chung: --token <tok> --out <dir> (mặc định notion_output) --depth <n> (mặc định 3)
"""
import argparse, datetime, json, os, re, sys, urllib.request

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

API = "https://api.notion.com/v1/"
VER = "2022-06-28"


def call(path, token, payload=None):
    req = urllib.request.Request(
        API + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": "Bearer " + token,
                 "Notion-Version": VER, "Content-Type": "application/json"},
        method="POST" if payload is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"[Notion API {e.code}] {path}: {e.read().decode('utf-8', 'replace')[:300]}")


def rich(arr):
    return "".join(t.get("plain_text", "") for t in arr or [])


def block_md(b, token, depth, indent=""):
    t = b["type"]; d = b.get(t, {}); out = []
    txt = rich(d.get("rich_text") or d.get("title") or [])
    line = {
        "paragraph": txt, "heading_1": "# " + txt, "heading_2": "## " + txt,
        "heading_3": "### " + txt, "bulleted_list_item": "- " + txt,
        "numbered_list_item": "1. " + txt, "quote": "> " + txt,
        "to_do": ("- [x] " if d.get("checked") else "- [ ] ") + txt,
        "toggle": "▸ " + txt, "callout": "> 💬 " + txt,
        "code": "```" + d.get("language", "") + "\n" + txt + "\n```",
        "divider": "---", "child_page": f"📄 child page: {d.get('title','')} (id={b['id']})",
        "child_database": f"🗃 child db: {d.get('title','')} (id={b['id']})",
        "bookmark": f"🔗 {d.get('url','')}", "embed": f"🔗 {d.get('url','')}",
        "image": f"🖼 image: {(d.get('external') or d.get('file') or {}).get('url','')}",
    }.get(t, f"({t}) {txt}".strip())
    if line:
        out.append(indent + line)
    if b.get("has_children") and depth > 0 and t not in ("child_page", "child_database"):
        if t == "table":
            rows = children(b["id"], token)
            for i, r in enumerate(rows):
                cells = [rich(c) for c in r.get("table_row", {}).get("cells", [])]
                out.append(indent + "| " + " | ".join(cells) + " |")
                if i == 0:
                    out.append(indent + "|" + "---|" * len(cells))
        else:
            for c in children(b["id"], token):
                out += block_md(c, token, depth - 1, indent + ("  " if t != "column_list" else ""))
    return out


def children(block_id, token):
    res, cur = [], None
    while True:
        q = f"blocks/{block_id}/children?page_size=100" + (f"&start_cursor={cur}" if cur else "")
        data = call(q, token)
        res += data.get("results", [])
        if not data.get("has_more"):
            return res
        cur = data["next_cursor"]


def page_title(p):
    props = p.get("properties", {})
    for v in props.values():
        if v.get("type") == "title":
            return rich(v["title"]) or "(no title)"
    return "(no title)"


def header(title, url, edited):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return [f"# {title}", "", "| | |", "|---|---|", f"| URL | {url} |",
            f"| last_edited | {edited} |", f"| fetched | {now} |", ""]


def save(out_dir, name, lines):
    os.makedirs(out_dir, exist_ok=True)
    name = re.sub(r"[^\w\-一-鿿ぁ-ヿ]+", "_", name)[:60] or "page"
    path = os.path.join(out_dir, name + ".md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("saved:", path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["search", "page", "db"])
    ap.add_argument("arg")
    ap.add_argument("--token", default=os.environ.get("NOTION_TOKEN"))
    ap.add_argument("--out", default="notion_output")
    ap.add_argument("--depth", type=int, default=3)
    a = ap.parse_args()
    if not a.token:
        sys.exit("Thiếu token: --token hoặc env NOTION_TOKEN (hỏi user, không lưu vào file).")

    if a.cmd == "search":
        data = call("search", a.token, {"query": a.arg, "page_size": 25})
        lines = [f"# Search: {a.arg}", ""]
        for r in data.get("results", []):
            title = page_title(r) if r["object"] == "page" else rich(r.get("title", []))
            lines.append(f"- [{r['object']}] **{title}** — id=`{r['id']}` — {r.get('url','')}"
                         f" (edited {r.get('last_edited_time','')[:10]})")
        save(a.out, "search_" + a.arg, lines)
    elif a.cmd == "page":
        p = call("pages/" + a.arg, a.token)
        lines = header(page_title(p), p.get("url", ""), p.get("last_edited_time", ""))
        for b in children(a.arg, a.token):
            lines += block_md(b, a.token, a.depth)
        save(a.out, page_title(p), lines)
    else:
        rows, cur = [], None
        while True:
            data = call(f"databases/{a.arg}/query", a.token,
                        {"page_size": 100, **({"start_cursor": cur} if cur else {})})
            rows += data.get("results", [])
            if not data.get("has_more"):
                break
            cur = data["next_cursor"]
        keys = list(rows[0]["properties"].keys()) if rows else []
        lines = header("Database " + a.arg, "", "") + \
            ["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)]
        for r in rows:
            def cell(v):
                t = v["type"]
                if t in ("title", "rich_text"):
                    return rich(v[t])
                if t == "select":
                    return (v[t] or {}).get("name", "")
                if t == "multi_select":
                    return ",".join(o["name"] for o in v[t])
                if t == "date":
                    return (v[t] or {}).get("start", "")
                return str(v.get(t, ""))[:40]
            lines.append("| " + " | ".join(cell(r["properties"][k]) for k in keys) + " |")
        save(a.out, "db_" + a.arg, lines)


if __name__ == "__main__":
    main()
