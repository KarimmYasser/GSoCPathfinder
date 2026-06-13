"""Data ingestion parser for GSoC JSON files."""

import json
from pathlib import Path
from bs4 import BeautifulSoup

from models import RawYearData

def clean_html(raw_html: str) -> str:
    """Strip HTML tags and unescape entities, returning clean text."""
    if not raw_html:
        return ""
    
    # If no obvious HTML tags are present, return as-is for speed
    if "<" not in raw_html and ">" not in raw_html and "&" not in raw_html:
        return raw_html.strip()

    soup = BeautifulSoup(raw_html, "html.parser")
    # get_text(separator=" ") ensures <p>A</p><p>B</p> becomes "A B", not "AB"
    text = soup.get_text(separator=" ")
    
    # Clean up excess whitespace
    return " ".join(text.split())

def parse_file(filepath: Path | str) -> RawYearData:
    """Parse a single JSON file into a RawYearData model."""
    path = Path(filepath)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return RawYearData.model_validate(data)

def parse_directory(data_dir: Path | str) -> list[RawYearData]:
    """Parse all JSON files in the given directory."""
    path = Path(data_dir)
    results = []
    
    for file in sorted(path.glob("*.json")):
        results.append(parse_file(file))
        
    return results
