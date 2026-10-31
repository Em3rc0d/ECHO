// Run in the gateway image before startup. Never writes secrets to stdout.
import { mkdir, writeFile, access } from "node:fs/promises";
import { randomBytes } from "node:crypto";
import webpush from "web-push";
await mkdir("/out", { recursive: true });
const exists = async (name) =>
  access("/out/" + name).then(
    () => true,
    () => false,
  );
const pub = await exists("vapid_public_key"),
  priv = await exists("vapid_private_key");
if (pub !== priv)
  throw new Error(
    "Partial VAPID pair exists; restore both key files before continuing",
  );
const values = {
  postgres_password: randomBytes(32).toString("base64url"),
  bootstrap_password: randomBytes(24).toString("base64url"),
};
if (!pub) {
  const keys = webpush.generateVAPIDKeys();
  values.vapid_public_key = keys.publicKey;
  values.vapid_private_key = keys.privateKey;
}
for (const [name, value] of Object.entries(values)) {
  // Parent directory stays host-private (0700); read-only file mounts must be readable by non-root containers.
  try {
    await writeFile("/out/" + name, value + "\n", { mode: 0o444, flag: "wx" });
  } catch (err) {
    if (err.code !== "EEXIST") throw err;
  }
}
// Public/private key files are generated as a pair. A partial pre-existing key pair must be repaired manually.
