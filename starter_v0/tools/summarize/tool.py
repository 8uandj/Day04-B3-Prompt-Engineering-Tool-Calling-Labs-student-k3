"""
tools/summarize/tool.py

Extractive summarization thuan Python - khong goi API ngoai, khong can
API key. Thuat toan: tach cau -> tinh diem tung cau dua tren tan suat tu
(loai stopword co ban) -> chon N cau diem cao nhat, giu nguyen thu tu xuat
hien trong van ban goc.

Day la thuat toan don gian (khong dung ML/model), phu hop de test khong
can key va van cho ket qua hop ly voi van ban tieng Viet/Anh thong thuong.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

# Stopword co ban - khong day du, du dung de loai bot tu qua pho bien
# khi tinh diem cau. Co the mo rong list nay neu can chinh xac hon.
STOPWORDS = {
    # tieng Viet
    "va", "la", "cua", "co", "khong", "duoc", "cho", "nay", "de", "trong",
    "voi", "mot", "cac", "nhung", "da", "se", "cung", "tai", "theo", "ve",
    "vao", "ra", "tu", "nhu", "hon", "the", "khi", "neu", "vi", "ma",
    # english
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "is",
    "are", "was", "were", "with", "that", "this", "it", "as", "by", "at",
    "be", "has", "have", "had", "but", "not", "from",
}


class SummarizeToolError(Exception):
    """Loi nghiep vu cua tool summarize."""


def _split_sentences(text: str) -> List[str]:
    # Tach cau don gian theo dau cham/hoi/than, giu nguyen dau cau.
    raw = re.split(r"(?<=[.!?…])\s+", text.strip())
    return [s.strip() for s in raw if s.strip()]


def _tokenize(sentence: str) -> List[str]:
    words = re.findall(r"[^\W\d_]+", sentence.lower(), flags=re.UNICODE)
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def summarize(text: str, num_sentences: int = 3) -> Dict[str, Any]:
    """
    Tom tat `text` bang extractive summarization, giu lai `num_sentences`
    cau quan trong nhat, theo dung thu tu xuat hien trong van ban goc.

    Raises:
        SummarizeToolError: khi text rong hoac num_sentences khong hop le.
    """
    if not text or not text.strip():
        raise SummarizeToolError("empty_text: 'text' khong duoc de rong")

    if num_sentences <= 0:
        raise SummarizeToolError(
            f"invalid_num_sentences: num_sentences phai > 0, nhan duoc {num_sentences}"
        )

    sentences = _split_sentences(text)
    total = len(sentences)

    if total <= num_sentences:
        return {
            "summary": " ".join(sentences),
            "sentence_count_original": total,
            "sentence_count_summary": total,
        }

    # Tinh tan suat tu tren toan van ban
    word_freq: Dict[str, int] = {}
    for sent in sentences:
        for w in _tokenize(sent):
            word_freq[w] = word_freq.get(w, 0) + 1

    # Diem moi cau = tong tan suat cac tu trong cau, chuan hoa theo do dai cau
    # de tranh thien vi cau qua dai.
    scored = []
    for idx, sent in enumerate(sentences):
        words = _tokenize(sent)
        score = sum(word_freq.get(w, 0) for w in words)
        norm_score = score / max(len(words), 1)
        scored.append((idx, norm_score))

    top_indices = sorted(
        sorted(scored, key=lambda x: x[1], reverse=True)[:num_sentences],
        key=lambda x: x[0],  # giu lai thu tu goc trong van ban
    )
    summary_sentences = [sentences[i] for i, _ in top_indices]

    return {
        "summary": " ".join(summary_sentences),
        "sentence_count_original": total,
        "sentence_count_summary": len(summary_sentences),
    }


# --- Tool registry entry point -------------------------------------------
def run(args: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper chuan hoa de dang ky trong tools/__init__.py."""
    try:
        return summarize(
            text=args.get("text", ""),
            num_sentences=int(args.get("num_sentences", 3)),
        )
    except SummarizeToolError as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Smoke test - chay: python tools/summarize/tool.py
    sample_text = (
        "Tri tue nhan tao dang phat trien rat nhanh trong nhung nam gan day. "
        "Nhieu cong ty cong nghe lon da dau tu hang ty do la vao nghien cuu AI. "
        "Cac mo hinh ngon ngu lon co the thuc hien nhieu tac vu phuc tap. "
        "Tuy nhien, van con nhieu thach thuc ve an toan va dao duc AI can giai quyet. "
        "Cac chinh phu tren the gioi cung dang xay dung khung phap ly cho AI. "
        "Nghien cuu ve AI an toan la mot linh vuc dang duoc quan tam dac biet."
    )
    result = summarize(sample_text, num_sentences=2)
    print(result)