"use client";

import Script, { type ScriptProps } from "next/script";

import { izinVar, type SecmeliKategori } from "@/lib/cerez-onayi";
import { useCerezOnayi, useIstemcide } from "@/lib/use-cerez-onayi";

/**
 * Bir betiği yalnızca kategorisine onay verildiyse yükler. Sunucu çiziminde hiçbir şey üretmez.
 * Örnek: <OnayliBetik kategori="pazarlama" id="meta-pixel" src="https://..." />
 */
export default function OnayliBetik({ kategori, ...betik }: ScriptProps & { kategori: SecmeliKategori }) {
  const istemcide = useIstemcide();
  const onay = useCerezOnayi();
  if (!istemcide || !izinVar(onay, kategori)) return null;
  return <Script {...betik} />;
}
