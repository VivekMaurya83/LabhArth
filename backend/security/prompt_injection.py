"""
LabhArth AI — Prompt Injection Detection Utility
===================================================
Scans client inputs for jailbreak attempts and system override commands.
"""

import re
from fastapi import HTTPException, status

PROMPT_INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"(?i)you\s+are\s+now\s+in\s+developer\s+mode",
    r"(?i)system\s+override",
    r"(?i)jailbreak",
    r"(?i)bypass\s+rate\s+limit",
    r"(?i)forget\s+what\s+you\s+were\s+told",
    r"(?i)you\s+are\s+no\s+longer\s+LabhArth\s+AI",
    r"(?i)you\s+must\s+now\s+act\s+as",
    r"(?i)stop\s+being\s+an\s+assistant",
    r"(?i)new\s+instruction:"
]

def scan_prompt_injection(message: str) -> None:
    """
    Scan client inputs for potential prompt injection or jailbreak attempts.
    Raises HTTPException (400 Bad Request) if a malicious signature is matched.
    """
    if not message or not isinstance(message, str):
        return

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, message):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security validation failed. Message contains restricted system keywords."
            )
