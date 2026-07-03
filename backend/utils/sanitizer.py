"""
LabhArth AI — Text Sanitization Utility
==========================================
Clean and formatting-fix crawled data descriptions and text fields.
"""

import re
from typing import Any, Dict, List, Union

def clean_text(text: str, is_description: bool = False, is_eligibility: bool = False) -> str:
    """Sanitize scraped text, remove layout scrapings, and fix encoding corruptions."""
    if not text or not isinstance(text, str):
        return text

    # Pre-normalize all tabs, newlines, and duplicate spaces to single spaces.
    # This guarantees regex matches succeed even when text has random layout tabs/newlines.
    text = text.replace("\t", " ")
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    # Remove the standard myScheme portal layout headers and login text boxes
    # It usually starts with "Are you sure you want to sign out?" or "CancelSign" up to "Check Eligibility"
    text = re.sub(r"(?i)Are you sure you want to sign out\?.*?Check Eligibility", "", text, flags=re.DOTALL)
    text = re.sub(r"(?i)CancelSign\s*Out.*?Check Eligibility", "", text, flags=re.DOTALL)
    text = re.sub(r"(?i)EngEnglish/à¤¹à¤¿à¤¨à¥ à¤¦à¥€.*?Check Eligibility", "", text, flags=re.DOTALL)
    text = re.sub(r"(?i)Something went wrong\..*?Check Eligibility", "", text, flags=re.DOTALL)
    
    # Remove standard webpage menu button strings if they are still scattered
    btn_junk = [
        "Are you sure you want to sign out?", "CancelSign Out", "CancelSign", 
        "EngEnglish/à¤¹à¤¿à¤¨à¥ à¤¦à¥€", "Sign In", "BackDetails", "BenefitsEligibilityExclusions", 
        "Application Process", "Documents Required", "Frequently Asked Questions", 
        "Sources And References", "Feedback", "Something went wrong. Please try again later.Ok", 
        "You need to sign in before applying for schemes", 
        "It seems you have already initiated your application earlier.To know more please visit", 
        "CancelApply Now", "Check Eligibility"
    ]
    for junk in btn_junk:
        text = text.replace(junk, " ")

    # Clean encoding issues:
    # 1. Rupee Symbol UTF-8 encoding corruption (e.g. â‚¹ or â\x82\xb9 -> ₹)
    text = text.replace("â\x82\xb9", "₹")
    text = text.replace("â‚¹", "₹")
    text = text.replace("â\x82\xb9 ", "₹ ")
    text = text.replace("â‚¹ ", "₹ ")
    # 2. BOM
    text = text.replace("ï»¿", "")
    # 3. Dashes
    text = text.replace("â€“", "–")
    text = text.replace("â€”", "—")
    # 4. Quotes
    text = text.replace("â€™", "'")
    text = text.replace("â€œ", "“")
    text = text.replace("â€ ", "”")
    text = text.replace("â\x80\x99", "'")
    text = text.replace("â\x80\x93", "–")
    text = text.replace("â\x80\x94", "—")
    text = text.replace("â\x80\x9c", "“")
    text = text.replace("â\x80\x9d", "”")
    # 5. General encoding artifacts
    text = text.replace("ï¿½", "")

    # Clean double spaces or leading/trailing garbage chars
    text = re.sub(r"\s+", " ", text)
    
    # Fix spacing between camelCase elements or lowercase/uppercase merges (e.g. books,equipment.Benefits -> books, equipment. Benefits)
    # 1. Add space after punctuation if missing
    text = re.sub(r"([.,;:])([a-zA-Z])", r"\1 \2", text)
    # 2. Add space between word components stuck together (e.g. etc.Benefits -> etc. Benefits, codeRegular -> code Regular)
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    text = re.sub(r"([0-9])([A-Z])", r"\1 \2", text)
    
    # Extra cleanup for spaces
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    # Truncate and clean description parameters if requested
    if is_description:
        # 1. Strip standard myScheme layout template headers at the beginning:
        # Format: "[Scheme Name] [Ministry] [Scheme Name] [Tags] Details [Actual Intro...]"
        # Find "Details" near the beginning of the text (within the first 350 characters)
        details_match = re.search(r"^(.*?Details)\s+", text, flags=re.IGNORECASE)
        if details_match:
            header_text = details_match.group(1)
            if len(header_text) < 350:
                # Safe-check: ensure the remaining text starts with normal introductory words
                intro_match = re.match(
                    r"^(A\s+|An\s+|This\s+|The\s+|Provides\s+|Under\s+|Scheme\s+|Ministry\s+|Government\s+|Centrally\s+)",
                    text[details_match.end():],
                    flags=re.IGNORECASE
                )
                if intro_match:
                    text = text[details_match.end():].strip()

        # 2. Truncate description at duplicate block start headers
        markers = [
            r"\bBenefits\b",
            r"\bEligibility\b",
            r"\bExclusions\b",
            r"\bApplication\s+Process\b",
            r"\bHow\s+to\s+Apply\b",
            r"\bDocuments\s+Required\b",
            r"\bFrequently\s+Asked\s+Questions\b",
            r"\bSources\s+and\s+References\b",
            r"\bSources\s+And\s+References\b",
            r"\bGuidelines\s+FAQ\b"
        ]
        earliest_idx = len(text)
        for marker in markers:
            match = re.search(marker, text)
            if match:
                idx = match.start()
                if idx < earliest_idx:
                    earliest_idx = idx
        if earliest_idx < len(text):
            text = text[:earliest_idx].strip()
            # Clean up trailing spacing and separators
            text = re.sub(r"[\s,;\-·・•*#=:+]+$", "", text)
            text = text.strip()

    # Truncate and clean eligibility criteria parameters if requested
    if is_eligibility:
        markers = [
            r"\bOnline\b",
            r"\bStep\s+\d+\b",
            r"\bBenefits\b",
            r"\bExclusions\b",
            r"\bDocuments\s+Required\b",
            r"\bRequired\s+Documents\b",
            r"\bGuidelines\b",
            r"\bWhat\s+is\b",
            r"\bWhat\s+are\b",
            r"\bWho\s+can\b",
            r"\bIs\s+there\b",
            r"\bHow\s+should\b",
            r"\bWhether\b"
        ]
        earliest_idx = len(text)
        for marker in markers:
            match = re.search(marker, text)
            if match:
                idx = match.start()
                if idx < earliest_idx:
                    earliest_idx = idx
        if earliest_idx < len(text):
            text = text[:earliest_idx].strip()
            # Clean up trailing spacing and separators
            text = re.sub(r"[\s,;\-·・•*#=:+]+$", "", text)
            text = text.strip()

    return text


def sanitize_value(val: Any) -> Any:
    """Recursively clean values, including strings, lists, and dicts."""
    if isinstance(val, str):
        return clean_text(val)
    elif isinstance(val, dict):
        return {k: sanitize_value(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [sanitize_value(item) for item in val]
    return val


def sanitize_eligibility(val: Any) -> Any:
    """Recursively clean eligibility criteria values with truncation flags enabled."""
    if isinstance(val, str):
        return clean_text(val, is_eligibility=True)
    elif isinstance(val, dict):
        return {k: sanitize_eligibility(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [sanitize_eligibility(item) for item in val]
    return val
