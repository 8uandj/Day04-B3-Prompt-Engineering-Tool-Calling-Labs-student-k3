# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. Xong trước 11:30 để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. Có thể hoàn thiện sau buổi debate để nộp bài.

## Team

- Team: B3
- Members: 5
- Provider/model: OpenAI / gpt-4o

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent dùng để tìm tin web/news, tìm tweet/post theo tài khoản hoặc chủ đề, đọc URL cụ thể, tổng hợp kết quả thành digest và đánh giá độ dễ đọc của văn bản. Agent được tối ưu để chọn đúng tool, truyền đúng arguments, hỏi lại khi thiếu thông tin và yêu cầu xác nhận trước các hành động gửi/đăng.

**Link dùng thử (truy cập được trong showdown):**

> URL: pending

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin hoặc cần xác nhận yes/no trước hành động nhạy cảm | không |
| timeline | Lấy tweet/post gần đây từ một tài khoản cụ thể, ví dụ `sama`, `elonmusk`, `karpathy` | không |
| social_search | Tìm tweet/post theo chủ đề, từ khóa, công ty, sản phẩm hoặc trend | không |
| lookup | Tìm kiếm thông tin web hoặc tin tức theo chủ đề và timeframe | không |
| fetch | Đọc nội dung từ một URL cụ thể do user cung cấp | không |
| format | Định dạng dữ liệu đã có thành markdown digest, bullet list, sections hoặc thread | không |
| send | Gửi nội dung ra Telegram sau khi user đã xác nhận rõ | không |
| policy | Tìm trong tài liệu policy nội bộ | không |
| papers | Tìm bài báo khoa học/arXiv theo chủ đề | không |
| paper_text | Trích text từ paper arXiv khi có ID hoặc URL cụ thể | không |
| readability | Đánh giá độ dễ đọc của văn bản, số từ, số câu, thời gian đọc và readability score | có |

## A3. Câu hỏi mẫu để thử

1. Tweet mới nhất của Sam Altman là gì?
2. Tin tức AI hôm nay có gì nổi bật?
3. Tóm tắt bài này giúp mình: https://openai.com/news/
4. Cho mình các tweet phổ biến nhất về OpenAI.
5. Đánh giá độ dễ đọc của đoạn văn này và gợi ý cách viết dễ hiểu hơn: "Bài viết này trình bày nhiều khái niệm kỹ thuật phức tạp trong một câu rất dài khiến người đọc khó nắm ý chính."

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Lấy tweet theo người nổi tiếng: “Tweet mới nhất của Sam Altman là gì?” | `timeline({"screenname":"sama"})` | Tool declaration làm rõ `screenname` là handle không có `@` và map Sam Altman -> `sama`, giúp giảm sai arguments | `runs/v3_B_base_openai_20260729T160146990209.json` |
| Tìm tin tức theo thời gian: “Tin AI hôm nay có gì nổi bật?” | `lookup({"query":"AI","topic":"news","timeframe":"day"})` | Schema description làm rõ `topic=news` cho tin tức và `timeframe=day` cho hôm nay | `runs/v3_B_base_openai_20260729T160146990209.json` |
| Đọc URL cụ thể: “Tóm tắt bài này: https://openai.com/news/” | `fetch({"url":"https://openai.com/news/"})` | Prompt và tool declaration nhấn mạnh có URL thì dùng `fetch`, không dùng `lookup`, và không tự đoán URL | `runs/v3_B_base_openai_20260729T160146990209.json` |
| Thiếu thông tin: “Tóm tắt 5 tweet mới nhất giúp mình” | `clarify({"response_type":"text"})` | Prompt mới không cho model đoán account mặc định; thiếu handle thì phải hỏi lại | `runs/v3_B_base_openai_20260729T160146990209.json` |
| Tool mới readability: “Đánh giá độ dễ đọc của đoạn văn này...” | `readability({"text":"...","language":"vi"})` | Tool mới xử lý text local, có validation cho input rỗng hoặc quá ngắn | Smoke test local: `status=success`, `readability_score=60.0`, `word_count=16` |

