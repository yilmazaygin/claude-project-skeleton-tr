"use client";

import OnayliBetik from "@/components/OnayliBetik";

/**
 * Umami izleme betiği. Umami çerez yazmaz ve IP saklamaz; yine de kural gereği varsayılan olarak
 * analitik onayına bağlıdır. Hukuki değerlendirmeden sonra onaysız yüklenmesine karar verilirse
 * OnayliBetik yerine doğrudan next/script kullanılır ve çerez listesine bu karar yazılır.
 * Adres ve kimlik: NEXT_PUBLIC_UMAMI_URL, NEXT_PUBLIC_UMAMI_WEBSITE_ID (canlı imajda build sırasında girer).
 */
export default function UmamiBetigi() {
  const adres = process.env.NEXT_PUBLIC_UMAMI_URL;
  const siteKimligi = process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID;
  if (!adres || !siteKimligi) return null;
  return (
    <OnayliBetik
      kategori="analitik"
      id="umami"
      src={`${adres.replace(/\/$/, "")}/script.js`}
      data-website-id={siteKimligi}
      strategy="afterInteractive"
    />
  );
}
