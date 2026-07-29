from __future__ import annotations

from datetime import date
import re
from typing import Any

from tools._shared import domain


def _clean(value: Any) -> str:
    return " ".join(str(value or "").replace("\n", " ").split())


def _authors(item: dict[str, Any]) -> list[str]:
    raw = item.get("authors", item.get("author", []))
    if isinstance(raw, str):
        parts = re.split(r"\s*(?:,|;|\band\b|\bva\b)\s*", raw)
        return [_clean(part) for part in parts if _clean(part)]
    if isinstance(raw, list):
        return [_clean(part) for part in raw if _clean(part)]
    return []


def _year(item: dict[str, Any]) -> str:
    raw = _clean(item.get("published") or item.get("date") or item.get("updated") or item.get("year"))
    match = re.search(r"(19|20)\d{2}", raw)
    return match.group(0) if match else "n.d."


def _source(item: dict[str, Any], url: str) -> str:
    return _clean(item.get("source") or item.get("publisher") or domain(url))


def _url(item: dict[str, Any]) -> str:
    return _clean(item.get("url") or item.get("pdf_url") or item.get("link"))


def _apa_author(name: str) -> str:
    pieces = [piece for piece in name.split() if piece]
    if len(pieces) <= 1:
        return name
    family = pieces[-1]
    initials = " ".join(f"{piece[0].upper()}." for piece in pieces[:-1] if piece)
    return f"{family}, {initials}" if initials else family


def _apa_authors(authors: list[str]) -> str:
    if not authors:
        return ""
    formatted = [_apa_author(author) for author in authors[:6]]
    if len(authors) > 6:
        formatted.append("et al.")
    if len(formatted) == 1:
        return formatted[0]
    return ", ".join(formatted[:-1]) + f", & {formatted[-1]}"


def _citation(item: dict[str, Any], index: int, style: str, accessed_date: str, include_accessed: bool) -> dict[str, Any]:
    url = _url(item)
    title = _clean(item.get("title") or item.get("headline") or f"Untitled source {index}")
    source = _source(item, url)
    authors = _authors(item)
    year = _year(item)

    if style == "apa":
        lead = _apa_authors(authors) or source or "Unknown author"
        citation = f"{lead} ({year}). {title}."
        if source and source != lead:
            citation += f" {source}."
        if url:
            citation += f" {url}"
        if include_accessed:
            citation += f" Accessed {accessed_date}."
    elif style == "source_notes":
        parts = [f"[{index}] {title}"]
        if authors:
            parts.append(f"Authors: {', '.join(authors)}")
        if source:
            parts.append(f"Source: {source}")
        if year != "n.d.":
            parts.append(f"Year: {year}")
        if url:
            parts.append(f"URL: {url}")
        citation = " | ".join(parts)
    else:
        label = source or (authors[0] if authors else "source")
        citation = f"[{index}] [{title}]({url}) - {label}" if url else f"[{index}] {title} - {label}"
        if year != "n.d.":
            citation += f", {year}"
        if include_accessed and url:
            citation += f" (accessed {accessed_date})"

    return {
        "index": index,
        "title": title,
        "authors": authors,
        "source": source,
        "year": year,
        "url": url,
        "citation": citation,
    }


def build_citations(
    sources: list[dict[str, Any]] | None = None,
    style: str = "markdown",
    headline: str = "Sources",
    include_accessed: bool = False,
    accessed_date: str = "",
) -> dict[str, Any]:
    sources = sources or []
    style = style if style in {"markdown", "apa", "source_notes"} else "markdown"
    accessed_date = _clean(accessed_date) or date.today().isoformat()

    valid_sources = [item for item in sources if isinstance(item, dict)]
    if not valid_sources:
        return {
            "tool": "citation_builder",
            "status": "error",
            "error_code": "EMPTY_SOURCES",
            "message": "No source items were provided for citation building.",
            "citations": [],
            "markdown": "",
            "source_count": 0,
        }

    citations = [
        _citation(item, index + 1, style, accessed_date, bool(include_accessed))
        for index, item in enumerate(valid_sources)
    ]
    title = _clean(headline) or "Sources"
    markdown = f"## {title}\n\n" + "\n".join(f"- {item['citation']}" for item in citations)

    return {
        "tool": "citation_builder",
        "status": "success",
        "style": style,
        "source_count": len(citations),
        "citations": citations,
        "markdown": markdown,
    }
