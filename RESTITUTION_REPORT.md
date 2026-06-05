# GRC Case #3 - Epoch 267 Kimi/Qwen Shortfall

Prepared for internal GRC review. Source of truth: direct chain API data from
node1-node4 only.

## Summary

The full-case audit found **1 confirmed restitution victim**. This participant
had zero reward where cPoC #1 Kimi failed by validation-weight plus guardian
shortfall, Qwen passed only by guardian protection, and the next three cPoCs
passed.

| participant | weight | cPoC #1 result | next cPoCs | proposed restitution |
| --- | ---: | --- | --- | ---: |
| `gonka1j7x6dv42xehe9e5au4ku3wvzwtqlegfjhlvzj6` | 19,518 | Qwen `pass_guardian`; Kimi `weight_and_guardian_shortfall` | Kimi `pass_guardian`, Kimi `pass_guardian`, Kimi `pass_guardian` | **10,262.057515369 GONKA** |

Draft restitution for that direct-failure row: **10,262.057515369 GONKA**.

### Broader 2026-06-05 Recheck

The original epoch 267 finding remains valid under the strict Kimi-only rule:
one direct victim address and one epoch 267 restitution row.

The broader recheck adds two scope options for GRC:

| scope | victim rows | amount |
| --- | ---: | ---: |
| Epoch 267 Kimi shortfall | 1 | 10,262.057515369 GONKA |
| Epoch 265 Kimi shortfall extension | 1 | 20,896.527179100 GONKA |
| **Kimi-only total if epoch 265 is accepted** | **2 participant-epoch rows, same address** | **31,158.584694469 GONKA** |
| Epoch 265 Qwen-only cPoC shortfall, if broader policy is accepted | 1 | 4,154.662338515 GONKA |
| **Broader cPoC-shortfall total** | **3 participant-epoch rows, 2 addresses** | **35,313.247032984 GONKA** |

The epoch 265 Kimi row is the same address as the epoch 267 victim:
`gonka1j7x6dv42xehe9e5au4ku3wvzwtqlegfjhlvzj6`.

The additional broader candidate is Qwen-only:
`gonka1myu058axjs62mc3e7na9krwvqpfl9z3gtcw9es`.

The audit also found related non-victim signals: one additional Qwen guardian
no-vote row that still passed by weight, plus Kimi cPoC #1 non-submit /
non-voting source candidates. Those rows help explain the validation shortfall
but do not themselves match the described victim pattern.

## Direct Chain Evidence

Epoch 267 has four confirmation PoC events:

| cPoC | trigger height | affected participant status |
| --- | ---: | --- |
| #1 | `4122271` | Qwen passed by guardian protection; Kimi failed by weight plus guardian shortfall |
| #2 | `4130085` | Kimi passed by guardian protection |
| #3 | `4133665` | Kimi passed by guardian protection |
| #4 | `4134529` | Kimi passed by guardian protection |

For the affected participant at cPoC #1:

| model | submitted count | valid weight / total | guardian valid | guardian no-vote | result |
| --- | ---: | ---: | ---: | ---: | --- |
| Qwen | 1,024 | 129,251 / 541,415 = 0.238728 | 1 | 2 | pass by guardian |
| Kimi | 57,664 | 171,571 / 541,415 = 0.316894 | 0 | 2 | fail |

For the next three cPoCs, the same participant submitted Kimi and passed:

| cPoC | model | submitted count | valid weight / total | guardian valid | result |
| --- | --- | ---: | ---: | ---: | --- |
| #2 | Kimi | 57,408 | 239,088 / 541,415 = 0.441598 | 2 | pass by guardian |
| #3 | Kimi | 45,376 | 302,807 / 541,415 = 0.559288 | 2 | pass by guardian |
| #4 | Kimi | 57,888 | 311,717 / 541,415 = 0.575745 | 2 | pass by guardian |

Actual epoch reward for this participant from
`epoch_performance_summary/267/{address}` is zero.

## Epoch 265 Extension Recheck

Epoch 265 has the same address failing a Kimi cPoC by validation-weight and
guardian shortfall, with zero actual reward:

| field | value |
| --- | --- |
| participant | `gonka1j7x6dv42xehe9e5au4ku3wvzwtqlegfjhlvzj6` |
| participant weight | 66,311 |
| root total weight | 904,177 |
| actual reward | 0.000000000 GONKA |
| candidate loss | 20,896.527179100 GONKA |
| cPoC #1 | Qwen `pass_guardian`; Kimi `pass_weight` |
| cPoC #2 | Qwen `pass_guardian`; Kimi `pass_guardian` |
| cPoC #3 | Qwen `pass_guardian`; Kimi `weight_and_guardian_shortfall` |

At the failing Kimi stage `4102890`:

| measure | value |
| --- | ---: |
| submitted count | 52,028 |
| valid weight / total | 256,727 / 904,177 = 0.283934 |
| invalid weight | 187,906 |
| no-vote weight | 398,021 |
| guardian valid / invalid / no-vote | 1 / 1 / 0 |

This fails the chain cPoC rule: validation weight is below the
greater-than-two-thirds threshold, and the guardian result is split.

There is also one Qwen-only epoch 265 broad-policy candidate:

