"""
InvestiLens — Text Preprocessing

Handles common PDF extraction artifacts:
repeated headers/footers, broken line breaks, excessive whitespace, etc.
"""

import re
from collections import Counter
from typing import List

# Typographic characters that PDFs commonly use, mapped to plain ASCII.
TYPOGRAPHIC_REPLACEMENTS = [
    ('’', "'"),    # right single quote
    ('‘', "'"),    # left single quote
    ('“', '"'),    # left double quote
    ('”', '"'),    # right double quote
    ('–', '-'),    # en dash
    ('—', '-'),    # em dash
    ('…', '...'),  # ellipsis
]

# (regex, section name) pairs, checked in order: the FIRST match wins,
# so more specific headings must stay above more generic ones (e.g. "Revenue").
SECTION_PATTERNS = [
    (r'(?i)\brisk\s+factors?\b', 'Risk Factors'),
    (r'(?i)\bmanagement.s?\s+discussion\b', "Management's Discussion and Analysis"),
    (r'(?i)\bfinancial\s+statements?\b', 'Financial Statements'),
    (r'(?i)\bbalance\s+sheet\b', 'Balance Sheet'),
    (r'(?i)\bincome\s+statement\b', 'Income Statement'),
    (r'(?i)\bcash\s+flow\b', 'Cash Flow'),
    (r'(?i)\bshareholders?\s+(?:equity|letter)\b', "Shareholders' Letter"),
    (r'(?i)\bbusiness\s+overview\b', 'Business Overview'),
    (r'(?i)\bexecutive\s+summary\b', 'Executive Summary'),
    (r'(?i)\boperating\s+results\b', 'Operating Results'),
    (r'(?i)\brevenue\b', 'Revenue'),
    (r'(?i)\bsegment\s+(?:information|results)\b', 'Segment Information'),
    (r'(?i)\bcorporate\s+governance\b', 'Corporate Governance'),
    (r'(?i)\bauditor.s?\s+report\b', "Auditor's Report"),
    (r'(?i)\bnotes?\s+to\s+(?:the\s+)?financial\b', 'Notes to Financial Statements'),
    (r'(?i)\bmarket\s+(?:risk|overview)\b', 'Market Risk'),
    (r'(?i)\bliquidity\b', 'Liquidity'),
    (r'(?i)\bcapital\s+(?:resources|expenditure)\b', 'Capital Resources'),
    (r'(?i)\bstrategic?\s+(?:priorities|outlook|overview)\b', 'Strategic Outlook'),
]

# Only the beginning of a page is searched for a section heading.
SECTION_SAMPLE_LENGTH = 500
DEFAULT_SECTION = "General"


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text while preserving financially-important content.
    """
    if not text:
        return ""

    # Fix broken line breaks (hyphenation at end of line)
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)

    # Replace multiple newlines with double newline (paragraph boundary)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Inside each paragraph, turn single newlines into spaces
    # (the double-newline paragraph breaks are preserved)
    paragraphs = text.split('\n\n')
    cleaned_paragraphs = []
    for paragraph in paragraphs:
        paragraph = paragraph.replace('\n', ' ')
        paragraph = re.sub(r'\s{2,}', ' ', paragraph)
        paragraph = paragraph.strip()
        if paragraph:
            cleaned_paragraphs.append(paragraph)

    text = '\n\n'.join(cleaned_paragraphs)

    # Remove common page artifacts
    # Page numbers like "Page 1 of 100", "- 1 -", etc.
    text = re.sub(r'(?i)page\s+\d+\s+of\s+\d+', '', text)
    text = re.sub(r'\n\s*-\s*\d+\s*-\s*\n', '\n', text)

    # Remove excessive whitespace
    text = re.sub(r'[ \t]{2,}', ' ', text)

    # Remove null/control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # Fix encoding artifacts
    for typographic_char, plain_char in TYPOGRAPHIC_REPLACEMENTS:
        text = text.replace(typographic_char, plain_char)

    return text.strip()


def remove_repeated_headers_footers(pages: List[str], threshold: int = 3) -> List[str]:
    """
    Detect and remove text lines that appear identically across many pages
    (likely headers or footers).

    A page's first (or last) line is removed when that exact line is the
    first (or last) line of at least `threshold` pages.
    """
    if len(pages) < threshold:
        return pages

    # Count how often each line appears as the first / last line of a page
    first_line_counts = Counter()
    last_line_counts = Counter()

    for page_text in pages:
        non_empty_lines = [line.strip() for line in page_text.strip().split('\n') if line.strip()]
        if not non_empty_lines:
            continue
        first_line_counts[non_empty_lines[0]] += 1
        last_line_counts[non_empty_lines[-1]] += 1

    # Lines that repeat often enough are treated as headers/footers
    repeated_headers = {line for line, count in first_line_counts.items() if count >= threshold}
    repeated_footers = {line for line, count in last_line_counts.items() if count >= threshold}

    cleaned_pages = []
    for page_text in pages:
        lines = page_text.strip().split('\n')
        if lines and lines[0].strip() in repeated_headers:
            lines = lines[1:]
        if lines and lines[-1].strip() in repeated_footers:
            lines = lines[:-1]
        cleaned_pages.append('\n'.join(lines))

    return cleaned_pages


def detect_section(text: str) -> str:
    """
    Attempt to detect the section name from the text content.
    Uses common financial document section headings.
    """
    sample = text[:SECTION_SAMPLE_LENGTH]

    for pattern, section_name in SECTION_PATTERNS:
        if re.search(pattern, sample):
            return section_name

    return DEFAULT_SECTION
