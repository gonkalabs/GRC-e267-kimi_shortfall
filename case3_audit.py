#!/usr/bin/env python3
"""
case3_audit.py - GRC case #3 / epoch 267 Kimi shortfall.

Chain-only audit. The script reads only direct chain API data from node1-node4:

  - epoch_group_data/{epoch}
  - epoch_group_data/{epoch}?model_id=...
  - confirmation_poc_events/{epoch}
  - all_poc_v2_store_commits/{cpoc_trigger_height}
  - poc_v2_validations_for_stage/{cpoc_trigger_height}
  - epoch_performance_summary/{epoch}/{participant}
  - params

Only direct chain API responses are used.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from decimal import Decimal, getcontext
from typing import Any

getcontext().prec = 40

EPOCH = 267
NODE_BASES = (
    "http://node1.gonka.ai:8000",
    "http://node2.gonka.ai:8000",
    "http://node3.gonka.ai:8000",
    "http://node4.gonka.ai:8000",
)
QWEN = "Qwen/Qwen3-235B-A22B-Instruct-2507-FP8"
KIMI = "moonshotai/Kimi-K2.6"
GUARDIANS = (
    "gonka1y2a9p56kv044327uycmqdexl7zs82fs5ryv5le",
    "gonka1dkl4mah5erqggvhqkpc8j3qs5tyuetgdy552cp",
    "gonka1kx9mca3xm8u8ypzfuhmxey66u0ufxhs7nm6wc5",
)
PASS_WEIGHT_RATIO = Decimal("0.5")
MIN_GUARDIAN_VALID = 2
HTTP_TIMEOUT = 30
HTTP_RETRIES = 3
USER_AGENT = "grc-e267-chain-only-audit/1.0"

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
RAW_DIR = os.path.join(OUT_DIR, "raw_chain")
LOG_PATH = os.path.join(OUT_DIR, "case3_log.txt")
os.makedirs(RAW_DIR, exist_ok=True)


def log(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def safe_cache_name(path: str, params: dict[str, Any] | None) -> str:
    suffix = path
    if params:
        suffix += "?" + urllib.parse.urlencode(sorted((str(k), str(v)) for k, v in params.items()))
    out = []
    for ch in suffix:
        out.append(ch if ch.isalnum() else "_")
    return os.path.join(RAW_DIR, "".join(out).strip("_")[:220] + ".json")


def http_get_chain(path: str, params: dict[str, Any] | None = None, *, cache: bool = True) -> dict:
    cache_path = safe_cache_name(path, params)
    if cache and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    qs = ("?" + urllib.parse.urlencode(params)) if params else ""
    last_err: Exception | None = None
    for attempt in range(1, HTTP_RETRIES + 1):
        for base in NODE_BASES:
            url = f"{base}{path}{qs}"
            try:
                req = urllib.request.Request(
                    url,
                    headers={"Accept": "application/json", "User-Agent": USER_AGENT},
                )
                with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                if isinstance(data, dict) and data.get("code") and not data.get("commits") and not data.get("poc_validation"):
                    last_err = RuntimeError(f"{url}: {data}")
                    continue
                if cache:
                    with open(cache_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, sort_keys=True)
                return data
            except Exception as e:  # noqa: BLE001
                last_err = e
                continue
        time.sleep(0.5 * attempt)
    log(f"WARN: failed {path} params={params}: {last_err}")
    return {}


def int_of(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def fixed_to_decimal(fp: Any) -> Decimal:
    if fp is None:
        return Decimal(0)
    if isinstance(fp, (int, float, str)):
        try:
            return Decimal(str(fp))
        except Exception:
            return Decimal(0)
    if isinstance(fp, dict):
        try:
            return Decimal(str(fp.get("value") or "0")) * (Decimal(10) ** int(fp.get("exponent") or 0))
        except Exception:
            return Decimal(0)
    return Decimal(0)


def compute_epoch_reward_ngonka(params: dict, epoch_index: int) -> int:
    br = params.get("bitcoin_reward_params") or {}
    initial = int_of(br.get("initial_epoch_reward"))
    decay = fixed_to_decimal(br.get("decay_rate"))
    genesis_epoch = int_of(br.get("genesis_epoch")) or 1
    elapsed = max(0, epoch_index - genesis_epoch)
    factor = Decimal(math.exp(float(decay) * elapsed))
    return int((Decimal(initial) * factor).to_integral_value())


def ngonka_to_gonka(v: int | Decimal) -> str:
    return f"{(Decimal(v) / Decimal(1_000_000_000)):.6f}"


def short_model(model_id: str) -> str:
    if model_id == KIMI or "Kimi" in model_id:
        return "Kimi"
    if model_id == QWEN or "Qwen" in model_id:
        return "Qwen"
    return model_id.split("/")[-1]


@dataclass
class VoteSummary:
    valid_count: int
    invalid_count: int
    no_vote_count: int
    valid_weight: int
    invalid_weight: int
    no_vote_weight: int
    total_weight: int
    guardian_valid: int
    guardian_invalid: int
    guardian_no_vote: int
    passed: bool
    reason: str
    valid_validators: list[tuple[str, int]]
    invalid_validators: list[tuple[str, int]]
    no_vote_validators: list[tuple[str, int]]


def model_members(model_group: dict) -> set[str]:
    return {
        str(vw.get("member_address") or "")
        for vw in model_group.get("validation_weights") or []
        if vw.get("member_address")
    }


def build_weight_map(aggregate: dict) -> dict[str, int]:
    return {
        str(vw.get("member_address") or ""): int_of(vw.get("weight"))
        for vw in aggregate.get("validation_weights") or []
        if vw.get("member_address")
    }


def flatten_validations(payload: dict) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for group in payload.get("poc_validation") or []:
        for row in group.get("poc_validation") or []:
            if isinstance(row, dict):
                out.append(row)
    return out


def vote_summary(
    *,
    rows: list[dict[str, Any]],
    participant: str,
    model_id: str,
    validator_universe: set[str],
    weights: dict[str, int],
) -> VoteSummary:
    by_validator: dict[str, int] = {}
    for row in rows:
        if row.get("participant_address") != participant:
            continue
        if row.get("model_id") != model_id:
            continue
        validator = str(row.get("validator_participant_address") or "")
        if not validator:
            continue
        by_validator[validator] = int_of(row.get("validated_weight"))

    valid_count = invalid_count = no_vote_count = 0
    valid_weight = invalid_weight = no_vote_weight = 0
    guardian_valid = guardian_invalid = guardian_no_vote = 0
    valid_validators: list[tuple[str, int]] = []
    invalid_validators: list[tuple[str, int]] = []
    no_vote_validators: list[tuple[str, int]] = []

    for validator in sorted(validator_universe):
        weight = weights.get(validator, 0)
        if validator not in by_validator:
            no_vote_count += 1
            no_vote_weight += weight
            no_vote_validators.append((validator, weight))
            if validator in GUARDIANS:
                guardian_no_vote += 1
            continue
        value = by_validator[validator]
        if value < 0:
            invalid_count += 1
            invalid_weight += weight
            invalid_validators.append((validator, weight))
            if validator in GUARDIANS:
                guardian_invalid += 1
        else:
            valid_count += 1
            valid_weight += weight
            valid_validators.append((validator, weight))
            if validator in GUARDIANS:
                guardian_valid += 1

    total_weight = sum(weights.get(v, 0) for v in validator_universe)
    weight_pass = Decimal(valid_weight) >= (Decimal(total_weight) * PASS_WEIGHT_RATIO)
    guardian_pass = guardian_valid >= MIN_GUARDIAN_VALID
    passed = bool(weight_pass and guardian_pass)
    if passed:
        reason = "pass"
    elif not weight_pass and not guardian_pass:
        reason = "weight_and_guardian_shortfall"
    elif not weight_pass:
        reason = "weight_shortfall"
    else:
        reason = "guardian_shortfall"

    return VoteSummary(
        valid_count=valid_count,
        invalid_count=invalid_count,
        no_vote_count=no_vote_count,
        valid_weight=valid_weight,
        invalid_weight=invalid_weight,
        no_vote_weight=no_vote_weight,
        total_weight=total_weight,
        guardian_valid=guardian_valid,
        guardian_invalid=guardian_invalid,
        guardian_no_vote=guardian_no_vote,
        passed=passed,
        reason=reason,
        valid_validators=sorted(valid_validators, key=lambda item: item[1], reverse=True),
        invalid_validators=sorted(invalid_validators, key=lambda item: item[1], reverse=True),
        no_vote_validators=sorted(no_vote_validators, key=lambda item: item[1], reverse=True),
    )


def fetch_reward(epoch: int, address: str) -> dict:
    body = http_get_chain(
        f"/chain-api/productscience/inference/inference/epoch_performance_summary/{epoch}/{address}"
    )
    return body.get("epochPerformanceSummary") or {}


def audit(args: argparse.Namespace) -> None:
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
    epoch = int(args.epoch)
    log(f"chain-only audit epoch={epoch}")

    params = http_get_chain("/chain-api/productscience/inference/inference/params").get("params", {})
    epoch_reward = compute_epoch_reward_ngonka(params, epoch)
    log(f"epoch_reward={ngonka_to_gonka(epoch_reward)} GONKA")

    aggregate = http_get_chain(f"/chain-api/productscience/inference/inference/epoch_group_data/{epoch}").get("epoch_group_data") or {}
    qwen_group = http_get_chain(
        f"/chain-api/productscience/inference/inference/epoch_group_data/{epoch}",
        {"model_id": QWEN},
    ).get("epoch_group_data") or {}
    kimi_group = http_get_chain(
        f"/chain-api/productscience/inference/inference/epoch_group_data/{epoch}",
        {"model_id": KIMI},
    ).get("epoch_group_data") or {}
    events = http_get_chain(
        f"/chain-api/productscience/inference/inference/confirmation_poc_events/{epoch}"
    ).get("events") or []
    events = sorted(events, key=lambda e: int_of(e.get("event_sequence")))
    stage_heights = [int_of(e.get("trigger_height")) for e in events if int_of(e.get("trigger_height"))]
    log(f"cpoc trigger heights={stage_heights}")

    weights = build_weight_map(aggregate)
    root_total_weight = int_of(aggregate.get("total_weight")) or sum(weights.values())
    log(f"aggregate participants={len(weights)} root_total_weight={root_total_weight}")

    universes = {
        QWEN: model_members(qwen_group),
        KIMI: model_members(kimi_group),
    }
    log(f"qwen members={len(universes[QWEN])} kimi members={len(universes[KIMI])}")

    stage_commits: dict[int, dict[tuple[str, str], int]] = {}
    stage_validations: dict[int, list[dict[str, Any]]] = {}
    for h in stage_heights:
        commits_payload = http_get_chain(
            f"/chain-api/productscience/inference/inference/all_poc_v2_store_commits/{h}"
        )
        commits: dict[tuple[str, str], int] = {}
        for row in commits_payload.get("commits") or []:
            addr = str(row.get("participant_address") or "")
            mid = str(row.get("model_id") or "")
            if addr and mid:
                commits[(addr, mid)] = int_of(row.get("count"))
        stage_commits[h] = commits

        validations_payload = http_get_chain(
            f"/chain-api/productscience/inference/inference/poc_v2_validations_for_stage/{h}"
        )
        stage_validations[h] = flatten_validations(validations_payload)
        log(f"stage={h} commits={len(commits)} validation_rows={len(stage_validations[h])}")

    reward_rows: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(fetch_reward, epoch, addr): addr for addr in sorted(weights)}
        for fut in as_completed(futs):
            reward_rows[futs[fut]] = fut.result()
    log(f"fetched reward summaries={len(reward_rows)}")

    rows: list[dict[str, Any]] = []
    for addr in sorted(weights):
        reward = reward_rows.get(addr, {})
        actual_reward = int_of(reward.get("rewarded_coins"))
        earned = int_of(reward.get("earned_coins"))
        missed = int_of(reward.get("missed_requests"))
        expected_reward = int((Decimal(weights[addr]) / Decimal(root_total_weight) * Decimal(epoch_reward)).to_integral_value()) if root_total_weight else 0

        per_stage_status: list[str] = []
        per_stage_detail: list[dict[str, Any]] = []
        for h in stage_heights:
            submitted_models = sorted(
                mid for (p, mid), count in stage_commits[h].items()
                if p == addr and count > 0
            )
            model_bits: list[str] = []
            detail_models: dict[str, Any] = {}
            for mid in submitted_models:
                summary = vote_summary(
                    rows=stage_validations[h],
                    participant=addr,
                    model_id=mid,
                    validator_universe=universes.get(mid) or set(weights),
                    weights=weights,
                )
                model_bits.append(f"{short_model(mid)}:{'pass' if summary.passed else summary.reason}")
                detail_models[short_model(mid)] = {
                    "count": stage_commits[h].get((addr, mid), 0),
                    "passed": summary.passed,
                    "reason": summary.reason,
                    "valid_weight": summary.valid_weight,
                    "total_weight": summary.total_weight,
                    "valid_weight_ratio": f"{(Decimal(summary.valid_weight) / Decimal(summary.total_weight)) if summary.total_weight else Decimal(0):.6f}",
                    "invalid_weight": summary.invalid_weight,
                    "no_vote_weight": summary.no_vote_weight,
                    "guardian_valid": summary.guardian_valid,
                    "guardian_invalid": summary.guardian_invalid,
                    "guardian_no_vote": summary.guardian_no_vote,
                    "valid_count": summary.valid_count,
                    "invalid_count": summary.invalid_count,
                    "no_vote_count": summary.no_vote_count,
                    "top_no_vote_validators": [
                        {"address": v, "weight": w}
                        for v, w in summary.no_vote_validators[:10]
                    ],
                }
            if not submitted_models:
                per_stage_status.append("no_submit")
            else:
                per_stage_status.append(";".join(model_bits))
            per_stage_detail.append({"stage": h, "models": detail_models})

        cpoc1_fails = "shortfall" in per_stage_status[0] if per_stage_status else False
        cpoc1_guardian_shortfall = (
            ("guardian_shortfall" in per_stage_status[0])
            or ("weight_and_guardian_shortfall" in per_stage_status[0])
            if per_stage_status
            else False
        )
        cpoc1_submitted = bool(per_stage_status and per_stage_status[0] != "no_submit")
        later_all_pass = bool(
            len(per_stage_status) >= 4
            and all(status != "no_submit" and "shortfall" not in status for status in per_stage_status[1:4])
        )
        zero_reward = actual_reward == 0

        # The narrow case #3 cohort: reward zero, cPoC #1 submitted but failed
        # by guardian/weight shortfall, and the next three cPoCs passed.
        affected = bool(zero_reward and cpoc1_submitted and cpoc1_fails and cpoc1_guardian_shortfall and later_all_pass)
        restitution = max(0, expected_reward - actual_reward) if affected else 0

        rows.append(
            {
                "participant_address": addr,
                "weight": weights[addr],
                "actual_reward_ngonka": actual_reward,
                "actual_reward_gonka": ngonka_to_gonka(actual_reward),
                "earned_ngonka": earned,
                "missed_requests": missed,
                "source": "direct_chain_node1_node2_node3_node4",
                "denominator_mode": "aggregate_epoch_group_data_total_weight",
                "root_total_weight": root_total_weight,
                "epoch_reward_ngonka": epoch_reward,
                "epoch_reward_gonka": ngonka_to_gonka(epoch_reward),
                "pass_weight_ratio": str(PASS_WEIGHT_RATIO),
                "min_guardian_valid": MIN_GUARDIAN_VALID,
                "cpoc1": per_stage_status[0] if len(per_stage_status) > 0 else "",
                "cpoc2": per_stage_status[1] if len(per_stage_status) > 1 else "",
                "cpoc3": per_stage_status[2] if len(per_stage_status) > 2 else "",
                "cpoc4": per_stage_status[3] if len(per_stage_status) > 3 else "",
                "zero_reward": zero_reward,
                "cpoc1_submitted": cpoc1_submitted,
                "cpoc1_guardian_shortfall": cpoc1_guardian_shortfall,
                "later_three_pass": later_all_pass,
                "affected": affected,
                "expected_reward_ngonka": expected_reward if affected else 0,
                "expected_reward_gonka": ngonka_to_gonka(expected_reward) if affected else "0.000000",
                "restitution_ngonka": restitution,
                "restitution_gonka": ngonka_to_gonka(restitution),
                "event_details_json": json.dumps(per_stage_detail, sort_keys=True),
            }
        )

    rows.sort(key=lambda r: (not r["affected"], -int(r["restitution_ngonka"]), r["participant_address"]))
    os.makedirs(OUT_DIR, exist_ok=True)
    csv_path = os.path.join(OUT_DIR, "case3_per_participant.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    affected_rows = [r for r in rows if r["affected"]]
    shortfall_rows = [r for r in rows if any("shortfall" in str(r.get(f"cpoc{i}", "")) for i in range(1, 5))]
    no_vote_detail_path = os.path.join(OUT_DIR, "case3_affected_no_vote_validators.csv")
    with open(no_vote_detail_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "participant_address",
            "stage",
            "model",
            "validator_address",
            "validator_weight",
            "rank_by_weight",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in affected_rows:
            details = json.loads(r["event_details_json"])
            for event in details:
                for model, detail in (event.get("models") or {}).items():
                    for idx, item in enumerate(detail.get("top_no_vote_validators") or [], 1):
                        writer.writerow(
                            {
                                "participant_address": r["participant_address"],
                                "stage": event.get("stage"),
                                "model": model,
                                "validator_address": item.get("address"),
                                "validator_weight": item.get("weight"),
                                "rank_by_weight": idx,
                            }
                        )
    zero_reward_rows = [r for r in rows if r["zero_reward"]]
    summary = {
        "epoch": epoch,
        "source": "direct chain API only: node1-node4",
        "chain_api_bases": list(NODE_BASES),
        "cpoc_trigger_heights": stage_heights,
        "root_total_weight": root_total_weight,
        "epoch_reward_ngonka": epoch_reward,
        "epoch_reward_gonka": float(Decimal(epoch_reward) / Decimal(1_000_000_000)),
        "participants": len(rows),
        "zero_reward_participants": len(zero_reward_rows),
        "affected_participants": len(affected_rows),
        "total_restitution_ngonka": sum(int(r["restitution_ngonka"]) for r in affected_rows),
        "total_restitution_gonka": float(sum(Decimal(r["restitution_ngonka"]) for r in affected_rows) / Decimal(1_000_000_000)),
        "cpoc_status_counts": {
            f"cpoc{i}": dict(Counter(str(r.get(f"cpoc{i}", "")) for r in rows))
            for i in range(1, 5)
        },
        "all_shortfall_participants": [
            {
                "participant_address": r["participant_address"],
                "weight": r["weight"],
                "actual_reward_gonka": r["actual_reward_gonka"],
                "cpoc1": r["cpoc1"],
                "cpoc2": r["cpoc2"],
                "cpoc3": r["cpoc3"],
                "cpoc4": r["cpoc4"],
                "affected": r["affected"],
                "why_excluded": ""
                if r["affected"]
                else "shortfall is outside cPoC #1 Kimi/Qwen guardian-shortfall pattern or participant received nonzero rewards",
            }
            for r in shortfall_rows
        ],
        "policy": {
            "classification": "zero reward + cPoC1 guardian/weight shortfall + next three cPoCs pass",
            "restitution_formula": "participant_weight / root_total_weight * fixed_epoch_reward - actual_reward",
            "denominator": "aggregate epoch_group_data.total_weight",
            "pass_rule": "valid_weight >= 0.5 * model_total_weight and guardian_valid >= 2",
        },
        "affected": [
            {
                "participant_address": r["participant_address"],
                "weight": r["weight"],
                "cpoc1": r["cpoc1"],
                "cpoc2": r["cpoc2"],
                "cpoc3": r["cpoc3"],
                "cpoc4": r["cpoc4"],
                "restitution_gonka": r["restitution_gonka"],
            }
            for r in affected_rows
        ],
        "zero_reward_non_affected": [
            {
                "participant_address": r["participant_address"],
                "weight": r["weight"],
                "cpoc1": r["cpoc1"],
                "cpoc2": r["cpoc2"],
                "cpoc3": r["cpoc3"],
                "cpoc4": r["cpoc4"],
                "why_excluded": "does not match narrow case #3 pattern",
            }
            for r in zero_reward_rows
            if not r["affected"]
        ],
    }
    with open(os.path.join(OUT_DIR, "case3_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)

    log(f"wrote {csv_path}")
    log(f"wrote {no_vote_detail_path}")
    log(f"affected={len(affected_rows)} total={summary['total_restitution_gonka']:.6f} GONKA")
    for r in affected_rows:
        log(f"  {r['participant_address']} weight={r['weight']} loss={r['restitution_gonka']} cpoc1={r['cpoc1']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epoch", type=int, default=EPOCH)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    audit(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
