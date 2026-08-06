---
name: notion-connect
description: >
  Kết nối Notion của dự án EMINEL Gateway (READ-ONLY mặc định) qua MCP server chính thức
  của Notion, có fallback REST API. Dùng để truy nguồn cấp 1: 定例議事録 (biên bản định kỳ),
  機能仕様一覧, các trang spec mà repo docs chỉ là bản chép lại cấp 2.
  Trigger khi user gõ "notion-connect", "/notion-connect", "tìm trên Notion",
  "đọc trang Notion", "biên bản định kỳ trên Notion", "truy nguồn Notion".
user_invocable: true
---

# notion-connect

Skill phục vụ bước "truy về nguồn gốc" của dự án E-GW (xem `requirements/onboarding_guide.md` Phụ lục E):
thứ tự tra là **docs → input → repo tham chiếu → Slack → Notion/OneDrive**. Repo
`../sources/eminel_gw_project/docs` là **tài liệu cấp 2**; khi cần đối chiếu bản chính (định期
議事録 6/3・6/10・6/15・6/19, 機能仕様一覧, trang QA với 北ガス…) thì dùng skill này.

## Quy tắc bắt buộc

1. **READ-ONLY mặc định** — không tạo/sửa/xoá page, không comment. Notion MCP *có* quyền ghi;
   chỉ được ghi khi user yêu cầu rõ ràng trong chính phiên đó, và phải xác nhận lại trước khi ghi.
2. **Token/OAuth hỏi user mỗi lần cần** — **CẤM ghi token** (`ntn_…`) vào script, SKILL.md,
   file output, memory, log. (Cùng quy ước với `fetch-ticket`.)
3. **Dữ liệu Notion là nội bộ mui ↔ 北ガス.** Nội dung tải về chỉ để phân tích trong workspace;
   không paste sang hệ thống ngoài, không đưa vào tài liệu gửi khách khi chưa được duyệt.
4. Trang lấy về phải **ghi kèm URL nguồn + ngày lấy** ở đầu file output — Notion là dữ liệu sống,
   bản md chỉ là cache đọc, không coi là log bất biến.
5. Trả lời user bằng tiếng Việt; giữ nguyên thuật ngữ tiếng Nhật trong nội dung trích.

## Đường ① — MCP (ưu tiên)

Notion có MCP server chính thức (hosted, OAuth — không cần tự quản token):

```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
# Trong Claude Code gõ /mcp → chọn "notion" → Authenticate → đăng nhập workspace mui
```

Tự host (khi cần chạy headless bằng integration token — tạo tại notion.so/my-integrations,
nhớ share các page cần đọc cho integration đó):

```bash
claude mcp add notion-local -e NOTION_TOKEN=<hỏi user, không lưu> -- npx -y @notionhq/notion-mcp-server
```

Sau khi kết nối, dùng các tool MCP (search / fetch page / query database) qua ToolSearch.
⚠️ Tên package/URL kiểm chứng đến 2026-08; nếu lỗi, xác nhận lại tài liệu Notion MCP mới nhất.

## Đường ② — REST API fallback (khi MCP không dùng được)

Script stdlib-only, không cần cài thêm gì:

```bash
python skillAI/notion-connect/scripts/notion_fetch.py search "議事録 6/10" --token <NOTION_TOKEN> --out notion_output
python skillAI/notion-connect/scripts/notion_fetch.py page <page_id> --token <NOTION_TOKEN> --out notion_output
python skillAI/notion-connect/scripts/notion_fetch.py db <database_id> --token <NOTION_TOKEN> --out notion_output
```

- Token cũng nhận qua env `NOTION_TOKEN` (đặt tạm trong phiên, không ghi file).
- Integration token chỉ thấy page đã được **share** cho integration — search ra ít kết quả
  thì khả năng cao là thiếu share, hỏi user share thêm.

## Luồng

```
User: /notion-connect "tìm 議事録 chốt phạm vi 6/10"  (+ OAuth MCP hoặc cấp token)
        │
        ▼
①MCP: search → fetch page      ②Fallback: notion_fetch.py search/page
        │
        ▼
notion_output/<slug>.md   (đầu file: URL + ngày lấy + ai lấy)
        │
        ▼
AI đọc, đối chiếu với ../sources/eminel_gw_project/docs (bản cấp 2) → báo khớp/lệch, kèm trích dẫn hai phía
```

## Output

Mỗi page một file md: `# <title>` ・ bảng meta (URL, last_edited_time, ngày fetch) ・ nội dung
block đã chuyển md (heading/list/toggle/code/bảng) ・ danh sách child page (link, chưa fetch).
Database: bảng md các row + property. Vị trí chuẩn: `notion_output/` (bị .gitignore nếu đưa vào repo).

## Liên hệ skill khác

- `../sources/eminel_gw_project/.claude/skills/trace-source` — skill này là "chân" Notion của trace-source.
- `slack-connect` — skill anh em: tin nhắn Slack thường dẫn link Notion; lần theo link bằng skill này.
