# postprocess.py
# This is place to add
# 1. Citation Injection / Context Reference / File Location
# 2. Grounding check - check if the response is grounded in the context
# 3. Data Normalization - format the response to the user's expected format like JSON
# 4. Addition of metadata like Confidence score, latency, used docs
# 5. Removal of values of certain formats like SSN, Phone numbers, etc.

import re

PII_REGEX = re.compile(r'\b\d{3}-\d{2}-\d{4}\b') # Social Security Number

def secured_output(text:str) -> str:
    if PII_REGEX.search(text):
        return "[REDACTED]"
    return text.strip()