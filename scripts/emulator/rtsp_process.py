"""Bounded, per-source FFmpeg transport supervision; no ML/runtime imports.

Transport threads drain pipes independently of inference. Overflow explicitly
ends a session instead of dropping PCM and stitching disjoint samples.
"""
from __future__ import annotations

from collections import deque
from contextlib import contextmanager
import math
import queue
import re
import subprocess
import threading
import time
from urllib.parse import parse_qsl, unquote, urlsplit


CHUNK_BYTES = 16384
STDERR_LINES = 16
STDERR_LINE_CHARS = 600
STDERR_RAW_LINE_BYTES = 4096


def redact(text, uri=""):
    """No URLs, credentials or terminal/control escapes in operator diagnostics."""
    value = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", str(text))
    value = "".join(c for c in value if c.isprintable() or c == "\t")
    value = re.sub(r"(?i)\b[a-z][a-z0-9+.-]*://[^\s\"'<>]+", "[URL_REDACTED]", value)
    value = re.sub(r"(?i)\b(?:authorization|cookie|set-cookie)\s*[:=].*", "[CREDENTIAL_REDACTED]", value)
    value = re.sub(r"(?i)\bbearer\s+\S+", "Bearer [REDACTED]", value)
    value = re.sub(r"(?i)\b(password|passwd|token|secret|session|username)\s*[:=]\s*[^\s,;]+", r"\1=[REDACTED]", value)
    try:
        parsed = urlsplit(uri)
        secrets = [parsed.username, parsed.password]
        secrets.extend(v for _, v in parse_qsl(parsed.query))
        for item in secrets:
            if item:
                for candidate in {item, unquote(item)}:
                    value = value.replace(candidate, "[REDACTED]")
    except ValueError:
        pass
    return value[:STDERR_LINE_CHARS]


class StderrTail:
    def __init__(self, uri=""):
        self.uri = uri
        self.lines = deque(maxlen=STDERR_LINES)
        self.pending = b""
        self.dropping = False
        self.truncated = False
        self.lock = threading.Lock()

    def feed(self, data):
        with self.lock:
            # The reader supplies fixed <=4KiB blocks; never retain a growing line.
            for part in data.splitlines(keepends=True):
                complete = part.endswith((b"\n", b"\r"))
                if self.dropping:
                    if complete:
                        self.dropping = False
                    continue
                if len(self.pending) + len(part) > STDERR_RAW_LINE_BYTES:
                    self.pending = b""
                    self.truncated = True
                    self.dropping = not complete
                    self.lines.append("[oversized stderr line omitted]")
                    continue
                self.pending += part
                if complete:
                    self._append(self.pending)
                    self.pending = b""

    def _append(self, raw):
        if len(self.lines) == STDERR_LINES:
            self.truncated = True
        self.lines.append(redact(raw.decode("utf-8", errors="replace"), self.uri))

    def finish(self):
        with self.lock:
            if self.pending and not self.dropping:
                self._append(self.pending)
            self.pending = b""

    def snapshot(self):
        with self.lock:
            return {"stderr_tail": list(self.lines), "stderr_truncated": self.truncated}


class Backoff:
    def __init__(self, base=2.0, maximum=30.0):
        if not math.isfinite(base) or not math.isfinite(maximum) or not 0 < base <= maximum:
            raise ValueError("require finite 0 < base <= maximum")
        self.base, self.maximum, self.failures = base, maximum, 0

    def failed(self, stable=False):
        if stable:
            self.failures = 0
        self.failures += 1
        return min(self.maximum, self.base * 2 ** min(self.failures - 1, 30))


class InferenceCancelled(Exception):
    pass


class ScorerGate:
    """FIFO access to the existing shared scorer, with stop-aware waiting."""
    def __init__(self):
        self.condition = threading.Condition()
        self.waiters = deque()
        self.busy = False

    @contextmanager
    def slot(self, cancelled):
        token = object()
        began = time.monotonic()
        with self.condition:
            self.waiters.append(token)
            self.condition.notify_all()
            while self.busy or self.waiters[0] is not token:
                if cancelled():
                    self.waiters.remove(token)
                    self.condition.notify_all()
                    raise InferenceCancelled()
                self.condition.wait(0.1)
            if cancelled():
                self.waiters.popleft()
                self.condition.notify_all()
                raise InferenceCancelled()
            self.waiters.popleft()
            self.busy = True
        try:
            yield time.monotonic() - began
        finally:
            with self.condition:
                self.busy = False
                self.condition.notify_all()


def ffmpeg_command(uri, sample_rate, *, timeout_seconds=10, threads=1, binary="ffmpeg"):
    return [binary, "-nostdin", "-hide_banner", "-nostats", "-loglevel", "warning",
            "-filter_threads", "1", "-filter_complex_threads", "1",
            "-rtsp_transport", "tcp", "-allowed_media_types", "audio",
            "-timeout", str(int(timeout_seconds * 1_000_000)), "-threads", str(threads),
            "-i", uri, "-map", "0:a:0", "-vn", "-sn", "-dn", "-threads:a", "1",
            "-ac", "1", "-ar", str(sample_rate), "-f", "f32le", "-acodec", "pcm_f32le", "pipe:1"]


