# Cloud Run scaling policy lab

**Toy batch-capacity arithmetic, not a Cloud Run autoscaler, benchmark, latency, billing or price forecast.** Local Docker only. No cloud project, billing account, load test, registry login, token or Actions run.

## Before class
Install Git and eligible local Docker runtime; start Docker and pre-pull `python:3.12-slim`. Sign in to free GitHub account, fork this public repo and clone your fork. Use Bash on Linux/macOS or Git Bash with Docker Desktop on Windows. Windows commands are reasoned, not Windows-tested. MSYS can rewrite container paths: these commands avoid volume paths; use `MSYS_NO_PATHCONV=1` if a later command's absolute container path is altered. Installs, downloads and account setup are outside 20-minute learning + 30-minute assignment. Novice recording/Git work may need extra support; timing not cohort-validated.

Create branch `fix/scaling-policy`. Edit only `policy.json` and `scaling-notes.md`; planner, Dockerfile and tests are trusted and must stay unchanged. Exactly three planted policy faults. Baseline intentionally fails all three task checks. No hidden app/port defect.

## Fixed scenario and derivable rules
12 identical work items arrive together. Each holds one simultaneous slot for one abstract wave. Every replica has toy memory budget 160 MiB: 32 base + 32 per simultaneous item. Each replica reserves a pool of 4 downstream connections; total budget 8. Service idle overnight; cold-start delay accepted, so reserve zero idle slots. Admit at least 8 items in the first wave and finish batch in at most two toy waves. These are assumed constants, not measured RAM/pools or actual Cloud Run behavior.

Policy keys: integer `min_instances >= 0`, positive integer `max_instances` and `concurrency`, min <= max. Concurrency means maximum simultaneous work per replica, **not requests per second**.

- slots = max * concurrency
- first-wave admitted = min(12, slots); deferred = max(0, 12 - slots)
- waves = ceil(12 / slots)
- idle reserved slots = min * concurrency = 0
- downstream connections = max * 4 <= 8
- per-replica toy memory = 32 + 32 * concurrency <= 160

Derive feasible settings from all rules. Do not increase memory/pool budgets or change tests to make a check green. Deferred means later abstract waves here, not a claim about Cloud Run's queue/rejection behavior.

## Real commands
Run from repo root. No host Python needed. Rebuild after every policy edit: copied files in old image do not update.

```bash
docker build -t scaling-policy:lab .
docker run --rm --network none --cpus 1 --memory 256m scaling-policy:lab python -m unittest discover -s tests -v
docker run --rm --network none --cpus 1 --memory 256m scaling-policy:lab python planner.py --report
```

A failed test exits nonzero; run report separately even when tests fail. `docker build` packages files; `docker run --rm` executes a new local container and removes it when done. Network disabled for runs. Build may fetch base image if not preloaded.

## Three tasks: 10 marks, 30 minutes
1. **Idle reservation (3):** fix minimum; show before/after task1 check and explain warm-floor and zero-bill misconceptions. Commit policy + notes.
2. **Downstream bound (3):** derive maximum from fixed pool/budget; show connections before/after. Explain max limit and ordinary alerts-only budget caveats. Commit policy + notes.
3. **Packing (4):** derive concurrency within memory and two-wave target. Compare max2/c1 and chosen policy, show four deferred items, all tests passing, then temporarily set concurrency to 5, rebuild and show memory rejection. Restore intended policy, rebuild, pass again. Commit policy + notes. Supply public personal-fork PR plus accessible video maximum 3:00, covering all three root causes, evidence and cloud limitations. No PDF/quiz/deck submission.

Suggested allocation: baseline4, task1 4, task2 5, task3 8, PR/video7, cleanup2. Capture original terminal evidence, never paste mentor output. Three meaningful solution commits. Open PR **inside your own fork**, base main, compare fix/scaling-policy; do not send fixes to starter main. Include video and before/after/negative evidence in PR description. Leave main broken. Learner can verify trusted files with `git diff main -- planner.py tests Dockerfile` (must be empty).

Rubric: task1 policy1 + evidence1 + explanation1; task2 derivation/fix1 + evidence1 + cloud/budget explanation1; task3 packing/memory derivation1 + comparative/deferred evidence1 + final/negative evidence1 + public PR/video explaining all root causes and limits1. Missing evidence affects its criterion, not automatic whole-assignment zero.

## Cloud boundaries
Cloud Run uses multiple autoscaling inputs and controls; memory utilization is not an autoscaling signal. Best-effort warm minimum can restart and bursts/rollouts can cold-start. Zero minimum permits scale-to-zero, not immediate termination or zero whole bill. Maximum can briefly be exceeded; scope across revisions matters. Pools, fan-out/retries and other workloads affect downstream demand.

Request-based billing treats processing/startup/shutdown and idle minimum capacity differently; instance-based bills whole lifetime including idle. Allocation, duration, requests, region and other services matter. No money model here. Ordinary alerts-only budgets notify and can lag, not shut down; separate supported spend-cap features have eligibility/coverage limits and are not this lab's safety boundary. Strictly local execution is boundary.

## Cleanup
Containers self-remove. Optionally remove only this lab image: `docker image rm scaling-policy:lab`. Never global-prune Docker. No cloud cleanup needed because no cloud resources created.
