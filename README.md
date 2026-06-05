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
| `gonka1j7x6dv42xehe9e5au4ku3wvzwtqlegfjhlvzj6` | **10,262.057515369 GONKA** |

The full-case matrix also lists related signals that are not restitution
victims under this case: one Qwen guardian-skip row that passed by weight, and
Kimi cPoC #1 non-submit / non-voting source candidates that may explain the
shortfall but did not themselves match the described loss pattern.

## Broader Recheck

`BROADER_REVIEW.md` records the 2026-06-05 recheck requested after the initial
GRC vote.

Under the strict Kimi-only rule, the direct victim count remains one address.
If GRC accepts epoch 265 as the same failure pattern, that same address has a
second participant-epoch row:

| scope | restitution |
| --- | ---: |
| Epoch 267 Kimi shortfall | 10,262.057515369 GONKA |
| Epoch 265 Kimi shortfall extension | 20,896.527179100 GONKA |
| **Kimi-only total** | **31,158.584694469 GONKA** |

If GRC broadens the case from Kimi-only to any cPoC quorum/guardian shortfall,
epoch 265 also has one Qwen-only candidate for
`gonka1myu058axjs62mc3e7na9krwvqpfl9z3gtcw9es`, adding
4,154.662338515 GONKA. The broader cPoC-shortfall total would therefore be
35,313.247032984 GONKA.

## Run It

```bash
python3 case3_audit.py
```

For the epoch 265 extension recheck:

```bash
python3 case3_audit.py --epoch 265
```

The script writes the standard `output/case3_*` files for the selected epoch.
Run the epoch 265 command in a clean copy if you want to preserve the checked-in
epoch 267 outputs unchanged.

To regenerate the cross-epoch broader-review artifacts in this repo:

```bash
python3 case3_audit.py --broader-review
```

That command reruns epoch 267 and epoch 265 from direct chain data, writes
`BROADER_REVIEW.md`, `output/case3_broader_victim_count_recheck.csv`, and
`output/case3_epoch265_same_host_recheck.csv`, then restores the standard
`output/case3_*` files to epoch 267.

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
| `BROADER_REVIEW.md` | 2026-06-05 scope recheck covering epoch 265 and broader cPoC shortfall candidates |
| `output/case3_broader_victim_count_recheck.csv` | strict Kimi and broader cPoC candidate rows from the recheck |
| `output/case3_epoch265_same_host_recheck.csv` | epoch 265 same-address Kimi shortfall evidence row |
| `output/case3_log.txt` | run log |
| `output/raw_chain/` | cached raw JSON from node1-node4 direct chain API endpoints |

## Caveat

The direct chain endpoints used here expose commits, validation rows,
guardian addresses, weights, rewards, and cPoC events. They do not expose an
explicit historical "preserved" label for the Kimi/Qwen nodes at the affected
height. The report therefore proves the victim cohort from observable cPoC
failure, guardian no-votes, and reward loss, while listing non-victim source
candidates separately.
