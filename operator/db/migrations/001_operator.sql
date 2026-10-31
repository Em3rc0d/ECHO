CREATE TABLE sites (site_id text PRIMARY KEY, name text NOT NULL);
CREATE TABLE sources (
 source_id text PRIMARY KEY, site_id text NOT NULL REFERENCES sites,
 name text NOT NULL, kind text NOT NULL CHECK (kind IN ('ip_camera','microphone','replay')),
 enabled boolean NOT NULL DEFAULT true, emulated boolean NOT NULL DEFAULT false,
 media_path text, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE users (
 user_id uuid PRIMARY KEY, username text UNIQUE NOT NULL, password_hash text NOT NULL,
 role text NOT NULL CHECK (role IN ('viewer','operator','admin')), enabled boolean NOT NULL DEFAULT true
);
CREATE TABLE user_sites (user_id uuid REFERENCES users ON DELETE CASCADE, site_id text REFERENCES sites,
 PRIMARY KEY(user_id,site_id));
CREATE TABLE sessions (token_hash text PRIMARY KEY, user_id uuid REFERENCES users ON DELETE CASCADE,
 expires_at timestamptz NOT NULL);
CREATE INDEX sessions_expiry ON sessions(expires_at);
CREATE TABLE acoustic_events (
 event_id text PRIMARY KEY, source_id text NOT NULL REFERENCES sources, site_id text NOT NULL REFERENCES sites,
 event_type text NOT NULL, stream_session_id text NOT NULL, onset_utc timestamptz NOT NULL,
 end_utc timestamptz, lifecycle text NOT NULL CHECK(lifecycle IN ('CONFIRMED','CLOSED')),
 origin text NOT NULL CHECK(origin IN ('LAB_DIAGNOSTIC','CONTROLLED_OR_UNASSESSED','ACCEPTED_OPERATIONAL')),
 model_version text NOT NULL, threshold_version text NOT NULL, confidence jsonb NOT NULL,
 received_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX events_history ON acoustic_events(site_id,onset_utc DESC,event_id);
CREATE TABLE event_receipts (
 event_id text REFERENCES acoustic_events ON DELETE CASCADE, lifecycle text NOT NULL,
 payload jsonb NOT NULL, received_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(event_id,lifecycle)
);
CREATE TABLE operational_alerts (
 alert_id uuid PRIMARY KEY, event_id text UNIQUE NOT NULL REFERENCES acoustic_events,
 severity text NOT NULL DEFAULT 'UNASSESSED' CHECK(severity IN ('UNASSESSED','LOW','MEDIUM','HIGH','CRITICAL')),
 state text NOT NULL DEFAULT 'NEW' CHECK(state IN ('NEW','ACKNOWLEDGED','RESOLVED')),
 acknowledged_by uuid REFERENCES users, resolved_by uuid REFERENCES users,
 acknowledged_at timestamptz, resolved_at timestamptz, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE source_health (
 source_id text PRIMARY KEY REFERENCES sources ON DELETE CASCADE, state text NOT NULL,
 emulator_generation integer, scenario text, source_at timestamptz, received_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE push_subscriptions (
 subscription_id uuid PRIMARY KEY, user_id uuid NOT NULL REFERENCES users ON DELETE CASCADE,
 endpoint text UNIQUE NOT NULL, subscription jsonb NOT NULL, enabled boolean NOT NULL DEFAULT true,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE notification_deliveries (
 delivery_id uuid PRIMARY KEY, subscription_id uuid NOT NULL REFERENCES push_subscriptions ON DELETE CASCADE,
 dedup_key text NOT NULL, payload jsonb NOT NULL,
 status text NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING','SENDING','RETRY','PROVIDER_ACCEPTED','FAILED','EXPIRED','SUPPRESSED')),
 attempts integer NOT NULL DEFAULT 0, next_attempt timestamptz NOT NULL DEFAULT now(),
 expires_at timestamptz NOT NULL, provider_status integer, last_error text,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(subscription_id,dedup_key)
);
CREATE INDEX push_pending ON notification_deliveries(status,next_attempt);
CREATE TABLE audit_logs (
 audit_id bigserial PRIMARY KEY, user_id uuid REFERENCES users, action text NOT NULL,
 entity_id text, detail jsonb NOT NULL DEFAULT '{}', created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE rejected_messages (
 digest text PRIMARY KEY, topic text NOT NULL, reason text NOT NULL, count integer NOT NULL DEFAULT 1,
 last_at timestamptz NOT NULL DEFAULT now()
);
