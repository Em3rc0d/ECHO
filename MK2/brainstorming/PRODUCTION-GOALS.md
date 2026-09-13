# MK2 Production Goals

**Status:** `GOAL_SET / NUMERIC VALUES PENDING MK1`

## Product-level goals

Operate the certified acoustic event pipeline continuously across multiple sources without silent backlog, source-state leakage or uncontrolled false alerts. Preserve reproducibility and privacy while making failures diagnosable and recoverable.

## Reliability goals

Source failures isolated; reconnect bounded; broker/model/storage degradation visible; deployment can roll back; bounded queues prevent memory/latency spirals; release artifacts reproducible.

## ML lifecycle goals

Every promoted model has data/checkpoint/config provenance, frozen evaluation, regression comparison and rollback compatibility. Drift/error evidence can trigger re-evaluation without online self-training.

## Security/privacy goals

Least privilege, authenticated delivery, secret rotation path, SBOM/provenance, no default raw-audio retention and field-data governance.

## Operability goals

Health dashboards/alerts distinguish source, model, queue, broker and storage failures. Capacity is stated as a measured envelope on declared hardware, not a marketing number.

## Cost goal

Prefer efficient/open-source/local components where they meet SLOs; measure compute/storage/network/operator costs rather than assuming “free”.

## Success

A production profile is successful only when test/certification evidence supports all frozen SLOs and known limitations are documented.