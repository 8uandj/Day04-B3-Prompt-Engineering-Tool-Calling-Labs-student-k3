# Tool: `sentiment`

## Mục đích

Phân tích cảm xúc (tích cực / tiêu cực / trung lập) của một đoạn text hoặc
một danh sách bài đăng (vd kết quả từ `social_search`/`timeline`), dùng
lexicon từ khóa cảm xúc có sẵn (tiếng Việt + tiếng Anh cơ bản). Không gọi
API ngoài, không cần API key.

## Khi nào dùng

- Khi user hỏi "mọi người phản ứng thế nào", "dư luận tích cực hay tiêu
  cực", "cảm xúc chung của các bài đăng này là gì" — sau khi đã có nội
  dung bài đăng/text trong context (thường từ `social_search`/`timeline`/
  `fetch`).
- Khi cần phân loại nhanh một batch bài đăng theo cảm xúc trước khi
  `format` trình bày kết quả.

## Khi nào KHÔNG dùng

- Không dùng để tìm bài đăng mới — gọi `social_search`/`timeline` trước
  nếu chưa có nội dung.
- Không dùng cho câu hỏi ý kiến cá nhân của agent (vd "bạn nghĩ AI có ý
  thức không") — đó không phải nội dung cần đo cảm xúc, agent nên trả lời
  trực tiếp, không gọi tool.
- Kết quả là ước lượng dựa trên từ khóa (lexicon-based), **không phải**
  phân tích sắc thái/mỉa mai chính xác tuyệt đối — nếu user cần phân tích
  cảm xúc chuyên sâu/học thuật, nên nói rõ giới hạn này trong câu trả lời.

## Arguments

| Field | Type | Bắt buộc | Convention / Default |
|---|---|---|---|
| `texts` | array[string] | Có | Danh sách đoạn text cần phân tích (mỗi bài đăng là 1 phần tử). Nếu chỉ có 1 đoạn, vẫn truyền dạng mảng 1 phần tử. |

## Confirmation boundary

Read-only / non-destructive — không cần `clarify`