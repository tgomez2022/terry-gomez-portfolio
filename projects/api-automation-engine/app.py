"""Process sample sales records and recommend actions without connecting to APIs."""
import argparse
import json
import math
import sys
from datetime import datetime, timezone

SAMPLE_DATA = [
    {"client": "Alpha Clinic", "status": "new_lead", "value": 4500},
    {"client": "Beta Health", "status": "follow_up", "value": 12000},
    {"client": "Gamma Labs", "status": "closed", "value": 8000},
]
ACTIONS = {
    "new_lead": "Draft an introduction email and create a CRM task",
    "follow_up": "Notify the sales team and propose a follow-up",
    "closed": "Prepare an onboarding workflow",
}

def fetch_sales_data():
    return [item.copy() for item in SAMPLE_DATA]

def normalize_record(record):
    if not isinstance(record, dict):
        raise ValueError("Each record must be a JSON object")
    client, status = record.get("client"), record.get("status")
    if not isinstance(client, str) or not client.strip() or not isinstance(status, str) or not status.strip():
        raise ValueError("client and status must be non-empty strings")
    raw_value = record.get("value", 0)
    if isinstance(raw_value, bool):
        raise ValueError("value must be a non-negative number")
    try:
        value = float(raw_value)
    except (ValueError, TypeError) as exc:
        raise ValueError("value must be a non-negative number") from exc
    if not math.isfinite(value) or value < 0:
        raise ValueError("value must be finite and non-negative")
    return {"client_name": client.strip(), "pipeline_status": status.strip().lower(), "deal_value": round(value, 2), "processed_at": datetime.now(timezone.utc).isoformat()}

def trigger_action(record):
    return ACTIONS.get(record["pipeline_status"], "Review manually: unknown status")

def run_workflow(records=None):
    data = fetch_sales_data() if records is None else records
    if not isinstance(data, list):
        raise ValueError("Input must be a JSON list")
    result = []
    for record in data:
        normalized = normalize_record(record)
        normalized["recommended_action"] = trigger_action(normalized)
        normalized["execution_status"] = "proposed_only"
        result.append(normalized)
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    args = parser.parse_args()
    try:
        with open(args.input, encoding="utf-8") as infile:
            data = json.load(infile) if args.input else None
    except TypeError:
        data = None
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)
    print(json.dumps(run_workflow(data), indent=2))
