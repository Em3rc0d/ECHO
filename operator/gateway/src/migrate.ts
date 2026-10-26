import { readdir, readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { db, transaction } from "./db.js";
const dir = process.env.MIGRATIONS_DIR || "/app/migrations";
try {
  await transaction(async (c) => {
    await c.query("SELECT pg_advisory_xact_lock(77210626)");
    await c.query(
      "CREATE TABLE IF NOT EXISTS schema_migrations(name text PRIMARY KEY,sha256 text NOT NULL,applied_at timestamptz NOT NULL DEFAULT now())",
    );
    for (const name of (await readdir(dir))
      .filter((n) => n.endsWith(".sql"))
      .sort()) {
      const sql = await readFile(`${dir}/${name}`, "utf8");
      const hash = createHash("sha256").update(sql).digest("hex");
      const old = await c.query(
        "SELECT sha256 FROM schema_migrations WHERE name=$1",
        [name],
      );
      if (old.rowCount) {
        if (old.rows[0].sha256 !== hash)
          throw new Error(`Migration drift: ${name}`);
        continue;
      }
      await c.query(sql);
      await c.query(
        "INSERT INTO schema_migrations(name,sha256) VALUES($1,$2)",
        [name, hash],
      );
    }
  });
} finally {
  await db.end();
}