class RtspSession:
    def __init__(self, uri, sample_rate, *, queue_seconds=12, idle_seconds=15,
                 timeout_seconds=10, threads=1, binary="ffmpeg", factory=subprocess.Popen,
                 clock=time.monotonic):
        self.uri, self.clock = uri, clock
        self.command = ffmpeg_command(uri, sample_rate, timeout_seconds=timeout_seconds, threads=threads, binary=binary)
        self.capacity = max(1, math.ceil(sample_rate * 4 * queue_seconds / CHUNK_BYTES))
        self.audio = queue.Queue(maxsize=self.capacity)
        self.tail = StderrTail(uri)
        self.idle_seconds, self.factory = idle_seconds, factory
        self.process = None
        self.started = self.last_pcm = clock()
        self.received_bytes = 0
        self.reason = None
        self.done = threading.Event()
        self.stdout_done = threading.Event()
        self.lock = threading.Lock()
        self.close_lock = threading.Lock()
        self.threads = []
        self.closed = False
        self.forced_kill = False
        self.termination_requested = False
        self.reaped = False

    def start(self):
        if self.process is not None:
            raise RuntimeError("transport already started")
        self.started = self.last_pcm = self.clock()
        self.process = self.factory(self.command, stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    bufsize=0, close_fds=True, start_new_session=True)
        for name, target in [("pcm", self._read_stdout), ("stderr", self._read_stderr), ("watchdog", self._watch)]:
            thread = threading.Thread(target=target, name=f"rtsp-{name}-{self.process.pid}", daemon=True)
            thread.start()
            self.threads.append(thread)

    def stop(self, reason):
        with self.lock:
            if self.reason is None:
                self.reason = reason
            self.done.set()
        if self.process is not None and self.process.poll() is None:
            self.termination_requested = True
            try:
                self.process.terminate()
            except ProcessLookupError:
                pass

    def _read_stdout(self):
        pending = b""
        try:
            while not self.done.is_set():
                raw = self.process.stdout.read(CHUNK_BYTES)
                if not raw:
                    if len(pending) % 4:
                        self.stop("PCM_TRUNCATED")
                    elif pending:
                        try:
                            self.audio.put_nowait(pending)
                        except queue.Full:
                            self.stop("PCM_QUEUE_OVERFLOW")
                    break
                with self.lock:
                    self.last_pcm = self.clock()
                    self.received_bytes += len(raw)
                raw = pending + raw
                pending = raw
                while len(pending) >= CHUNK_BYTES:
                    try:
                        self.audio.put_nowait(pending[:CHUNK_BYTES])
                        pending = pending[CHUNK_BYTES:]
                    except queue.Full:
                        self.stop("PCM_QUEUE_OVERFLOW")
                        break
        except (OSError, ValueError):
            if not self.done.is_set():
                self.stop("PCM_READ_ERROR")
        finally:
            self.stdout_done.set()

    def _read_stderr(self):
        try:
            while True:
                raw = self.process.stderr.read(STDERR_RAW_LINE_BYTES)
                if not raw:
                    break
                self.tail.feed(raw)
        except (OSError, ValueError):
            if not self.done.is_set():
                self.stop("STDERR_READ_ERROR")
        finally:
            self.tail.finish()

    def _watch(self):
        while not self.done.wait(0.2):
            if self.stdout_done.is_set():
                return
            if self.clock() - self.last_pcm >= self.idle_seconds:
                self.stop("RTSP_IDLE_TIMEOUT")
                return

    def chunks(self, stop_event):
        while True:
            if stop_event.is_set():
                self.stop("SHUTDOWN")
            if self.done.is_set():
                return
            try:
                yield self.audio.get(timeout=0.2)
            except queue.Empty:
                if self.stdout_done.is_set():
                    return

    def snapshot(self):
        with self.lock:
            data = {"pid": self.process.pid if self.process else None,
                    "session_duration_seconds": round(max(0, self.clock() - self.started), 3),
                    "last_pcm_age_seconds": round(max(0, self.clock() - self.last_pcm), 3),
                    "transport_bytes": self.received_bytes, "pcm_queue_depth": self.audio.qsize(),
                    "pcm_queue_capacity": self.capacity, "transport_stop_reason": self.reason,
                    "forced_kill": self.forced_kill, "process_reaped": self.reaped}
            data["termination_requested"] = self.termination_requested
            data["cleanup_complete"] = self.closed
            data["current_exit_code"] = self.process.poll() if self.process else None
        return {**data, **self.tail.snapshot()}

    def close(self):
        """Never replace a decoder before bounded terminate/kill/reap succeeds."""
        with self.close_lock:
            if self.closed:
                return self.snapshot()
            self.done.set()
            proc = self.process
            if proc is not None:
                if proc.poll() is None:
                    self.termination_requested = True
                    try:
                        proc.terminate()
                    except ProcessLookupError:
                        pass
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.forced_kill = True
                    try:
                        proc.kill()
                    except ProcessLookupError:
                        pass
                    try:
                        proc.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        # Caller keeps this same process; no replacement is allowed.
                        return {**self.snapshot(), "process_reaped": False}
                self.reaped = True
                for thread in self.threads:
                    thread.join(timeout=1)
                for stream in [proc.stdout, proc.stderr]:
                    if stream:
                        stream.close()
                for thread in self.threads:
                    if thread.is_alive():
                        thread.join(timeout=0.2)
            else:
                self.reaped = True
            self.closed = not any(thread.is_alive() for thread in self.threads)
            return self.snapshot()
