#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Slack READ-ONLY fetch (Web API, stdlib-only).

Token: --token hoặc env SLACK_TOKEN (xoxb-/xoxp- — KHÔNG ghi vào file).
Lệnh:
  channels                       liệt kê kênh bot thấy được
  history <channel_id>           lịch sử kênh (--limit, --oldest, --latest)
  thread <channel_id> <ts>       toàn bộ reply của 1 thread
  search "<query>"               tìm tin nhắn (CẦN user token xoxp + search:read)
Tuỳ chọn chung: --token <tok> --out <dir> (mặc định slack_output)
"""
import argparse, datetime, json, os, re, sys, urllib.parse, urllib.request

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

API = "https://slack.com/api/"


def call(method, token, **params):
    params = {k: v for k, v in params.items() if v is not None}
    url = API + method + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if not data.get("ok"):
        sys.exit(f"[Slack API error] {method}: {data.get('error')} "
                 f"(gợi ý: thiếu scope? bot chưa được mời vào kênh? search cần xoxp?)")
    return data


def users_map(token):
    m, cur = {}, None
    try:
        while True:
            d = call("users.list", token, limit=200, cursor=cur)
            for u in d.get("members", []):
                m[u["id"]] = u.get("profile", {}).get("display_name") or u.get("real_name") or u["id"]
            cur = d.get("response_metadata", {}).get("next_cursor") or None
            if not cur:
                break
    except SystemExit:
        pass  # thiếu users:read thì hiển thị U-id thô
    return m


def fmt_ts(ts):
    return datetime.datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M")


def render(msgs, users, indent=""):
    out = []
    for m in msgs:
        who = users.get(m.get("user") or m.get("bot_id", "?"), m.get("user") or m.get("username", "?"))
        text = re.sub(r"<@(U\w+)>", lambda x: "@" + users.get(x.group(1), x.group(1)), m.get("text", ""))
        out.append(f"{indent}- **[{fmt_ts(m['ts'])}] {who}**: {text}")
        for f in m.get("files", []):
            out.append(f"{indent}  - 📎 {f.get('name')} ({f.get('mimetype','')}) {f.get('url_private','')}")
        if m.get("reply_count"):
            out.append(f"{indent}  ↳ thread {m['reply_count']} reply — ts=`{m['ts']}` (dùng lệnh thread)")
    return out


def header(title, extra=""):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return [f"# {title}", "", f"*fetched: {now}* {extra}", ""]


def save(out_dir, name, lines):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, re.sub(r"[^\w\-]+", "_", name)[:60] + ".md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("saved:", path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["channels", "history", "thread", "search"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--token", default=os.environ.get("SLACK_TOKEN"))
    ap.add_argument("--out", default="slack_output")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--oldest"); ap.add_argument("--latest")
    a = ap.parse_args()
    if not a.token:
        sys.exit("Thiếu token: --token hoặc env SLACK_TOKEN (hỏi user, không lưu vào file).")

    if a.cmd == "channels":
        d = call("conversations.list", a.token, limit=200,
                 types="public_channel,private_channel", exclude_archived="true")
        lines = header("Channels")
        for c in sorted(d.get("channels", []), key=lambda x: x["name"]):
            lines.append(f"- `{c['id']}` **#{c['name']}** ({c.get('num_members','?')} người)"
                         + (" 🔒" if c.get("is_private") else ""))
        save(a.out, "channels", lines)

    elif a.cmd == "history":
        cid = a.args[0]
        users = users_map(a.token)
        msgs, cur = [], None
        while len(msgs) < a.limit:
            d = call("conversations.history", a.token, channel=cid, limit=min(200, a.limit),
                     cursor=cur, oldest=a.oldest, latest=a.latest)
            msgs += d.get("messages", [])
            cur = d.get("response_metadata", {}).get("next_cursor") or None
            if not d.get("has_more") or not cur:
                break
        msgs.reverse()  # cũ → mới
        lines = header(f"History {cid}", f"({len(msgs)} tin, oldest={a.oldest}, latest={a.latest})")
        lines += render(msgs, users)
        save(a.out, f"history_{cid}", lines)

    elif a.cmd == "thread":
        cid, ts = a.args[0], a.args[1]
        users = users_map(a.token)
        d = call("conversations.replies", a.token, channel=cid, ts=ts, limit=200)
        msgs = d.get("messages", [])
        lines = header(f"Thread {cid} / {ts}", f"({len(msgs)} tin)")
        lines += render(msgs[:1], users) + render(msgs[1:], users, indent="  ")
        save(a.out, f"thread_{cid}_{ts.replace('.','_')}", lines)

    else:  # search
        q = a.args[0]
        d = call("search.messages", a.token, query=q, count=min(100, a.limit), sort="timestamp")
        users = users_map(a.token)
        lines = header(f"Search: {q}")
        for m in d.get("messages", {}).get("matches", []):
            ch = m.get("channel", {}).get("name", "?")
            lines.append(f"- **[{fmt_ts(m['ts'])}] #{ch} — "
                         f"{m.get('username') or users.get(m.get('user'),'?')}**: {m.get('text','')[:300]}")
            lines.append(f"  - permalink: {m.get('permalink','')}")
        save(a.out, "search_" + q, lines)


if __name__ == "__main__":
    main()
