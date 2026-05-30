# GRC Case Intake Form - Epoch 267 Kimi Shortfall

Internal GRC form for this restitution case. Updated with the first
chain-only investigation pass. The audit uses only direct chain data from
node1, node2, node3, and node4.

## 1. Case Basics

| Field | Answer |
| --- | --- |
| Case ID | Case #3 / GRC-e267-kimi-shortfall |
| Short title | Epoch 267 Kimi preserved-node validation shortfall |
| Reporter / proposer | @votkon |
| Date opened (UTC) | 2026-05-26 |
| Related links | https://github.com/gonkalabs/GRC-e267-kimi_shortfall<br>https://github.com/gonka-ai/gonka/blob/d8b8e9073d1a420d344d3ecc33ef23957f4142b1/deploy/join/docker-compose.yml#L133 |
| Affected epoch(s) / block range | Epoch 267, cPoC #1 at trigger height `4122271`; comparison cPoCs at `4130085`, `4133665`, and `4134529` |
| Affected software version(s) | Versions before the v0.2.13 fix; exact deployed version during epoch 267 still needs confirmation |
| Fix / patch reference | Reported by core team as fixed in v0.2.13 after the cancellation; related finding: `poc/proofs` was missing from `GONKA_API_EXEMPT_ROUTES`, so artifact requests could be cut by the rate limiter |

## 2. Short Summary

| Question | Answer |
| --- | --- |
| What happened? | During one cPoC in epoch 267, two large Kimi nodes were reportedly preserved. At the same time, two guardian nodes failed to validate the proposer address. Direct chain data shows Kimi failed by validation-weight plus guardian shortfall; Qwen had a weight shortfall but passed by guardian protection. |
| Why might restitution be needed? | The proposer reports that the node behaved the same as in previous epochs and passed the next three cPoC events in the same epoch, but failed this specific cPoC and received zero rewards. If the failure was caused by preserved high-voting-power nodes plus guardian validation skips, the participant may have lost rewards due to a network/software issue. |
| Who may be affected? | The full-case direct-chain audit confirms one restitution victim: `gonka1j7x6dv42xehe9e5au4ku3wvzwtqlegfjhlvzj6`. Related guardian-skip and Kimi non-voting source candidates are listed in `output/case3_full_case_matrix.csv`, but they do not match the described victim pattern. |
| What is already confirmed? | Direct chain data shows the participant submitted cPoC #1, had Qwen `pass_guardian`, had Kimi `weight_and_guardian_shortfall`, received zero epoch reward, and passed the next three cPoCs. Core-team note: `poc/proofs` was not exempted from API rate limiting, so proof artifact requests could be blocked. |
| What is still uncertain? | The direct chain endpoints used in the audit do not expose an explicit historical "preserved" label at height `4122271`. Exact fix commit and release/deployment timestamp still need final validator confirmation. |

## 3. Timeline

Use UTC times. Add block heights when available.

| Event | Epoch | Block | Time (UTC) | Source / link | Notes |
| --- | --- | --- | --- | --- | --- |
| Issue starts | 267 | `4122271` |  | Direct chain cPoC event | cPoC #1 in epoch 267 |
| First known impact | 267 | `4122271` |  | Direct chain audit; @votkon report | Participant failed Kimi for cPoC #1 and received zero rewards; Qwen passed by guardian protection |
| Fix or mitigation available |  |  |  | Core-team comments; v0.2.13 | Reported as the reason for the v0.2.13 post-cancellation fix so such nodes would not remain preserved |
| Rate-limit cause identified |  |  |  | https://github.com/gonka-ai/gonka/blob/d8b8e9073d1a420d344d3ecc33ef23957f4142b1/deploy/join/docker-compose.yml#L133 | `poc/proofs` missing from `GONKA_API_EXEMPT_ROUTES`; artifact requests could be blocked by rate limiter |
| Issue ends |  |  |  |  | Needs confirmation from v0.2.13 deployment and chain behavior after the fix |

## 4. Initial Technical Claim

| Question | Answer |
| --- | --- |
| What should have happened? | Guardian nodes should have been able to fetch PoC proof artifacts and validate the participant normally. Preserved high-voting-power Kimi nodes should not have caused a validation shortfall that makes otherwise healthy participants fail cPoC. |
| What actually happened? | Two large Kimi nodes were reportedly preserved, and two guardian nodes did not validate the proposer. The proposer had Kimi failure in this specific cPoC, while Qwen passed by guardian protection and the next three cPoCs passed. |
| What component caused or may have caused it? | Likely interaction between cPoC preservation logic, Kimi high-voting-power preserved nodes, guardian validation, API proof artifact fetching, and API rate limiting. |
| What commit, release, config, or migration is involved? | Config at `deploy/join/docker-compose.yml` around `GONKA_API_EXEMPT_ROUTES`; `poc/proofs` was reportedly missing at commit `d8b8e9073d1a420d344d3ecc33ef23957f4142b1`. The protective fix is reported to be in v0.2.13 after the cancellation. Exact fix commit still needs to be identified. |
| Is the issue fixed? | Reported fixed in v0.2.13; needs verification against the exact patch and post-fix behavior. |

