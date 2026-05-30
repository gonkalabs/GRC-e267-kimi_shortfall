# GRC Case #3 - Epoch 267 Kimi/Qwen Shortfall

Prepared for internal GRC review. Source of truth: direct chain API data from
node1-node4 only.

## Summary

The current audit has a narrow direct-symptom result, not the final full
affected cohort. It found **1 participant** matching the exact reported
symptom: zero reward, simultaneous Qwen and Kimi guardian/weight shortfall at
cPoC #1, and the next three cPoCs passing.

| participant | weight | cPoC #1 result | next cPoCs | proposed restitution |
| --- | ---: | --- | --- | ---: |
| `gonka1j7x6dv42xehe9e5au4ku3wvzwtqlegfjhlvzj6` | 19,518 | Qwen and Kimi both `weight_and_guardian_shortfall` | Kimi pass, Kimi pass, Kimi pass | **10,262.057515 GONKA** |

Draft restitution for that direct-symptom row: **10,262.057515 GONKA**.

The full case is broader. The root bug is that high-voting-power Kimi nodes
were preserved for the cPoC event, but the event evaluation did not correctly
credit preserved node weight. The next required step is to reconstruct the
event-local preserved-node set and recompute which participants lost
confirmation weight because of that bug.

## Direct Chain Evidence

Epoch 267 has four confirmation PoC events:

| cPoC | trigger height | affected participant status |
| --- | ---: | --- |
| #1 | `4122271` | Qwen and Kimi both failed by weight plus guardian shortfall |
| #2 | `4130085` | Kimi passed |
| #3 | `4133665` | Kimi passed |
| #4 | `4134529` | Kimi passed |

For the affected participant at cPoC #1:

| model | submitted count | valid weight / total | guardian valid | guardian no-vote | result |
| --- | ---: | ---: | ---: | ---: | --- |
| Qwen | 1,024 | 93,535 / 426,417 = 0.219351 | 1 | 2 | fail |
| Kimi | 57,664 | 114,174 / 334,289 = 0.341543 | 0 | 2 | fail |

For the next three cPoCs, the same participant submitted Kimi and passed:

| cPoC | model | submitted count | valid weight / total | guardian valid | result |
| --- | --- | ---: | ---: | ---: | --- |
| #2 | Kimi | 57,408 | 178,021 / 334,289 = 0.532536 | 2 | pass |
| #3 | Kimi | 45,376 | 241,740 / 334,289 = 0.723147 | 2 | pass |
| #4 | Kimi | 57,888 | 250,650 / 334,289 = 0.749800 | 2 | pass |

Actual epoch reward for this participant from
`epoch_performance_summary/267/{address}` is zero.

## Eligibility Rule Used

The classification is intentionally narrow for this first case decision:

- participant was in epoch 267 aggregate `epoch_group_data`;
- actual rewarded coins were zero;
- participant submitted cPoC #1;
- cPoC #1 failed by guardian and validation-weight shortfall;
- the next three cPoCs passed;
- excluded participants are kept visible in the summary file.

This found three zero-reward participants. Two were excluded:

| participant | reason excluded |
| --- | --- |
| `gonka1tmk2tzdneht6smu34pkmqdvu7p34qavvmwtwq2` | no submissions in all four cPoCs |
| `gonka1ujnc662v6g69jm6fgxnr79a2m7ehzeut059239` | cPoC #1 passed; cPoC #3 had no submission |

## Cohort Sanity Checks

The audit reviewed all **51** participants in epoch 267 aggregate
`epoch_group_data`.

cPoC #1 status distribution:

| status | count |
| --- | ---: |
| no submission | 16 |
| Qwen pass | 15 |
| Kimi pass | 14 |
| Qwen pass and Kimi pass | 5 |
| Qwen and Kimi both weight plus guardian shortfall | 1 |

So, under the narrow direct-symptom rule, exactly one participant had cPoC #1
shortfall. This does not prove that only one participant was affected by the
preserved-node bug.

Across all four cPoCs there were three participants with any shortfall:

| participant | shortfall | reward | case #3 decision |
| --- | --- | ---: | --- |
| `gonka1j7x6dv42xehe9e5au4ku3wvzwtqlegfjhlvzj6` | cPoC #1 Qwen and Kimi weight plus guardian shortfall | 0.000000 | included |
| `gonka1d694r00czmq75txghwjcuk07lxvc8d4ekgsha0` | cPoC #2 Qwen weight shortfall, guardians 3/3 | 232.392121 | excluded |
| `gonka1w29nvdy6caqtrw30whz9h6ghl0xszwh3egndah` | cPoC #2 Qwen weight shortfall, guardians 3/3 | 104.103258 | excluded |

The two excluded shortfalls are later cPoC #2 Qwen-only rows, had all three
guardians validating, and received nonzero rewards. They do not match the
reported Kimi/Qwen simultaneous guardian-shortfall failure mode.

## Restitution Calculation

This follows the main correction from the prior GRC audit: use the aggregate
root denominator, not the model subgroup denominator.

Inputs:

```text
epoch_reward_ngonka = 284,661,946,392,228
root_total_weight   = 541,415
participant_weight  = 19,518
actual_reward       = 0
```

Formula:

```text
expected_reward_ngonka =
  participant_weight / root_total_weight * epoch_reward_ngonka

eligible_loss_ngonka =
  max(0, expected_reward_ngonka - actual_reward_ngonka)
```

Result:

```text
19,518 / 541,415 * 284,661,946,392,228
= 10,262,057,515,369 ngonka
= 10,262.057515 GONKA
```

## Files

| file | purpose |
| --- | --- |
| `case3_audit.py` | reproducible chain-only audit script |
| `output/case3_summary.json` | machine-readable result summary |
| `output/case3_per_participant.csv` | all participants and cPoC statuses |
| `output/case3_affected_no_vote_validators.csv` | no-vote validator detail for affected row |
| `output/raw_chain/` | cached raw node1-node4 direct-chain API responses |

## Caveats

The chain endpoints used here do not expose an explicit historical "preserved"
flag for the Kimi/Qwen nodes at height `4122271`. The chain evidence is
consistent with the reported preserved-node explanation, but this report does
not independently label any validator as preserved. It proves the directly
observable effect: simultaneous Kimi and Qwen validation-weight shortfall,
two guardian no-votes, zero reward, and clean passes in the next three cPoCs.
