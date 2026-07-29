# Tool: `summarize`

## Mục đích

Tóm tắt một đoạn text dài (bài báo, nhiều bài đăng gộp lại, nội dung đã
`fetch`/`readability`) thành N câu chính quan trọng nhất, dùng thuật toán
extractive summarization (chọn ra câu quan trọng nhất trong văn bản gốc,
không sinh câu mới). Không cần gọi API ngoài, chạy hoàn toàn local.

## Khi nào dùng

- Khi user yêu cầu "tóm tắt", "rút gọn", "cho mình ý chính" của một đoạn
  nội dung đã có sẵn trong context (thường sau khi `fetch`/`readability`/
  `social_search` đã trả về nội dung).
- Khi nội dung quá dài để đưa thẳng vào `format` mà không mất trọng tâm —
  dùng `summarize` trước để rút gọn, rồi mới `format` để trình bày.

## Khi nào KHÔNG dùng

- Không dùng để tìm nội dung mới — đó là việc của `lookup`/`fetch`/
  `social_search`/`timeline`. Nếu chưa có nội dung gốc trong context, phải
  gọi tool lấy nội dung trước.
- Không dùng khi văn bản đã ngắn (dưới khoảng 3-4 câu) — tóm tắt văn bản
  ngắn không có giá trị và sẽ bị tính là `unnecessary_tool`.
- Không phải tool dịch thuật — nếu user cần cả tóm tắt lẫn dịch, tóm tắt
  trước bằng ngôn ngữ gốc, việc dịch là trách nhiệm của tool/khâu khác.

## Arguments

| Field | Type | Bắt buộc | Convention / Default |
|---|---|---|---|
| `text` | string | Có | Văn bản gốc cần tóm tắt. |
| `num_sentences` | integer | Không | Số câu muốn giữ lại trong bản tóm tắt. Default: `3`. Tối thiểu 1, tối đa bằng tổng số câu trong văn bản gốc. |

## Confirmation boundary

Read-only / non-destructive — không cần `clarify` xác nhận trước khi gọi.

## Output

```json
{
  "summary": "Câu 1 quan trọng nhất. Câu 2 quan trọng nhì. Câu 3 quan trọng thứ ba.",
  "sentence_count_original": 24,
  "sentence_count_summary": 3
}
```

## Ví dụ gọi tool

```json
{
  "tool": "summarize",
  "args": {
    "text": "<nội dung dài đã fetch được>",
    "num_sentences": 3
  }
}
```

## Lỗi thường gặp

- `text` rỗng hoặc chỉ có whitespace → lỗi `empty_text`.
- `num_sentences <= 0` → lỗi `invalid_num_sentences`.
- Văn bản gốc có ít câu hơn `num_sentences` yêu cầu → tool tự động trả về
  toàn bộ văn bản gốc dưới dạng summary, không lỗi, nhưng nên log lại để
  agent biết không có gì để rút gọn thêm.