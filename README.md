# GRC Case #3 - Epoch 267 Kimi Shortfall

Chain-only audit for the GRC-e267 Kimi/Qwen guardian validation shortfall case.

The reproducer reads only direct chain API responses from:

- `http://node1.gonka.ai:8000`
- `http://node2.gonka.ai:8000`
- `http://node3.gonka.ai:8000`
- `http://node4.gonka.ai:8000`

The narrative report is `RESTITUTION_REPORT.md`.

## Current Status

The current script identifies **1 direct symptom match** under a narrow rule:
zero reward, Qwen and Kimi guardian/weight shortfall at cPoC #1, and the next
three cPoCs passing.

| participant | restitution |
| --- | ---: |
| `gonka1j7x6dv42xehe9e5au4ku3wvzwtqlegfjhlvzj6` | **10,262.057515 GONKA** |

This is **not yet the final full affected cohort**. The full case must
reconstruct the preserved Kimi nodes at the affected cPoC and compute which
participants lost confirmation weight because those preserved nodes were not
counted correctly.

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
- cPoC #1 failed by validation-weight and guardian shortfall;
- the next three cPoCs in the same epoch passed;
- restitution uses the aggregate/root `epoch_group_data.total_weight`
  denominator, matching the correction GRC applied in the previous audit.

The next audit step is broader: reconstruct the event-local preserved-node
set and replay the confirmation-weight update with preserved weights included.

The pass rule used by the script is:

```text
valid_weight >= 0.5 * model_total_weight
guardian_valid >= 2
```

## Outputs

| file | description |
| --- | --- |
| `output/case3_summary.json` | totals, policy assumptions, affected list, exclusions |
| `output/case3_per_participant.csv` | all epoch 267 participants with cPoC status and restitution columns |
| `output/case3_affected_no_vote_validators.csv` | top no-vote validators for the affected participant |
| `output/case3_log.txt` | run log |
| `output/raw_chain/` | cached raw JSON from node1-node4 direct chain API endpoints |

## Caveat

The direct chain endpoints used here expose commits, validation rows,
guardian addresses, weights, rewards, and cPoC events. They do not expose an
explicit historical "preserved" label for the Kimi/Qwen nodes at the affected
height. The report therefore claims only what the direct chain data proves:
the affected participant had a simultaneous Kimi and Qwen validation-weight
plus guardian shortfall at cPoC #1, zero reward, and passed the next three
cPoCs.
