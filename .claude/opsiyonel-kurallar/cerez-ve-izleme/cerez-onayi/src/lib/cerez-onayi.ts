/**
 * Çerez onayı (çerez-ve-izleme kuralı).
 *
 * Kategoriler: zorunlu (her zaman açık), tercih, analitik, pazarlama.
 * Onay `cerez_tercihi` çerezinde tutulur. Zorunlu olmayan hiçbir betik onaydan önce yüklenmez;
 * betikler OnayliBetik bileşeniyle bu dosyadaki izinVar() kontrolüne bağlanır.
 *
 * Bu dosya React içermez; mantığı Node ile birim testine girebilir.
 */

export type Kategori = "zorunlu" | "tercih" | "analitik" | "pazarlama";
export type SecmeliKategori = Exclude<Kategori, "zorunlu">;
export type Secim = Record<SecmeliKategori, boolean>;
export type Onay = Secim & { surum: number; tarih: string };

export const CEREZ_ADI = "cerez_tercihi";
/** Kategoriler veya banner metni değişince artırılır; eski onaylar geçersiz sayılır ve banner yeniden çıkar. */
export const ONAY_SURUMU = 1;
export const SURE_GUN = 365;
export const DEGISTI_OLAYI = "cerez-onayi-degisti";
export const AYARLARI_AC_OLAYI = "cerez-ayarlarini-ac";
/** Doluysa onay değişikliği bu adrese POST edilir (denetim kaydı için). Örnek: /api/cerez-onayi */
export const KAYIT_ADRESI: string =
  typeof process !== "undefined" ? (process.env.NEXT_PUBLIC_CEREZ_ONAY_KAYDI ?? "") : "";

export const TUMU_KABUL: Secim = { tercih: true, analitik: true, pazarlama: true };
export const TUMU_RET: Secim = { tercih: false, analitik: false, pazarlama: false };

export function onayOlustur(secim: Secim, simdi: Date = new Date()): Onay {
  return {
    surum: ONAY_SURUMU,
    tarih: simdi.toISOString(),
    tercih: secim.tercih === true,
    analitik: secim.analitik === true,
    pazarlama: secim.pazarlama === true,
  };
}

/** Çerez değerini çözer. Bozuk, eski sürümlü veya eksik değer onay sayılmaz (null). */
export function onayiCoz(deger: string | null | undefined): Onay | null {
  if (!deger) return null;
  try {
    const v = JSON.parse(decodeURIComponent(deger)) as Partial<Onay> | null;
    if (!v || v.surum !== ONAY_SURUMU || typeof v.tarih !== "string") return null;
    return {
      surum: v.surum,
      tarih: v.tarih,
      tercih: v.tercih === true,
      analitik: v.analitik === true,
      pazarlama: v.pazarlama === true,
    };
  } catch {
    return null;
  }
}

/** document.cookie için yazılacak satır. https'te Secure eklenir. HttpOnly olamaz: tarayıcı okur. */
export function cerezSatiri(onay: Onay, https: boolean): string {
  const deger = encodeURIComponent(JSON.stringify(onay));
  return `${CEREZ_ADI}=${deger}; Max-Age=${SURE_GUN * 86400}; Path=/; SameSite=Lax${https ? "; Secure" : ""}`;
}

/** "a=1; cerez_tercihi=...; b=2" içinden adı verilen çerezin değerini bulur. */
export function cerezDegeriniBul(cerezler: string, ad: string = CEREZ_ADI): string | null {
  for (const parca of cerezler.split(";")) {
    const esittir = parca.indexOf("=");
    if (esittir > -1 && parca.slice(0, esittir).trim() === ad) {
      return parca.slice(esittir + 1).trim();
    }
  }
  return null;
}

export function izinVar(onay: Onay | null, kategori: Kategori): boolean {
  if (kategori === "zorunlu") return true;
  return onay !== null && onay[kategori] === true;
}

/** Önceki onayda açık olup yeni seçimde kapanan kategori var mı? (Yüklenmiş betik ancak sayfa yenilenince kalkar.) */
export function geriCekildiMi(onceki: Onay | null, yeni: Secim): boolean {
  if (!onceki) return false;
  return (["tercih", "analitik", "pazarlama"] as const).some((k) => onceki[k] && !yeni[k]);
}

// --- Tarayıcı ---------------------------------------------------------------

export function onayiOku(): Onay | null {
  if (typeof document === "undefined") return null;
  return onayiCoz(cerezDegeriniBul(document.cookie));
}

export function onayiKaydet(secim: Secim): Onay {
  const onceki = onayiOku();
  const onay = onayOlustur(secim);
  document.cookie = cerezSatiri(onay, window.location.protocol === "https:");
  window.dispatchEvent(new CustomEvent(DEGISTI_OLAYI, { detail: onay }));

  if (KAYIT_ADRESI) {
    const xsrf = cerezDegeriniBul(document.cookie, "XSRF-TOKEN");
    fetch(KAYIT_ADRESI, {
      method: "POST",
      credentials: "same-origin",
      keepalive: true,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...(xsrf ? { "X-XSRF-TOKEN": decodeURIComponent(xsrf) } : {}),
      },
      body: JSON.stringify(onay),
    }).catch(() => {
      // Onay kaydı gönderilemezse ziyaretçinin seçimi yine geçerlidir.
    });
  }

  // Geri çekilen kategoriye ait yüklenmiş betikler ancak sayfa yenilenince kalkar.
  if (geriCekildiMi(onceki, secim)) {
    window.location.reload();
  }
  return onay;
}

export function ayarlariAc(): void {
  window.dispatchEvent(new Event(AYARLARI_AC_OLAYI));
}
