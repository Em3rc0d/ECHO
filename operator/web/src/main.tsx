import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import Hls from "hls.js";
import "./style.css";

type User = {
  user_id: string;
  username: string;
  role: "viewer" | "operator" | "admin";
  sites: string[];
};
type Me = {
  user: User;
  lab_push_enabled: boolean;
  push_ready: boolean;
  vapid_public_key: string;
};
type Acoustic = {
  event_id: string;
  source_id: string;
  site_id: string;
  event_type: string;
  lifecycle: string;
  origin: string;
  onset_utc: string;
  end_utc: string | null;
  confidence: { peak: number; mean: number };
  stream_session_id: string;
  model_version: string;
  threshold_version: string;
  provenance?: { lifecycle?: string };
};
type Alert = Acoustic & { alert_id: string; state: string; severity: string };
type Live = {
  state: string;
  at?: string;
  updated_at?: string;
  diagnostics?: {
    phase?: string;
    phase_seconds?: number;
    worker_instance_id?: string;
    pid?: number;
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
    pcm_queue_depth?: number;
    pcm_queue_capacity?: number;
    transport_bytes?: number;
    model_wait_seconds?: number;
    inference_seconds?: number;
    last_pcm_age_seconds?: number;
    process_reaped?: boolean;
    cleanup_complete?: boolean;
    forced_kill?: boolean;
    stderr_tail: string[];
    stderr_truncated?: boolean;
  };
  session?: string;
  worker_generation?: number;
  scores: Record<string, number>;
  waveform_envelope: number[];
  windows: number;
  rms: number;
  peak: number;
  window_start_utc: string;
  window_end_utc: string;
  estimated_lag_ms: number | null;
  events: {
    event_id?: string;
    event_type?: string;
    provenance?: { lifecycle?: string };
  }[];
  age_ms: number | null;
  stale: boolean;
};
type Source = {
  source_id: string;
  site_id: string;
  name: string;
  kind: string;
  enabled: boolean;
  emulated: boolean;
  media_path: string | null;
  camera_state: string;
  emulator_generation: number;
  scenario: string;
  source_at: string | null;
  live: Live | null;
};
type Snapshot = {
  at: string;
  sources: Source[];
  events: Acoustic[];
  alerts: Alert[];
  alert_totals: Record<string, number>;
  mqtt: { connected: boolean; last_message_at: string | null };
  boundary: string;
};
type Detail = {
  event: Acoustic;
  receipts: { lifecycle: string; payload: unknown; received_at: string }[];
  alert: Alert | null;
  history: { action: string; created_at: string }[];
};
const names: Record<string, string> = {
  GLASS_SHATTER: "Rotura de vidrio",
  SIREN: "Sirena",
  VEHICLE_HORN: "Claxon",
};
const origins: Record<string, string> = {
  LAB_DIAGNOSTIC: "Laboratorio · diagnóstico",
  CONTROLLED_OR_UNASSESSED: "Controlado / sin aceptación operativa",
  ACCEPTED_OPERATIONAL: "Aceptación operativa autorizada",
};
const short = (s: string) => s?.replace("VMT-CAM-", "CAM ") || "—";
const when = (s?: string | null) =>
  s
    ? new Date(s).toLocaleTimeString("es-PE", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })
    : "—";
const age = (s?: string | null) =>
  s ? Math.max(0, Math.round((Date.now() - Date.parse(s)) / 1000)) : null;
const percent = (n?: number) =>
  typeof n === "number" ? `${(n * 100).toFixed(1)}%` : "—";
const isStale = (s: Source) =>
  !s.live?.at || (age(s.live.at) ?? Infinity) > 15 || s.live.stale;
const canOperate = (m: Me) => m.user.role !== "viewer";
const humanError = (code: string) =>
  ({
    SESSION_REQUIRED: "Tu sesión terminó. Vuelve a ingresar.",
    INVALID_CREDENTIALS: "Usuario o contraseña incorrectos.",
    ORIGIN_DENIED: "El origen no coincide con PUBLIC_ORIGIN.",
    FORBIDDEN: "Esta acción requiere permisos adicionales.",
    NO_PUSH_SUBSCRIPTION: "Primero activa las notificaciones.",
    ALERT_STATE_CONFLICT: "La alerta cambió. Actualiza la vista.",
    SERVICE_ERROR:
      "No se pudo completar la operación. Revisa el estado del servicio.",
    PUSH_PROVIDER_DENIED:
      "El proveedor push no está autorizado en este despliegue.",
  })[code] || code;
