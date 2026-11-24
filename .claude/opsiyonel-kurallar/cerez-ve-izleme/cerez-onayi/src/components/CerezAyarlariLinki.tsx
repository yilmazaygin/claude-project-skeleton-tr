"use client";

import { ayarlariAc } from "@/lib/cerez-onayi";

/** Alt bilgide durur; ziyaretçi seçimini her zaman değiştirebilir. */
export default function CerezAyarlariLinki({ className = "underline" }: { className?: string }) {
  return (
    <button type="button" className={className} onClick={ayarlariAc}>
      Çerez ayarları
    </button>
  );
}
