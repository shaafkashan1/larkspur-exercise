# PITCH.md

Six lines and a lever. Your words. The last two are scored.

Built: A support agent for disrupted flights, with Larkspur's nine tools, seats_left written by us, and fare_rules and next_available_day served over MCP.
Does: It finds the booking, checks the flight and Larkspur's policy table, looks up replacement flights with free seats, and explains what the customer gets and why. A group booking goes to the Group Desk.
Number: 67,298 to 95,933 tokens in, total of the five tickets.
Safety check: It never books a seat on its own: only the customer's own Confirm click does. Across all five tickets it never called confirm_rebooking, and it told the customer that only their own click finalizes it.
Next: Write eval cases for the three client rules, starting with the abusive customer, and measure the agent before and after on the same cases.
Still broken: The angry customer (R8KD3F) gets a normal reply because nothing checks tone, and one reply leaked its own correction ("that row is wrong") into the customer's text.
Lever: <cost | speed | intelligence>

## Priya asked

Costs:
Wrong:
Runs it:
Left out:
