"""Interpret plain-English commands. This prototype proposes actions but does not execute them."""
import json
import re
import sys
from datetime import datetime, timezone

INTENTS = [
    ("create_task", r"\b(follow[ -]?up|task|remind|schedule)\b"),
    ("send_message", r"\b(email|message|reply|contact)\b"),
    ("lookup_record", r"\b(lookup|look up|find|search)\b"),
]

def parse_command(command: str) -> dict:
    if not isinstance(command, str) or not command.strip():
        raise ValueError("A non-empty command is required")
    command = command.strip()
    intent = next((name for name, pattern in INTENTS if re.search(pattern, command, re.I)), "unknown")
    timeframe = next((name for name in ("tomorrow", "today", "next week") if re.search(r"\b" + name + r"\b", command, re.I)), "unspecified")
    match = re.search(r"\b(?:for|to|with)\s+(.+?)(?=\s+(?:today|tomorrow|next week)\b|[.!?]|$)", command, re.I)
    entity = match.group(1).strip(" ,") if match else "unknown"
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "original_command": command,
        "intent": intent,
        "entity": entity,
        "timeframe": timeframe.replace(" ", "_"),
        "action_payload": {"action": intent, "target": entity, "schedule": timeframe.replace(" ", "_")},
        "execution_status": "proposed_only",
    }

if __name__ == "__main__":
    command = " ".join(sys.argv[1:]) or "Create a follow-up task for Beta Health tomorrow"
    print(json.dumps(parse_command(command), indent=2))
