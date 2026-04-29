import re

class PIIScrubber:
    """
    Detects and redacts Personally Identifiable Information (PII) from user queries.
    Focuses on PAN, Aadhaar, Bank Account Numbers, Emails, and Phone Numbers.
    """
    
    # Ordered list of (Type, Pattern) to ensure correct precedence
    PATTERNS = [
        ("PAN", r"[A-Z]{5}[0-9]{4}[A-Z]{1}"),
        ("AADHAAR", r"[2-9]{1}[0-9]{3}[ \-]?[0-9]{4}[ \-]?[0-9]{4}"),
        ("EMAIL", r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
        ("PHONE", r"\b(?:\+91|91|0)?[6-9][0-9]{9}\b"),
        ("BANK_ACCOUNT", r"\b[0-9]{9,18}\b") # Generic 9-18 digit numbers last
    ]

    @classmethod
    def scrub(cls, text: str) -> str:
        """
        Redacts all detected PII patterns with [REDACTED].
        """
        scrubbed_text = text
        for pii_type, pattern in cls.PATTERNS:
            scrubbed_text = re.sub(pattern, f"[REDACTED {pii_type}]", scrubbed_text)
        return scrubbed_text

    @classmethod
    def has_pii(cls, text: str) -> bool:
        """
        Returns True if any PII pattern is found in the text.
        """
        for _, pattern in cls.PATTERNS:
            if re.search(pattern, text):
                return True
        return False
