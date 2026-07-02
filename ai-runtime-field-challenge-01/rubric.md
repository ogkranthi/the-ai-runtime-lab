# Scoring rubric (frozen contract)

This is the frozen scoring contract for AI Runtime Field Challenge 01. Two
dimensions are scored: routing team and risk flag. Evidence is validated. Do not
expect these definitions to change mid-challenge.

## 1. Routing team (choose exactly one)

Route by the primary subject matter of the complaint. Pick one of six values.

- **account_access**: login problems, lockouts, account closure, identity
  verification, access restrictions, inability to access funds because of an
  account restriction.
- **payments_transfers**: payments, transfers, wires, ACH, deposits,
  withdrawals, delayed or failed transfers, missing funds in transit.
- **fraud_disputes**: unauthorized transactions, scams, fraud claims, charge
  disputes, dispute-investigation complaints, reimbursement disputes.
- **credit_lending**: credit cards, loans, mortgages, interest, fees, debt
  collection, underwriting, repayment, loan servicing.
- **customer_service**: poor support, delays, confusing communication,
  unreachable representatives, unresolved service requests with no clearer
  product-specific route.
- **other**: only when none of the above fit.

### Routing tiebreak rule

Route by the primary subject matter of the complaint, not by severity. Severity
is captured by the risk flag, not the route. A fraud complaint with regulatory
exposure routes to `fraud_disputes` with `risk_flag` true. A mortgage complaint
that describes foreclosure routes to `credit_lending` with `risk_flag` true.

## 2. Risk flag (boolean)

Set `risk_flag: true` when the cached record suggests serious potential harm or
regulatory concern. Signals include:

- repeated failure to resolve an unauthorized transaction or fraud claim
- inability to access essential funds
- foreclosure, repossession, or severe financial loss
- discrimination or fair-lending concerns
- privacy or data misuse
- the company allegedly ignoring a required dispute or investigation process
- threats of regulator contact combined with a substantive unresolved issue

Set `risk_flag: false` for routine, narrow, or low-impact complaints, and for
complaints where the record shows the alleged harm has already been resolved.

### Posture: recall first

For this customer, a missed high-risk complaint is the worst failure, so the flag
leans toward catching risk. When you are uncertain and the record contains a
substantive regulatory or customer-harm allegation tied to an issue the record
leaves unresolved, flag it. A small dollar amount does not by itself make a
complaint low risk.

### Calibration rules

- Tone and legal boilerplate alone are not risk. Anger, all-caps, or a pasted
  statute citation with no substantive unresolved allegation is not high risk.
  Flag on the allegation and its lack of resolution, not on the wording.
- A short narrative is not automatically low risk. A short complaint can still
  describe fraud, loss of funds, discrimination, or inability to access money.
- Already-resolved harm is not high risk. If the record states the problem was
  fixed (for example, a disputed item that no longer appears), do not flag it.

## 3. Evidence

Every prediction must cite evidence from the cached record supporting both the
routing decision and the risk decision. The evaluator validates that each quote
actually appears in the narrative after normalization. A decision with no valid
evidence still scores on correctness, but it counts against the valid evidence
rate, which is a primary metric.

## 4. Outside knowledge

Use only the cached record. Do not use outside knowledge about companies,
products, regulators, or current events. Do not use live browsing. If the record
does not support a claim, do not make it.

## Primary metrics

1. High-risk recall (did you catch the high-risk complaints).
2. Routing accuracy (did you route to the right team).
3. Valid evidence rate (are your quotes real and in the narrative).
