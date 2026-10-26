import { readFile } from "node:fs/promises";
import { randomUUID } from "node:crypto";
import { db, transaction } from "./db.js";
import { hashPassword } from "./auth.js";
import { secret } from "./config.js";
const inventory = JSON.parse(
  await readFile(process.env.CAMERAS_FILE || "/app/vmt-cameras.json", "utf8"),
);
const password = secret("BOOTSTRAP_PASSWORD");
if (password.length < 16)
  throw new Error("Bootstrap password must have at least 16 characters");
try {
  await transaction(async (c) => {
    await c.query("SELECT pg_advisory_xact_lock(77210627)");
    await c.query("INSERT INTO sites VALUES($1,$2) ON CONFLICT DO NOTHING", [
      inventory.site_id,
      "Laboratorio VMT · fuentes emuladas",
    ]);
    for (const row of inventory.cameras)
      await c.query(
        `INSERT INTO sources(source_id,site_id,name,kind,emulated,media_path)
 VALUES($1,$2,$3,'ip_camera',true,$4) ON CONFLICT DO NOTHING`,
        [row.source_id, inventory.site_id, row.source_id, row.rtsp_path],
      );
    const id = randomUUID();
    const user = await c.query(
      `INSERT INTO users(user_id,username,password_hash,role) VALUES($1,$2,$3,'admin')
 ON CONFLICT(username) DO NOTHING RETURNING user_id`,
      [id, process.env.BOOTSTRAP_USER || "admin", hashPassword(password)],
    );
    if (user.rowCount)
      await c.query("INSERT INTO user_sites VALUES($1,$2)", [
        id,
        inventory.site_id,
      ]);
  });
} finally {
  await db.end();
}
