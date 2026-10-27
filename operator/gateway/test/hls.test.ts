// Regression cases WRITTEN / NOT_EXECUTED for PR #57 HLS review.
import test from "node:test";
import assert from "node:assert/strict";
import { fetchHls, mediaTarget } from "../src/hls.js";

const origin = "http://rtsp-server:8888";
const path = "vmt/cam-002";
const session = "01234567-89ab-4cde-8fab-0123456789ab";
const target = (filename = "index.m3u8", query = "") =>
  mediaTarget(origin, path, filename, new URLSearchParams(query));
function scripted(responses: Response[]) {
  const calls: { url: URL; options: RequestInit }[] = [];
  const request: typeof fetch = async (input, options) => {
    calls.push({
      url: new URL(input instanceof Request ? input.url : String(input)),
      options: options || {},
    });
    const response = responses.shift();
    assert.ok(response, "Unexpected extra upstream request");
    return response;
  };
  return { calls, request };
}
const controller = () => new AbortController().signal;

test("302 cookieCheck handshake uses query sessions through audio/video playlists and fragments", async () => {
  const master = `#EXTM3U\n#EXT-X-MEDIA:TYPE=AUDIO,URI="audio2_stream.m3u8?session=${session}"\n#EXT-X-STREAM-INF:BANDWIDTH=100000\nvideo1_stream.m3u8?session=${session}\n`;
  const { calls, request } = scripted([
    new Response(null, {
      status: 302,
      headers: {
        Location: "/vmt/cam-002/index.m3u8?cookieCheck=1",
        "Set-Cookie":
          "cookieCheck=1; Secure; HttpOnly; SameSite=None; Partitioned",
      },
    }),
    new Response(master, {
      headers: { "Content-Type": "application/vnd.apple.mpegurl" },
    }),
    new Response(
      `#EXTM3U\n#EXT-X-MAP:URI="init.mp4?session=${session}"\nsegment0.mp4?session=${session}\n`,
    ),
    new Response(`#EXTM3U\nvideo0.mp4?session=${session}\n`),
    new Response(new Uint8Array([0, 0, 1])),
    new Response(new Uint8Array([1, 2, 3])),
  ]);
  const signal = controller();
  assert.equal(
    await (await fetchHls(target(), signal, request)).text(),
    master,
  );
  const child = target(
    "audio2_stream.m3u8",
    `session=${session}&_HLS_msn=1&_HLS_part=0&_HLS_skip=YES`,
  );
  assert.equal((await fetchHls(child, signal, request)).status, 200);
  assert.equal(
    (
      await fetchHls(
        target("video1_stream.m3u8", `session=${session}`),
        signal,
        request,
      )
    ).status,
    200,
  );
  assert.deepEqual(
    new Uint8Array(
      await (
        await fetchHls(
          target("init.mp4", `session=${session}`),
          signal,
          request,
        )
      ).arrayBuffer(),
    ),
    new Uint8Array([0, 0, 1]),
  );
  assert.deepEqual(
    new Uint8Array(
      await (
        await fetchHls(
          target("segment0.mp4", `session=${session}`),
          signal,
          request,
        )
      ).arrayBuffer(),
    ),
    new Uint8Array([1, 2, 3]),
  );
  assert.equal(calls.length, 6);
  assert.equal(
    calls[1].url.href,
    origin + "/vmt/cam-002/index.m3u8?cookieCheck=1",
  );
  assert.equal(calls[2].url.searchParams.get("session"), session);
  assert.equal(calls[2].url.searchParams.get("_HLS_part"), "0");
  assert.equal(calls[3].url.searchParams.get("session"), session);
  assert.equal(calls[4].url.searchParams.get("session"), session);
  assert.equal(calls[5].url.searchParams.get("session"), session);
  for (const call of calls) {
    assert.equal(call.options.redirect, "manual");
    assert.equal(call.options.credentials, "omit");
    assert.equal(new Headers(call.options.headers).has("cookie"), false);
    assert.equal(new Headers(call.options.headers).has("authorization"), false);
    assert.equal(call.options.signal, signal);
  }
});

test("relative cookieCheck Location preserves the original allowed HLS query", async () => {
  const { calls, request } = scripted([
    new Response(null, {
      status: 302,
      headers: { Location: "?_HLS_msn=12&cookieCheck=1" },
    }),
    new Response("#EXTM3U"),
  ]);
  await fetchHls(target("index.m3u8", "_HLS_msn=12"), controller(), request);
  assert.equal(calls[1].url.pathname, "/vmt/cam-002/index.m3u8");
  assert.equal(calls[1].url.searchParams.get("_HLS_msn"), "12");
});

