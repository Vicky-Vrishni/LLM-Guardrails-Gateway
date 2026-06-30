from app.policy_engine import PolicyEngine
from app.llm_client import classify_output_against_policy

policy = PolicyEngine()


def check_output_length(llm_response: str):
    max_length = policy.get_max_output_length()
    return len(llm_response) <= max_length


def check_blocked_topics(llm_response: str):
    blocked_topics = policy.get_blocked_topics()
    result = classify_output_against_policy(llm_response, blocked_topics)

    if result["violation"]:
        return [result["topic"]]

    return []


def add_disclaimer_if_needed(llm_response: str, flagged_topics: list):
    if policy.is_disclaimer_required() and len(flagged_topics) > 0:
        disclaimer = policy.get_disclaimer_text()
        return f"{llm_response}\n\n{disclaimer}"

    return llm_response


def run_output_guardrails(llm_response: str):
    issues = []

    if not check_output_length(llm_response):
        issues.append("Output exceeds maximum allowed length")

    flagged_topics = check_blocked_topics(llm_response)
    if flagged_topics:
        issues.append(f"Response touches blocked topics: {', '.join(flagged_topics)}")

    final_response = add_disclaimer_if_needed(llm_response, flagged_topics)

    is_safe = len(flagged_topics) == 0 and check_output_length(llm_response)

    return final_response, issues