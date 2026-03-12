def describe_build_agent() -> dict:
    return {
        "name": "build_agent",
        "purpose": "Run builds, tests, and summarize failures.",
        "rules": [
            "Do not invent outputs.",
            "Return exact commands and failure summaries.",
        ],
    }
