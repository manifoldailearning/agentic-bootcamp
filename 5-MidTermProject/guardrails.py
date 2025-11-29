# Secret / API detection
# PII detection
# Prompt Injection detection
# Hallucination detection
# Context Drift detection
# Tonality detection
# Toxicity detection
# Hate speech detection
# Spam detection
# Malware detection
# Phishing detection
# Fraud detection
# etc.

import re
import logging

BANNED_WORDS = {"kill", "die", "attack"}
PII_PATTERNS = [
    (r'\b\d{3}-\d{3}-\d{4}\b', "[REDACTED]"), # Phone Number
    (r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', "[REDACTED]"), # Email Address
    (r'\b\d{3}-\d{3}-\d{4}\b', "[REDACTED]"), # Credit Card Number
]

def apply_guardrails(text:str) -> str:

    original_text = text
    for word in BANNED_WORDS:
        if word.lower() in text.lower():
            logging.warning(f"Banned word detected: {word}")
            text = text.replace(word, "[BANNED_CONTENT]")
    
    # PII detection
    for pattern, replacement in PII_PATTERNS:
        text = re.sub(pattern, replacement, text)
    
    if original_text != text:
        logging.info(f"Guardrails applied to text: {text}")
    
    return text