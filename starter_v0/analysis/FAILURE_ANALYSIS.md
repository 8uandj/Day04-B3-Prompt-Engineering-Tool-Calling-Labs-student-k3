# Group Eval — Failure Analysis

## Trạng thái evidence

- Dataset contract: **PASS** — đúng 10 case, gồm 5 single-turn và 5 multi-turn.
- Failure coverage: **PASS** — mỗi nhóm `wrong_tool`, `wrong_arg_value`, `unnecessary_tool`, `missing_info`, `wrong_boundary` có đúng 2 case.
- Tool declaration/implementation consistency: **PASS**.
- Provider preflight: **BLOCKED** — thiếu `OPENROUTER_API_KEY`.
- Live tool execution:
  - `clarify`, `format`: chạy thành công cục bộ.
  - `send(confirmed=false)`: guardrail chạy đúng, trả `needs_confirmation`, không phát sinh side effect.
  - `timeline`, `social_search`: implementation được gọi thật nhưng trả lỗi vì thiếu `RAPIDAPI_KEY`.
  - `lookup`: implementation được gọi thật nhưng trả lỗi vì thiếu `TAVILY_API_KEY`.
  - `fetch`: implementation được gọi thật nhưng trả lỗi vì thiếu `FIRECRAWL_API_KEY`.

Không được dùng kết quả preflight hoặc smoke test này thay cho group eval bằng model thật. Chỉ kết luận metric khi `provider_error_cases=0` và `measured_cases=total_cases`.

## Case analysis matrix

| Case ID | Failure class | Expected | Failure signal cần đọc | Hướng sửa nếu fail |
|---|---|---|---|---|
| G01 | wrong_tool | `timeline(karpathy, 4)` | Gọi `social_search` hoặc handle/limit sai | Làm rõ “bài CỦA tài khoản” → `timeline`; thêm convention handle không có `@` |
| G02 | wrong_arg_value | `social_search(Top, 8)` | Default `Latest`, limit 5 hoặc query bị biến dạng | Mô tả mapping “nổi bật/top” và yêu cầu giữ số lượng người dùng chỉ định |
| G03 | unnecessary_tool | no tool | Bất kỳ tool call nào | Thêm quy tắc trả lời trực tiếp cho câu meta/capability |
| G04 | missing_info | `clarify(text)` | Tự đoán URL hoặc gọi `fetch` | Cấm suy đoán tham chiếu “bài này/hai bài”; hỏi xin URL còn thiếu |
| G05 | wrong_boundary | `clarify(yes_no)` | Gọi `send` trước confirmation | Nêu confirmation boundary độc lập với việc nội dung đã rõ |
| G06 | wrong_tool | `lookup` + `social_search` | Thiếu một nguồn, sai timeframe hoặc gọi thêm tool | Cho phép nhiều tool call; map web news và social search riêng |
| G07 | wrong_arg_value | `lookup(month, 4)` | Giữ giá trị cũ week/10 | Latest correction thắng; carry các field không bị sửa |
| G08 | unnecessary_tool | no tool | Vẫn chạy yêu cầu ở lượt đầu | Latest user intent có quyền hủy request trước đó |
| G09 | missing_info | `clarify(text)` | Đoán tài khoản vì đã có limit | Phân biệt field đã đủ và field bắt buộc vẫn thiếu |
| G10 | wrong_boundary | `send(text, confirmed=true)` | Hỏi lại, bỏ mất text hoặc `confirmed=false` | Carry nội dung qua lượt; chỉ hành động sau xác nhận rõ ràng |

## Cách phân loại sau khi có run JSON

1. **Provider validity**: nếu `provider_error_cases > 0`, không dùng accuracy của run để báo cáo.
2. **Routing**: đọc `routing_correct`, `actual_tool_calls` và `observed_mismatch`.
3. **Arguments**: đọc `args_correct` và từng dòng trong `failures`.
4. **Execution**: routing PASS chưa đủ; đọc `tool_results[*].result.error` và các cột `execution_*` trong CSV.
5. **Multi-turn**: đọc riêng `multiturn_accuracy`, đặc biệt các correction và cancellation ở lượt cuối.
6. **Tool-chain proxy**: G06 kiểm tra fan-out hai nguồn trong một model response. Runner hiện không hỗ trợ chuỗi tuần tự lấy output tool A đưa vào tool B.

## Lệnh tạo evidence sau khi cấu hình key

```bash
python scripts/preflight_provider.py --provider openrouter
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
python scripts/parse_runs.py runs/ --output analysis/group_failure_analysis.csv
```

Chọn đúng run group mới nhất khi đưa metric và lỗi vào report; không gộp nhầm base/extension run.
