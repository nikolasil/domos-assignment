import uuid
import json
import os
from datetime import datetime


def create_locked_out_ticket(context, action_items):
    """
    Example: tenant locked out → create urgent access request.
    """
    ticket = {
        "id": str(uuid.uuid4()),
        "type": "locked_out",
        "priority": "urgent",
        "timestamp": datetime.utcnow().isoformat(),
        "tenant": context.get("tenant"),
        "unit": context.get("unit"),
        "details": "Tenant is locked out - dispatch assistance.",
        "actions": action_items
    }
    return ticket


def create_maintenance_ticket(context, action_items):
    """
    Example: maintenance issue → dispatch maintenance worker.
    """
    ticket = {
        "id": str(uuid.uuid4()),
        "type": "maintenance",
        "priority": "normal",
        "timestamp": datetime.utcnow().isoformat(),
        "tenant": context.get("tenant"),
        "unit": context.get("unit"),
        "details": "Issue reported",
        "actions": action_items
    }
    return ticket


def create_rent_info_event(context):
    """
    Rent info log event.
    """
    event = {
        "id": str(uuid.uuid4()),
        "type": "rent_request",
        "timestamp": datetime.utcnow().isoformat(),
        "tenant": context.get("tenant"),
        "unit": context.get("unit"),
        "details": "Tenant asked about rent/balance information."
    }
    return event


def save_action_item(data):
    """
    Generic save: writes JSON to output/
    """
    os.makedirs("output", exist_ok=True)
    file_path = f"output/{data['id']}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return file_path
