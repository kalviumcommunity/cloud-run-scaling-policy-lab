"""Toy batch-capacity arithmetic, NOT a Cloud Run autoscaler or price forecast."""
import argparse
import json
from pathlib import Path

BURST = 12
MEMORY = 160
BASE_MEMORY = 32
REQUEST_MEMORY = 32
POOL = 4
CONNECTION_LIMIT = 8


def load_policy(path="policy.json"):
    policy = json.loads(Path(path).read_text())
    keys = {"min_instances", "max_instances", "concurrency"}
    if not isinstance(policy, dict) or set(policy) != keys:
        raise ValueError("Policy must contain exactly min_instances, max_instances, concurrency")
    if any(type(v) is not int for v in policy.values()):
        raise ValueError("All policy values must be integers, not booleans")
    lo, hi, c = (policy[k] for k in ("min_instances", "max_instances", "concurrency"))
    if not (0 <= lo <= hi and hi > 0 and c > 0):
        raise ValueError("Require 0 <= min <= max, max > 0, concurrency > 0")
    return policy


def report(policy):
    lo, hi, c = (policy[k] for k in ("min_instances", "max_instances", "concurrency"))
    slots = hi * c
    return dict(slots=slots, admitted_first_wave=min(BURST, slots),
                deferred_first_wave=max(0, BURST-slots), waves=(BURST+slots-1)//slots,
                idle_reserved_slots=lo*c, per_replica_memory_mib=BASE_MEMORY+REQUEST_MEMORY*c,
                downstream_connections=hi*POOL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--policy", default="policy.json")
    args = parser.parse_args()
    print("TOY assumptions only: not measured RAM, Cloud Run scaling, latency, billing or pricing")
    print(json.dumps(report(load_policy(args.policy)), indent=2))
