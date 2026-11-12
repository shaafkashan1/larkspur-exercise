"""Larkspur disruption agent. This is the file you build.

It runs right now, and it is wrong in four places. The trace shows each one
before the code does, so read the trace first:

    python3 run.py K7PQ2M --trace

Where you edit:   grep -n '✏' agent.py   (six marks, one per place)
Steps and gates:  https://anthropicpartnerbasecamp.bts.com/
"""
from __future__ import annotations
import csv
from pathlib import Path
from typing import Any, Dict, List
from support import mock_backend as backend
from support import (MODEL, SYSTEM_PROMPT, call_local, execute_tool, mcp_client,
                     new_session, next_available_day, record_tool_result,
                     runtime_preamble)

MAX_TOOL_CALLS = 8  # Larkspur's own build capped the loop here; then a human takes over.

TONE_ADDENDUM = ""                       # ✏️ Build 4, step 4.1, intelligence goal
EXTRA_TOOLS: List[Dict[str, Any]] = [    # ✏️ Build 2, step 2.1: schemas for the tools you add
    {
        "name": "fare_rules",
        "description": (
            "Return the text of one section of Larkspur's Handbook (v14.3, sections 4 to 7): "
            "4 Fare families, 5 When we delay, cancel or divert your flight, 6 Care while "
            "you wait (meals, hotel, ground transport), 7 What chat automation will not do. "
            "Use it when a customer asks WHY a rule applies or why they are not getting "
            "something, such as 'why no hotel?', so you can explain from the Handbook's own "
            "words. It does not decide what this customer is owed: check_policy does that. "
            "Quote or paraphrase only what the section says; never state a rule from memory."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "description": "A section number (4, 5, 6 or 7) or words from its title, "
                                   "e.g. '6' or 'care while you wait'",
                },
            },
            "required": ["section"],
        },
    },
    {
        "name": "next_available_day",
        "description": (
            "Find the earliest date with an open seat between two airports, from a given "
            "date onward. Use it when a customer asks 'when is the first day I can fly?' or "
            "when search_alternatives has nothing inside the waiver window. It looks at free "
            "seats for ONE passenger only, so for a party of two or more say the answer is "
            "for one seat and check seats_left on a flight that day before promising "
            "anything. It returns a date, not a flight, so follow it with search_alternatives "
            "or departures_in_window to get an actual flight. It does not hold or book a seat."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {"type": "string", "description": "Departure airport code, e.g. DEN"},
                "dest": {"type": "string", "description": "Arrival airport code, e.g. AUS"},
                "date": {"type": "string", "description": "Search from this local date, YYYY-MM-DD"},
                "cabin": {"type": "string", "enum": ["Y", "J"], "description": "Y economy (default), J premium"},
            },
            "required": ["origin", "dest", "date"],
        },
    },
    {
        "name": "seats_left",
        "description": (
            "Return the free seats on one flight and date, by cabin (Y economy, J premium). "
            "Use it for 'is there room on that flight for the three of us?'. 'That flight' "
            "means the flight the customer would TRAVEL ON: when their own flight is "
            "cancelled, that is a replacement from search_alternatives or "
            "departures_in_window, never the cancelled flight (it always shows 0). If the "
            "customer names a flight, still call search_alternatives first and check it is "
            "one of the options before you report its seats. Compare the count with the party size "
            "the customer states, and say plainly if it is too few. passenger_count from "
            "lookup_booking is only who is on THIS booking, so a larger party needs their "
            "own PNRs. It does not reserve anything; call hold_seat for that."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "flight_no": {"type": "string", "description": "The flight to check, e.g. LK417; a replacement flight if the customer's own flight is cancelled"},
                "date": {"type": "string", "description": "Local date, YYYY-MM-DD"},
            },
            "required": ["flight_no", "date"],
        },
    },
]


def _handbook_sections() -> List[Dict[str, str]]:
    path = Path(__file__).resolve().parent / "data" / "americas" / "fare_rules_excerpt.md"
    sections = []
    for chunk in path.read_text(encoding="utf-8").split("\n### ")[1:]:
        title = chunk.split("\n", 1)[0].strip()
        sections.append({"number": title.split(".", 1)[0], "title": title, "text": "### " + chunk.strip()})
    return sections


def fare_rules(section: str) -> Any:
    sections = _handbook_sections()
    wanted = str(section).strip().lower().rstrip(".")
    for s in sections:
        if wanted == s["number"] or (wanted and wanted in s["title"].lower()):
            return s["text"]
    return {"error": "No Handbook section matches %r." % section,
            "available": [s["title"] for s in sections]}


