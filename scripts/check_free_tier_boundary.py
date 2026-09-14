#!/usr/bin/env python3
"""Fail closed when ECHO drifts outside the global zero-cost execution boundary."""

from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "configs/data_foundry/free_tier_boundary.v1.json"
WORKFLOWS = ROOT / ".github/workflows"

TEN_GIB = 10 * 1024 * 1024 * 1024
ONE_DAY = 1
MAX_PROJECT_ARTIFACT_BYTES = 250 * 1024 * 1024
MAX_PREFERRED_RUN_ARTIFACT_BYTES = 100 * 1024 * 1024
STANDARD_LINUX_LABELS = {
    "ubuntu-latest",
    "ubuntu-24.04",
    "ubuntu-22.04",
    "ubuntu-slim",
}


def _require_false(mapping: dict, key: str, failures: list[str]) -> None:
    if mapping.get(key) is not False:
        failures.append(f"policy must keep {key}=false")


def _require_true(mapping: dict, key: str, failures: list[str]) -> None:
    if mapping.get(key) is not True:
        failures.append(f"policy must keep {key}=true")


def main() -> int:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    failures: list[str] = []

    if policy.get("policy_id") != "ECHO-FREE-TIER-001":
        failures.append("policy_id must remain ECHO-FREE-TIER-001")

    scope = policy.get("project_scope", {})
    for key in (
        "global_invariant",
        "applies_to_all_mks",
        "applies_to_research_execution",
        "applies_to_dataset_materialization",
        "applies_to_ci",
        "applies_to_benchmarks",
        "applies_to_model_evaluation",
        "applies_to_integration",
        "applies_to_certification",
    ):
        _require_true(scope, key, failures)
    _require_false(scope, "implicit_override_allowed", failures)

    billing = policy.get("billing_policy", {})
    for key in (
        "paid_services_allowed",
        "paid_runners_allowed",
        "paid_storage_allowed",
        "paid_apis_allowed",
        "paid_gpu_allowed",
        "paid_dataset_access_allowed",
        "automatic_overage_allowed",
    ):
        _require_false(billing, key, failures)

    gh = policy.get("github_actions", {})
    allowed = set(gh.get("allowed_runner_labels", []))
    if not allowed:
        failures.append("allowed_runner_labels must not be empty")
    if not allowed.issubset(STANDARD_LINUX_LABELS):
        failures.append(
            "allowed_runner_labels contains labels outside the frozen standard Linux set: "
            f"{sorted(allowed - STANDARD_LINUX_LABELS)}"
        )

    max_retention = int(gh.get("artifact_default_retention_days", 0))
    if max_retention > ONE_DAY:
        failures.append(f"artifact_default_retention_days must remain <= {ONE_DAY}")

    max_working_set = int(gh.get("project_max_working_set_bytes", 0))
    if max_working_set <= 0 or max_working_set > TEN_GIB:
        failures.append("project_max_working_set_bytes must remain in (0, 10 GiB]")

    total_artifact_budget = int(gh.get("artifact_total_project_budget_bytes", 0))
    if total_artifact_budget <= 0 or total_artifact_budget > MAX_PROJECT_ARTIFACT_BYTES:
        failures.append("artifact_total_project_budget_bytes must remain in (0, 250 MiB]")

    preferred_run_artifact = int(gh.get("artifact_per_run_preferred_max_bytes", 0))
    if preferred_run_artifact <= 0 or preferred_run_artifact > MAX_PREFERRED_RUN_ARTIFACT_BYTES:
        failures.append("artifact_per_run_preferred_max_bytes must remain in (0, 100 MiB]")
    if preferred_run_artifact > total_artifact_budget:
        failures.append("per-run artifact budget cannot exceed total project artifact budget")

    _require_false(gh, "dataset_cache_allowed", failures)

    dataset_rules = policy.get("dataset_rules", {})
    _require_true(dataset_rules, "process_shard_then_delete", failures)
    _require_false(dataset_rules, "full_dataset_artifact_upload", failures)
    _require_false(dataset_rules, "full_corpus_git_commit", failures)
    _require_false(dataset_rules, "quality_threshold_reduction_to_fit_free_tier_allowed", failures)

    model_rules = policy.get("model_and_benchmark_rules", {})
    _require_true(model_rules, "mandatory_certified_path_must_be_zero_cost_reproducible", failures)
    _require_false(model_rules, "paid_compute_as_required_baseline_allowed", failures)
    _require_false(model_rules, "paid_model_api_as_required_baseline_allowed", failures)

    certificate_rule = policy.get("certificate_rule", {})
    _require_false(certificate_rule, "certificate_may_pass_when_boundary_fails", failures)

    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text(encoding="utf-8")

        # ECHO default CI must stay on standard hosted Linux runners only.
        for match in re.finditer(r"(?m)^\s*runs-on:\s*(.+?)\s*$", text):
            raw = match.group(1).strip().strip("'\"")
            if raw.startswith("["):
                failures.append(
                    f"{path}: runner arrays are not allowed by the default free-tier policy: {raw}"
                )
            elif "${{" in raw:
                failures.append(f"{path}: dynamic runner selection is not allowed: {raw}")
            elif raw not in allowed:
                failures.append(
                    f"{path}: runner {raw!r} is outside allowed standard labels {sorted(allowed)}"
                )

        # Artifact retention is intentionally stricter than provider defaults.
        for match in re.finditer(r"(?m)^\s*retention-days:\s*(\d+)\s*$", text):
            days = int(match.group(1))
            if days > max_retention:
                failures.append(f"{path}: artifact retention {days}d exceeds {max_retention}d")

        lowered = text.casefold()
        forbidden_markers = (
            "runs-on: self-hosted",
            "runs-on: [self-hosted",
            "larger-runner",
            "gpu-runner",
        )
        for forbidden in forbidden_markers:
            if forbidden in lowered:
                failures.append(f"{path}: forbidden runner marker {forbidden!r}")

    if failures:
        print("FREE-TIER BOUNDARY: FAIL")
        for failure in failures:
            print(" -", failure)
        return 2

    print("FREE-TIER BOUNDARY: PASS")
    print("policy:", policy["policy_id"])
    print("global invariant:", scope["global_invariant"])
    print("all MKs:", scope["applies_to_all_mks"])
    print("allowed runners:", ", ".join(sorted(allowed)))
    print("max artifact retention days:", max_retention)
    print("max project working set bytes:", max_working_set)
    print("max active artifact bytes:", total_artifact_budget)
    print("preferred max artifact bytes/run:", preferred_run_artifact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