## 5. Affected Scope

| Question | Answer |
| --- | --- |
| Affected participant type(s) | ML node participants in epoch 267 cPoC, especially participants whose pass/fail result depended on Kimi/Qwen guardian validation during the affected event |
| Affected reward stream(s) | Epoch rewards lost due to cPoC failure; whether other reward streams are in scope is a GRC policy question |
| Affected model / subgroup, if relevant | Kimi is central to the report; Qwen was reportedly also skipped for the proposer |
| Affected rounds, CPoCs, or epochs | Epoch 267 cPoC #1 at trigger height `4122271` |
| Baseline state to compare against | Previous successful epochs for the same node and the next three successful cPoCs in epoch 267 |
| Estimated affected count | 1 confirmed restitution victim; 0 additional confirmed victims from the described cPoC #1 Kimi/guardian failure |
| Estimated restitution exposure | 10,262.057515 GONKA under the full described failure rule |

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
| Participants with only one model affected | Direct chain data shows Kimi failure for the direct row and Qwen guardian protection; GRC should decide whether partial-model impact is enough |
| Participants near the pass/fail threshold | Need full recomputation or strong spot checks |
| Participants where preserved-node state cannot be reconstructed | The main known investigation blocker is where to pull preserved nodes from at the exact point in time |
| Participants with operator-side logs showing local issues | Could be unrelated to the network bug |

## 7. Evidence Needed

| Evidence | Location / command / endpoint | Status |
| --- | --- | --- |
| Chain data source | Direct chain API from node1-node4 for epoch 267 cPoCs | Collected in `output/raw_chain/` |
| Historical query method | `case3_audit.py` reconstructs cPoC commits, validator rows, guardian validation counts, model weights, and rewards from direct chain endpoints | Complete for directly observable chain state |
| Relevant code / commits | `GONKA_API_EXEMPT_ROUTES` config at commit `d8b8e9073d1a420d344d3ecc33ef23957f4142b1`; v0.2.13 fix commit | Partially identified |
| Release or deployment timestamps | v0.2.13 after cancellation; exact release and deployment timestamps needed | To collect |
| Operator reports, if any | @votkon report; Gleb/core-team comment; Evgeny Maksimenkov comment | Need source links or screenshots if available |
| Existing scripts, CSVs, or JSON files | `case3_audit.py`, `output/case3_summary.json`, `output/case3_per_participant.csv`, `output/case3_affected_no_vote_validators.csv`, `output/raw_chain/` | Draft complete |

## 8. Draft Restitution Method

| Question | Answer |
| --- | --- |
| What baseline will be used? | Same-epoch comparison: cPoC #1 failed, while cPoCs #2, #3, and #4 passed |
| Why is that baseline fair? | It isolates the unusual validation shortfall inside the same epoch while the participant continued to pass later cPoCs |
| What denominator will be used? | Aggregate/root `epoch_group_data.total_weight` for epoch 267: `541415` |
| Should actual rewards already received be subtracted? | Yes: compute expected reward minus actual reward. Actual reward is zero for the affected participant. |
| Should partial payouts stay eligible? | GRC decision needed |
| Should downtime, misses, invalidation, or slashing affect eligibility? | Suggested default: exclude independent participant-side failures; GRC decision needed for borderline cases |
| Should the calculation include only fixed rewards or other losses too? | GRC decision needed |

Formula draft:

```text
eligible_loss_ngonka = max(0, expected_reward_ngonka - actual_rewarded_ngonka)

expected_reward_ngonka =
  participant_weight / root_total_weight * fixed_epoch_reward_ngonka
```

Units and rounding:

| Item | Answer |
| --- | --- |
| Internal unit | ngonka |
| Display unit | GONKA |
| Rounding rule | Integer ngonka calculation, displayed to 6 decimals in GONKA |
| Final payout precision | 10,262.057515 GONKA in the draft output |

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
| Which exact cPoC in epoch 267 is the official case window? | Draft: cPoC #1, trigger height `4122271` |
| What is the accepted source of preserved-node state at that historical point? | Still open; direct chain endpoints used here do not expose an explicit historical preserved label |
| Should eligibility require final cPoC failure, or is a confirmed preserved-node reward reduction enough? |  |
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
| Does any proposed validator benefit from the case? | No |
| Did any assigned person work on the faulty component? | No |
| Are any conflicts disclosed and accepted by GRC? | No |

## 13. Ready For Assignment

- [x] Case basics are filled.
- [x] Time window is clear.
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
| Investigator | @mikenosov | 2026-05-28 15:44 UTC | Assigned from GRC matrix for Case #3 |
| Validator | @dem_ww | 2026-05-28 15:44 UTC | Assigned from GRC matrix for Case #3 |
| Validator | @votkon | 2026-05-28 15:44 UTC | Assigned from GRC matrix for Case #3 |

Expected completion date: 2026-05-30
