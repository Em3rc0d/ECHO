/** MediaMTX v1.21.3 HLS transport. No shared cookie jar or browser cookies.
 * Not forwarding cookieCheck makes MediaMTX emit its supported session query
 * fallback, so child playlists/segments can stay on the authenticated proxy.
 */
export class HlsProxyError extends Error {
  readonly statusCode = 502;
}

const filenamePattern = /^[A-Za-z0-9_-]+\.(?:m3u8|mp4|m4s|mp|ts)$/;
const mediaPathPattern = /^[A-Za-z0-9_-]+(?:\/[A-Za-z0-9_-]+)*$/;
const sessionPattern =
  /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i;

export function mediaTarget(
  origin: string,
  mediaPath: string,
  filename: string,
  query: URLSearchParams,
): URL {
  if (!filenamePattern.test(filename) || !mediaPathPattern.test(mediaPath))
    throw Object.assign(new Error("MEDIA_PATH_INVALID"), { statusCode: 400 });
  const base = new URL(origin);
  if (
    !["http:", "https:"].includes(base.protocol) ||
    base.username ||
    base.password ||
    base.pathname !== "/" ||
    base.search ||
    base.hash
  )
    throw new HlsProxyError("MEDIA_ORIGIN_INVALID");
  const target = new URL(`/${mediaPath}/${filename}`, base);
  for (const [key, pattern] of [
    ["session", sessionPattern],
    ["_HLS_msn", /^\d{1,20}$/],
    ["_HLS_part", /^\d{1,20}$/],
    ["_HLS_skip", /^(?:YES|v2)$/],
  ] as const) {
    const values = query.getAll(key);
    if (values.length > 1 || (values.length && !pattern.test(values[0])))
      throw Object.assign(new Error("MEDIA_QUERY_INVALID"), {
        statusCode: 400,
      });
    if (values.length) target.searchParams.set(key, values[0]);
  }
  // Unknown parameters (including client cookieCheck/auth/target) never cross
  // the trust boundary. cookieCheck is generated only by the validated 302.
  return target;
}

function sortedQuery(url: URL): string {
  const params = new URLSearchParams(url.search);
  params.sort();
  return params.toString();
}

/** Fetch one resource; at most one narrowly constrained cookie-check redirect. */
export async function fetchHls(
  target: URL,
  signal: AbortSignal = AbortSignal.timeout(20000),
  request: typeof fetch = fetch,
): Promise<Response> {
  const options: RequestInit = {
    signal,
    redirect: "manual",
    credentials: "omit",
    headers: {
      Accept: "application/vnd.apple.mpegurl,video/mp4,video/mp2t,*/*",
    },
  };
  let response = await request(target, options);
  if (response.status < 300 || response.status >= 400) return response;
  const location = response.headers.get("location");
  await response.body?.cancel();
  if (
    response.status !== 302 ||
    !location ||
    location.length > 2048 ||
    /[\u0000-\u0020\u007f\\]/.test(location) ||
    !target.pathname.endsWith("/index.m3u8") ||
    target.searchParams.has("cookieCheck")
  )
    throw new HlsProxyError("MEDIA_REDIRECT_DENIED");
  let next: URL;
  try {
    next = new URL(location, target);
  } catch {
    throw new HlsProxyError("MEDIA_REDIRECT_DENIED");
  }
  const expected = new URL(target);
  expected.searchParams.set("cookieCheck", "1");
  if (
    next.origin !== target.origin ||
    next.username ||
    next.password ||
    next.hash ||
    next.pathname !== target.pathname ||
    sortedQuery(next) !== sortedQuery(expected)
  )
    throw new HlsProxyError("MEDIA_REDIRECT_DENIED");
  // Intentionally do not forward Set-Cookie, Cookie or the Operator session.
  // MediaMTX chooses query-mode session propagation for the returned playlists.
  response = await request(next, options);
  if (response.status >= 300 && response.status < 400) {
    await response.body?.cancel();
    throw new HlsProxyError("MEDIA_REDIRECT_LIMIT");
  }
  return response;
}