async function api<T = any>(
  path: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  const r = await fetch("/api" + path, {
    method,
    credentials: "same-origin",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const value = await r.json();
  if (!r.ok) throw new Error(humanError(value.error || `HTTP ${r.status}`));
  return value;
}
function Icon({ name, size = 20 }: { name: string; size?: number }) {
  const paths: Record<string, React.ReactNode> = {
    grid: (
      <>
        <rect x="3" y="3" width="7" height="7" rx="1.5" />
        <rect x="14" y="3" width="7" height="7" rx="1.5" />
        <rect x="3" y="14" width="7" height="7" rx="1.5" />
        <rect x="14" y="14" width="7" height="7" rx="1.5" />
      </>
    ),
    camera: (
      <>
        <rect x="3" y="6" width="12" height="12" rx="2" />
        <path d="m15 10 6-3v10l-6-3" />
      </>
    ),
    pulse: <path d="M2 12h4l3-8 5 16 3-8h5" />,
    bell: (
      <>
        <path d="M5 17h14l-2-3V9a5 5 0 0 0-10 0v5z" />
        <path d="M10 21h4" />
      </>
    ),
    settings: (
      <>
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v3m0 14v3M2 12h3m14 0h3M5 5l2 2m10 10 2 2M5 19l2-2M17 7l2-2" />
      </>
    ),
    arrow: <path d="m9 5 7 7-7 7" />,
    check: <path d="m5 12 4 4 10-10" />,
    wave: <path d="M3 10v4m4-7v10m5-14v18m5-14v10m4-7v4" />,
  };
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name] || paths.pulse}
    </svg>
  );
}
function Badge({
  children,
  tone = "muted",
}: {
  children: React.ReactNode;
  tone?: string;
}) {
  return <span className={"badge " + tone}>{children}</span>;
}
function Empty({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="empty">
      <Icon name="wave" size={32} />
      <h3>{title}</h3>
      <p>{children}</p>
    </div>
  );
}
function Wave({
  values,
  stale = false,
}: {
  values: number[];
  stale?: boolean;
}) {
  return (
    <svg
      className={"wave " + (stale ? "stale" : "")}
      viewBox="0 0 512 72"
      role="img"
      aria-label={
        stale
          ? "Envolvente sin datos recientes"
          : "Envolvente de amplitud medida en la última ventana"
      }
    >
      <path d="M0 36H512" className="baseline" />
      {values.map((v, i) => (
        <line
          key={i}
          x1={i * 8 + 4}
          x2={i * 8 + 4}
          y1={36 - v * 34}
          y2={36 + v * 34}
        />
      ))}
    </svg>
  );
}
function Player({
  source,
  preview = false,
}: {
  source: Source;
  preview?: boolean;
}) {
  const ref = useRef<HTMLVideoElement>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    setError("");
    const url = `/api/media/${source.source_id}/index.m3u8`;
    let h: Hls | undefined;
    if (el.canPlayType("application/vnd.apple.mpegurl")) el.src = url;
    else if (Hls.isSupported()) {
      h = new Hls({
        maxBufferLength: 8,
        backBufferLength: 0,
        manifestLoadingMaxRetry: 2,
        fragLoadingMaxRetry: 2,
      });
      h.loadSource(url);
      h.attachMedia(el);
      h.on(Hls.Events.ERROR, (_, data) => {
        if (data.fatal)
          setError(
            "Stream no disponible. Reabre el reproductor cuando la fuente se recupere.",
          );
      });
    } else setError("Este navegador no admite HLS.");
    if (preview) void el.play().catch(() => {});
    return () => {
      h?.destroy();
      el.pause();
      el.removeAttribute("src");
      el.load();
    };
  }, [source.source_id, source.emulator_generation, preview]);
  return (
    <div className={"player " + (preview ? "preview" : "")}>
      <video
        ref={ref}
        controls={!preview}
        muted
        playsInline
        autoPlay={preview}
        onError={() => setError("No se pudo reproducir el stream.")}
        aria-label={`Video sintético y audio de ${source.name}`}
      />
      {error && <p className="player-error">{error}</p>}
      <span className="player-label">VMT / VIDEO SINTÉTICO</span>
    </div>
  );
}
function Login({ onLogin }: { onLogin: () => void }) {
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  return (
    <main className="login">
      <div className="login-art">
        <div className="brand">
          <Icon name="wave" size={40} />
          <b>
            ECHO<span>OPERATOR</span>
          </b>
        </div>
        <h1>
          Escucha el entorno.
          <br />
          <em>Enfoca tu atención.</em>
        </h1>
        <p>
          Inteligencia acústica por fuente, con evidencia y límites visibles.
        </p>
        <div className="static-signal" aria-hidden="true">
          <Icon name="wave" size={180} />
        </div>
        <Badge tone="blue">Plataforma experimental · MK1</Badge>
      </div>
      <form
        className="login-form panel"
        onSubmit={async (e) => {
          e.preventDefault();
          setBusy(true);
          setError("");
          const f = new FormData(e.currentTarget);
          try {
            await api("/login", "POST", {
              username: f.get("username"),
              password: f.get("password"),
            });
            onLogin();
          } catch (err) {
            setError((err as Error).message);
          } finally {
            setBusy(false);
          }
        }}
      >
        <span className="eyebrow">ACCESO DEL OPERADOR</span>
        <h2>Bienvenido a ECHO</h2>
        <p>Ingresa con una cuenta autorizada para tu sitio.</p>
        <label>
          Usuario
          <input
            name="username"
            required
            maxLength={80}
            autoComplete="username"
          />
        </label>
        <label>
          Contraseña
          <input
            name="password"
            type="password"
            required
            maxLength={256}
            autoComplete="current-password"
          />
        </label>
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        <button className="primary" disabled={busy}>
          {busy ? "Ingresando…" : "Abrir centro de operaciones"}
          <Icon name="arrow" />
        </button>
        <small>Detección acústica ≠ confirmación de incidentes.</small>
      </form>
    </main>
  );
}
function App() {
  const [me, setMe] = useState<Me | null>(null),
    [checking, setChecking] = useState(true),
    [data, setData] = useState<Snapshot | null>(null);
  const [connection, setConnection] = useState("CONNECTING"),
    [page, setPage] = useState("operations"),
    [selected, setSelected] = useState("");
  const [search, setSearch] = useState(""),
    [activity, setActivity] = useState(false),
    [order, setOrder] = useState("source"),
    [layout, setLayout] = useState("grid"),
    [previews, setPreviews] = useState(false),
    [playing, setPlaying] = useState(false);
  const [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false),
    [now, setNow] = useState(Date.now());
  const [history, setHistory] = useState<Acoustic[]>([]),
    [offset, setOffset] = useState(0),
    [filters, setFilters] = useState<Record<string, string>>({}),
    [detail, setDetail] = useState<Detail | null>(null);
  const [pushInfo, setPushInfo] = useState<any>(null),
    [users, setUsers] = useState<any[]>([]),
    [deferredInstall, setDeferredInstall] = useState<any>(null);
  const traces = useRef(
    new Map<string, { session: string; at: string; values: number[] }>(),
  );
  const refreshMe = async () => {
    try {
      setMe(await api<Me>("/me"));
    } catch {
      setMe(null);
    } finally {
      setChecking(false);
    }
  };
  useEffect(() => {
    void refreshMe();
    const clock = setInterval(() => setNow(Date.now()), 1000);
    const install = (e: Event) => {
      e.preventDefault();
      setDeferredInstall(e);
    };
    window.addEventListener("beforeinstallprompt", install);
    return () => {
      clearInterval(clock);
      window.removeEventListener("beforeinstallprompt", install);
    };
  }, []);
  const notify = (err: unknown) =>
    setMessage(err instanceof Error ? err.message : String(err));
  const openEvent = async (id: string, navigate = true) => {
    try {
      setDetail(await api<Detail>(`/events/${encodeURIComponent(id)}`));
      setPage("events");
      if (navigate)
        window.history.pushState({}, "", `/events/${encodeURIComponent(id)}`);
    } catch (err) {
      notify(err);
    }
  };
  useEffect(() => {
    if (!me) return;
    let active = true;
    const initial = () =>
      void api<Snapshot>("/snapshot")
        .then((d) => {
          if (active) setData(d);
        })
        .catch(notify);
    initial();
    const stream = new EventSource("/api/stream");
    stream.addEventListener("snapshot", (e) => {
      setData(JSON.parse((e as MessageEvent).data));
      setConnection("LIVE");
    });
    stream.addEventListener("capacity", () => {
      setConnection("CAPACITY");
      setMessage(
        "La actualización excede el límite de esta instancia. Revisa la capacidad antes de ampliar las fuentes.",
      );
      stream.close();
    });
    stream.onerror = () => {
      setConnection("RECONNECTING");
      void api("/me").catch(() => {
        setMe(null);
        stream.close();
      });
    };
    const restore = () => {
      const match = /^\/events\/(.+)$/.exec(window.location.pathname);
      if (match) void openEvent(decodeURIComponent(match[1]), false);
      else setDetail(null);
    };
    restore();
    window.addEventListener("popstate", restore);
    return () => {
      active = false;
      stream.close();
      window.removeEventListener("popstate", restore);
    };
  }, [me?.user.user_id]);
  useEffect(() => {
    if (!data) return;
    for (const s of data.sources) {
      if (!s.live?.at || isStale(s)) continue;
      const previous = traces.current.get(s.source_id);
      const fresh = previous?.session === s.live.session ? previous : undefined;
      if (fresh?.at === s.live.at) continue;
      traces.current.set(s.source_id, {
        session: s.live.session || "",
        at: s.live.at,
        values: [
          ...(fresh?.values || []),
          Math.max(0, ...Object.values(s.live.scores)),
        ].slice(-30),
      });
    }
    if (!selected && data.sources.length)
      setSelected(data.sources[0].source_id);
  }, [data, selected]);
  useEffect(() => {
    if (!me || page !== "events") return;
    const query = new URLSearchParams({
      ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)),
      offset: String(offset),
    });
    let active = true;
    void api<{ events: Acoustic[] }>("/events?" + query)
      .then((r) => {
        if (active) setHistory(r.events);
      })
      .catch(notify);
    return () => {
      active = false;
    };
  }, [me?.user.user_id, page, filters, offset, data?.events[0]?.event_id]);
  const loadSettings = async () => {
    try {
      setPushInfo(await api("/push"));
      if (me?.user.role === "admin")
        setUsers((await api("/admin/users")).users);
    } catch (err) {
      notify(err);
    }
  };
  useEffect(() => {
    if (me && page === "settings") void loadSettings();
  }, [page, me?.user.user_id]);
  const changePage = (p: string) => {
    setPage(p);
    setDetail(null);
    window.history.pushState({}, "", "/");
  };
  const act = async (
    fn: () => Promise<unknown>,
    success: string,
    refresh = true,
  ) => {
    setBusy(true);
    setMessage("");
    try {
      await fn();
      setMessage(success);
      if (me && refresh) setData(await api<Snapshot>("/snapshot"));
    } catch (err) {
      notify(err);
    } finally {
      setBusy(false);
    }
  };
  const cameraControl = (command: object) => {
    if (!selected) return;
    void act(
      () => api(`/sources/${selected}/control`, "POST", command),
      "Orden recibida por el broker. Confirma el cambio en la telemetría de cámara.",
    );
  };
  const enablePush = async () => {
    if (
      !("Notification" in window) ||
      !("PushManager" in window) ||
      !("serviceWorker" in navigator)
    )
      throw new Error(
        "Este navegador no admite Web Push. En iOS, prueba desde la app instalada.",
      );
    if ((await Notification.requestPermission()) !== "granted")
      throw new Error(
        "Permiso de notificaciones no concedido. Revísalo en ajustes del navegador.",
      );
    const registration = await navigator.serviceWorker.ready;
    const raw = atob(
      me!.vapid_public_key.replace(/-/g, "+").replace(/_/g, "/"),
    );
    const key = Uint8Array.from(raw, (c) => c.charCodeAt(0));
    const sub =
      (await registration.pushManager.getSubscription()) ||
      (await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: key,
      }));
    await api("/push/subscriptions", "POST", sub.toJSON());
    await loadSettings();
  };
  const disablePush = async () => {
    if (!("serviceWorker" in navigator)) return;
    const reg = await navigator.serviceWorker.getRegistration();
    if (!reg) return;
    const sub = await reg.pushManager.getSubscription();
    if (sub) {
      await api("/push/subscriptions", "DELETE", { endpoint: sub.endpoint });
      await sub.unsubscribe();
    }
    await loadSettings();
  };
  if (checking) return <div className="loading">Conectando con ECHO…</div>;
  if (!me) return <Login onLogin={() => void refreshMe()} />;
  const source = data?.sources.find((s) => s.source_id === selected);
  const sources = (data?.sources || [])
    .filter(
      (s) =>
        (s.name + " " + s.source_id)
          .toLowerCase()
          .includes(search.toLowerCase()) &&
        (!activity ||
          (!isStale(s) &&
            Math.max(0, ...Object.values(s.live?.scores || {})) >= 0.15)),
    )
    .sort((a, b) =>
      order === "activity"
        ? (isStale(b)
            ? -1
            : Math.max(0, ...Object.values(b.live?.scores || {}))) -
          (isStale(a)
            ? -1
            : Math.max(0, ...Object.values(a.live?.scores || {})))
        : a.source_id.localeCompare(b.source_id),
    );
  const online =
    data?.sources.filter((s) => s.camera_state === "ONLINE").length || 0;
  const fresh =
    data?.sources.filter((s) => s.live?.state === "ONLINE" && !isStale(s))
      .length || 0;
  const newAlerts = data?.alert_totals.NEW || 0;
  const currentDataAge = data
    ? Math.max(0, (now - Date.parse(data.at)) / 1000)
    : Infinity;
  const connected = connection === "LIVE" && currentDataAge < 6;
  const nav = [
    ["operations", "grid", "Operaciones"],
    ["sources", "camera", "Fuentes"],
    ["events", "pulse", "Eventos"],
    ["alerts", "bell", "Alertas"],
    ["settings", "settings", "Ajustes"],
  ];
  const eventList = (events: Acoustic[]) =>
    events.length ? (
      <div className="event-list">
        {events.map((e) => (
          <button
            className="event-row"
            key={e.event_id}
            onClick={() => void openEvent(e.event_id)}
          >
            <span
              className={
                "event-icon " +
                (e.origin === "ACCEPTED_OPERATIONAL" ? "accepted" : "")
              }
            >
              <Icon name="wave" />
            </span>
            <span className="event-copy">
              <b>{names[e.event_type] || e.event_type}</b>
              <small>
                {short(e.source_id)} · {origins[e.origin]}
              </small>
            </span>
            <span className="event-meta">
              <Badge tone={e.lifecycle === "CLOSED" ? "muted" : "blue"}>
                {e.lifecycle}
              </Badge>
              <time>{when(e.onset_utc)}</time>
            </span>
            <Icon name="arrow" />
          </button>
        ))}
      </div>
    ) : (
      <Empty title="Aún no hay eventos">
        Los eventos aparecerán al recibir evidencia del motor acústico.
      </Empty>
    );
  return (
    <div className="shell">
      <a href="#main" className="skip">
        Ir al contenido
      </a>
      <aside className="rail">
        <a
          href="/"
          className="brand"
          onClick={(e) => {
            e.preventDefault();
            changePage("operations");
          }}
        >
          <Icon name="wave" size={30} />
          <b>
            ECHO<span>OPERATOR</span>
          </b>
        </a>
        <span className="rail-label">WORKSPACE / MK1</span>
        <nav aria-label="Navegación principal">
          {nav.map(([p, i, label]) => (
            <button
              key={p}
              className={page === p ? "active" : ""}
              onClick={() => changePage(p)}
              aria-current={page === p ? "page" : undefined}
            >
              <Icon name={i} />
              <span>{label}</span>
              {p === "alerts" && newAlerts > 0 && <i>{newAlerts}</i>}
            </button>
          ))}
        </nav>
        <div className="rail-footer">
          <Badge tone="blue">LABORATORIO</Badge>
          <p>
            Inteligencia acústica
            <br />
            con evidencia.
          </p>
          <span className="version">ECHO Operator 0.1</span>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> {nav.find((n) => n[0] === page)?.[2]}
          </div>
          <div className="header-right">
            <Badge tone={connected ? "green" : "amber"}>
              <span className={connected ? "live-dot" : "dot"} />
              {connected ? "CONECTADO" : "RECONECTANDO"}
            </Badge>
            <span className="clock">
              {new Date(now).toLocaleTimeString("es-PE")}
            </span>
            <button
              className="account"
              onClick={() =>
                void act(
                  async () => {
                    await disablePush().catch(() => {});
                    await api("/logout", "POST");
                    setMe(null);
                    setData(null);
                    setDetail(null);
                    traces.current.clear();
                  },
                  "",
                  false,
                )
              }
              title="Cerrar sesión"
            >
              <span className="avatar">
                {me.user.username.slice(0, 1).toUpperCase()}
              </span>
              <span>
                {me.user.username}
                <small>{me.user.role}</small>
              </span>
            </button>
          </div>
        </header>
        <main id="main">
          <div className="page-heading">
            <div>
              <span className="eyebrow">ACOUSTIC INTELLIGENCE PLATFORM</span>
              <h1>
                {page === "operations"
                  ? "Centro de operaciones"
                  : nav.find((n) => n[0] === page)?.[2]}
              </h1>
              <p>
                {page === "operations"
                  ? "Cada fuente tiene una señal. Encuentra la que necesita tu atención."
                  : "Evidencia acústica, contexto y trazabilidad por fuente."}
              </p>
            </div>
            <Badge tone="blue">
              {me.user.sites.join(" / ") || "Sin sitio asignado"}
            </Badge>
          </div>
          <div className="evidence-banner">
            <Icon name="pulse" />
            <div>
              <b>Entorno experimental · fuentes emuladas</b>
              <span>
                Inferencia real de tres clases. Los candidatos RTSP son
                diagnósticos; la aceptación de campo continúa pendiente.
              </span>
            </div>
            <Badge tone="amber">GATE ABIERTO</Badge>
          </div>
          {message && (
            <div className="notice" role="status">
              {message}
              <button
                aria-label="Cerrar mensaje"
                onClick={() => setMessage("")}
              >
                ×
              </button>
            </div>
          )}
          {!connected && (
            <p className="connection-warning" role="status">
              {data
                ? `Sin actualizaciones recientes (${Math.floor(currentDataAge)} s). Los valores mostrados pueden estar desactualizados.`
                : "Esperando datos del servidor…"}
            </p>
          )}
          {(page === "operations" || page === "sources") && (
            <>
              <section className="kpis" aria-label="Resumen de monitoreo">
                <article>
                  <span>
                    Fuentes registradas
                    <Icon name="camera" />
                  </span>
                  <b>
                    {data?.sources.length ?? "—"}
                    <small>fuentes</small>
                  </b>
                  <footer>
                    {online} online · {(data?.sources.length || 0) - online}{" "}
                    otros estados
                  </footer>
                </article>
                <article>
                  <span>
                    Inferencia reciente
                    <Icon name="wave" />
                  </span>
                  <b>
                    {fresh}
                    <small>fuentes</small>
                  </b>
                  <footer>Ventana completa · 6 s / hop 1 s</footer>
                </article>
                <article>
                  <span>
                    Alertas pendientes
                    <Icon name="bell" />
                  </span>
                  <b className={newAlerts ? "amber-text" : ""}>
                    {newAlerts.toString().padStart(2, "0")}
                  </b>
                  <footer>Solo aceptación operativa autorizada</footer>
                </article>
                <article>
                  <span>
                    Transporte MQTT
                    <Icon name="pulse" />
                  </span>
                  <b className="status-kpi">
                    {data?.mqtt.connected ? "Conectado" : "Sin conexión"}
                  </b>
                  <footer>
                    Último mensaje {when(data?.mqtt.last_message_at)}
                  </footer>
                </article>
              </section>
              <div className="operations-layout">
                <section className="panel cameras">
                  <div className="section-heading">
                    <div>
                      <h2>
                        Fuentes acústicas{" "}
                        <span>{data?.sources.length || 0}</span>
                      </h2>
                      <p>Identidad y actividad por cámara</p>
                    </div>
                    <Badge tone="muted">EMULADOR VMT</Badge>
                  </div>
                  <div className="toolbar">
                    <label className="search">
                      <span className="sr-only">Buscar fuente</span>
                      <input
                        placeholder="Buscar cámara…"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                      />
                    </label>
                    <label>
                      <span className="sr-only">Orden</span>
                      <select
                        value={order}
                        onChange={(e) => setOrder(e.target.value)}
                      >
                        <option value="source">Por cámara</option>
                        <option value="activity">Por score reciente</option>
                      </select>
                    </label>
                    <button
                      aria-pressed={layout === "list"}
                      onClick={() =>
                        setLayout(layout === "grid" ? "list" : "grid")
                      }
                    >
                      {layout === "grid" ? "Lista" : "Grid"}
                    </button>
                  </div>
                  <div className="source-options">
                    <label>
                      <input
                        type="checkbox"
                        checked={activity}
                        onChange={(e) => setActivity(e.target.checked)}
                      />{" "}
                      Solo score ≥ 0.15 <small>(filtro visual)</small>
                    </label>
                    <label>
                      <input
                        type="checkbox"
                        checked={previews}
                        onChange={(e) => setPreviews(e.target.checked)}
                      />{" "}
                      Previews · máx. 4
                    </label>
                  </div>
                  <div className={"camera-grid " + layout}>
                    {sources.map((s, i) => {
                      const stale = isStale(s) || !connected;
                      const scores = Object.entries(s.live?.scores || {}).sort(
                        (a, b) => b[1] - a[1],
                      );
                      return (
                        <article
                          key={s.source_id}
                          className={
                            "camera-card " +
                            (selected === s.source_id ? "selected" : "") +
                            (stale ? " stale-card" : "")
                          }
                        >
                          <button
                            className="camera-select"
                            aria-pressed={selected === s.source_id}
                            onClick={() => {
                              setSelected(s.source_id);
                              setPlaying(false);
                            }}
                          >
                            <div className="camera-card-header">
                              <span>
                                <Icon name="camera" />
                                {short(s.source_id)}
                              </span>
                              <Badge
                                tone={
                                  s.camera_state === "ONLINE"
                                    ? "green"
                                    : "amber"
                                }
                              >
                                {s.camera_state || "UNKNOWN"}
                              </Badge>
                            </div>
                            {!(previews && i < 4 && s.enabled) && (
                              <div className="camera-placeholder">
                                <Icon name="wave" size={42} />
                                <span>
                                  {stale
                                    ? "Sin evidencia reciente"
                                    : "Audio en análisis"}
                                </span>
                                <small>
                                  VIDEO SINTÉTICO ·{" "}
                                  {s.emulated ? "LAB" : "FUENTE REGISTRADA"}
                                </small>
                              </div>
                            )}
                            <div className="camera-caption">
                              <strong>{s.name}</strong>
                              <span>{s.scenario || "Sin telemetría"}</span>
                            </div>
                            <Wave
                              values={s.live?.waveform_envelope || []}
                              stale={stale}
                            />
                            <div className="camera-card-bottom">
                              <span>
                                <i className={!stale ? "tiny-live" : ""} />
                                {stale
                                  ? "SIN DATOS RECIENTES"
                                  : names[scores[0]?.[0]] || "Analizando"}
                              </span>
                              <b>{stale ? "—" : percent(scores[0]?.[1])}</b>
                            </div>
                          </button>
                          {previews && i < 4 && s.enabled && (
                            <Player source={s} preview />
                          )}
                        </article>
                      );
                    })}
                  </div>
                  {!sources.length && (
                    <Empty title="Sin fuentes en esta vista">
                      Prueba otro filtro o registra una fuente autorizada.
                    </Empty>
                  )}
                </section>
                <section className="panel monitor">
                  <div className="section-heading">
                    <div>
                      <span className="eyebrow">MONITOR DE FUENTE</span>
                      <h2>
                        {source
                          ? short(source.source_id)
                          : "Selecciona una cámara"}
                      </h2>
                    </div>
                    <Badge
                      tone={
                        source && !isStale(source) && connected
                          ? "green"
                          : "muted"
                      }
                    >
                      {source && !isStale(source) && connected
                        ? "DATOS RECIENTES"
                        : "SIN DATOS RECIENTES"}
                    </Badge>
                  </div>
                  {source && (
                    <>
                      <div className="monitor-media">
                        {playing && source.media_path ? (
                          <Player source={source} />
                        ) : (
                          <div className="play-placeholder">
                            <Icon name="camera" size={46} />
                            <b>Vista audiovisual</b>
                            <p>Video sintético + audio del escenario</p>
                            <button
                              className="primary"
                              disabled={!source.enabled || !source.media_path}
                              onClick={() => setPlaying(true)}
                            >
                              Abrir reproductor
                              <Icon name="arrow" />
                            </button>
                          </div>
                        )}
                      </div>
                      {playing && (
                        <button
                          className="text-button"
                          onClick={() => setPlaying(false)}
                        >
                          Cerrar reproductor
                        </button>
                      )}
                      <p className="media-note">
                        Activa el audio desde el reproductor. HLS e inferencia
                        pueden tener distinto retraso.
                      </p>
                      <div className="monitor-subhead">
                        <h3>Inferencia acústica</h3>
                        <Badge tone="blue">PANNS / 3 CLASES</Badge>
                      </div>
                      <Wave
                        values={source.live?.waveform_envelope || []}
                        stale={isStale(source) || !connected}
                      />
                      <div className="score-list">
                        {Object.keys(names).map((label) => (
                          <div key={label}>
                            <span>
                              {names[label]}
                              <b>{percent(source.live?.scores[label])}</b>
                            </span>
                            <div className="score-track">
                              <i
                                style={{
                                  width: `${(source.live?.scores[label] || 0) * 100}%`,
                                }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                      <p className="microcopy">
                        Scores del modelo. No son probabilidades de un
                        incidente.
                      </p>
                      <div className="trace-label">
                        Pico de score por actualización <span>últimas 30</span>
                      </div>
                      <svg
                        className="trace"
                        viewBox="0 0 300 60"
                        role="img"
                        aria-label="Evolución de los scores máximos recientes"
                      >
                        <path className="baseline" d="M0 59H300M0 30H300" />
                        <polyline
                          points={(
                            traces.current.get(source.source_id)?.values || []
                          )
                            .map((v, i) => `${i * 10},${58 - v * 54}`)
                            .join(" ")}
                        />
                      </svg>
                      <dl className="telemetry">
                        <div>
                          <dt>Worker</dt>
                          <dd>{source.live?.state || "Sin datos"}</dd>
                        </div>
                        <div>
                          <dt>Edad de última inferencia</dt>
                          <dd>
                            {source.live?.at ? `${age(source.live.at)} s` : "—"}
                          </dd>
                        </div>
                        <div>
                          <dt>Desfase estimado</dt>
                          <dd>
                            {source.live?.estimated_lag_ms != null
                              ? `${(source.live.estimated_lag_ms / 1000).toFixed(1)} s`
                              : "—"}
                          </dd>
                        </div>
                        <div>
                          <dt>Ventanas completas</dt>
                          <dd>{source.live?.windows ?? "—"}</dd>
                        </div>
                        <div>
                          <dt>Gen. cámara / worker</dt>
                          <dd>
                            {source.emulator_generation ?? "—"} /{" "}
                            {source.live?.worker_generation ?? "—"}
                          </dd>
                        </div>
                        <div>
                          <dt>Último lifecycle</dt>
                          <dd>
                            {source.live?.events.at(-1)?.provenance
                              ?.lifecycle || "Sin transición registrada"}
                          </dd>
                        </div>
                        <div>
                          <dt>RMS / peak</dt>
                          <dd>
                            {source.live?.rms?.toFixed(4) ?? "—"} /{" "}
                            {source.live?.peak?.toFixed(4) ?? "—"}
                          </dd>
                        </div>
                      </dl>
                      <details className="session-detail rtsp-diagnostics">
                        <summary>Diagnóstico RTSP por fuente</summary>
                        <dl className="telemetry">
                          <div>
                            <dt>Heartbeat</dt>
                            <dd>
                              {source.live?.updated_at
                                ? `${age(source.live.updated_at)} s`
                                : "—"}
                            </dd>
                          </div>
                          <div>
                            <dt>Fase</dt>
                            <dd>
                              {source.live?.diagnostics?.phase || "—"} ·{" "}
                              {source.live?.diagnostics?.phase_seconds?.toFixed(
                                1,
                              ) ?? "—"}{" "}
                              s
                            </dd>
                          </div>
                          <div>
                            <dt>PID / ventanas de sesión</dt>
                            <dd>
                              {source.live?.diagnostics?.pid ?? "—"} /{" "}
                              {source.live?.diagnostics?.session_windows ?? "—"}
                            </dd>
                          </div>
                          <div>
                            <dt>Duración de sesión</dt>
                            <dd>
                              {source.live?.diagnostics?.session_duration_seconds?.toFixed(
                                1,
                              ) ?? "—"}{" "}
                              s
                            </dd>
                          </div>
                          <div>
                            <dt>Última salida FFmpeg</dt>
                            <dd>
                              {source.live?.diagnostics?.current_exit_code ??
                                source.live?.diagnostics?.last_exit_code ??
                                "—"}
                            </dd>
                          </div>
                          <div>
                            <dt>Última sesión: duración / ventanas</dt>
                            <dd>
                              {source.live?.diagnostics?.last_session_duration_seconds?.toFixed(
                                1,
                              ) ?? "—"}{" "}
                              s /{" "}
                              {source.live?.diagnostics?.last_session_windows ??
                                "—"}
                            </dd>
                          </div>
                          <div>
                            <dt>Parada de transporte actual</dt>
                            <dd>
                              {source.live?.diagnostics
                                ?.transport_stop_reason || "—"}
                            </dd>
                          </div>
                          <div>
                            <dt>Último motivo de reconexión</dt>
                            <dd>
                              {source.live?.diagnostics?.reconnect_reason ||
                                "—"}
                            </dd>
                          </div>
                          <div>
                            <dt>Fallos seguidos / backoff</dt>
                            <dd>
                              {source.live?.diagnostics?.consecutive_failures ??
                                0}{" "}
                              / {source.live?.diagnostics?.backoff_seconds ?? 0}{" "}
                              s
                            </dd>
                          </div>
                          <div>
                            <dt>Próximo intento</dt>
                            <dd>
                              {when(source.live?.diagnostics?.next_retry_utc)}
                            </dd>
                          </div>
                          <div>
                            <dt>Cola PCM</dt>
                            <dd>
                              {source.live?.diagnostics?.pcm_queue_depth ?? "—"}{" "}
                              /{" "}
                              {source.live?.diagnostics?.pcm_queue_capacity ??
                                "—"}
                            </dd>
                          </div>
                          <div>
                            <dt>Edad PCM / bytes recibidos</dt>
                            <dd>
                              {source.live?.diagnostics?.last_pcm_age_seconds?.toFixed(
                                1,
                              ) ?? "—"}{" "}
                              s /{" "}
                              {source.live?.diagnostics?.transport_bytes ?? "—"}
                            </dd>
                          </div>
                          <div>
                            <dt>Última espera / inferencia</dt>
                            <dd>
                              {source.live?.diagnostics?.model_wait_seconds?.toFixed(
                                2,
                              ) ?? "—"}{" "}
                              /{" "}
                              {source.live?.diagnostics?.inference_seconds?.toFixed(
                                2,
                              ) ?? "—"}{" "}
                              s
                            </dd>
                          </div>
                          <div>
                            <dt>Limpieza / kill forzado</dt>
                            <dd>
                              {source.live?.diagnostics?.cleanup_complete ==
                              null
                                ? "—"
                                : source.live.diagnostics.cleanup_complete
                                  ? "Completa"
                                  : "Pendiente"}{" "}
                              /{" "}
                              {source.live?.diagnostics?.forced_kill
                                ? "Sí"
                                : "No"}
                            </dd>
                          </div>
                        </dl>
                        <p>
                          Instancia del worker:{" "}
                          {source.live?.diagnostics?.worker_instance_id || "—"}
                        </p>
                        <p>
                          stderr de FFmpeg · cola acotada y redactada
                          {source.live?.diagnostics?.stderr_truncated
                            ? " · truncada"
                            : ""}
                        </p>
                        <pre className="rtsp-stderr">
                          {source.live?.diagnostics?.stderr_tail.length
                            ? source.live.diagnostics.stderr_tail.join("\n")
                            : "Sin mensajes capturados."}
                        </pre>
                        <p>
                          Un heartbeat reciente no implica inferencia reciente.
                          La causa del fallo requiere revisar estos datos; no se
                          atribuye automáticamente al modelo.
                        </p>
                      </details>
                      <details className="session-detail">
                        <summary>Procedencia y tiempos</summary>
                        <p>Sesión: {source.live?.session || "—"}</p>
                        <p>
                          Ventana UTC: {source.live?.window_start_utc || "—"} →{" "}
                          {source.live?.window_end_utc || "—"}
                        </p>
                        <p>
                          La generación de cámara no equivale a la sesión del
                          worker. El desfase estima fin de ventana a snapshot;
                          incluye buffering y procesamiento, y no es una
                          latencia certificada.
                        </p>
                      </details>
                      {source.emulated && canOperate(me) && (
                        <div className="controls">
                          <h3>Controles de laboratorio</h3>
                          <label>
                            Escenario
                            <select
                              disabled={busy || !connected}
                              value={source.scenario || "negative"}
                              onChange={(e) =>
                                cameraControl({
                                  command: "set_scenario",
                                  scenario: e.target.value,
                                })
                              }
                            >
                              {[
                                "negative",
                                "glass_shatter",
                                "siren",
                                "vehicle_horn",
                                "silence",
                              ].map((s) => (
                                <option key={s} value={s}>
                                  {s}
                                </option>
                              ))}
                            </select>
                          </label>
                          <div>
                            <button
                              disabled={busy || !connected}
                              onClick={() =>
                                cameraControl({
                                  command: "set_online",
                                  online: source.camera_state !== "ONLINE",
                                })
                              }
                            >
                              {source.camera_state === "ONLINE"
                                ? "Poner offline"
                                : "Poner online"}
                            </button>
                            <button
                              disabled={busy || !connected}
                              onClick={() =>
                                cameraControl({ command: "restart" })
                              }
                            >
                              Reiniciar
                            </button>
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </section>
              </div>
              {page === "operations" && (
                <section className="panel timeline">
                  <div className="section-heading">
                    <div>
                      <h2>Actividad reciente</h2>
                      <p>Eventos temporales con procedencia explícita</p>
                    </div>
                    <button
                      className="text-button"
                      onClick={() => changePage("events")}
                    >
                      Ver historial <Icon name="arrow" />
                    </button>
                  </div>
                  {eventList(data?.events || [])}
                </section>
              )}
            </>
          )}
          {page === "events" && (
            <section className="panel">
              <div className="section-heading">
                <div>
                  <h2>Historial acústico</h2>
                  <p>CONFIRMED / CLOSED describen el ciclo acústico.</p>
                </div>
              </div>
              <div className="filters">
                {[
                  [
                    "source",
                    "Cámara",
                    data?.sources.map((s) => s.source_id) || [],
                  ],
                  ["type", "Categoría", Object.keys(names)],
                  ["lifecycle", "Lifecycle", ["CONFIRMED", "CLOSED"]],
                  ["origin", "Evidencia", Object.keys(origins)],
                ].map(([key, label, options]) => (
                  <label key={key as string}>
                    {label as string}
                    <select
                      value={filters[key as string] || ""}
                      onChange={(e) => {
                        setOffset(0);
                        setFilters({
                          ...filters,
                          [key as string]: e.target.value,
                        });
                      }}
                    >
                      <option value="">Todas</option>
                      {(options as string[]).map((o) => (
                        <option key={o} value={o}>
                          {names[o] || origins[o] || o}
                        </option>
                      ))}
                    </select>
                  </label>
                ))}
                {["from", "to"].map((key, i) => (
                  <label key={key}>
                    {i ? "Hasta (hora local)" : "Desde (hora local)"}
                    <input
                      type="datetime-local"
                      onChange={(e) => {
                        setOffset(0);
                        setFilters({
                          ...filters,
                          [key]: e.target.value
                            ? new Date(e.target.value).toISOString()
                            : "",
                        });
                      }}
                    />
                  </label>
                ))}
              </div>
              {eventList(history)}
              <div className="pagination">
                <button
                  disabled={!offset}
                  onClick={() => setOffset(Math.max(0, offset - 50))}
                >
                  Anterior
                </button>
                <span>
                  {offset + 1}–{offset + history.length}
                </span>
                <button
                  disabled={history.length < 50}
                  onClick={() => setOffset(offset + 50)}
                >
                  Siguiente
                </button>
              </div>
            </section>
          )}
          {detail && page === "events" && (
            <section className="panel event-detail">
              <div className="section-heading">
                <h2>
                  {names[detail.event.event_type]} ·{" "}
                  {short(detail.event.source_id)}
                </h2>
                <button
                  onClick={() => {
                    setDetail(null);
                    window.history.pushState({}, "", "/");
                  }}
                >
                  Cerrar detalle
                </button>
              </div>
              <Badge tone="blue">{origins[detail.event.origin]}</Badge>
              <dl className="telemetry">
                {Object.entries({
                  Evento: detail.event.event_id,
                  Lifecycle: detail.event.lifecycle,
                  Inicio: detail.event.onset_utc,
                  Fin: detail.event.end_utc || "—",
                  Modelo: detail.event.model_version,
                  Umbrales: detail.event.threshold_version,
                  Sesión: detail.event.stream_session_id,
                  "Score peak": percent(detail.event.confidence.peak),
                }).map(([k, v]) => (
                  <div key={k}>
                    <dt>{k}</dt>
                    <dd>{v}</dd>
                  </div>
                ))}
              </dl>
              <h3>Transiciones recibidas</h3>
              {detail.receipts.map((r) => (
                <details key={r.lifecycle}>
                  <summary>
                    {r.lifecycle} · {when(r.received_at)}
                  </summary>
                  <pre>{JSON.stringify(r.payload, null, 2)}</pre>
                </details>
              ))}
              <h3>Atención del operador</h3>
              <p>
                {detail.alert?.state ||
                  "Este evento no tiene una alerta operativa."}
              </p>
              {detail.history.map((h, i) => (
                <p key={i}>
                  {when(h.created_at)} · {h.action}
                </p>
              ))}
            </section>
          )}
          {page === "alerts" && (
            <section className="panel">
              <div className="section-heading">
                <div>
                  <h2>Centro de alertas</h2>
                  <p>
                    La atención humana se gestiona por separado del lifecycle
                    acústico.
                  </p>
                </div>
                <Badge tone="amber">{newAlerts} NUEVAS</Badge>
              </div>
              <div className="toolbar">
                <label>
                  Estado
                  <select
                    value={filters.alertState || ""}
                    onChange={(e) =>
                      setFilters({ ...filters, alertState: e.target.value })
                    }
                  >
                    <option value="">Todos</option>
                    {["NEW", "ACKNOWLEDGED", "RESOLVED"].map((x) => (
                      <option key={x}>{x}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Cámara
                  <select
                    value={filters.alertSource || ""}
                    onChange={(e) =>
                      setFilters({ ...filters, alertSource: e.target.value })
                    }
                  >
                    <option value="">Todas</option>
                    {data?.sources.map((s) => (
                      <option key={s.source_id}>{s.source_id}</option>
                    ))}
                  </select>
                </label>
              </div>
              {data?.alerts.length ? (
                data.alerts
                  .filter(
                    (a) =>
                      (!filters.alertState || filters.alertState === a.state) &&
                      (!filters.alertSource ||
                        filters.alertSource === a.source_id),
                  )
                  .map((a) => (
                    <article key={a.alert_id} className="alert-card">
                      <div>
                        <Badge tone={a.state === "NEW" ? "amber" : "green"}>
                          {a.state}
                        </Badge>
                        <h3>{names[a.event_type]}</h3>
                        <small>Severidad: {a.severity || "UNASSESSED"}</small>
                        <p>
                          {short(a.source_id)} · {when(a.onset_utc)} · revisión
                          de fuente recomendada
                        </p>
                      </div>
                      <div>
                        <button onClick={() => void openEvent(a.event_id)}>
                          Ver evidencia
                        </button>
                        {canOperate(me) && a.state !== "RESOLVED" && (
                          <button
                            disabled={busy}
                            className="primary"
                            onClick={() =>
                              void act(
                                () =>
                                  api(
                                    `/alerts/${a.alert_id}/${a.state === "NEW" ? "acknowledge" : "resolve"}`,
                                    "POST",
                                  ),
                                a.state === "NEW"
                                  ? "Alerta reconocida."
                                  : "Alerta resuelta.",
                              )
                            }
                          >
                            {a.state === "NEW" ? "Reconocer" : "Resolver"}
                          </button>
                        )}
                      </div>
                    </article>
                  ))
              ) : (
                <Empty title="Sin alertas operativas">
                  Los candidatos de laboratorio no se convierten en alertas. El
                  perfil de aceptación operativa está vacío hasta cerrar los
                  gates correspondientes.
                </Empty>
              )}
            </section>
          )}
          {page === "settings" && (
            <div className="settings-grid">
              <section className="panel">
                <div className="section-heading">
                  <div>
                    <h2>Notificaciones móviles</h2>
                    <p>Permisos y entregas de esta cuenta</p>
                  </div>
                  <Icon name="bell" />
                </div>
                <p>
                  {me.push_ready
                    ? "Web Push configurado. Actívalo en este dispositivo."
                    : "Web Push pendiente de configurar claves VAPID en el despliegue."}
                </p>
                <div className="button-row">
                  <button
                    className="primary"
                    disabled={busy || !me.push_ready}
                    onClick={() =>
                      void act(
                        enablePush,
                        "Suscripción registrada en este dispositivo.",
                      )
                    }
                  >
                    Activar notificaciones
                  </button>
                  <button
                    disabled={busy}
                    onClick={() =>
                      void act(
                        disablePush,
                        "Suscripción cancelada en este dispositivo.",
                      )
                    }
                  >
                    Desactivar
                  </button>
                  {me.lab_push_enabled && canOperate(me) && (
                    <button
                      disabled={busy || !me.push_ready}
                      onClick={() =>
                        void act(
                          () => api("/push/lab", "POST"),
                          "Prueba de laboratorio en cola. La aceptación del proveedor no confirma recepción en el móvil.",
                        )
                      }
                    >
                      Enviar prueba LAB
                    </button>
                  )}
                </div>
                <h3>Entregas recientes</h3>
                <button
                  className="text-button"
                  onClick={() => void loadSettings()}
                >
                  Actualizar entregas
                </button>
                {pushInfo?.deliveries?.length ? (
                  pushInfo.deliveries.map((d: any) => (
                    <div className="delivery" key={d.delivery_id}>
                      <span>{when(d.created_at)}</span>
                      <Badge>{d.status}</Badge>
                      <small>{d.attempts} intentos</small>
                    </div>
                  ))
                ) : (
                  <p className="muted">No hay intentos registrados.</p>
                )}
                <p className="microcopy">
                  PROVIDER_ACCEPTED confirma aceptación por el servicio push. La
                  recepción o lectura del dispositivo no se puede inferir.
                </p>
              </section>
              <section className="panel">
                <div className="section-heading">
                  <h2>Instalar ECHO</h2>
                  <Icon name="grid" />
                </div>
                <p>
                  Instala la PWA desde el menú de Chrome o utiliza el botón
                  cuando esté disponible. En iOS: Compartir → Agregar a inicio.
                </p>
                {deferredInstall && (
                  <button
                    className="primary"
                    onClick={async () => {
                      await deferredInstall.prompt();
                      setDeferredInstall(null);
                    }}
                  >
                    Instalar aplicación
                  </button>
                )}
                <h3>Conexión y privacidad</h3>
                <p>
                  La aplicación conserva solo sus archivos estáticos para abrir
                  una pantalla sin conexión. No guarda sesiones, eventos, audio
                  ni credenciales en caché.
                </p>
                <p>
                  Capacidad de cámaras: <b>sin medición certificada</b>.
                </p>
                <p className="microcopy">
                  La operación en tiempo real requiere conexión con el servidor.
                </p>
              </section>
              {me.user.role === "admin" && (
                <>
                  <section className="panel">
                    <div className="section-heading">
                      <h2>Usuarios y roles</h2>
                    </div>
                    <form
                      className="admin-form"
                      onSubmit={(e) => {
                        e.preventDefault();
                        const form = e.currentTarget;
                        const f = new FormData(form);
                        void act(async () => {
                          await api("/admin/users", "POST", {
                            username: f.get("username"),
                            password: f.get("password"),
                            role: f.get("role"),
                            sites: me.user.sites,
                          });
                          form.reset();
                          await loadSettings();
                        }, "Usuario creado.");
                      }}
                    >
                      <label>
                        Usuario
                        <input
                          name="username"
                          required
                          pattern="[A-Za-z0-9_-]{1,80}"
                          autoComplete="off"
                        />
                      </label>
                      <label>
                        Contraseña inicial
                        <input
                          name="password"
                          type="password"
                          required
                          minLength={16}
                          maxLength={256}
                          autoComplete="new-password"
                        />
                      </label>
                      <label>
                        Rol
                        <select name="role">
                          <option value="viewer">Viewer · lectura</option>
                          <option value="operator">
                            Operator · atención y control
                          </option>
                          <option value="admin">Admin · administración</option>
                        </select>
                      </label>
                      <small>Acceso a los sitios asignados a tu cuenta.</small>
                      <button disabled={busy} className="primary">
                        Crear usuario
                      </button>
                    </form>
                    <div className="user-list">
                      {users.map((u) => (
                        <div key={u.user_id}>
                          <span>
                            <b>{u.username}</b>
                            <small>
                              {u.role} ·{" "}
                              {u.enabled ? "Activo" : "Deshabilitado"}
                            </small>
                          </span>
                          {u.user_id !== me.user.user_id && (
                            <button
                              disabled={busy}
                              onClick={() =>
                                void act(async () => {
                                  await api(
                                    `/admin/users/${u.user_id}`,
                                    "PATCH",
                                    {
                                      enabled: !u.enabled,
                                      role: u.role,
                                      sites: u.sites,
                                    },
                                  );
                                  await loadSettings();
                                }, "Permisos actualizados; sesiones revocadas.")
                              }
                            >
                              {u.enabled ? "Deshabilitar" : "Habilitar"}
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                  </section>
                  <section className="panel">
                    <div className="section-heading">
                      <h2>Registro de fuentes</h2>
                    </div>
                    <form
                      className="admin-form"
                      onSubmit={(e) => {
                        e.preventDefault();
                        const form = e.currentTarget;
                        const f = new FormData(form);
                        void act(async () => {
                          await api("/admin/sources", "POST", {
                            source_id: f.get("source_id"),
                            site_id: f.get("site_id"),
                            name: f.get("name"),
                            kind: f.get("kind"),
                            enabled: true,
                            emulated: false,
                            media_path: null,
                          });
                          form.reset();
                        }, "Fuente registrada. Su ingesta requiere configuración explícita del Acoustic Plane.");
                      }}
                    >
                      <label>
                        ID de fuente
                        <input
                          name="source_id"
                          required
                          pattern="[A-Za-z0-9_-]{1,80}"
                        />
                      </label>
                      <label>
                        Nombre
                        <input name="name" required maxLength={100} />
                      </label>
                      <label>
                        Sitio
                        <select name="site_id">
                          {me.user.sites.map((s) => (
                            <option key={s}>{s}</option>
                          ))}
                        </select>
                      </label>
                      <label>
                        Tipo
                        <select name="kind">
                          <option value="ip_camera">Cámara IP</option>
                          <option value="microphone">Micrófono</option>
                          <option value="replay">Replay</option>
                        </select>
                      </label>
                      <button className="primary" disabled={busy}>
                        Registrar fuente
                      </button>
                      <p className="microcopy">
                        Registrar una fuente no configura credenciales RTSP ni
                        inicia inferencia automáticamente.
                      </p>
                    </form>
                  </section>
                </>
              )}
            </div>
          )}
          <footer className="page-footer">
            <span>
              <Icon name="wave" size={16} /> ECHO · Detección y clasificación de
              eventos acústicos mediante IA
            </span>
            <span>MK1 experimental · Sin certificación operativa nueva</span>
          </footer>
        </main>
      </div>
    </div>
  );
}
if ("serviceWorker" in navigator)
  window.addEventListener("load", () => {
    void navigator.serviceWorker.register("/sw.js").catch(() => {});
  });
createRoot(document.getElementById("root")!).render(<App />);
