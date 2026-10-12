"""Synthetic, read-only ticket lookup used by the Service Desk Helper demo.

Every record is fictional. The module has no write path and makes no network calls.
"""
import json
import re

TICKET_ID = re.compile(r"TCK-\d{4}")

TICKETS = {
    "TCK-1042": {"status": "Investigating", "owner": "Demo Queue", "updated_at": "2026-10-11T10:15:00Z"},
    "TCK-2117": {"status": "Waiting on customer", "owner": "Demo Queue", "updated_at": "2026-10-10T16:40:00Z"},
}

FUNCTION_SCHEMA = {
    "name": "get_ticket_status",
    "description": "Return the current synthetic status, owner and last update time for one demo ticket. Read-only.",
    "parameters": {
        "type": "object",
        "properties": {
            "ticket_id": {"type": "string", "description": "Synthetic ticket ID in the form TCK-####, for example TCK-1042"}
        },
        "required": ["ticket_id"],
        "additionalProperties": False,
    },
}


class InvalidTicketId(ValueError):
    pass


def get_ticket_status(ticket_id: str) -> dict:
    key = (ticket_id or "").strip().upper()
    if not TICKET_ID.fullmatch(key):
        raise InvalidTicketId(f"'{ticket_id}' is not in the form TCK-####")
    ticket = TICKETS.get(key)
    if ticket is None:
        return {"found": False, "ticket_id": key, "message": "No synthetic demo ticket found."}
    return {"found": True, "ticket_id": key, **ticket, "synthetic": True}


def run_tool_call(name: str, arguments: str) -> str:
    """Execute a model-requested call. Only the allow-listed function is supported."""
    if name != FUNCTION_SCHEMA["name"]:
        return json.dumps({"error": f"unknown function '{name}'"})
    try:
        args = json.loads(arguments or "{}")
        result = get_ticket_status(args.get("ticket_id", ""))
    except (ValueError, AttributeError) as exc:
        result = {"error": str(exc)}
    return json.dumps(result)
