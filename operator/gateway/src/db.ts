import pg from "pg";
import { secret } from "./config.js";
export const db = new pg.Pool({
  host: process.env.PGHOST || "db",
  port: Number(process.env.PGPORT || 5432),
  database: process.env.PGDATABASE || "echo_operator",
  user: process.env.PGUSER || "echo",
  password: secret("PGPASSWORD"),
  max: 10,
  connectionTimeoutMillis: 5000,
  statement_timeout: 10000,
});
export async function transaction<T>(
  fn: (client: pg.PoolClient) => Promise<T>,
): Promise<T> {
  const c = await db.connect();
  try {
    await c.query("BEGIN");
    const out = await fn(c);
    await c.query("COMMIT");
    return out;
  } catch (e) {
    await c.query("ROLLBACK");
    throw e;
  } finally {
    c.release();
  }
}
export async function audit(
  user: string | null,
  action: string,
  entity: string | null,
  detail: unknown = {},
) {
  await db.query(
    "INSERT INTO audit_logs(user_id,action,entity_id,detail) VALUES($1,$2,$3,$4)",
    [user, action, entity, detail],
  );
}
