def describe_code_agent() -> dict:
    return {
        "name": "code_agent",
        "purpose": "Modify code, tests, configs, and nearby documentation.",
        "rules": [
            "Stay in task scope.",
            "Do not claim tests passed without deterministic tool output.",
            "Prefer small, reviewable patches.",
        ],
    }
