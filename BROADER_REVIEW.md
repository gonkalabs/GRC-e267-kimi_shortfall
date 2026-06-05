# Case #3 Broader Victim Count Recheck

Date: 2026-06-05

Reviewed repo: `gonkalabs/GRC-e267-kimi_shortfall` at `c13d859`.

## Short Answer

Under the strict original rule, this is still one direct Kimi-shortfall victim
address:

```text
gonka1j7x6dv42xehe9e5au4ku3wvzwtqlegfjhlvzj6
```

However, if GRC accepts epoch 265 as the same failure pattern, this is not only
one loss row:

| scope | victim rows | amount |
| --- | ---: | ---: |
| Epoch 267 Kimi shortfall | 1 | 10,262.057515369 GONKA |
| Epoch 265 Kimi shortfall extension | 1 | 20,896.527179100 GONKA |
| **Kimi-only total** | **2 participant-epoch rows, same address** | **31,158.584694469 GONKA** |

If GRC broadens the case from Kimi-only to any cPoC quorum/guardian shortfall,
epoch 265 adds one more Qwen-only candidate:

| scope | victim rows | amount |
| --- | ---: | ---: |
| Kimi-only total above | 2 | 31,158.584694469 GONKA |
| Epoch 265 Qwen-only cPoC shortfall | 1 | 4,154.662338515 GONKA |
| **Broader cPoC-shortfall total** | **3 participant-epoch rows, 2 addresses** | **35,313.247032984 GONKA** |

## Why The Strict Kimi Count Is Still One Address

Epoch 267 has only three zero-reward participants:

| address | cPoC status | why not more victims |
| --- | --- | --- |
| `gonka1j7x6dv42xehe9e5au4ku3wvzwtqlegfjhlvzj6` | Qwen passed by guardian; Kimi failed by shortfall; later Kimi passed | direct Kimi-shortfall victim |
| `gonka1tmk2tzdneht6smu34pkmqdvu7p34qavvmwtwq2` | no submit in all four cPoCs | no submitted cPoC row to rescue |
| `gonka1ujnc662v6g69jm6fgxnr79a2m7ehzeut059239` | Kimi passed cPoC #1/#2/#4; no submit cPoC #3 | not a Kimi quorum failure victim |

Across all epoch 267 cPoCs, the only participant with an actual Kimi
`weight_and_guardian_shortfall` and zero reward is `gonka1j7x6...`.

Epoch 265 has many zero-reward rows, but most are no-submit rows. The same
`gonka1j7x6...` row is the only Kimi shortfall candidate with submitted work
and zero reward.

## Epoch 265 Kimi Extension Candidate

Epoch 265 has three confirmation PoC events at trigger heights `4095682`,
`4098879`, and `4102890`.

For the same address affected in epoch 267:

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

This fails both checks used by the chain rule: validation weight is below the
greater-than-two-thirds threshold, and guardians are split.

## Additional Broad Candidate

Epoch 265 has one more zero-reward shortfall if the case is not restricted to
Kimi:

```text
gonka1myu058axjs62mc3e7na9krwvqpfl9z3gtcw9es
```

This is Qwen-only:

| epoch | cPoC | model | valid weight / total | guardian valid | guardian invalid | guardian no-vote | amount |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 265 | #3 | Qwen | 6,794 / 904,177 = 0.007514 | 0 | 0 | 3 | 4,154.662338515 GONKA |

This is not part of a strict Kimi-only case, but it is a real cPoC
quorum/guardian shortfall candidate.

## Source Candidates Are Not Direct Victims

There are also Kimi non-submit / non-voting source candidates. Some have
positive full-weight gaps. They help explain why Kimi validation weight was
short, but they are not direct victims of the "my submitted nonces could not be
validated" pattern unless GRC explicitly broadens policy to compensate
source/non-voting participants too.

Examples from epoch 267:

| address | signal | gap |
| --- | --- | ---: |
| `gonka17gpuntq09zsaqtmpe544gc32tk4424dwv5t34f` | no Kimi cPoC #1 commit | 5,737.771988 GONKA |
| `gonka1zktn8j65wlys8a8e38hqhf4y3x6m4x04zskkrx` | Kimi commit, no Kimi validation rows | 2,961.159336 GONKA |
| `gonka168rtjfkszuhcggg4dfyse4yh7xn9zwfglnkns2` | no Kimi cPoC #1 commit | 5.257740 GONKA |
| `gonka1kx9mca3xm8u8ypzfuhmxey66u0ufxhs7nm6wc5` | no Kimi cPoC #1 commit, some validation rows | 6.835062 GONKA |

These are different from the direct victim row. Treating them as restitution
victims would be a separate policy decision.

## Current Framing

```text
Kimi-only direct victim count:
1 address, 2 participant-epoch rows if epoch 265 is accepted.

Broader cPoC-shortfall victim count:
2 addresses, 3 participant-epoch rows if the epoch 265 Qwen-only row is also
accepted.

Source/non-voting candidates:
visible and relevant to root cause, but not direct restitution victims under
the current case rule.
```
