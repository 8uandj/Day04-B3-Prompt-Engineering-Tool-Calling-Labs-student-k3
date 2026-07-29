import json
import re

def run(text: str, language: str = "vi") -> str:
    """
    Phân tích văn bản và trả về thông số độ dễ đọc.
    Xử lý an toàn các trường hợp text rỗng hoặc không đủ dữ liệu.
    """
    # 1. Kiểm tra dữ liệu đầu vào rỗng hoặc không hợp lệ
    if not text or not text.strip():
        return json.dumps({
            "status": "error",
            "error_code": "EMPTY_INPUT",
            "message": "Văn bản đầu vào rỗng, không thể phân tích độ dễ đọc."
        }, ensure_ascii=False)

    cleaned_text = text.strip()
    words = re.findall(r'\w+', cleaned_text)
    word_count = len(words)

    # 2. Kiểm tra không đủ dữ liệu (ít hơn 5 từ)
    if word_count < 5:
        return json.dumps({
            "status": "insufficient_data",
            "word_count": word_count,
            "message": "Văn bản quá ngắn (dưới 5 từ). Cần cung cấp thêm nội dung để phân tích chính xác."
        }, ensure_ascii=False)

    # Tách câu đơn giản bằng các dấu chấm, chấm hỏi, chấm cảm
    sentences = [s.strip() for s in re.split(r'[.!?]+', cleaned_text) if s.strip()]
    sentence_count = max(len(sentences), 1)

    avg_words_per_sentence = round(word_count / sentence_count, 2)
    reading_time_minutes = round(word_count / 200, 2)  # Giả định tốc độ đọc 200 từ/phút

    # Ước tính điểm readability đơn giản (Score từ 0 đến 100)
    # Câu càng dài thì điểm readability càng giảm
    base_score = 100 - (avg_words_per_sentence * 2.5)
    readability_score = max(0, min(100, round(base_score, 1)))

    if readability_score >= 80:
        assessment = "Rất dễ đọc, câu từ ngắn gọn phù hợp cho đại chúng."
    elif readability_score >= 50:
        assessment = "Độ khó trung bình, cấu trúc câu vừa phải."
    else:
        assessment = "Khó đọc, câu quá dài hoặc phức tạp. Nên chia nhỏ câu."

    return json.dumps({
        "status": "success",
        "data": {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_words_per_sentence": avg_words_per_sentence,
            "reading_time_minutes": reading_time_minutes,
            "readability_score": readability_score,
            "assessment": assessment
        }
    }, ensure_ascii=False)