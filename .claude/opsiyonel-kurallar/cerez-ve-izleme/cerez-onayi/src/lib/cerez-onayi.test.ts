import { describe, expect, it } from "vitest";

import {
  CEREZ_ADI,
  ONAY_SURUMU,
  TUMU_KABUL,
  TUMU_RET,
  cerezDegeriniBul,
  cerezSatiri,
  geriCekildiMi,
  izinVar,
  onayOlustur,
  onayiCoz,
} from "./cerez-onayi";

const deger = (satir: string) => satir.split(";")[0].slice(CEREZ_ADI.length + 1);
const SECMELI = ["tercih", "analitik", "pazarlama"] as const;

describe("çerez onayı", () => {
  it("onay yokken yalnızca zorunlu kategori açık", () => {
    expect(izinVar(null, "zorunlu")).toBe(true);
    for (const k of SECMELI) expect(izinVar(null, k)).toBe(false);
  });

  it("tümünü kabul et: çerez yazılır, geri okunur, bütün kategoriler açık", () => {
    const onay = onayOlustur(TUMU_KABUL, new Date("2026-11-23T10:00:00Z"));
    const okunan = onayiCoz(deger(cerezSatiri(onay, true)));
    expect(okunan).toEqual(onay);
    expect(okunan?.surum).toBe(ONAY_SURUMU);
    for (const k of SECMELI) expect(izinVar(okunan, k)).toBe(true);
  });

  it("reddet: bütün seçmeli kategoriler kapalı", () => {
    const okunan = onayiCoz(deger(cerezSatiri(onayOlustur(TUMU_RET), false)));
    for (const k of SECMELI) expect(izinVar(okunan, k)).toBe(false);
  });

  it("kısmi onay: yalnızca analitik", () => {
    const okunan = onayiCoz(deger(cerezSatiri(onayOlustur({ tercih: false, analitik: true, pazarlama: false }), true)));
    expect(izinVar(okunan, "analitik")).toBe(true);
    expect(izinVar(okunan, "pazarlama")).toBe(false);
  });

  it("çerez satırı: 365 gün, Path=/, SameSite=Lax; Secure yalnızca https'te; HttpOnly yok", () => {
    const onay = onayOlustur(TUMU_RET);
    expect(cerezSatiri(onay, true)).toMatch(/; Max-Age=31536000; Path=\/; SameSite=Lax; Secure$/);
    expect(cerezSatiri(onay, false)).not.toMatch(/Secure/);
    expect(cerezSatiri(onay, true)).not.toMatch(/HttpOnly/);
  });

  it("bozuk, eski sürümlü veya hileli değer onay sayılmaz", () => {
    expect(onayiCoz(null)).toBeNull();
    expect(onayiCoz("")).toBeNull();
    expect(onayiCoz("%E0%A4%A")).toBeNull();
    expect(onayiCoz("{bozuk")).toBeNull();
    expect(onayiCoz(encodeURIComponent(JSON.stringify({ ...onayOlustur(TUMU_KABUL), surum: ONAY_SURUMU + 1 })))).toBeNull();
    const hile = onayiCoz(encodeURIComponent(JSON.stringify({ surum: ONAY_SURUMU, tarih: "x", analitik: "true", pazarlama: 1 })));
    expect(izinVar(hile, "analitik")).toBe(false);
    expect(izinVar(hile, "pazarlama")).toBe(false);
  });

  it("document.cookie içinden doğru çerez bulunur", () => {
    const c = `XSRF-TOKEN=abc; ${CEREZ_ADI}=deger%20x; ${CEREZ_ADI}_eski=yanlis; app-session=s`;
    expect(cerezDegeriniBul(c)).toBe("deger%20x");
    expect(cerezDegeriniBul(c, "XSRF-TOKEN")).toBe("abc");
    expect(cerezDegeriniBul("a=1")).toBeNull();
  });

  it("geri çekme algılanır (sayfa yenilenir)", () => {
    expect(geriCekildiMi(null, TUMU_RET)).toBe(false);
    expect(geriCekildiMi(onayOlustur(TUMU_KABUL), TUMU_KABUL)).toBe(false);
    expect(geriCekildiMi(onayOlustur(TUMU_KABUL), { ...TUMU_KABUL, analitik: false })).toBe(true);
    expect(geriCekildiMi(onayOlustur(TUMU_RET), TUMU_KABUL)).toBe(false);
  });
});