---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: `provider_error_cases` phải bằng `0`; `measured_cases` phải bằng `total_cases`; và bất kỳ `tool_results` nào có error đều phải được review thủ công vì routing PASS không chứng minh tool execution đã đúng.

Lưu ý bằng chứng: team đang cấu hình provider mục tiêu là Gemini, nhưng các run JSON hợp lệ hiện có trong thư mục `runs/` là OpenAI. Khi chạy lại bằng Gemini, thay cột run file bằng run Gemini tương ứng nếu nhóm muốn report chỉ dùng một provider.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | Baseline prompt | Đo hành vi trước khi tối ưu prompt/tool declaration | case_accuracy | 0.00 | 0.85 | `runs/v0_B_base_openai_20260729T155805888045.json` |
| v1 | `artifacts/system_prompt.md` | Thêm luật parallel calling và query normalization giúp giảm sai tool/query thừa | case_accuracy | 0.85 | 0.95 | `runs/v1_B_base_openai_20260729T155835620279.json` |
| v2 | `artifacts/system_prompt.md` | Làm rõ confirmation boundary để request gửi/post gọi `clarify(response_type="yes_no")` trước | case_accuracy | 0.95 | 0.95 | `runs/v2_B_base_openai_20260729T155931297980.json` |
| v3 | `artifacts/system_prompt.md` | Tối ưu multi-turn context, tool switch, cancel intent và carry confirmation | case_accuracy | 0.95 | 1.00 | `runs/v3_B_base_openai_20260729T160146990209.json` |
| v3 group | `data/eval_group.json` | Edge cases kiểm tra wrong tool, wrong args, missing info, boundary và multi-turn | case_accuracy | pending | 0.80 | `runs/v3_B_group_openai_20260729T160157316061.json` |

Metric đáng chú ý ở run base tốt nhất:

- `case_accuracy`: 1.0
- `tool_routing_accuracy`: 1.0
- `argument_accuracy`: 1.0
- `multiturn_accuracy`: 1.0
- `provider_error_cases`: 0

## B2. Failure analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `G07_multi_corrected_web_args` | `wrong_arg_value` | `lookup({"query":"chip AI","topic":"news","timeframe":"month","max_results":4})` + extra `social_search({"query":"chip AI","limit":4})` | Agent đã gọi đúng `lookup` nhưng gọi thừa `social_search` sau khi user chỉ yêu cầu tìm web/news. | Bổ sung rule trong prompt: khi user switch hoặc giới hạn nguồn sang web/news thì không carry tool social cũ. |
| `G09_multi_still_missing_handle` | `missing_info` | `timeline({"screenname":"sama","limit":5})` | Agent đoán Sam Altman dù người dùng chưa cung cấp account/handle. | Tăng độ ưu tiên rule: thiếu account cụ thể thì luôn `clarify(response_type="text")`, không map tên mặc định. |
| Base `v1` provider error run | `provider_error` | Không có tool call đo được | Run lỗi provider/API nên metric không hợp lệ. | Không dùng run có `provider_error_cases > 0` làm bằng chứng chính; chạy lại với provider/key đúng. |

## B3. Team eval cases

