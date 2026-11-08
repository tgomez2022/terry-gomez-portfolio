"""Classify support tickets and draft responses with deterministic rules; no messages are sent."""
import json
import re
import sys
from datetime import datetime, timezone

CATEGORIES = (
    ("Billing", ("refund", "charge", "billing", "invoice", "payment")),
    ("Technical Support", ("error", "bug", "broken", "not working", "crash")),
    ("Account Management", ("cancel", "unsubscribe", "close account")),
)
HIGH = ("urgent", "immediately", "asap", "angry", "complaint")
MEDIUM = ("soon", "follow up", "follow-up", "waiting")

def contains_phrase(message, phrase):
    return bool(re.search(r"\b" + re.escape(phrase) + r"\b", message, re.I))

def classify_ticket(message):
    if not isinstance(message, str) or not message.strip():
        raise ValueError("A non-empty support message is required")
    message = message.strip()
    category = next((name for name, words in CATEGORIES if any(contains_phrase(message, word) for word in words)), "General Support")
    priority = "High" if any(contains_phrase(message, word) for word in HIGH) else ("Medium" if any(contains_phrase(message, word) for word in MEDIUM) else "Low")
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "category": category,
        "priority": priority,
        "summary": message[:140] + ("..." if len(message) > 140 else ""),
        "draft_response": f"Hello, thank you for reaching out. We understand your request regarding {category.lower()}. Our team will review this and follow up with the next steps. We appreciate your patience.",
        "execution_status": "draft_only",
    }

if __name__ == "__main__":
    message = " ".join(sys.argv[1:]) or "URGENT: I was charged twice and need a refund immediately."
    print(json.dumps(classify_ticket(message), indent=2))
