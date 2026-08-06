---
name: slack-connect
description: >
  Kết nối Slack workspace mui (READ-ONLY) qua MCP server, có fallback REST API — để đọc
  kênh #proj_kitagas_eminel-gateway, tìm tin nhắn, lần theo thread khi truy nguồn dự án E-GW.
  Trigger khi user gõ "slack-connect", "/slack-connect", "tìm trên Slack",
  "đọc kênh Slack", "tin nhắn Slack về X", "truy nguồn Slack".
user_invocable: true
---

# slack-connect

Skill anh em với `notion-connect`, phục vụ bước truy nguồn **docs → … → Slack → Notion/OneDrive**
(`requirements/onboarding_guide.md` Phụ lục E). Nhiều mục trong `../sources/eminel_gw_project/docs` ghi 出典 là
Slack (`#proj_kitagas_eminel-gateway`, trao đổi QA 6/17 齋藤–kihara…) — khi cần đối chiếu
nguyên văn hoặc tìm bối cảnh quyết định, dùng skill này.

## Quy tắc bắt buộc

1. **READ-ONLY tuyệt đối** — không post, không react, không sửa/xoá tin nhắn, không tạo kênh.
2. **Token hỏi user mỗi lần chạy** — `xoxb-…` (bot) hoặc `xoxp-…` (user). **CẤM ghi token** vào
   script, SKILL.md, output, memory, log.
3. **Tin nhắn Slack là trao đổi nội bộ mui ↔ 北ガス.** Chỉ trích dẫn vào tài liệu nội bộ; tuyệt đối
   không đưa nguyên văn vào bất kỳ thứ gì gửi khách khi chưa được duyệt (bài học từ `qa_kitagas.md`:
   khối gửi khách không chứa ID/nguồn nội bộ).
4. Tin nhắn lấy về phải ghi **kênh + ts + permalink + ngày lấy**; thread có thể đảo ngược kết luận
   của tin gốc — luôn đọc **cả replies** trước khi kết luận (giống quy tắc journals của `fetch-ticket`).
5. Trả lời user bằng tiếng Việt; giữ nguyên tiếng Nhật trong nội dung trích.

## Phạm vi quyền (scope) cần có

| Việc | Scope (bot token) | Ghi chú |
|---|---|---|
| Liệt kê kênh | `channels:read`, `groups:read` | kênh private phải mời bot vào |
| Đọc lịch sử kênh | `channels:history`, `groups:history` | |
| Tên người dùng | `users:read` | để đổi `U012ABC` → tên thật |
| **Tìm kiếm** (`search.messages`) | ⚠️ chỉ có ở **user token** `xoxp` với `search:read` | bot token KHÔNG tìm kiếm được |

## Đường ① — MCP (ưu tiên)

Slack chưa có MCP hosted chính thức; dùng server npx (token truyền qua env, không lưu file):

```bash
claude mcp add slack -e SLACK_BOT_TOKEN=<hỏi user> -e SLACK_TEAM_ID=<T…> -- npx -y @modelcontextprotocol/server-slack
```

Sau khi kết nối, dùng các tool MCP (list channels / get history / get thread replies) qua ToolSearch.
⚠️ Package trên là bản reference (đã archive nhưng vẫn chạy); nếu lỗi, kiểm tra server thay thế
mới nhất rồi cập nhật SKILL này. Tìm kiếm toàn workspace vẫn phải đi đường ② với user token.

## Đường ② — REST API fallback

Script stdlib-only:

```bash
python skillAI/slack-connect/scripts/slack_fetch.py channels --token <TOKEN> --out slack_output
python skillAI/slack-connect/scripts/slack_fetch.py history <C_CHANNEL_ID> --limit 200 --token <TOKEN> --out slack_output
python skillAI/slack-connect/scripts/slack_fetch.py thread <C_CHANNEL_ID> <thread_ts> --token <TOKEN> --out slack_output
python skillAI/slack-connect/scripts/slack_fetch.py search "暖房制御 ロジック" --token <XOXP_TOKEN> --out slack_output
```

- Token cũng nhận qua env `SLACK_TOKEN`.
- `history` nhận `--oldest/--latest` (unix ts) để khoanh khoảng thời gian (vd quanh ngày 2026-06-17).

## Luồng

```
User: /slack-connect "tìm trao đổi về 見守り通知"   (+ cấp token)
        │
        ▼
①MCP tools          ②slack_fetch.py search/history/thread
        │
        ▼
slack_output/<file>.md  (mỗi tin: [ts] tên người: nội dung, thread gom theo cây, kèm permalink)
        │
        ▼
AI đọc → đối chiếu docs cấp 2 → báo khớp/lệch; link Notion trong tin nhắn → chuyển sang /notion-connect
```

## Output

`slack_output/` — mỗi lần chạy một file md: bảng meta (kênh, khoảng thời gian, ngày lấy) rồi
tin nhắn theo thứ tự thời gian, reply thụt lề dưới tin gốc. Là cache đọc, không phải log bất biến.

## Liên hệ skill khác

- `notion-connect` — tin Slack hay dẫn link Notion; lần tiếp bằng skill đó.
- `../sources/eminel_gw_project/.claude/skills/trace-source` — skill này là "chân" Slack của trace-source.