File `data/eval_group.json` có đúng 10 case: 5 single-turn và 5 multi-turn.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `G01_single_account_vs_topic` | Phân biệt bài đăng của một account với tìm bài theo chủ đề | `timeline({"screenname":"karpathy"})` | PASS trong group run v3 |
| `G02_single_top_social_args` | Trích `query`, `search_type=Top`, `limit=8` | `social_search({"query":"...","search_type":"Top","limit":8})` | PASS trong group run v3 |
| `G03_single_meta_no_tool` | Câu hỏi meta không cần tra cứu | `no_tool=true` | PASS trong group run v3 |
| `G04_single_missing_comparison_urls` | Yêu cầu đọc bài nhưng thiếu URL | `clarify({"response_type":"text"})` | PASS trong group run v3 |
| `G05_single_send_confirmation` | Gửi nội dung cần confirmation boundary | `clarify({"response_type":"yes_no"})` | PASS trong group run v3 |
| `G06_multi_two_source_fanout` | Multi-turn carry subject/timeframe và gọi hai nguồn | `lookup` + `social_search` | PASS trong group run v3 |
| `G07_multi_corrected_web_args` | Correction mới nhất cho web args, không gọi tool social cũ | Chỉ `lookup` | FAIL: extra `social_search` |
| `G08_multi_cancelled_request` | Latest intent hủy request cũ | `no_tool=true` | PASS trong group run v3 |
| `G09_multi_still_missing_handle` | Vẫn thiếu handle dù có limit | `clarify({"response_type":"text"})` | FAIL: đoán `sama` |
| `G10_multi_confirmation_carryover` | Carry nội dung và dùng confirmation ở lượt cuối | `send({"confirmed":true})` | PASS trong group run v3 |

## B4. Live chat evidence

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| Base eval: Sam Altman timeline | v3 | `timeline({"screenname":"sama"})` | `runs/v3_B_base_openai_20260729T160146990209.json` | PASS, đúng tool và đúng handle |
| Base eval: AI news today | v3 | `lookup({"query":"AI","topic":"news","timeframe":"day"})` | `runs/v3_B_base_openai_20260729T160146990209.json` | PASS, đúng topic/timeframe |
| Base eval: missing tweet handle | v3 | `clarify({"response_type":"text"})` | `runs/v3_B_base_openai_20260729T160146990209.json` | PASS, không đoán account |
| Group eval: two-source fanout | v3 group | `lookup` + `social_search` | `runs/v3_B_group_openai_20260729T160157316061.json` | PASS, gọi nhiều tool cho nhiều nguồn |
| Readability smoke test | local | `readability({"text":"...","language":"vi"})` | Direct registry smoke test | PASS, `status=success`, score `60.0` |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên | `tools/readability/tool.py`, `tools/readability/TOOL.md`, `artifacts/tools.yaml`, `tools/__init__.py` | Tool `readability` đã được đăng ký trong registry, có schema trong `tools.yaml`, có docs `TOOL.md`, smoke test trả `status=success` | Có validation cho input rỗng (`EMPTY_INPUT`) và text quá ngắn (`insufficient_data`) để tránh kết quả nhiễu |
| Optional built-in | `tools/policy`, `tools/papers`, `tools/paper_text`, `tools/send` | Declaration được giữ để dùng khi cần policy/paper/Telegram | `send` có confirmation boundary; arXiv/PDF/Telegram chỉ nên demo khi credentials và quota sẵn sàng |
| Core tool declaration | `artifacts/tools.yaml` | Schema đã làm rõ enum/default/required fields: `search_type`, `topic`, `timeframe`, `confirmed`, `limit`, `url` | Không đổi tên tool để tránh lệch registry/eval; YAML đã parse OK |
| Team eval | `data/eval_group.json` | JSON hợp lệ, đúng 10 case, 5 single-turn, 5 multi-turn | Group run còn 2 failure dùng làm backlog tối ưu tiếp |

## B6. Reflection

- Fix thuộc `system_prompt.md`: luật chọn tool, thứ tự gọi tool, điều kiện không gọi tool, hỏi lại khi thiếu thông tin, confirmation boundary, multi-turn carryover/correction/cancel.
- Fix thuộc `tools.yaml`: mô tả tool rõ hơn, schema argument chặt hơn, enum/default/required fields, handle convention, URL exact match, `send.confirmed` boundary, schema tool mới `readability`.
- Failure cần manual review: các tool execution error do API/credential/quota không chứng minh routing sai; chỉ nên chấm routing/args khi provider không lỗi và tool call đã được sinh đúng.
- Cải thiện tiếp theo: chạy lại toàn bộ base/group bằng Gemini để đồng bộ provider trong report; sửa 2 group failures còn lại; bổ sung UI transcript thật; thêm scenario chain `lookup -> fetch -> format -> readability` nếu nhóm muốn demo flow nhiều tool rõ hơn.
