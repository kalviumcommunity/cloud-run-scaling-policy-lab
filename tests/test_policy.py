"""Trusted scenario checks: repair policy.json, never weaken these checks."""
import json
import tempfile
import unittest
from pathlib import Path
from planner import load_policy, report


class PolicyChecks(unittest.TestCase):
    def setUp(self):
        self.result = report(load_policy())

    def test_task1_idle_reservation(self):
        self.assertEqual(self.result["idle_reserved_slots"], 0,
                         "Idle overnight; cold-start delay accepted: reserve zero slots")

    def test_task2_downstream_bound(self):
        self.assertLessEqual(self.result["downstream_connections"], 8,
                             "Pool 4 per replica must fit total connection budget 8")

    def test_task3_packing_and_memory(self):
        with self.subTest(rule="waves"):
            self.assertLessEqual(self.result["waves"], 2, "12 items must finish within two toy waves")
        with self.subTest(rule="first-wave"):
            # Evaluate packing under allowed replica budget, so max8 cannot mask c1.
            c = load_policy()["concurrency"]
            self.assertGreaterEqual((8 // 4) * c, 8,
                                    "At most 2 allowed replicas must admit 8 first-wave items")
        with self.subTest(rule="memory"): 
            self.assertLessEqual(self.result["per_replica_memory_mib"], 160,
                                 "32 base + 32 per simultaneous item must fit 160 MiB")


class PlannerContract(unittest.TestCase):
    def test_arithmetic(self):
        self.assertEqual(report(dict(min_instances=0, max_instances=2, concurrency=4)),
                         dict(slots=8, admitted_first_wave=8, deferred_first_wave=4, waves=2,
                              idle_reserved_slots=0, per_replica_memory_mib=160,
                              downstream_connections=8))
        self.assertEqual(report(dict(min_instances=0, max_instances=2, concurrency=1))["waves"], 6)
        self.assertEqual(report(dict(min_instances=0, max_instances=2, concurrency=5))["per_replica_memory_mib"], 192)

    def test_invalid_policy(self):
        bad = [dict(min_instances=0,max_instances=0,concurrency=1),
               dict(min_instances=3,max_instances=2,concurrency=1),
               dict(min_instances=False,max_instances=2,concurrency=4),
               dict(min_instances=0,max_instances=2,concurrency=0),
               dict(min_instances=0,max_instances=2,concurrency=1.5), {}]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"policy.json"
            for policy in bad:
                with self.subTest(policy=policy):
                    path.write_text(json.dumps(policy))
                    with self.assertRaises(ValueError):
                        load_policy(path)


if __name__ == "__main__":
    unittest.main()
