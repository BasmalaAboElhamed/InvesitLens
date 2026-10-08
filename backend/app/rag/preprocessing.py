"""
InvestiLens — Text Preprocessing

Handles common PDF extraction artifacts:
repeated headers/footers, broken line breaks, excessive whitespace, etc.
"""

import re
from typing import List


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

    # Replace single newlines within paragraphs with space
    # (but preserve double-newline paragraph breaks)
    lines = text.split('\n\n')
    cleaned_paragraphs = []
    for para in lines:
        cleaned_para = para.replace('\n', ' ')
        cleaned_para = re.sub(r'\s{2,}', ' ', cleaned_para)
        cleaned_para = cleaned_para.strip()
        if cleaned_para:
            cleaned_paragraphs.append(cleaned_para)

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
    text = text.replace('\u2019', "'")
    text = text.replace('\u2018', "'")
    text = text.replace('\u201c', '"')
    text = text.replace('\u201d', '"')
    text = text.replace('\u2013', '-')
    text = text.replace('\u2014', '-')
    text = text.replace('\u2026', '...')

    return text.strip()


def remove_repeated_headers_footers(pages: List[str], threshold: int = 3) -> List[str]:
    """
    Detect and remove text lines that appear identically across many pages
    (likely headers or footers).
    """
    if len(pages) < threshold:
        return pages

    # Count first and last lines across pages
    first_lines = {}
    last_lines = {}

    for page_text in pages:
        lines = [l.strip() for l in page_text.strip().split('\n') if l.strip()]
        if not lines:
            continue
        first = lines[0]
        last = lines[-1]
        first_lines[first] = first_lines.get(first, 0) + 1
        last_lines[last] = last_lines.get(last, 0) + 1

    # Identify repeated headers/footers
    repeated_first = {line for line, count in first_lines.items() if count >= threshold}
    repeated_last = {line for line, count in last_lines.items() if count >= threshold}

    cleaned_pages = []
    for page_text in pages:
        lines = page_text.strip().split('\n')
        if lines and lines[0].strip() in repeated_first:
            lines = lines[1:]
        if lines and lines[-1].strip() in repeated_last:
            lines = lines[:-1]
        cleaned_pages.append('\n'.join(lines))

    return cleaned_pages


def detect_section(text: str) -> str:
    """
    Attempt to detect the section name from the text content.
    Uses common financial document section headings.
    """
    section_patterns = [
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

    # Check the first ~500 chars for section headings
    sample = text[:500]
    for pattern, section_name in section_patterns:
        if re.search(pattern, sample):
            return section_name

    return "General"