test("a direct upstream success or failure is returned without retrying or bypassing auth", async () => {
  for (const status of [200, 401, 403, 404, 503]) {
    const { calls, request } = scripted([new Response("upstream", { status })]);
    const result = await fetchHls(target(), controller(), request);
    assert.equal(result.status, status);
    assert.equal(calls.length, 1);
  }
});

test("external, cross-source, traversal, credential and query-changing redirects are rejected before follow-up", async () => {
  for (const location of [
    "https://untrusted.invalid/index.m3u8?cookieCheck=1",
    "//untrusted.invalid/vmt/cam-002/index.m3u8?cookieCheck=1",
    "http://rtsp-server:9999/vmt/cam-002/index.m3u8?cookieCheck=1",
    "http://user:password@rtsp-server:8888/vmt/cam-002/index.m3u8?cookieCheck=1",
    "/vmt/cam-003/index.m3u8?cookieCheck=1",
    "../cam-003/index.m3u8?cookieCheck=1",
    "/vmt/cam-002/video1_stream.m3u8?cookieCheck=1",
    "?cookieCheck=1&session=" + session,
    "?cookieCheck=1&cookieCheck=1",
    "?cookieCheck=1#fragment",
    "?cookieCheck=0",
    "?cookieCheck=1&target=http://untrusted.invalid",
  ]) {
    const { calls, request } = scripted([
      new Response(null, { status: 302, headers: { Location: location } }),
    ]);
    await assert.rejects(
      () => fetchHls(target(), controller(), request),
      /MEDIA_REDIRECT_DENIED/,
    );
    assert.equal(calls.length, 1);
  }
});

test("redirect loops, missing Location, unexpected statuses and fragment redirects fail closed", async () => {
  const loop = scripted([
    new Response(null, {
      status: 302,
      headers: { Location: "?cookieCheck=1" },
    }),
    new Response(null, {
      status: 302,
      headers: { Location: "?cookieCheck=1" },
    }),
  ]);
  await assert.rejects(
    () => fetchHls(target(), controller(), loop.request),
    /MEDIA_REDIRECT_LIMIT/,
  );
  assert.equal(loop.calls.length, 2);
  for (const status of [301, 302, 303, 307, 308]) {
    const stub = scripted([
      new Response(null, {
        status,
        headers: status === 302 ? {} : { Location: "?cookieCheck=1" },
      }),
    ]);
    await assert.rejects(
      () => fetchHls(target(), controller(), stub.request),
      /MEDIA_REDIRECT_DENIED/,
    );
    assert.equal(stub.calls.length, 1);
  }
  const fragment = scripted([
    new Response(null, {
      status: 302,
      headers: { Location: "?cookieCheck=1" },
    }),
  ]);
  await assert.rejects(
    () => fetchHls(target("init.mp4"), controller(), fragment.request),
    /MEDIA_REDIRECT_DENIED/,
  );
});

test("targets cannot escape a registered camera or accept arbitrary/doubled session parameters", () => {
  for (const filename of [
    "../cam-003/index.m3u8",
    "%2e%2e/index.m3u8",
    "/index.m3u8",
    "cam-003/index.m3u8",
    "index.m3u8?session=other",
  ])
    assert.throws(() => target(filename), /MEDIA_PATH_INVALID/);
  for (const query of [
    "session=invalid",
    `session=${session}&session=${session}`,
    "_HLS_msn=-1",
    "_HLS_part=1x",
    "_HLS_skip=NO",
  ])
    assert.throws(
      () => target("video1_stream.m3u8", query),
      /MEDIA_QUERY_INVALID/,
    );
  const safe = target(
    "index.m3u8",
    `session=${session}&cookieCheck=1&target=https://untrusted.invalid&authorization=secret`,
  );
  assert.equal(safe.search, `?session=${session}`);
  assert.equal(target("part0.mp").pathname, "/vmt/cam-002/part0.mp");
  assert.throws(
    () =>
      mediaTarget(origin, "../cam-003", "index.m3u8", new URLSearchParams()),
    /MEDIA_PATH_INVALID/,
  );
});

test("both handshake requests share the deadline and propagate cancellation without retries", async () => {
  const abort = new AbortController();
  let calls = 0;
  const request: typeof fetch = async (_input, options) => {
    calls++;
    assert.equal(options?.signal, abort.signal);
    abort.abort();
    throw new DOMException("Aborted", "AbortError");
  };
  await assert.rejects(() => fetchHls(target(), abort.signal, request), {
    name: "AbortError",
  });
  assert.equal(calls, 1);
});
