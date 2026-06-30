rubric v1

# Design-partner fit rubric, Field Lab 01

The customer frame, written down before anything is built, so the target cannot
drift to match whatever the agent happens to produce. The trust core decides
whether a claim is true. This rubric decides whether a true claim fits. The
policy filter (`policy.py`) reads these rules and nothing else.

The founder: seed to Series A B2B SaaS, selling a developer-facing product, no
growth hire, wants a weekly list of qualified design-partner candidates.

## Rules

Each rule has an explicit pass and fail. A record fits only when every rule
passes. A field the trust core did not accept counts as a fail, never a pass.

1. **US-based**
   - pass: `location` resolves to the United States.
   - fail: outside the US, or no accepted location.

2. **Size 50 to 300**
   - pass: `size` carries a headcount and it is between 50 and 300 inclusive.
   - fail: outside the range, or no accepted headcount.

3. **Developer-facing product**
   - pass: `product_type` reads as developer-facing (developer tools, API, SDK,
     CI/CD, platform, infrastructure, observability, and the like).
   - fail: not developer-facing, or no accepted product type.

4. **Engineering-leader contact**
   - pass: `eng_leader_contact` names a person with an engineering-leadership
     title (VP Engineering, Head of Engineering, CTO, Director of Engineering).
   - fail: no such contact, or no accepted contact.

5. **A real reason to reach out now**
   - pass: `reason_to_reach_out` names a recent, specific event (a launch, a
     raise, a hiring push, a public change).
   - fail: generic or absent, or no accepted reason.

## How to change a rule

Freeze the rubric before tuning anything. When a rule turns out wrong, write
`rubric v2` and re-score from scratch. Never edit a rule in place to match what
the agent already produced. That is how you grade your own homework.
