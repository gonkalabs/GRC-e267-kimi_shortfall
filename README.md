# GRC Case #3 - Epoch 267 Kimi Shortfall

Chain-only audit for the GRC-e267 Kimi/Qwen guardian validation shortfall case.

The reproducer reads only direct chain API responses from:

- `http://node1.gonka.ai:8000`
- `http://node2.gonka.ai:8000`
- `http://node3.gonka.ai:8000`
- `http://node4.gonka.ai:8000`

The narrative report is `RESTITUTION_REPORT.md`.

## Current Status

The current script identifies **1 confirmed victim** under the full described
case mechanism: zero reward, a Kimi guardian/weight shortfall at cPoC #1, Qwen
rescued by guardian protection in the same cPoC, and the next three cPoCs
passing.

| participant | restitution |
| --- | ---: |
| `gonka1j7x6dv42xehe9e5au4ku3wvzwtqlegfjhlvzj6` | **10,262.057515 GONKA** |

The full-case matrix also lists related signals that are not restitution
victims under this case: one Qwen guardian-skip row that passed by weight, and
Kimi cPoC #1 non-submit / non-voting source candidates that may explain the
shortfall but did not themselves match the described loss pattern.

## Run It

```bash
python3 case3_audit.py
```

The script is Python 3.9+ stdlib-only. It caches raw direct-chain JSON under
`output/raw_chain/`, so repeat runs can be checked without changing inputs.

## What The Script Checks

The confirmed-victim rule is:

- epoch 267 participant had zero actual reward;
- participant submitted at cPoC #1, trigger height `4122271`;
- cPoC #1 Kimi failed by validation-weight and guardian shortfall;
- cPoC #1 Qwen had validation-weight shortfall but passed by guardian
  protection;
- the next three cPoCs in the same epoch passed;
- restitution uses the aggregate/root `epoch_group_data.total_weight`
  denominator, matching the correction GRC applied in the previous audit.

The broader full-case matrix also records:

- any cPoC #1 model row with guardian no-votes or failure;
- Kimi subgroup members that did not submit Kimi cPoC #1 or made no Kimi
  validation rows;
- why those related rows are not restitution victims under the described
  Votkon failure pattern.

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
| `output/case3_full_case_matrix.csv` | confirmed victim plus every related cPoC #1 guardian-skip / Kimi non-voting signal |
| `output/case3_kimi_cpoc1_non_submit_candidates.csv` | Kimi cPoC #1 non-submit / non-voting candidates for preserved-node review |
| `output/case3_log.txt` | run log |
| `output/raw_chain/` | cached raw JSON from node1-node4 direct chain API endpoints |

## Caveat

The direct chain endpoints used here expose commits, validation rows,
guardian addresses, weights, rewards, and cPoC events. They do not expose an
explicit historical "preserved" label for the Kimi/Qwen nodes at the affected
height. The report therefore proves the victim cohort from observable cPoC
failure, guardian no-votes, and reward loss, while listing non-victim source
candidates separately.
