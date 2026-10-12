"""Interactive Service Desk Helper for the live session.

Usage:
    python chat_demo.py           rehearsal mode: deterministic routing, no Azure needed
    python chat_demo.py --live    Microsoft Foundry: the real model in your project

Commands at the "You>" prompt:
    /script   walk through prompts A to E, pausing for Enter before each one
    /prompts  list the demo prompts
    /reset    start a new conversation (live mode keeps context between turns)
    /help     show commands
    /quit     exit

Live mode needs PROJECT_ENDPOINT and MODEL_DEPLOYMENT_NAME, as in foundry_demo.py.
Optional VECTOR_STORE_ID enables playbook citations for prompts A and C.
"""
import json
import os
import sys

from offline_rehearsal import PROMPTS, extract_ticket, retrieve, route
from ticket_tool import FUNCTION_SCHEMA, run_tool_call

MAX_TOOL_ROUNDS = 4
AGENT_NAME = "service-desk-chat"


def first_paragraph(text):
    for block in text.strip().split("\n\n"):
        block = block.strip()
        if block and not block.startswith("#"):
            return block
    return ""


def rehearsal_turn(question):
    """Return (trace lines, answer) using the same routing rules as the offline rehearsal."""
    decision = route(question)
    trace = [f"[route] {decision.upper()}"]
    if decision == "pause":
        return trace, "I can't change or close tickets in this demo. I can show the current status or the playbook guidance."
    if decision == "clarify":
        return trace, "Which ticket ID should I check? Use the TCK-#### format, or ask about the Sev 2 playbook."

    parts = []
    if decision in ("knowledge", "both"):
        heading, body = retrieve(question)
        if heading:
            trace.append(f"[retrieval] sev2-playbook.md > {heading}")
            parts.append(f"According to the sample playbook: {first_paragraph(body)}")
    if decision in ("tool", "both"):
        ticket = extract_ticket(question)
        arguments = json.dumps({"ticket_id": ticket})
        trace.append(f"[tool call] {FUNCTION_SCHEMA['name']}({arguments})")
        output = run_tool_call(FUNCTION_SCHEMA["name"], arguments)
        trace.append(f"[tool output] {output}")
        data = json.loads(output)
        if data.get("found"):
            parts.append(
                f"{data['ticket_id']} is {data['status']}, owned by {data['owner']}, "
                f"last updated {data['updated_at']}."
            )
        else:
            parts.append(f"I couldn't find {ticket} in the synthetic demo data.")
    return trace, " ".join(parts) or "That isn't covered by the playbook or the ticket data."


class LiveSession:
    """Keeps one Foundry agent and one conversation for the whole session."""

    def __init__(self):
        from azure.ai.projects import AIProjectClient
        from azure.ai.projects.models import PromptAgentDefinition
        from azure.identity import DefaultAzureCredential

        from foundry_demo import INSTRUCTIONS, build_tools

        endpoint = os.environ.get("PROJECT_ENDPOINT")
        model = os.environ.get("MODEL_DEPLOYMENT_NAME")
        if not endpoint or not model:
            sys.exit("Live mode needs PROJECT_ENDPOINT and MODEL_DEPLOYMENT_NAME set in this terminal.")
        self.project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
        self.openai = self.project.get_openai_client()
        self.agent = self.project.agents.create_version(
            agent_name=AGENT_NAME,
            definition=PromptAgentDefinition(model=model, instructions=INSTRUCTIONS, tools=build_tools()),
        )
        self.agent_ref = {"agent_reference": {"name": self.agent.name, "type": "agent_reference"}}
        print(f"Live agent ready: {self.agent.name} version {self.agent.version}")
        self.reset()

    def reset(self):
        self.conversation_id = self.openai.conversations.create().id
        print("New conversation started.")

    def ask(self, question):
        response = self.openai.responses.create(
            input=question, conversation=self.conversation_id, extra_body=self.agent_ref
        )
        for _ in range(MAX_TOOL_ROUNDS):
            for item in response.output:
                if item.type == "file_search_call":
                    print(f"  [retrieval] file_search queries={list(getattr(item, 'queries', None) or [])}")
            calls = [item for item in response.output if item.type == "function_call"]
            if not calls:
                break
            outputs = []
            for call in calls:
                print(f"  [tool call] {call.name}({call.arguments})")
                result = run_tool_call(call.name, call.arguments)
                print(f"  [tool output] {result}")
                outputs.append({"type": "function_call_output", "call_id": call.call_id, "output": result})
            response = self.openai.responses.create(
                input=outputs, conversation=self.conversation_id, extra_body=self.agent_ref
            )
        return response.output_text

    def close(self):
        self.project.agents.delete_version(agent_name=self.agent.name, agent_version=self.agent.version)
        print(f"Live agent version {self.agent.version} deleted.")


def answer(question, session):
    if session:
        print("  [mode] live Foundry model")
        text = session.ask(question)
    else:
        print("  [mode] rehearsal (deterministic routing, not the model)")
        trace, text = rehearsal_turn(question)
        for line in trace:
            print(f"  {line}")
    print(f"\nAssistant> {text}")


def run_script(session):
    for label, question in PROMPTS.items():
        print(f"\n--- Prompt {label} ---")
        print(question)
        input("Press Enter to ask, or Ctrl+C to stop... ")
        answer(question, session)


def print_help():
    print("Commands: /script, /prompts, /reset (live), /help, /quit")
    print("Anything else is sent to the assistant.")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    live = "--live" in sys.argv[1:]
    print("=" * 60)
    print("Service Desk Helper: Building agents with tools and knowledge")
    print("Mode: " + ("LIVE (Microsoft Foundry)" if live else "REHEARSAL (offline)"))
    print("Synthetic data only. Type /help for commands.")
    print("=" * 60)

    session = LiveSession() if live else None
    try:
        while True:
            try:
                text = input("\nYou> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not text:
                continue
            if text in ("/quit", "/exit"):
                break
            if text == "/help":
                print_help()
            elif text == "/prompts":
                for label, question in PROMPTS.items():
                    print(f"  {label}. {question}")
            elif text == "/script":
                run_script(session)
            elif text == "/reset":
                if session:
                    session.reset()
                else:
                    print("Rehearsal mode has no conversation memory to reset.")
            else:
                answer(text, session)
    finally:
        if session:
            session.close()
        print("\nSession ended.")


if __name__ == "__main__":
    main()
