import re
from app.policy_engine import PolicyEngine

policy = PolicyEngine()

PII_PATTERNS = {
    "EMAIL_ADDRESS": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "PHONE_NUMBER": r"\b(\+?\d{1,3}[\s.-]?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}\b",
    "CREDIT_CARD": r"\b(?:\d{4}[\s.-]?){3}\d{4}\b",
    "US_SSN": r"\b\d{3}-\d{2}-\d{4}\b",
}


def check_jailbreak(user_input: str):
    lowered_input = user_input.lower()
    blocked_keywords = policy.get_blocked_keywords()
    for keyword in blocked_keywords:
        if keyword.lower() in lowered_input:
            return True, keyword
    return False, None


def check_pii(user_input: str):
    detected = []
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, user_input):
            detected.append(pii_type)
    if detected:
        return True, detected
    return False, []


def check_input_length(user_input: str):
    max_length = policy.get_max_input_length()
    return len(user_input) <= max_length


def run_input_guardrails(user_input: str):
    issues = []

    is_jailbreak, matched_keyword = check_jailbreak(user_input)
    if is_jailbreak:
        issues.append(f"Jailbreak attempt detected: '{matched_keyword}'")

    if not policy.is_pii_allowed():
        has_pii, pii_types = check_pii(user_input)
        if has_pii:
            issues.append(f"PII detected: {', '.join(pii_types)}")

    if not check_input_length(user_input):
        issues.append("Input exceeds maximum allowed length")

    is_safe = len(issues) == 0
    return is_safe, issues