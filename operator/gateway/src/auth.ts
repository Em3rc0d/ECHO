import {
  randomBytes,
  scryptSync,
  timingSafeEqual,
  createHash,
} from "node:crypto";
import type { FastifyRequest } from "fastify";
import { db } from "./db.js";
export const digest = (s: string) =>
  createHash("sha256").update(s).digest("hex");
export function hashPassword(password: string) {
  const salt = randomBytes(16).toString("hex");
  return salt + ":" + scryptSync(password, salt, 64).toString("hex");
}
export function verifyPassword(password: string, stored: string) {
  const [salt, hash] = stored.split(":");
  if (!salt || !hash) return false;
  const value = scryptSync(password, salt, 64);
  const expected = Buffer.from(hash, "hex");
  return value.length === expected.length && timingSafeEqual(value, expected);
}
export type User = {
  user_id: string;
  username: string;
  role: "viewer" | "operator" | "admin";
  sites: string[];
  expires_at: string;
};
declare module "fastify" {
  interface FastifyRequest {
    user: User;
  }
}
export async function authenticate(req: FastifyRequest): Promise<User | null> {
  const token = req.cookies.echo_session;
  if (!token || token.length !== 64) return null;
  const r = await db.query(
    `SELECT u.user_id,u.username,u.role,s.expires_at,
 ARRAY(SELECT site_id FROM user_sites WHERE user_id=u.user_id) AS sites
 FROM sessions s JOIN users u USING(user_id) WHERE s.token_hash=$1 AND s.expires_at>now() AND u.enabled`,
    [digest(token)],
  );
  return r.rows[0] || null;
}
export function operator(user: User) {
  return user.role === "admin" || user.role === "operator";
}
