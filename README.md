# GRC Case #3 - Epoch 267 Kimi Shortfall

Chain-only audit for the GRC-e267 Kimi/Qwen guardian validation shortfall case.

The reproducer reads only direct chain API responses from:

- `http://node1.gonka.ai:8000`
- `http://node2.gonka.ai:8000`
- `http://node3.gonka.ai:8000`
- `http://node4.gonka.ai:8000`

The narrative report is `RESTITUTION_REPORT.md`.

## Current Status

The current script identifies **1 direct failure match** under a narrow rule:
zero reward, a Kimi guardian/weight shortfall at cPoC #1, Qwen rescued by
guardian protection in the same cPoC, and the next three cPoCs passing.

| participant | restitution |
| --- | ---: |
| `gonka1j7x6dv42xehe9e5au4ku3wvzwtqlegfjhlvzj6` | **10,262.057515 GONKA** |

This is **not yet the final full affected cohort**. Direct chain data also
shows Kimi cPoC #1 non-submit / non-voting candidates, including a high
Kimi voting-power participant. Those rows are exported separately because GRC
still needs to confirm which of them were preserved-node effects and which
losses are causally in scope.

## Run It

```bash
python3 case3_audit.py
```

The script is Python 3.9+ stdlib-only. It caches raw direct-chain JSON under
`output/raw_chain/`, so repeat runs can be checked without changing inputs.

## What The Script Checks

The first-pass symptom rule is intentionally narrow:

- epoch 267 participant had zero actual reward;
- participant submitted at cPoC #1, trigger height `4122271`;
- cPoC #1 Kimi failed by validation-weight and guardian shortfall;
- cPoC #1 Qwen had validation-weight shortfall but passed by guardian
  protection;
- the next three cPoCs in the same epoch passed;
- restitution uses the aggregate/root `epoch_group_data.total_weight`
  denominator, matching the correction GRC applied in the previous audit.

The next audit step is broader: confirm the event-local preserved-node set
used at height `4122271` and replay the counterfactual reward impact for all
participants whose own Kimi commit/validation behavior or rewards changed.

The pass rule used by the script is:

```text
valid_weight > 2/3 * total_network_weight
or guardian_valid > 0 and guardian_invalid == 0
```

## Outputs

| file | description |
| --- | --- |
| `output/case3_summary.json` | totals, policy assumptions, affected list, exclusions |
| `output/case3_per_participant.csv` | all epoch 267 participants with cPoC status and restitution columns |
| `output/case3_affected_no_vote_validators.csv` | top no-vote validators for the affected participant |
| `output/case3_kimi_cpoc1_non_submit_candidates.csv` | Kimi cPoC #1 non-submit / non-voting candidates for preserved-node review |
| `output/case3_log.txt` | run log |
| `output/raw_chain/` | cached raw JSON from node1-node4 direct chain API endpoints |

## Caveat

The direct chain endpoints used here expose commits, validation rows,
guardian addresses, weights, rewards, and cPoC events. They do not expose an
explicit historical "preserved" label for the Kimi/Qwen nodes at the affected
height. The report therefore separates proven direct-failure restitution from
candidate preserved-node rows. The proven direct failure is Kimi cPoC #1
guardian/weight shortfall with zero reward and clean passes in the next three
cPoCs.
