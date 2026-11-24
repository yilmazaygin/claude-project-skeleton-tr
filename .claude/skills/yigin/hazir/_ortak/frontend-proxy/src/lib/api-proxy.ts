/**
 * Tarayıcıdan gelen /api ve /sanctum isteklerini Laravel'e (INTERNAL_API_URL) aktarır.
 *
 * Tarayıcı yalnızca frontend alan adını görür. CORS gerekmez; Sanctum'un oturum
 * çerezleri frontend alan adında kalır. Laravel tarafında trustProxies ayarlanmalıdır,
 * yoksa Laravel gerçek alan adını ve https şemasını göremez.
 */
import type { NextRequest } from "next/server";

const INTERNAL_API_URL = process.env.INTERNAL_API_URL ?? "http://nginx";

// Yalnızca tek bir bağlantıya ait başlıklar aktarılmaz.
const HOP_BY_HOP = new Set([
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailer",
  "transfer-encoding",
  "upgrade",
  "host",
  "content-length",
]);

export async function proxyToLaravel(req: NextRequest): Promise<Response> {
  const incoming = new URL(req.url);
  const target = new URL(incoming.pathname + incoming.search, INTERNAL_API_URL);

  const headers = new Headers();
  req.headers.forEach((value, key) => {
    if (!HOP_BY_HOP.has(key.toLowerCase())) headers.set(key, value);
  });
  headers.set(
    "x-forwarded-host",
    req.headers.get("x-forwarded-host") ?? req.headers.get("host") ?? incoming.host,
  );
  headers.set(
    "x-forwarded-proto",
    req.headers.get("x-forwarded-proto") ?? incoming.protocol.replace(":", ""),
  );

  const hasBody = req.method !== "GET" && req.method !== "HEAD";
  const upstream = await fetch(target, {
    method: req.method,
    headers,
    body: hasBody ? await req.arrayBuffer() : undefined,
    redirect: "manual",
    cache: "no-store",
  });

  // fetch gövdeyi zaten açtığı için content-encoding geri verilmez.
  const responseHeaders = new Headers();
  upstream.headers.forEach((value, key) => {
    const k = key.toLowerCase();
    if (HOP_BY_HOP.has(k) || k === "set-cookie" || k === "content-encoding") return;
    responseHeaders.set(key, value);
  });
  // Birden çok Set-Cookie başlığı tek tek aktarılır (XSRF-TOKEN ve oturum çerezi).
  for (const cookie of upstream.headers.getSetCookie()) {
    responseHeaders.append("set-cookie", cookie);
  }

  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: responseHeaders,
  });
}
