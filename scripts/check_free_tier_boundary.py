#!/usr/bin/env python3
"""Fail closed when ECHO workflows drift outside the zero-cost boundary."""

from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "configs/data_foundry/free_tier_boundary.v1.json"
WORKFLOWS = ROOT / ".github/workflows"


def main() -> int:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    gh = policy["github_actions"]
    allowed = set(gh["allowed_runner_labels"])
    max_retention = int(gh["artifact_default_retention_days"])
    failures: list[str] = []

    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text(encoding="utf-8")

        # ECHO default CI must stay on standard hosted Linux runners only.
        for match in re.finditer(r"(?m)^\s*runs-on:\s*(.+?)\s*$", text):
            raw = match.group(1).strip().strip("'\"")
            if raw.startswith("["):
                failures.append(f"{path}: runner arrays are not allowed by the default free-tier policy: {raw}")
            elif "${{" in raw:
                failures.append(f"{path}: dynamic runner selection is not allowed: {raw}")
            elif raw not in allowed:
                failures.append(f"{path}: runner {raw!r} is outside allowed standard labels {sorted(allowed)}")

        for match in re.finditer(r"(?m)^\s*retention-days:\s*(\d+)\s*$", text):
            days = int(match.group(1))
            if days > max_retention:
                failures.append(f"{path}: artifact retention {days}d exceeds {max_retention}d")

        lowered = text.casefold()
        for forbidden in ("larger-runner", "gpu-runner", "runs-on: self-hosted"):
            if forbidden in lowered:
                failures.append(f"{path}: forbidden paid/external runner marker {forbidden!r}")

    if policy["billing_policy"].get("paid_services_allowed") is not False:
        failures.append("policy must keep paid_services_allowed=false")
    if policy["billing_policy"].get("automatic_overage_allowed") is not False:
        failures.append("policy must keep automatic_overage_allowed=false")

    if failures:
        print("FREE-TIER BOUNDARY: FAIL")
        for failure in failures:
            print(" -", failure)
        return 2

    print("FREE-TIER BOUNDARY: PASS")
    print("allowed runners:", ", ".join(sorted(allowed)))
    print("max artifact retention days:", max_retention)
    print("max project working set bytes:", gh["project_max_working_set_bytes"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
