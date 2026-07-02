Triage the complaint below in four steps, then return one JSON object.

1. Extract signals. Note the concrete facts in the narrative: what happened, what
   the consumer tried, what the outcome was, and whether the issue is resolved.

2. Choose exactly one routing team. Route by the primary subject matter, not by
   severity. Use these six values:
   - account_access: login problems, lockouts, account closure, identity
     verification, access restrictions, inability to access funds due to a
     restriction.
   - payments_transfers: payments, transfers, wires, ACH, deposits, withdrawals,
     delayed or failed transfers, missing funds in transit.
   - fraud_disputes: unauthorized transactions, scams, fraud claims, charge
     disputes, dispute-investigation complaints, reimbursement disputes.
   - credit_lending: credit cards, loans, mortgages, interest, fees, debt
     collection, underwriting, repayment, loan servicing.
   - customer_service: poor support, delays, confusing communication,
     unreachable representatives, unresolved service requests with no clearer
     product-specific route.
   - other: only when none of the above fit.

3. Decide the risk flag. Set it true when the narrative suggests serious harm or
   regulatory concern: repeated failure to resolve fraud, inability to access
   essential funds, foreclosure or repossession or severe loss, discrimination or
   fair-lending concerns, privacy or data misuse, the company ignoring a required
   dispute or investigation process, or a regulator threat plus a substantive
   unresolved issue. Use a recall-first posture: when you are uncertain and the
   record contains a substantive regulatory or harm allegation tied to an issue
   the record leaves unresolved, flag it, and a small dollar amount does not by
   itself make a complaint low risk. Apply the calibration rules: tone and legal
   boilerplate alone are not risk, a short narrative can still be high risk, and
   an allegation the record says was already resolved is not high risk.

4. Select evidence. Pick short verbatim quotes copied exactly from the narrative,
   at least one supporting the routing decision and at least one supporting the
   risk decision. Use the source_id from the complaint's sources.

Return exactly this JSON object and nothing else:

{
  "routing_team": "<one of the six values>",
  "risk_flag": true or false,
  "confidence": <number between 0 and 1>,
  "reason": "<one or two sentences grounded in the narrative>",
  "evidence": [
    {"criterion": "routing_team", "source_id": "<source_id>", "quote": "<verbatim quote>"},
    {"criterion": "risk_flag", "source_id": "<source_id>", "quote": "<verbatim quote>"}
  ]
}