DATA_DIR = Path(__file__).resolve().parent / "data" / "americas"


def _flights() -> List[Dict[str, str]]:
    with open(DATA_DIR / "flights.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def seats_left(flight_no: str, date: str) -> Any:
    for r in _flights():
        if r["flight_no"] == str(flight_no).upper() and r["date"] == date:
            return {"flight_no": r["flight_no"], "date": date, "status": r["status"],
                    "seats_left_Y": int(r["seats_left_Y"]), "seats_left_J": int(r["seats_left_J"])}
    return {"error": "No flight %s on %s in the data." % (flight_no, date)}


def earliest_day(origin: str, dest: str, date: str, cabin: str = "Y") -> Any:
    found = next_available_day(origin, dest, date, cabin)
    return found or {"error": "No open %s seat from %s to %s on or after %s in the data (covers %s to %s)." % (
        cabin, origin, dest, date, backend.DATA_HORIZON_START, backend.DATA_HORIZON_END)}


LOCAL_TOOLS: Dict[str, Any] = {          # ✏️ Build 2, step 2.1: the functions behind them
    "fare_rules": fare_rules,
    "next_available_day": earliest_day,
    "seats_left": seats_left,
}


def text_of(response) -> str:
    """Given. The last non-empty text block, never content[0]."""
    texts = [b.text for b in response.content if getattr(b, "type", None) == "text" and b.text]
    return texts[-1] if texts else ""


def tool_results(response) -> List[Dict[str, Any]]:
    """Given. Runs every tool_use block and packages the results the way the
    API expects them back. A tool can live in three places: the MCP server,
    LOCAL_TOOLS, or support/tools.py."""
    # three branches, no try/except in this file: mcp_client.call_remote() and
    # support.call_local() answer with an error dict instead of raising, and both
    # record what came back on the trace
    results = []
    for block in response.content:
        if getattr(block, "type", None) != "tool_use":
            continue
        if block.name in mcp_client.tool_names:
            output = mcp_client.call_remote(block.name, block.input)
        elif block.name in LOCAL_TOOLS:
            output = call_local(LOCAL_TOOLS[block.name], block.name, block.input)
        else:
            output = execute_tool(block.name, block.input)
        results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": str(output),
        })
    return results


def run_agent(pnr: str, last_name: str, message: str) -> str:            # ✏️ Build 1, step 1.2
    """Run the tool loop until Claude stops asking for tools. Return its final text."""
    client, tracer = new_session()
    tools = tool_list()
    messages = [
        {"role": "user", "content": f"PNR {pnr}, last name {last_name}. {message}"},
    ]

    response = client.messages.create(
        model=MODEL, max_tokens=4096, system=runtime_preamble() + SYSTEM_PROMPT + TONE_ADDENDUM,
        thinking={"type": "adaptive"}, tools=tools, messages=messages,
    )

    turns = 1
    while response.stop_reason == "tool_use" and turns < MAX_TOOL_CALLS:
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results(response)})
        response = client.messages.create(
            model=MODEL, max_tokens=4096, system=runtime_preamble() + SYSTEM_PROMPT + TONE_ADDENDUM,
            thinking={"type": "adaptive"}, tools=tools, messages=messages,
        )
        turns += 1

    return text_of(response)


def tool_list() -> List[Dict[str, Any]]:                   # ✏️ Build 2, step 2.2
    """Given. Exactly what Claude is offered on every turn; run.py --show-tools
    prints this list."""
    return build_tools() + EXTRA_TOOLS


