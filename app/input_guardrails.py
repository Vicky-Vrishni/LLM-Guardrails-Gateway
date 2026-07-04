from presidio_analyzer import AnalyzerEngine
from app.policy_engine import PolicyEngine

from presidio_analyzer.nlp_engine import NlpEngineProvider

nlp_configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
}

provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
nlp_engine = provider.create_engine()

analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
policy = PolicyEngine()


def check_jailbreak(user_input: str):
    lowered_input = user_input.lower()
    blocked_keywords = policy.get_blocked_keywords()

    for keyword in blocked_keywords:
        if keyword.lower() in lowered_input:
            return True, keyword

    return False, None


SENSITIVE_PII_TYPES = [
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "CREDIT_CARD",
    "US_SSN",
    "US_BANK_NUMBER",
    "IBAN_CODE",
    "CRYPTO"
]


def check_pii(user_input: str):
    results = analyzer.analyze(text=user_input, language="en")

    filtered_results = [
        result for result in results
        if result.entity_type in SENSITIVE_PII_TYPES and result.score >= 0.5
    ]

    if len(filtered_results) > 0:
        detected_types = [result.entity_type for result in filtered_results]
        return True, detected_types

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