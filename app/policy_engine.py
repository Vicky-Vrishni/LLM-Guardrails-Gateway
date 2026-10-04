import yaml
import os

#Guardril Policy engine
class PolicyEngine:
    def __init__(self, policy_path="config/policy.yaml"):
        self.policy_path = policy_path
        self.policy = self._load_policy()

    def _load_policy(self):
        if not os.path.exists(self.policy_path):
            raise FileNotFoundError(f"Policy file not found at {self.policy_path}")

        with open(self.policy_path, "r") as file:
            policy_data = yaml.safe_load(file)

        return policy_data

    def get_blocked_topics(self):
        return self.policy.get("blocked_topics", [])

    def get_blocked_keywords(self):
        return self.policy.get("blocked_keywords", [])

    def get_max_input_length(self):
        return self.policy.get("max_input_length", 2000)

    def get_max_output_length(self):
        return self.policy.get("max_output_length", 3000)

    def is_pii_allowed(self):
        return self.policy.get("allow_pii_in_input", False)

    def get_disclaimer_text(self):
        return self.policy.get("disclaimer_text", "")

    def is_disclaimer_required(self):
        return self.policy.get("require_disclaimer", False)