| participant | model | stage | valid weight / total | guardian valid / invalid / no-vote | candidate loss |
| --- | --- | ---: | ---: | ---: | ---: |
| `gonka1myu058axjs62mc3e7na9krwvqpfl9z3gtcw9es` | Qwen | `4102890` | 6,794 / 904,177 = 0.007514 | 0 / 0 / 3 | 4,154.662338515 GONKA |

This Qwen row is not part of the strict Kimi-only case, but it is included for
GRC policy review because it has the same direct cPoC quorum/guardian shortfall
shape.

## Full-Case Eligibility Rule

The confirmed victim rule is:

- participant was in epoch 267 aggregate `epoch_group_data`;
- actual rewarded coins were zero;
- participant submitted cPoC #1;
- cPoC #1 Kimi failed by guardian and validation-weight shortfall;
- cPoC #1 Qwen passed only by guardian protection;
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
| Qwen pass by weight | 14 |
| Kimi pass by guardian | 14 |
| Qwen pass by weight and Kimi pass by guardian | 5 |
| Qwen pass by guardian | 1 |
| Qwen pass by guardian and Kimi weight plus guardian shortfall | 1 |

So, under the full described failure rule, exactly one participant had cPoC #1
Kimi shortfall that maps to zero reward and clean later passes.

Across all four cPoCs, the direct chain status check found one shortfall row:

| participant | shortfall | reward | case #3 decision |
| --- | --- | ---: | --- |
| `gonka1j7x6dv42xehe9e5au4ku3wvzwtqlegfjhlvzj6` | cPoC #1 Kimi weight plus guardian shortfall | 0.000000 | included |

## Related Non-Victim Signals

The full-case matrix includes every directly observable cPoC #1 guardian-skip
or failure row:

| row type | participant | model | status | conclusion |
| --- | --- | --- | --- | --- |
| confirmed victim | `gonka1j7x6dv42xehe9e5au4ku3wvzwtqlegfjhlvzj6` | Kimi | weight plus guardian shortfall, reward 0 | eligible |
| related guardian skip | `gonka1j7x6dv42xehe9e5au4ku3wvzwtqlegfjhlvzj6` | Qwen | passed by guardian protection | same victim, no separate restitution row |
| related guardian skip | `gonka1w29nvdy6caqtrw30whz9h6ghl0xszwh3egndah` | Qwen | passed by weight with one guardian no-vote | not a Kimi/preserved failure victim |

### Kimi Non-Voting Source Candidates

Direct chain data at cPoC #1 also shows Kimi subgroup members that either did
not submit a Kimi commit or made no Kimi validation rows. These are possible
causal source rows for the shortfall, not restitution victims from the
described Votkon failure:

| participant | Kimi voting power | cPoC #1 Kimi commit | Kimi validations made | full-weight reward gap |
| --- | ---: | --- | ---: | ---: |
| `gonka17gpuntq09zsaqtmpe544gc32tk4424dwv5t34f` | 159,432 | no | 0 | 5,737.771988 GONKA |
| `gonka1zktn8j65wlys8a8e38hqhf4y3x6m4x04zskkrx` | 15,605 | yes | 0 | 2,961.159336 GONKA |
| `gonka168rtjfkszuhcggg4dfyse4yh7xn9zwfglnkns2` | 7,068 | no | 0 | 5.257740 GONKA |
| `gonka1kx9mca3xm8u8ypzfuhmxey66u0ufxhs7nm6wc5` | 3,083 | no | 19 | 6.835062 GONKA |

Other Kimi cPoC #1 non-submit rows have zero full-weight gap under the
full-weight comparison. The full candidate export is
`output/case3_kimi_cpoc1_non_submit_candidates.csv`.

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
= 10,262.057515369 GONKA
```

## Files

| file | purpose |
| --- | --- |
| `case3_audit.py` | reproducible chain-only audit script |
| `output/case3_summary.json` | machine-readable result summary |
| `output/case3_per_participant.csv` | all participants and cPoC statuses |
| `output/case3_affected_no_vote_validators.csv` | no-vote validator detail for affected row |
| `output/case3_full_case_matrix.csv` | confirmed victim plus every related cPoC #1 guardian-skip / Kimi non-voting signal |
| `output/case3_kimi_cpoc1_non_submit_candidates.csv` | Kimi cPoC #1 non-submit / non-voting candidate rows |
| `BROADER_REVIEW.md` | 2026-06-05 scope recheck covering epoch 265 and broader cPoC shortfall candidates |
| `output/case3_broader_victim_count_recheck.csv` | strict Kimi and broader cPoC candidate rows from the recheck |
| `output/case3_epoch265_same_host_recheck.csv` | epoch 265 same-address Kimi shortfall evidence row |
| `output/raw_chain/` | cached raw node1-node4 direct-chain API responses |

## Caveats

The chain endpoints used here do not expose an explicit historical "preserved"
flag for the Kimi/Qwen nodes at height `4122271`. The chain evidence is
consistent with the reported preserved-node explanation, but this report does
not independently label any validator or ML node as preserved. It identifies
victims through observable failed cPoC status, guardian no-votes, and reward
loss, and lists non-victim source candidates separately.
