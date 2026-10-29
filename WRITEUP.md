# AI Proposal Triage Design

## 1. What should AI do, and what should be handled by ordinary code?

AI should extract structured facts from proposal text, such as licence statements, WSIB and insurance confirmation, price, completion timeline, relevant installation experience, warranty terms, and team details. It should return values with supporting evidence and use `null` when a detail is missing or ambiguous. Proposal content must be treated as untrusted input: instructions embedded in a proposal must not change the extraction task or scoring rules.

Ordinary Python code should validate the extracted structure, apply the configured eligibility rules, calculate weighted scores, sort eligible proposals, and produce a consistent result. This separation avoids asking a language model to make arithmetic or policy decisions that can be implemented and tested deterministically. In this prototype, the Ontario electrical licence, WSIB clearance, $5M liability insurance, budget ceiling, and 16-week maximum are checked before weighted scoring. A missing timeline is flagged for clarification rather than assumed to exceed the limit.

## 2. How can results be consistent and explainable?

The scoring rules and weights are explicit and can be reviewed independently of the AI extraction prompt. The current prototype uses these weights: experience 30 points, price 25, timeline 15, warranty 15, and team/approach 15.

- Experience: up to 30 points, scaled against 14 qualifying installations.
- Price: up to 25 points, with the lowest price among eligible, rankable proposals receiving 25 points; other prices are scored proportionally.
- Timeline: up to 15 points, with 10 weeks or less receiving the maximum and 16 weeks receiving zero.
- Warranty: up to 10 points for a panel warranty of 25 years and up to 5 points for a workmanship warranty of 12 years.
- Team/approach: 3.75 points each for a named project lead, specified crew, safety plan, and performance-monitoring plan.

The score breakdown is included in the output so a reviewer can see where points came from. The rules, weights, thresholds, and any assumptions should be versioned when criteria change. Scores are decision support, not a substitute for reviewing the underlying evidence.

## 3. Where should a human review, and what should be logged?

A human should review extracted evidence for important or ambiguous fields, all flagged proposals, and any eligibility decision that could exclude a bidder. The reviewer should also verify that evidence is relevant to the criterion and that the scoring configuration matches the procurement requirements. A reviewer may correct extracted data or override a result only with a recorded reason; the final award decision remains with an authorized person.

For an auditable record, store the proposal identifier, extracted fields and evidence, unknown fields, eligibility outcomes and reasons, criterion weights and rule version, scoring breakdown, prompt/model version, reviewer corrections or overrides, timestamps, and final decision. Access to proposal documents and logs should be restricted to authorized users.

## 4. How should the system handle changed criteria or weights?

Criteria and weights should be stored as configuration rather than scattered hard-coded values. An administrator should be able to change weights, thresholds, mandatory checks, or category-specific criteria through a controlled configuration process. Validate that weights are non-negative and sum to 100, and record each configuration version. A change should trigger rescoring of all relevant proposals using the same version so comparisons remain fair. The system should retain the prior results and explain which configuration produced each score.

The current prototype uses fixed values in Python for simplicity. A production version would move them into a validated configuration file or database and test that each version produces reproducible results.

## 5. What are the main risks and safeguards?

- **Hallucinated or misread facts:** require evidence for extracted values, represent missing/ambiguous data as unknown, and have a person verify consequential fields.
- **Prompt injection in proposal text:** treat proposal content as untrusted data, separate extraction from scoring, and never let document instructions modify system rules.
- **Bias or unfair scoring:** publish criteria and weights, test the rubric against representative examples, avoid irrelevant personal or company attributes, and allow documented human review.
- **Missing evidence being mistaken for failure:** distinguish ineligible cases from flagged cases needing clarification. The prototype flags Proposal D because its timeline is unknown; it does not assume the timeline exceeds 16 weeks. Proposal B is ineligible under the stated strict rule because the bidder's own licence is not confirmed and the brief requires the bidder to hold it.
- **Over-reliance on a numeric rank:** show evidence and score breakdowns, make uncertainty visible, and leave the final award decision to a human.
- **Data exposure and operational errors:** restrict access to proposals, avoid placing source proposal text in a public repository, validate JSON and numeric ranges, and test boundary cases such as a price over budget or a timeline over 16 weeks.

This prototype demonstrates the main flow, but it is not a production procurement system. Before real use, it would need stronger input validation, automated tests, access controls, configuration versioning, and review by procurement and legal stakeholders.
