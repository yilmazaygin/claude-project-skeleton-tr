// @vitest-environment node
import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { proxyToLaravel } from "./api-proxy";

afterEach(() => vi.unstubAllGlobals());

describe("api proxy", () => {
  it("isteği iç adrese aktarır, bağlantıya özgü başlıkları atar, X-Forwarded-* ekler", async () => {
    const fetchSahte = vi.fn(async () => new Response("{}", { status: 201 }));
    vi.stubGlobal("fetch", fetchSahte);

    const istek = new NextRequest("http://app.localhost:8080/api/v1/kayit?x=1", {
      method: "POST",
      headers: { connection: "keep-alive", cookie: "oturum=abc", "content-type": "application/json" },
      body: JSON.stringify({ ad: "Ayşe" }),
    });
    const yanit = await proxyToLaravel(istek);

    expect(yanit.status).toBe(201);
    const [hedef, ayar] = fetchSahte.mock.calls[0] as unknown as [URL, RequestInit];
    expect(String(hedef)).toMatch(/\/api\/v1\/kayit\?x=1$/);
    const basliklar = new Headers(ayar.headers);
    expect(basliklar.get("connection")).toBeNull();
    expect(basliklar.get("cookie")).toBe("oturum=abc");
    expect(basliklar.get("x-forwarded-proto")).toBe("http");
    expect(basliklar.get("x-forwarded-host")).toBeTruthy();
    expect(ayar.redirect).toBe("manual");
  });

  it("birden çok Set-Cookie başlığını ayrı ayrı geri verir, content-encoding'i atar", async () => {
    const backend = new Headers();
    backend.append("set-cookie", "XSRF-TOKEN=a; Path=/");
    backend.append("set-cookie", "oturum=b; Path=/; HttpOnly");
    backend.set("content-encoding", "gzip");
    vi.stubGlobal("fetch", vi.fn(async () => new Response(null, { status: 204, headers: backend })));

    const yanit = await proxyToLaravel(new NextRequest("http://app.localhost/sanctum/csrf-cookie"));

    expect(yanit.headers.getSetCookie()).toEqual(["XSRF-TOKEN=a; Path=/", "oturum=b; Path=/; HttpOnly"]);
    expect(yanit.headers.get("content-encoding")).toBeNull();
  });
});
