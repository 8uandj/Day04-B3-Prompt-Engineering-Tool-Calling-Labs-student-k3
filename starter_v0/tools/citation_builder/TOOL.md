---
name: citation_builder
track: bonus
kind: local_formatter
provider:
requires_env: []
inputs: [sources, style, headline, include_accessed, accessed_date]
outputs: [citations, markdown, source_count]
side_effect: false
---

# Citation Builder Tool

## Purpose

Build a clean citation list from source items that are already available in the conversation or returned by other tools. Use it after `lookup`, `fetch`, `papers`, or `paper_text` when the user asks for sources, bibliography, references, citation notes, or an APA/markdown source list.

Do not use this tool to discover new sources. Call research tools first when the user still needs information gathering.

## Usage & Arguments

- `sources` (array, required): Source objects with fields such as `title`, `url`, `source`, `authors`, `published`, `date`, `updated`, `year`, or `summary`.
- `style` (string, optional): `markdown`, `apa`, or `source_notes`. Default: `markdown`.
- `headline` (string, optional): Heading for the rendered markdown. Default: `Sources`.
- `include_accessed` (boolean, optional): Add an accessed date for URL citations. Default: `false`.
- `accessed_date` (string, optional): Explicit ISO-style date to use when `include_accessed` is true.

## Returns

JSON object with:

- `status`: `success` or `error`
- `style`: selected citation style
- `source_count`: number of cited sources
- `citations`: normalized citation records
- `markdown`: rendered citation list ready to include in an answer
