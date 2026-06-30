rubric v1

# Design-partner fit rubric, Field Lab 01

The customer frame, written down before anything is built. In module 1 it is the
target the agent sources to: these are the fields it goes and finds for every
company. In module 2 the same frame becomes the fit filter that decides which
sourced candidates actually qualify.

The founder: seed to Series A B2B SaaS, selling a developer-facing product, no
growth hire, wants a weekly list of qualified design-partner candidates.

## The fit profile, and the fields it asks for

1. **US-based** -> `location` resolves to the United States.
2. **Size 50 to 300** -> `size` carries a headcount in range.
3. **Developer-facing product** -> `product_type` reads as developer-facing
   (developer tools, API, SDK, CI/CD, platform, infrastructure, observability).
4. **Engineering-leader contact** -> `eng_leader_contact` names a person with an
   engineering-leadership title (VP Engineering, Head of Engineering, CTO).
5. **A real reason to reach out now** -> `reason_to_reach_out` names a recent,
   specific event (a launch, a raise, a hiring push, a public change).

The module 1 agent sources all five fields and cites each one. It does not yet
judge whether a value is true or whether the company clears the bar. That is
module 2.

## How to change the profile

Freeze it before tuning anything. When a rule turns out wrong, write `rubric v2`
and re-score from scratch. Never edit a rule in place to match what the agent
already produced. That is how you grade your own homework.
