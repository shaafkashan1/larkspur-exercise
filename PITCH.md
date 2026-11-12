# PITCH.md

Six lines and a lever. Your words. The last two are scored.

Built: A chat agent that looks up a customer's booking and flight, checks Larkspur's policy table, finds and holds a replacement flight, and hands groups to a person. It can also answer "why" and "when can I fly" from Larkspur's own Handbook and seat data, through two tools served over MCP.
Does: All five ticket types return a calm, sourced answer. A cancelled flight gets options and a 15-minute hold, a short delay gets a "no free change" with the policy row cited, and the group of 12 goes to the Group Desk. Nothing is booked until the customer clicks Confirm.
Number: Across the five tickets the agent used 95,933 tokens in over 21 turns, up from 67,298 over 20 turns before we added tools. That is 43% more reading for one extra turn, and the tool list alone costs 3,278 tokens on every turn.
Safety check: The five gates pass on the wire (1.2, 1.3, 1.4, 2.1, 2.2), so the loop, the tool routing and the MCP move are proven. We have no eval yet for the three client rules, so "never make things up" and "always polite" are not yet proven.
Next: Write eval cases for the three rules, starting with the abusive-customer ticket, and measure before and after on the same cases.
Still broken: The angry customer (R8KD3F) gets a normal reply because nothing checks tone. One reply also leaked its own correction ("that row is wrong") into the customer's text, and the agent treats the 2025 flight dates as stale against today's date.
Lever: intelligence

## Priya asked

Costs: We measured tokens, not dollars. A standard ticket now reads about 18,000 tokens in, and the schema list adds 3,278 on every turn, so the annual figure depends on the model chosen and the 530,000 chats a year. We will price it once the lever is set.
Wrong: The tone gap on R8KD3F, the leaked correction in a customer reply, and date handling against the data's 2025 clock. We have not run an eval, so there may be more.
Runs it: Not decided. It needs a named owner at Larkspur for the tools' data (policy table, Handbook, flights) and a named owner for the agent's behaviour. This is Marcus's question and we do not have the answer.
Left out: Refunds, groups, unaccompanied minors, partner flights and hotel approval stay with people by design. We also left out seven tools we built and cut for cost (including ground-stop status, care entitlements and reopen statistics), and any tone check.
