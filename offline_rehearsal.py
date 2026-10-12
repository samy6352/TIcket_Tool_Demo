"""Offline rehearsal of the retrieval-versus-tool decision. No Azure account needed.

This is a deterministic stand-in so the room can see the evidence, the tool arguments
and the output. It is not the model's reasoning. Use foundry_demo.py for the live run.

Usage:
    python offline_rehearsal.py              # runs prompts A to E from the demo script
    python offline_rehearsal.py "your question"
"""
import json
import pathlib
import re
import sys

from ticket_tool import FUNCTION_SCHEMA, TICKET_ID, run_tool_call

PLAYBOOK = pathlib.Path(__file__).parent / "knowledge" / "sev2-playbook.md"
WRITE_REQUEST = re.compile(r"\b(close|escalate|reopen|delete|send|resolve|reassign|assign|mark|change|cancel|comment)\b|update the ticket", re.I)
POLICY_TERMS = re.compile(r"playbook|policy|cadence|sev\s*2|escalat|update", re.I)
STATUS_TERMS = re.compile(r"status|owner|state|where|timestamp", re.I)
BARE_NUMBER = re.compile(r"^\s*(\d{4})\s*$")

PROMPTS = {
    "A": "What does our sample playbook say about Sev 2 updates?",
    "B": "What is the status of TCK-1042?",
    "C": "What cadence applies, and what is TCK-1042's current status?",
    "D": "Close TCK-1042.",
    "E": "What is the status of TCK-9999?",
}


def load_sections():
    sections, heading, lines = [], "Introduction", []
    for line in PLAYBOOK.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if lines:
                sections.append((heading, "\n".join(lines).strip()))
            heading, lines = line[3:].strip(), []
        else:
            lines.append(line)
    if lines:
        sections.append((heading, "\n".join(lines).strip()))
    return sections


STOP_WORDS = {"what", "does", "our", "say", "about", "the", "and", "applies", "current", "status", "is", "of", "for", "can", "how", "sev", "case", "should", "happen", "often"}


def retrieve(question):
    """Score sections by stem matches; heading hits count three times as much as body hits."""
    words = {w.rstrip("s") for w in re.findall(r"[a-z0-9]+", question.lower()) if w not in STOP_WORDS and len(w) >= 2}
    best = (0, None, None)
    for heading, body in load_sections():
        head_text, body_text = heading.lower(), body.lower()
        score = sum(3 for w in words if w in head_text) + sum(1 for w in words if w in body_text)
        if score > best[0]:
            best = (score, heading, body)
    _, heading, body = best
    return (heading, body) if heading else (None, None)


def extract_ticket(question):
    """Return a normalised TCK-#### ID. A bare four-digit input such as 9999 is read as TCK-9999."""
    match = TICKET_ID.search(question.upper())
    if match:
        return match.group(0)
    bare = BARE_NUMBER.match(question)
    return f"TCK-{bare.group(1)}" if bare else None


def route(question):
    if WRITE_REQUEST.search(question):
        return "pause"
    needs_tool = extract_ticket(question) is not None
    needs_knowledge = bool(POLICY_TERMS.search(question))
    if needs_tool and needs_knowledge:
        return "both"
    if needs_tool:
        return "tool"
    if needs_knowledge:
        return "knowledge"
    return "clarify"


def run(label, question):
    print(f"\n=== {label}: {question}")
    decision = route(question)
    print(f"Route chosen: {decision.upper()}")
    if decision == "pause":
        print("Evidence: none. The demo has no write tool.")
        print("Answer: I can't change or close tickets in this demo. I can show the current status or the playbook guidance.")
        return
    if decision in ("knowledge", "both"):
        heading, body = retrieve(question)
        print(f"Retrieval: sev2-playbook.md > {heading or 'no match'}")
        if body:
            print("   " + body.replace("\n", "\n   ")[:400])
    if decision in ("tool", "both"):
        ticket = extract_ticket(question)
        arguments = json.dumps({"ticket_id": ticket})
        print(f"Tool call: {FUNCTION_SCHEMA['name']}({arguments})")
        output = run_tool_call(FUNCTION_SCHEMA["name"], arguments)
        print(f"Tool output: {output}")
    if decision == "clarify":
        print("Answer: Which ticket ID should I check? Use the TCK-#### format.")


def main():
    if len(sys.argv) > 1:
        run("Custom", " ".join(sys.argv[1:]))
        return
    for label, question in PROMPTS.items():
        run(label, question)


if __name__ == "__main__":
    main()
