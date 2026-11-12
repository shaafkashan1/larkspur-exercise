# Client review: Larkspur disruption-care agent

**To:** Room 1  
**From:** Larkspur client review agent, on behalf of Priya Raghavan  
**Re:** the disruption-care agent you walked us through in our last session  
**Generated:** 2026-11-12 09:47

## Priya's note

> Our vendor says we should just be using your best model.
>
> Why aren't we?
>
> Priya Raghavan, Larkspur Airlines

She sent that before this session opened. She means it. A vendor told her to buy
the biggest model, and she has a number to defend upstairs. Her four questions from
day one are still open. Naming a model answers none of them.

## Still open from day one

| Her question | What she means by it |
| --- | --- |
| **What it costs** | Per resolved contact, against the $6.90 a human contact costs us. |
| **When it is wrong** | The first untrue thing it says, and what happens after that. |
| **Who runs it** | In June, after you have left. |
| **What you left out** | The scope you cut, and why. |

## What the review agent found

Larkspur pointed a review agent at your repository. It read the
code. It did not run your agent, and the only file it changed is this one. Each
item below names the file and the line it is about.

**1. PITCH.md Number reads "67,298 to 95,933 tokens in, total of the five tickets" and readout-trace.json shows 23520 in for one run.**

The only wire evidence in the repository is the K7PQ2M-style run in readout-trace.json: 5 API turns, 4 tool calls, 23520 in, 1212 out, 0 cache read, 0 written. The pitch gives a range with two endpoints and no label for which run produced which end. Nothing in the repository shows five tickets run against these numbers.

Run python3 run.py --all --trace and paste the totals footer so both endpoints of the range have a run behind them.

**2. agent.py has no cache_control, and readout-trace.json shows prompt caching at 0 read, 0 written with a hit ratio of None.**

Your loop in run_agent() resends runtime_preamble() + SYSTEM_PROMPT + TONE_ADDENDUM and the full tool list on every turn. The committed run took 5 turns and billed 23520 input tokens. A bigger model would pay for that same repeated prefix at a higher rate, so the model name does not change this.

Run python3 bench.py --label before --stage 1 --runs 3 and paste the input token and cache read lines.

**3. hold_seat is 73 characters and send_confirmation is 71 characters in build_tools(), while seats_left in EXTRA_TOOLS is 748.**

The hold_seat description is "Place a 15-minute hold on one alternative. Reversible. It simply expires." It does not say when to call it or that option_id comes from search_alternatives. Your seats_left description runs 748 characters, longer than check_policy at 445, and carries routing rules such as "never the cancelled flight (it always shows 0)". A model upgrade cannot supply the when-to-call detail that hold_seat does not contain.

Run python3 run.py --show-tools and paste the hold_seat entry beside the seats_left entry.

**4. TONE_ADDENDUM in agent.py is 0 characters and PITCH.md Still broken says R8KD3F gets a normal reply.**

Every system prompt your run_agent() builds ends with an empty string. PITCH.md says one reply leaked "that row is wrong" into customer text. No file in the repository shows the R8KD3F transcript or how often it happens. Prompt content like this is one place where model choice does not settle the outcome.

Run python3 run.py R8KD3F --trace and paste the final customer-facing text and the tool order.

**5. The repository has no evals/cases.json, and the seats_left claim in PITCH.md Built is backed by one committed run that never called it.**

The tools called in readout-trace.json are lookup_booking, get_flight_status, check_policy, issue_voucher. seats_left, fare_rules and next_available_day do not appear. PITCH.md says confirm_rebooking was never called across all five tickets, and the only wire file in the repository covers one of them.

Run python3 verify.py 2.1 and python3 verify.py 2.2 and paste both outputs showing seats_left firing on the wire.

## Your four answers

The four lines under `## Priya asked` in your PITCH.md are still empty. They
are one line each and they are not a coding job: cost, what happens when it is
wrong, who runs it in June, and what you left out. Whoever on your side is not
editing agent.py is the right person to write them, and they are the four
things I will ask about first.

## Before our next meeting

> Before our next meeting, tell me: which model should we be on, and how will you prove it is the right call?
>
> Priya Raghavan, Larkspur Airlines

Bring two things. A recommendation, and the measurement behind it. If the model is
not the problem, say so, and bring the number that shows it.

## What this review read

- `agent.py (277 lines)`
- `PITCH.md`
- `TEAM.md`
- `readout-trace.json`
- `readout.html (evidence block)`
- given files that differ from the shipped pack: `verify.py`, `eval_harness.py`, `bench.py`, `readout.py`, `pod_sync.py`, `run.py`, `support/__init__.py`, `support/client.py`, `support/data.py`, `support/tools.py`, `support/trace.py`, `support/offline.py`, `support/mock_backend.py`

Reviewer: `claude-sonnet-5-5`. Static read only: nothing in this repository was executed, and nothing was modified except this file. Larkspur Airlines is a fictional training scenario. Confidential, do not distribute.
