// /api/* isteklerini Laravel'e aktarır. Ayrıntı: src/lib/api-proxy.ts
import { proxyToLaravel } from "@/lib/api-proxy";

// "export const dynamic" yazılmaz: Next.js 16 cacheComponents ile uyumsuzdur.
// Route handler istek okuduğu için zaten her istekte çalışır, önbelleğe alınmaz.

export const GET = proxyToLaravel;
export const HEAD = proxyToLaravel;
export const POST = proxyToLaravel;
export const PUT = proxyToLaravel;
export const PATCH = proxyToLaravel;
export const DELETE = proxyToLaravel;
export const OPTIONS = proxyToLaravel;
