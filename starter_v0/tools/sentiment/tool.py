"""
tools/sentiment/tool.py

Phan tich cam xuc dua tren lexicon (tu khoa tich cuc/tieu cuc) thuan
Python - khong goi API ngoai, khong can API key. Ho tro ca tieng Viet
(khong dau va co dau) va tieng Anh co ban.

Day la phuong phap don gian, phu hop de test/demo trong lab nay. Neu can
do chinh xac cao hon cho bao cao/production, nen thay bang mot mo hinh
sentiment chuyen dung.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

POSITIVE_WORDS = {
    # vietnamese
    "tuyet voi", "tot", "tich cuc", "ung ho", "hai long", "yeu thich",
    "xuat sac", "hieu qua", "an tuong", "vui", "thanh cong", "dang tin",
    # english
    "great", "good", "excellent", "amazing", "positive", "support",
    "happy", "love", "success", "impressive", "effective", "wonderful",
}

NEGATIVE_WORDS = {
    # vietnamese
    "te", "xau", "tieu cuc", "phan doi", "that vong", "lo ngai",
    "kem", "thap", "khong hai long", "buon", "that bai", "chi trich",
    "nguy hiem", "sai lam",
    # english
    "bad", "terrible", "negative", "oppose", "disappointed", "concerned",
    "poor", "unhappy", "failure", "criticize", "dangerous", "wrong",
}


class SentimentToolError(Exception):
    """Loi nghiep vu cua tool sentiment."""


def _normalize(text: str) -> str:
    return text.lower().strip()


def _score_text(text: str) -> float:
    norm = _normalize(text)
    pos_hits = sum(1 for phrase in POSITIVE_WORDS if phrase in norm)
    neg_hits = sum(1 for phrase in NEGATIVE_WORDS if phrase in norm)
    total_hits = pos_hits + neg_hits
    if total_hits == 0:
        return 0.0
    # score trong [-1, 1], ty le thuan voi chenh lech pos/neg
    raw = (pos_hits - neg_hits) / total_hits
    return round(raw, 3)


def _label_for_score(score: float) -> str:
    if score > 0.15:
        return "positive"
    if score < -0.15:
        return "negative"
    return "neutral"


def analyze_sentiment(texts: List[str]) -> Dict[str, Any]:
    """
    Phan tich cam xuc cho danh sach text.

    Raises:
        SentimentToolError: khi `texts` khong hop le (rong / khong phai list).
    """
    if not isinstance(texts, list) or len(texts) == 0:
        raise SentimentToolError("invalid_texts: 'texts' phai la mang khong rong")

    results = []
    overall = {"positive": 0, "negative": 0, "neutral": 0}

    for t in texts:
        if not isinstance(t, str) or not t.strip():
            results.append({"text": t, "label": "neutral", "score": 0.0})
            overall["neutral"] += 1
            continue

        score = _score_text(t)
        label = _label_for_score(score)
        results.append({"text": t, "label": label, "score": score})
        overall[label] += 1

    return {"results": results, "overall": overall}


# --- Tool registry entry point -------------------------------------------
def run(args: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper chuan hoa de dang ky trong tools/__init__.py."""
    try:
        return analyze_sentiment(texts=args.get("texts", []))
    except SentimentToolError as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Smoke test - chay: python tools/sentiment/tool.py
    sample = [
        "San pham nay that tuyet voi, toi rat hai long!",
        "Dich vu qua te, that vong nang ne.",
        "Cuoc hop se dien ra vao thu Hai tuan sau.",
    ]
    result = analyze_sentiment(sample)
    print(result)