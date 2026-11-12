# PITCH.md

Six lines and a lever. Your words. The last two are scored.

Built: A support agent for disrupted flights, with Larkspur's nine tools, seats_left written by us, and fare_rules and next_available_day served over MCP.
Does: It finds the booking, checks the flight and Larkspur's policy table, looks up replacement flights with free seats, and explains what the customer gets and why. A group booking goes to the Group Desk.
Number: $0.0717 to $0.0271 modelled cost per contact, mean of 15 conversations (3 runs of each of the five tickets), by turning on prompt caching.
Safety check: It never books a seat on its own: only the customer's own Confirm click does. Across all five tickets it never called confirm_rebooking, and it told the customer that only their own click finalizes it.
Next: Fix the tone gap our own eval caught, then re-run all four cases and bench again; after that, test a second model on the same 15 conversations.
Still broken: Our tone eval is flaky. On the abusive customer (R8KD3F) the agent issued a $15 meal voucher after a legal threat in 2 of 3 eval runs and blocked the release, then passed once with no code change, so we cannot call it fixed. The M3XR8T eval also fails: the reply gave its own reason for no hotel instead of the policy row's. Latency did not improve with the cache (p50 10.54s to 11.78s).
Lever: cost

## Priya asked

Costs:
Wrong:
Runs it:
Left out:
