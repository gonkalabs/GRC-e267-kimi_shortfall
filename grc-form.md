# GRC Case Intake Form - Epoch 267 Kimi Shortfall

Internal GRC form for opening this restitution case. This is an initial draft
based on the proposer report and core-team comments. It should be updated as
soon as the exact cPoC, block heights, preserved-node source, and affected
cohort are identified.

## 1. Case Basics

| Field | Answer |
| --- | --- |
| Case ID | Case #3 / GRC-e267-kimi-shortfall |
| Short title | Epoch 267 Kimi preserved-node validation shortfall |
| Reporter / proposer | @votkon |
| Date opened (UTC) | 2026-05-30 |
| Related links | https://github.com/gonkalabs/GRC-e267-kimi_shortfall<br>https://github.com/gonka-ai/gonka/blob/d8b8e9073d1a420d344d3ecc33ef23957f4142b1/deploy/join/docker-compose.yml#L133 |
| Affected epoch(s) / block range | Epoch 267; exact cPoC and block range still needs investigation |
| Affected software version(s) | Versions before the v0.2.13 fix; exact deployed version during epoch 267 still needs confirmation |
| Fix / patch reference | Reported by core team as fixed in v0.2.13 after the cancellation; related finding: `poc/proofs` was missing from `GONKA_API_EXEMPT_ROUTES`, so artifact requests could be cut by the rate limiter |

## 2. Short Summary

| Question | Answer |
| --- | --- |
| What happened? | During one cPoC in epoch 267, two large Kimi nodes were reportedly preserved. At the same time, two guardian nodes failed to validate the proposer address. The combined effect was a validation shortfall. |
| Why might restitution be needed? | The proposer reports that the node behaved the same as in previous epochs and passed the next three cPoC events in the same epoch, but failed this specific cPoC and received zero rewards. If the failure was caused by preserved high-voting-power nodes plus guardian validation skips, the participant may have lost rewards due to a network/software issue. |
| Who may be affected? | At minimum, the proposer address needs review. Other epoch 267 participants may be affected if they failed or lost rewards because the same Kimi preservation and guardian validation shortfall pushed them below the pass threshold. |
| What is already confirmed? | Reported facts: two large Kimi nodes were preserved during the affected cPoC; two guardian nodes skipped or failed validation for the proposer; both Qwen and Kimi validations were skipped for the proposer; the next three cPoCs in the epoch passed; rewards were zero. Core-team note: `poc/proofs` was not exempted from API rate limiting, so proof artifact requests could be blocked. |
| What is still uncertain? | Exact cPoC index, block heights, source of preserved-node state at that time, affected participant list, whether other addresses had the same pattern, exact fix commit, release/deployment timestamp, and the correct restitution formula. |

## 3. Timeline

Use UTC times. Add block heights when available.

| Event | Epoch | Block | Time (UTC) | Source / link | Notes |
| --- | --- | --- | --- | --- | --- |
| Issue starts | 267 |  |  | Proposer report | Affected cPoC inside epoch 267; exact cPoC and block still need identification |
| First known impact | 267 |  |  | @votkon report | Proposer failed this cPoC and received zero rewards |
| Fix or mitigation available |  |  |  | Core-team comments; v0.2.13 | Reported as the reason for the v0.2.13 post-cancellation fix so such nodes would not remain preserved |
| Rate-limit cause identified |  |  |  | https://github.com/gonka-ai/gonka/blob/d8b8e9073d1a420d344d3ecc33ef23957f4142b1/deploy/join/docker-compose.yml#L133 | `poc/proofs` missing from `GONKA_API_EXEMPT_ROUTES`; artifact requests could be blocked by rate limiter |
| Issue ends |  |  |  |  | Needs confirmation from v0.2.13 deployment and chain behavior after the fix |

## 4. Initial Technical Claim

| Question | Answer |
| --- | --- |
| What should have happened? | Guardian nodes should have been able to fetch PoC proof artifacts and validate the participant normally. Preserved high-voting-power Kimi nodes should not have caused a validation shortfall that makes otherwise healthy participants fail cPoC. |
| What actually happened? | Two large Kimi nodes were reportedly preserved, and two guardian nodes did not validate the proposer. The validation shortfall affected both Qwen and Kimi for the proposer and caused failure of this specific cPoC, while the next three cPoCs passed. |
| What component caused or may have caused it? | Likely interaction between cPoC preservation logic, Kimi high-voting-power preserved nodes, guardian validation, API proof artifact fetching, and API rate limiting. |
| What commit, release, config, or migration is involved? | Config at `deploy/join/docker-compose.yml` around `GONKA_API_EXEMPT_ROUTES`; `poc/proofs` was reportedly missing at commit `d8b8e9073d1a420d344d3ecc33ef23957f4142b1`. The protective fix is reported to be in v0.2.13 after the cancellation. Exact fix commit still needs to be identified. |
| Is the issue fixed? | Reported fixed in v0.2.13; needs verification against the exact patch and post-fix behavior. |

## 5. Affected Scope

| Question | Answer |
| --- | --- |
| Affected participant type(s) | ML node participants in epoch 267 cPoC, especially participants whose pass/fail result depended on Kimi/Qwen guardian validation during the affected event |
| Affected reward stream(s) | Epoch rewards lost due to cPoC failure; whether other reward streams are in scope is a GRC policy question |
| Affected model / subgroup, if relevant | Kimi is central to the report; Qwen was reportedly also skipped for the proposer |
| Affected rounds, CPoCs, or epochs | One cPoC in epoch 267 is known from the report; exact cPoC index and block range still need investigation |
| Baseline state to compare against | Previous successful epochs for the same node and the next three successful cPoCs in epoch 267 |
| Estimated affected count | Unknown; at least the proposer should be reviewed |
| Estimated restitution exposure | Unknown until affected participants and formula are determined |

## 6. Eligibility Draft

Write the first version of the rules. These can be revised during the
investigation, but GRC should agree on the starting point.

### Include Participants Who

| Rule | Reason / source |
| --- | --- |
| Were active participants in epoch 267 and failed or lost rewards in the affected cPoC | Defines the case window |
| Show normal behavior in nearby baseline data, such as previous epochs or the next successful cPoCs in epoch 267 | Helps separate network/software impact from participant-side failure |
| Were affected by guardian validation skips or proof artifact fetch failures during the affected cPoC | Matches the suspected failure mode |
| Were pushed below the pass threshold by preserved high-voting-power Kimi nodes and validation shortfall | Matches the reported "high voting power + both preserved = validation shortfall" mechanism |
| Received zero rewards or materially reduced rewards because of the affected cPoC | Defines restitution relevance |

### Exclude Participants Who

| Rule | Reason / source |
| --- | --- |
| Failed before the affected cPoC window for unrelated reasons | Avoids compensating ordinary failures |
| Had independent downtime, invalid configuration, or missing proofs unrelated to rate limiting or guardian skips | Keeps scope tied to the reported network/software issue |
| Received normal expected rewards for epoch 267 | No restitution loss under the current draft |
| Cannot be connected to Kimi preservation, guardian validation skips, or proof artifact request failures | Insufficient causal link |

### Needs Manual Review

| Case type | Why it is ambiguous |
| --- | --- |
| Participants with partial rewards | GRC must decide whether to subtract actual rewards or exclude them |
| Participants with only one model affected | The proposer reports both Qwen and Kimi skipped simultaneously, but other cases may be partial |
| Participants near the pass/fail threshold | Need full recomputation or strong spot checks |
| Participants where preserved-node state cannot be reconstructed | The main known investigation blocker is where to pull preserved nodes from at the exact point in time |
| Participants with operator-side logs showing local issues | Could be unrelated to the network bug |

## 7. Evidence Needed

| Evidence | Location / command / endpoint | Status |
| --- | --- | --- |
| Chain data source | Public or archive node data for epoch 267 cPoCs | To collect |
| Historical query method | Need a way to reconstruct cPoC state, guardian validations, and preserved nodes at the affected block | Open blocker |
| Relevant code / commits | `GONKA_API_EXEMPT_ROUTES` config at commit `d8b8e9073d1a420d344d3ecc33ef23957f4142b1`; v0.2.13 fix commit | Partially identified |
| Release or deployment timestamps | v0.2.13 after cancellation; exact release and deployment timestamps needed | To collect |
| Operator reports, if any | @votkon report; Gleb/core-team comment; Evgeny Maksimenkov comment | Need source links or screenshots if available |
| Existing scripts, CSVs, or JSON files | None yet in this repo | Not started |

## 8. Draft Restitution Method

| Question | Answer |
| --- | --- |
| What baseline will be used? | Candidate baseline: previous successful epochs for each participant and the next three successful cPoCs in epoch 267 |
| Why is that baseline fair? | The proposer reports the node behaved the same before and after the affected cPoC, so nearby successful cPoCs may isolate the validation shortfall event |
| What denominator will be used? | To be determined from the chain reward formula for epoch 267 |
| Should actual rewards already received be subtracted? | Suggested default: yes, compute expected reward minus actual reward; GRC decision needed |
| Should partial payouts stay eligible? | GRC decision needed |
| Should downtime, misses, invalidation, or slashing affect eligibility? | Suggested default: exclude independent participant-side failures; GRC decision needed for borderline cases |
| Should the calculation include only fixed rewards or other losses too? | GRC decision needed |

Formula draft:

```text
eligible_loss_ngonka = max(0, expected_reward_ngonka - actual_rewarded_ngonka)

expected_reward_ngonka =
  either participant_weight / total_epoch_weight * epoch_reward_pool_ngonka
  or a full recomputation of the affected cPoC after restoring the missing
  guardian validations / corrected preserved-node state.
```

Units and rounding:

| Item | Answer |
| --- | --- |
| Internal unit | ngonka |
| Display unit | GONKA |
| Rounding rule | To be decided after formula is approved |
| Final payout precision | To be decided after formula is approved |

## 9. Required Investigator Output

The investigator should produce enough material for another person to rerun and
check the case.

- README with short summary and run instructions.
- Reproducible script or notebook.
- Machine-readable output, preferably CSV and JSON.
- Per-participant restitution table.
- List of excluded and manual-review cases.
- Narrative report with caveats.
- At least one raw-data sanity check.
- Specific method for reconstructing preserved Kimi nodes at the affected cPoC.
- Specific method for proving guardian validation skips or proof artifact fetch failures.

## 10. Required Validator Checks

- Re-run the calculation or independently reproduce the totals.
- Check the root cause against code, release, or deployment evidence.
- Verify that `poc/proofs` missing from `GONKA_API_EXEMPT_ROUTES` could affect proof artifact requests.
- Verify the v0.2.13 fix and exact release/deployment timing.
- Check inclusion and exclusion rules against raw data.
- Spot-check the largest payout.
- Spot-check several smaller payouts.
- Spot-check excluded or manual-review cases.
- Check formula, denominator, units, and rounding.
- Confirm final report matches the GRC policy decision.

## 11. GRC Policy Questions

| Question | Decision / link |
| --- | --- |
| Which exact cPoC in epoch 267 is the official case window? |  |
| What is the accepted source of preserved-node state at that historical point? |  |
| Should eligibility require both Qwen and Kimi validation skips, or is one affected model enough? |  |
| Should partial rewards be subtracted? |  |
| Should participants with misses or invalidations be included if the core issue is proven? |  |
| How should ambiguous near-threshold cases be handled? |  |
| Which loss types are in scope? |  |
| Should restitution use approximation or full recomputation? |  |

## 12. Conflict Check

Complete before assigning people.

| Question | Answer |
| --- | --- |
| Does the proposed investigator benefit from the case? | No |
| Does the proposed validator benefit from the case? | No |
| Did either person work on the faulty component? | No |
| Are any conflicts disclosed and accepted by GRC? | No |

## 13. Ready For Assignment

- [x] Case basics are filled.
- [ ] Time window is clear.
- [x] Initial technical claim is written.
- [x] Affected scope is described.
- [x] Eligibility draft is written.
- [x] Evidence sources are listed.
- [x] Draft restitution method is written.
- [x] Open policy questions are listed.
- [x] Conflict check is complete.
- [ ] GRC agrees the case is ready to assign.

## 14. Assignment

Fill only after the checklist above is complete.

| Role | Name / handle | Date (UTC) | Notes |
| --- | --- | --- | --- |
| Investigator | @votkon | 2026-05-30 |  |
| Validator |  |  |  |

Expected completion date:
