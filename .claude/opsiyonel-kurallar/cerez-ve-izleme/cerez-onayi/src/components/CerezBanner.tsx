"use client";

import { useEffect, useState } from "react";

import {
  AYARLARI_AC_OLAYI,
  TUMU_KABUL,
  TUMU_RET,
  onayiKaydet,
  onayiOku,
  type Secim,
  type SecmeliKategori,
} from "@/lib/cerez-onayi";
import { useCerezOnayi, useIstemcide } from "@/lib/use-cerez-onayi";

// Metinler projenin çerez listesine (docs/mantik/cerez-ve-izleme.md) göre düzenlenir.
const KATEGORILER: { ad: SecmeliKategori; baslik: string; aciklama: string }[] = [
  { ad: "tercih", baslik: "Tercih", aciklama: "Dil ve tema gibi seçimlerinizi hatırlar." },
  { ad: "analitik", baslik: "Analitik", aciklama: "Siteyi nasıl kullandığınızı anonim olarak ölçer." },
  { ad: "pazarlama", baslik: "Pazarlama", aciklama: "Reklamların ölçülmesi ve kişiselleştirilmesi içindir." },
];

// Üç düğme aynı boyut ve ağırlıktadır: "Reddet", "Kabul et" kadar kolay ve görünür olmalıdır.
const DUGME =
  "flex-1 rounded-md border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-900 hover:bg-zinc-100 " +
  "dark:border-zinc-600 dark:text-zinc-100 dark:hover:bg-zinc-800";

export default function CerezBanner({ politikaAdresi = "/cerez-politikasi" }: { politikaAdresi?: string }) {
  const istemcide = useIstemcide();
  const onay = useCerezOnayi();
  const [acikZorla, setAcikZorla] = useState(false);
  const [ayarlar, setAyarlar] = useState(false);
  const [secim, setSecim] = useState<Secim>(TUMU_RET);

  useEffect(() => {
    const ac = () => {
      setSecim(onayiOku() ?? TUMU_RET);
      setAyarlar(true);
      setAcikZorla(true);
    };
    window.addEventListener(AYARLARI_AC_OLAYI, ac);
    return () => window.removeEventListener(AYARLARI_AC_OLAYI, ac);
  }, []);

  if (!istemcide || (onay !== null && !acikZorla)) return null;

  const kaydet = (s: Secim) => {
    onayiKaydet(s);
    setAcikZorla(false);
    setAyarlar(false);
  };

  return (
    <div
      role="dialog"
      aria-label="Çerez tercihleri"
      className="fixed inset-x-0 bottom-0 z-50 border-t border-zinc-200 bg-white p-4 shadow-lg dark:border-zinc-700 dark:bg-zinc-900"
    >
      <div className="mx-auto flex max-w-3xl flex-col gap-3">
        <p className="text-sm text-zinc-700 dark:text-zinc-300">
          Sitenin çalışması için gerekli çerezleri kullanıyoruz. Onay verirseniz tercih, analitik ve pazarlama
          çerezleri de kullanılır. Ayrıntılar:{" "}
          <a href={politikaAdresi} className="underline">
            Çerez politikası
          </a>
          .
        </p>

        {ayarlar && (
          <fieldset className="flex flex-col gap-2 text-sm">
            <label className="flex items-start gap-2 opacity-70">
              <input type="checkbox" checked disabled className="mt-1" />
              <span>
                <strong>Zorunlu</strong> — oturum ve güvenlik için gereklidir, kapatılamaz.
              </span>
            </label>
            {KATEGORILER.map((k) => (
              <label key={k.ad} className="flex items-start gap-2">
                <input
                  type="checkbox"
                  className="mt-1"
                  checked={secim[k.ad]}
                  onChange={(e) => setSecim({ ...secim, [k.ad]: e.target.checked })}
                />
                <span>
                  <strong>{k.baslik}</strong> — {k.aciklama}
                </span>
              </label>
            ))}
          </fieldset>
        )}

        <div className="flex flex-col gap-2 sm:flex-row">
          <button type="button" className={DUGME} onClick={() => kaydet(TUMU_RET)}>
            Reddet
          </button>
          {ayarlar ? (
            <button type="button" className={DUGME} onClick={() => kaydet(secim)}>
              Seçimi kaydet
            </button>
          ) : (
            <button type="button" className={DUGME} onClick={() => setAyarlar(true)}>
              Ayarlar
            </button>
          )}
          <button type="button" className={DUGME} onClick={() => kaydet(TUMU_KABUL)}>
            Kabul et
          </button>
        </div>
      </div>
    </div>
  );
}
