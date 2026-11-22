"""Validate handoff consistency and golden arithmetic, not application behavior."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/evidence/handoff-validation.json"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--write-report", action="store_true")
args = parser.parse_args()
checks = []


def check(name: str, condition: bool, detail: str = "") -> None:
    checks.append({"check": name, "status": "passed" if condition else "failed", "detail": detail})


def read_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


required = ["AGENTS.md", "START_HERE.md", "README.md", "plan.md", ".gitignore", "docs/PROGRESS.md", "docs/progress.json", "docs/GIT_CHECKPOINTS.md", "docs/VALIDATION.md", "docs/DECISIONS.md", "docs/INTEGRATIONS.md", "docs/KNOWN_ISSUES.md", "docs/context/README.md", "tests/fixtures/contracts/README.md"]
for relative in required:
    check("required-file:" + relative, (ROOT / relative).is_file())
if not all(c["status"] == "passed" for c in checks):
    raise SystemExit(json.dumps(checks, indent=2))

plan = (ROOT / "plan.md").read_text(encoding="utf-8")
task_ids = re.findall(r"^- (P\d{2}-T\d{2}):", plan, re.M)
tracker = read_json("docs/progress.json")
tracked = [task for phase in tracker["phases"] for task in phase["tasks"]]
check("unique-plan-task-ids", len(task_ids) == len(set(task_ids)))
check("tracker-matches-plan-tasks", set(task_ids) == {t["id"] for t in tracked})
check("unique-tracker-task-ids", len(tracked) == len({t["id"] for t in tracked}))
states = {"not_started", "in_progress", "blocked", "complete"}
phase_ids = {p["id"] for p in tracker["phases"]}
policy = tracker.get("git_policy", {})
check("mandatory-phase-commit-and-push", all(policy.get(k) is True for k in ("commit_after_each_phase", "push_after_each_phase", "verify_remote", "publish_checkpoint_receipt")))
check("checkpoint-authorization-scope", policy.get("authorized_remote") == "https://github.com/sakibul-shovon/Shongoti.git" and policy.get("allow_force_push") is False and policy.get("allow_visibility_change") is False)
human_progress = (ROOT / "docs/PROGRESS.md").read_text(encoding="utf-8")
for phase in tracker["phases"]:
    check("phase-state:" + phase["id"], phase["status"] in states)
    check("phase-dependencies:" + phase["id"], set(phase["depends_on"]).issubset(phase_ids) and phase["id"] not in phase["depends_on"])
    row = next((line for line in human_progress.splitlines() if line.startswith("| " + phase["id"] + " |")), "")
    check("human-machine-phase-state:" + phase["id"], "| " + phase["status"] + " |" in row)
    checkpoint = phase.get("git_checkpoint", {})
    check("checkpoint-required:" + phase["id"], checkpoint.get("required") is True and checkpoint.get("status") in {"not_started", "pending", "blocked", "published"})
    for task in phase["tasks"]:
        check("task-state:" + task["id"], task["status"] in states)
        if task["status"] == "complete":
            check("completed-task-evidence-list:" + task["id"], bool(task["evidence"]))
            for evidence in task["evidence"]:
                target = ROOT / evidence
                self_report = args.write_report and target.resolve() == REPORT.resolve() and task["id"].startswith("P00-")
                check("completed-task-evidence:" + task["id"], target.is_file() or self_report, evidence)
    if phase["status"] == "complete":
        check("complete-phase-has-complete-tasks:" + phase["id"], all(t["status"] == "complete" for t in phase["tasks"]))
        receipt_path = checkpoint.get("receipt_path")
        milestone_sha = checkpoint.get("milestone_sha") or ""
        check("complete-phase-published-checkpoint:" + phase["id"], checkpoint.get("status") == "published" and bool(re.fullmatch(r"[0-9a-f]{40}", milestone_sha)))
        receipt = ROOT / receipt_path if receipt_path else None
        check("complete-phase-checkpoint-receipt:" + phase["id"], receipt is not None and receipt.is_file())
        if receipt is not None and receipt.is_file():
            observed = json.loads(receipt.read_text(encoding="utf-8"))
            check("receipt-matches-phase:" + phase["id"], observed.get("phase_id") == phase["id"] and observed.get("milestone_sha") == milestone_sha and observed.get("status") == "published")
        if re.fullmatch(r"[0-9a-f]{40}", milestone_sha):
            ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", milestone_sha, "HEAD"], cwd=ROOT, capture_output=True)
            check("checkpoint-is-local-ancestor:" + phase["id"], ancestor.returncode == 0)

markdown_paths = [ROOT / p for p in required if p.endswith(".md")]
for path in markdown_paths:
    content = path.read_text(encoding="utf-8")
    check("markdown-code-fences:" + path.relative_to(ROOT).as_posix(), content.count("```") % 2 == 0)
    check("utf8-no-replacement:" + path.relative_to(ROOT).as_posix(), "\ufffd" not in content)
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", content):
        target = match.group(1).strip("<>")
        if target.startswith(("https://", "http://", "#", "mailto:")):
            continue
        resolved = path.parent / target.split("#", 1)[0]
        check("local-link:" + path.relative_to(ROOT).as_posix(), resolved.exists(), target)

fixtures = ROOT / "tests/fixtures/contracts"
all_case_ids = []
rec = read_json("tests/fixtures/contracts/reconciliation.json")
facts = rec["source_facts"]
for case in rec["cases"]:
    p = [True, False] if case["payment_included"] is None else [case["payment_included"]]
    r = [True, False] if case["return_included"] is None else [case["return_included"]]
    payable = sorted({facts["demand"]["amount"] - (0 if pi else facts["eligible_payment"]["amount"]) - (0 if ri else facts["accepted_return"]["amount"]) for pi, ri in itertools.product(p, r)})
    check("golden-reconciliation:" + case["id"], payable == case["expected_payables"])
    all_case_ids.append(case["id"])
check("other-receipt-capacity-zero", facts["unavailable_other_receipt"]["amount"] == facts["unavailable_other_receipt"]["allocated_amount"])

scenarios = read_json("tests/fixtures/contracts/cash-scenarios.json")
for case in scenarios["cases"]:
    balance = scenarios["opening_cash"]
    expected = []
    for index, (date, outflow) in enumerate(zip(scenarios["dates"], scenarios["planned_outflows"], strict=True)):
        balance += scenarios["assumed_daily_cash_receipt"] - outflow
        if index == 0:
            balance -= case["extra_expense_day_1"]
        promise = case["conditional_promise"]
        if promise and date == promise["date"]:
            balance += promise["amount"]
        expected.append(balance)
    reserve_breach = next((d for d, b in zip(scenarios["dates"], expected, strict=True) if b < scenarios["reserve_target"]), None)
    shortfall = next((d for d, b in zip(scenarios["dates"], expected, strict=True) if b < 0), None)
    check("golden-scenario:" + case["id"], expected == case["expected_closing_cash"] and reserve_breach == case["expected_first_reserve_breach"] and shortfall == case["expected_first_funding_shortfall"])
    all_case_ids.append(case["id"])

liq = read_json("tests/fixtures/contracts/liquidity.json")
for case in liq["cases"]:
    all_case_ids.append(case["id"])
    if "illustrative_permitted_cashout" in case:
        move = case["illustrative_permitted_cashout"]
        after = dict(liq["accounts"])
        after[move["from"]] -= move["principal"] + move["fee"]
        after["cash"] += move["principal"]
        check("golden-cashout:" + case["id"], after == case["expected_accounts_after_cashout"] and sum(after.values()) == case["expected_total_after_cashout"])
    else:
        cash = liq["accounts"]["cash"] + case["actual_cash_receipt"]
        due = liq["obligation"]["amount"]
        check("golden-current-liquidity:" + case["id"], case.get("expected_available_cash", case.get("expected_cash_before_payment", cash)) == cash)
        if "expected_cash_after_payment" in case:
            check("golden-postpayment-cash:" + case["id"], cash - due == case["expected_cash_after_payment"])
        for key in ("expected_funding_shortfall", "expected_funding_shortfall_now"):
            if key in case:
                check("golden-shortfall:" + case["id"], max(0, due - cash) == case[key])
        if "expected_reserve_shortfall" in case:
            check("golden-reserve-shortfall:" + case["id"], max(0, case["cash_reserve"] - (cash - due)) == case["expected_reserve_shortfall"])

posting = read_json("tests/fixtures/contracts/posting.json")
for case in posting["cases"]:
    all_case_ids.append(case["id"])
    if case["operation"] == "split_sale":
        check("golden-split-sale", case["cash_received"] + case["expected_receivable_change"] == case["amount"] and case["expected_sales_revenue_change"] == case["amount"])
check("golden-case-ids-unique", len(all_case_ids) == len(set(all_case_ids)))
for path in fixtures.glob("*.json"):
    data = json.loads(path.read_text(encoding="utf-8"))
    check("explicit-synthetic-money-units:" + path.name, data["synthetic"] is True and data["currency"] == "BDT" and data["money_unit"] == "paisa")

remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, text=True, capture_output=True)
check("git-origin", remote.returncode == 0 and remote.stdout.strip() == "https://github.com/sakibul-shovon/Shongoti.git")
for path, ignored in [(".env", True), ("apps/api/.env.production", True), ("node_modules/a.js", True), ("apps/web/node_modules/a.js", True), ("uploads/customer.png", True), ("docs/evidence/raw/provider.log", True), (".env.example", False), ("apps/api/.env.example", False), ("pnpm-lock.yaml", False), ("tests/fixtures/contracts/cash-scenarios.json", False), ("docs/evidence/phase-02/result.json", False)]:
    outcome = subprocess.run(["git", "check-ignore", "--no-index", path], cwd=ROOT, capture_output=True)
    check("gitignore:" + path, outcome.returncode == (0 if ignored else 1))

preview = (ROOT / "docs/reference-ui/shongoti-product-preview.html").read_text(encoding="utf-8")
scripts = re.findall(r"<script>([\s\S]*?)</script>", preview)
for index, code in enumerate(scripts):
    syntax = subprocess.run(["node", "--check"], input=code, text=True, encoding="utf-8", capture_output=True)
    check("reference-preview-script-syntax:" + str(index), syntax.returncode == 0)

secret_patterns = [re.compile(r"AIza[0-9A-Za-z_-]{35}"), re.compile(r"ghp_[A-Za-z0-9]{36}"), re.compile(r"github_pat_[A-Za-z0-9_]{60,}"), re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")]
source_hashes = []
for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or ".git" in path.relative_to(ROOT).parts or path.resolve() == REPORT.resolve():
        continue
    relative = path.relative_to(ROOT).as_posix()
    source_hashes.append({"path": relative, "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    if path.suffix in {".md", ".json", ".html", ".py"}:
        text = path.read_text(encoding="utf-8")
        check("credential-pattern-scan:" + relative, not any(pattern.search(text) for pattern in secret_patterns), "Limited pattern scan; not a guarantee of absence of all secrets.")

passed = all(c["status"] == "passed" for c in checks)
report = {"status": "passed" if passed else "failed", "scope": "handoff consistency and synthetic contract arithmetic only", "application_tests_run": False, "live_ai_verified": False, "real_integrations_verified": False, "browser_layout_verified": False, "ran_at_utc": datetime.now(timezone.utc).isoformat(), "command": "python tools/verify_handoff.py" + (" --write-report" if args.write_report else ""), "working_directory": "repository root", "mode": "offline", "exit_code": 0 if passed else 1, "phase_count": len(tracker["phases"]), "task_count": len(tracked), "synthetic_case_count": len(all_case_ids), "checks": checks, "files": source_hashes}
if args.write_report:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({k: v for k, v in report.items() if k not in {"checks", "files"}}, ensure_ascii=False))
for failure in (c for c in checks if c["status"] != "passed"):
    print(json.dumps(failure, ensure_ascii=False))
raise SystemExit(0 if passed else 1)
