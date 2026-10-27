// Presentation-only adapter. No acoustic acceptance or scientific decisions.
export type WorkerDiagnostics = {
  phase?: string;
  phase_seconds?: number;
  worker_instance_id?: string;
  reconnect_reason?: string;
  transport_stop_reason?: string;
  current_exit_code?: number;
  last_error_type?: string;
  last_exit_code?: number;
  session_duration_seconds?: number;
  last_session_duration_seconds?: number;
  session_windows?: number;
  last_session_windows?: number;
  consecutive_failures?: number;
  backoff_seconds?: number;
  next_retry_utc?: string;
  pid?: number;
  pcm_queue_depth?: number;
  pcm_queue_capacity?: number;
  transport_bytes?: number;
  last_pcm_age_seconds?: number;
  model_wait_seconds?: number;
  inference_seconds?: number;
  forced_kill?: boolean;
  process_reaped?: boolean;
  cleanup_complete?: boolean;
  termination_requested?: boolean;
  stderr_truncated?: boolean;
  stderr_tail: string[];
};
const record = (x: unknown): Record<string, unknown> =>
  x !== null && typeof x === "object" && !Array.isArray(x)
    ? (x as Record<string, unknown>)
    : {};
export function workerDiagnostics(raw: unknown): WorkerDiagnostics {
  const value = record(raw),
    result: Record<string, unknown> = { stderr_tail: [] };
  for (const key of [
    "phase",
    "reconnect_reason",
    "transport_stop_reason",
    "last_error_type",
  ])
    if (typeof value[key] === "string" && /^[A-Za-z_]{1,64}$/.test(value[key]))
      result[key] = value[key];
  if (
    typeof value.worker_instance_id === "string" &&
    /^[a-f0-9]{32}$/.test(value.worker_instance_id)
  )
    result.worker_instance_id = value.worker_instance_id;
  for (const key of [
    "phase_seconds",
    "session_duration_seconds",
    "last_session_duration_seconds",
    "session_windows",
    "last_session_windows",
    "consecutive_failures",
    "backoff_seconds",
    "pid",
    "pcm_queue_depth",
    "pcm_queue_capacity",
    "transport_bytes",
    "last_pcm_age_seconds",
    "model_wait_seconds",
    "inference_seconds",
  ]) {
    const n = value[key];
    if (
      typeof n === "number" &&
      Number.isFinite(n) &&
      n >= 0 &&
      n <= Number.MAX_SAFE_INTEGER
    )
      result[key] = n;
  }
  for (const key of ["last_exit_code", "current_exit_code"])
    if (
      Number.isSafeInteger(value[key]) &&
      Math.abs(value[key] as number) <= 2147483647
    )
      result[key] = value[key];
  if (
    typeof value.next_retry_utc === "string" &&
    Number.isFinite(Date.parse(value.next_retry_utc))
  )
    result.next_retry_utc = new Date(value.next_retry_utc).toISOString();
  for (const key of [
    "forced_kill",
    "process_reaped",
    "cleanup_complete",
    "termination_requested",
    "stderr_truncated",
  ])
    if (typeof value[key] === "boolean") result[key] = value[key];
  if (Array.isArray(value.stderr_tail))
    result.stderr_tail = value.stderr_tail
      .slice(-16)
      .filter((s): s is string => typeof s === "string")
      .map((s) =>
        s
          .replace(/\x1b\[[0-?]*[ -/]*[@-~]/g, "")
          .replace(/[\u0000-\u001f\u007f\u202a-\u202e\u2066-\u2069]/g, " ")
          .replace(/\b[a-z][a-z0-9+.-]*:\/\/[^\s"'<>]+/gi, "[URL_REDACTED]")
          .replace(
            /\b(?:authorization|cookie|set-cookie)\s*[:=].*/gi,
            "[CREDENTIAL_REDACTED]",
          )
          .replace(/\bbearer\s+\S+/gi, "Bearer [REDACTED]")
          .replace(
            /\b(password|passwd|token|secret|session|username)\s*[:=]\s*[^\s,;]+/gi,
            "$1=[REDACTED]",
          )
          .slice(0, 600),
      );
  return result as WorkerDiagnostics;
}

export function snapshotFreshness(raw: unknown, now = Date.now()) {
  const data = record(raw);
  const stamp = typeof data.at === "string" ? Date.parse(data.at) : NaN;
  const heartbeat =
    typeof data.updated_at === "string" ? Date.parse(data.updated_at) : stamp;
  const age = Number.isFinite(stamp) ? Math.max(0, now - stamp) : null;
  const heartbeatAge = Number.isFinite(heartbeat)
    ? Math.max(0, now - heartbeat)
    : null;
  const snapshotStale =
    heartbeatAge === null || heartbeatAge > 15000 || heartbeat > now + 5000;
  const allowed = [
    "STARTING",
    "CONNECTING",
    "ONLINE",
    "RECONNECTING",
    "REAPING",
    "WORKER_STOPPED",
    "STOPPED",
  ];
  const state =
    typeof data.state === "string" && allowed.includes(data.state)
      ? data.state
      : "UNKNOWN";
  return {
    state: snapshotStale ? "STALE" : state,
    age_ms: age,
    snapshot_age_ms: heartbeatAge,
    stale:
      snapshotStale ||
      age === null ||
      age > 15000 ||
      stamp > now + 5000 ||
      state !== "ONLINE",
  };
}
