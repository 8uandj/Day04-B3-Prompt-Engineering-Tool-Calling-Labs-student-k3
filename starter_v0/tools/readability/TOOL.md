# Readability & Text Quality Analyzer Tool

## Purpose
Phân tích văn bản đầu vào để tính toán độ dài, số từ, cấu trúc câu, ước tính thời gian đọc và điểm độ dễ đọc (Readability Score). Dùng để kiểm tra chất lượng nội dung trước khi tóm tắt hoặc định dạng digest.

## Usage & Arguments
- `text` (string, required): Đoạn văn bản cần phân tích.
- `language` (string, optional): "vi" hoặc "en". Mặc định "vi".

## Returns
Một JSON object chứa các chỉ số:
- `word_count`: Tổng số từ
- `sentence_count`: Tổng số câu
- `avg_words_per_sentence`: Số từ trung bình/câu
- `reading_time_minutes`: Thời gian đọc ước tính
- `readability_score`: Điểm độ dễ đọc từ 0 - 100
- `assessment`: Đánh giá ngắn gọn