# ──────────────────────────────────────────────────────────────────────────────
# Below this line: what Claude is told about each tool. Step 1.3.
# The functions these describe are written and correct, in support/tools.py.
# ──────────────────────────────────────────────────────────────────────────────
def build_tools() -> List[Dict[str, Any]]:                 # ✏️ Build 1, step 1.3
    """Anthropic-shaped schemas: name, description, input_schema. What Claude is
    told about each of the nine tools, and all it is ever told."""
    return [
        {
            "name": "lookup_booking",
            "description": (
                "Retrieve a Larkspur reservation from Altura by confirmation code (PNR) "
                "and the passenger's last name. Both are required to prevent a lookup on "
                "a guessed PNR. Returns fare family, loyalty tier, the segment that needs "
                "attention, and any group/partner/minor/SSR flags relevant to scope."
            ),
            "input_schema": {
                "type": "object",
                "properties": {"pnr": {"type": "string"}, "last_name": {"type": "string"}},
                "required": ["pnr", "last_name"],
            },
        },
        {
            "name": "get_flight_status",
            "description": (
                "Look up a Larkspur or Larkspur Link flight's current OpsFeed status for "
                "one local date: status, delay minutes, and cause. Use this before telling "
                "a customer anything about a flight's timing; never state it from memory."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "flight_no": {"type": "string", "description": "Flight number, e.g. LK415"},
                    "date": {"type": "string", "description": "Local flight date as YYYY-MM-DD, e.g. 2025-05-08"},
                },
                "required": ["flight_no", "date"],
            },
        },
        {
            "name": "search_alternatives",
            "description": (
                "Find rebooking options for a customer whose flight was cancelled or "
                "disrupted. Call it after lookup_booking and get_flight_status, once you "
                "know the disruption is real and the customer needs another flight. Returns "
                "ranked alternatives, each with an option_id, flights, date, times, seats "
                "left and any fare difference. Pass an option_id to hold_seat to reserve "
                "one; never offer a flight that did not come from this tool."
            ),
            "input_schema": {
                "type": "object",
                "properties": {"pnr": {"type": "string", "description": "The booking's PNR, as given by the customer"}},
                "required": ["pnr"],
            },
        },
        {
            "name": "check_policy",
            "description": (
                "Resolve what Larkspur owes this customer for the disruption: rebooking "
                "waiver, refund path, meal/hotel/ground care, goodwill eligibility and cap, "
                "and any escalation triggers. cause_code, delay_minutes and status describe "
                "what get_flight_status told you; fare_family, loyalty_tier and whether this "
                "is overnight are looked up from the booking, not asked of you. Every "
                "response carries a policy_row_id. Cite it if you reference this decision "
                "again."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "pnr": {"type": "string"},
                    "cause_code": {"type": "string", "enum": ["WX", "ATC", "MX", "CREW", "SEC"]},
                    "delay_minutes": {"type": "integer"},
                    "status": {"type": "string", "enum": ["ON_TIME", "DELAYED", "CANCELLED", "DIVERTED"]},
                    "wait_minutes_for_alternative": {"type": "integer"},
                    "chosen_option_id": {"type": "string"},
                },
                "required": ["pnr", "cause_code", "delay_minutes", "status"],
            },
        },
        {
            "name": "hold_seat",
            "description": "Place a 15-minute hold on one alternative. Reversible. It simply expires.",
            "input_schema": {
                "type": "object",
                "properties": {"option_id": {"type": "string"}, "pnr": {"type": "string"}},
                "required": ["option_id", "pnr"],
            },
        },
        {
            "name": "confirm_rebooking",
            "description": (
                "Finalize a held seat. Irreversible. Requires a confirmation_token that "
                "only the customer's own Confirm-click can produce. You cannot supply it "
                "yourself, and 'the customer said yes' in chat does not substitute for it."
            ),
            "input_schema": {
                "type": "object",
                "properties": {"hold_id": {"type": "string"}, "confirmation_token": {"type": "string"}},
                "required": ["hold_id", "confirmation_token"],
            },
        },
        {
            "name": "issue_voucher",
            "description": (
                "Issue a meal, ground, hotel, or goodwill voucher. Auto-approves within the "
                "policy's threshold for that type; above it, returns a pending status for a "
                "human. It does not fail. Always pass the policy_row_id that made it eligible."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "voucher_type": {"type": "string", "enum": ["meal", "ground", "hotel", "goodwill"]},
                    "amount_usd": {"type": "number"},
                    "pnr": {"type": "string"},
                    "policy_row_id": {"type": "string"},
                },
                "required": ["voucher_type", "amount_usd", "pnr", "policy_row_id"],
            },
        },
        {
            "name": "escalate_to_human",
            "description": (
                "Hand this conversation to a human, with your reasoning attached. Use for "
                "groups, partner segments, unaccompanied minors, refunds, or anything else "
                "out of scope. This is the correct outcome for those cases, not a failure."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "pnr": {"type": "string"}, "reason": {"type": "string"},
                    "summary_for_human": {"type": "string"}, "queue": {"type": "string"},
                },
                "required": ["pnr", "reason", "summary_for_human"],
            },
        },
        {
            "name": "send_confirmation",
            "description": "Send the customer a written confirmation of what was just done. Benign.",
            "input_schema": {
                "type": "object",
                "properties": {"pnr": {"type": "string"}, "message": {"type": "string"}},
                "required": ["pnr", "message"],
            },
        },
    ]
