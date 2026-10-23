"""
IncuBrix Ingestion Module
Handles loading, text extraction, normalization, and source claims extraction.
"""

import io
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class IngestedDocument(BaseModel):
    title: str = Field(..., description="Extracted or campaign document title")
    raw_text: str = Field(..., description="Cleaned and normalized text")
    word_count: int = Field(..., description="Total word count")
    source_url: Optional[str] = Field(None, description="Optional source reference URL")
    key_ideas: List[str] = Field(default_factory=list, description="Extracted key ideas")
    extracted_claims: List[Dict[str, str]] = Field(default_factory=list, description="Source claims with verbatim passages")
    audience_angles: List[str] = Field(default_factory=list, description="Target audience operational angles")


def normalize_text(text: str) -> str:
    """Normalize whitespace, remove carriage returns, and strip excessive empty lines."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespaces per line
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines).strip()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using pypdf."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for i, page in enumerate(reader.pages):
            t = page.extract_text()
            if t:
                pages_text.append(t)
        return "\n\n".join(pages_text)
    except Exception as e:
        raise ValueError(f"Failed to parse PDF document: {str(e)}")


def extract_claims_and_ideas(text: str) -> Tuple[List[str], List[Dict[str, str]], List[str]]:
    """
    Extract key ideas, claims, and audience angles from normalized text.
    Preserves exact verbatim sentences for factual traceability.
    """
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 25]
    
    # Identify key ideas from headings, bullet points, or high-information sentences
    key_ideas = []
    lines = text.split("\n")
    for line in lines:
        cleaned = line.strip().lstrip("#*-0123456789. ")
        if 20 <= len(cleaned) <= 180 and not cleaned.startswith("http"):
            if any(term in cleaned.lower() for term in ["framework", "workflow", "engine", "rule", "step", "repurpose", "creator"]):
                key_ideas.append(cleaned)
    if not key_ideas and sentences:
        key_ideas = sentences[:5]
    else:
        key_ideas = key_ideas[:6]

    # Extract source-supported claims (with verbatim passage reference)
    extracted_claims = []
    for s in sentences:
        if any(marker in s.lower() for marker in ["percent", "%", "hours", "study", "framework", "reduce", "tested", "results"]):
            extracted_claims.append({
                "claim_summary": s[:120] + ("..." if len(s) > 120 else ""),
                "verbatim_passage": s
            })
        if len(extracted_claims) >= 6:
            break
    if not extracted_claims and sentences:
        extracted_claims.append({
            "claim_summary": sentences[0][:120],
            "verbatim_passage": sentences[0]
        })

    # Derive audience angles
    audience_angles = [
        "Time-poor solo creators looking to eliminate repetitive repurposing tasks",
        "Growth marketers needing multi-platform distribution consistency with verified UTM attribution",
        "Digital agencies scaling client deliverables from 1 long-form anchor piece into 30 assets"
    ]

    return key_ideas, extracted_claims, audience_angles


def process_input(
    content: str,
    source_type: str = "text",
    campaign_name: str = "IncuBrix Growth Engine",
    source_url: Optional[str] = None,
    raw_bytes: Optional[bytes] = None
) -> IngestedDocument:
    """
    Ingest, validate, and normalize input content.
    Enforces minimum and maximum size checks.
    """
    if source_type == "pdf" and raw_bytes:
        extracted = extract_text_from_pdf(raw_bytes)
    elif raw_bytes and source_type in ["txt", "md", "markdown"]:
        extracted = raw_bytes.decode("utf-8", errors="replace")
    else:
        extracted = content

    normalized = normalize_text(extracted)
    word_count = len(normalized.split())

    if word_count < 15:
        raise ValueError("Input text is too short. Please provide at least 15 words of long-form content.")
    if word_count > 60000:
        raise ValueError("Input exceeds maximum supported size (60,000 words). Please provide a single article or chapter.")

    # Infer title if not explicitly named
    title = campaign_name
    lines = normalized.split("\n")
    first_meaningful_line = next((l.strip("# ").strip() for l in lines if len(l.strip("# ").strip()) > 5), "")
    if first_meaningful_line and campaign_name == "IncuBrix Growth Engine":
        title = first_meaningful_line[:80]

    key_ideas, claims, angles = extract_claims_and_ideas(normalized)

    return IngestedDocument(
        title=title,
        raw_text=normalized,
        word_count=word_count,
        source_url=source_url,
        key_ideas=key_ideas,
        extracted_claims=claims,
        audience_angles=angles
    )
