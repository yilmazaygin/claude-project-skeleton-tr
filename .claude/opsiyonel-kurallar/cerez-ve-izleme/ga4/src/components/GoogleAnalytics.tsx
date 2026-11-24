"use client";

import Script from "next/script";
import { useEffect } from "react";

import { izinVar } from "@/lib/cerez-onayi";
import { useCerezOnayi, useIstemcide } from "@/lib/use-cerez-onayi";

type Gtag = (...args: unknown[]) => void;

/**
 * Google Analytics 4 + Consent Mode v2, "temel" kip: gtag betiği analitik onayı gelmeden hiç yüklenmez.
 * Pazarlama onayı reklam izinlerini (ad_storage, ad_user_data, ad_personalization) belirler.
 * Onay sonradan değişirse "consent update" gönderilir; geri çekmede sayfa yenilenir (cerez-onayi.ts).
 * Kimlik: NEXT_PUBLIC_GA_ID (G-XXXXXXX). Canlı imajda build sırasında girer.
 */
export default function GoogleAnalytics({ gaId = process.env.NEXT_PUBLIC_GA_ID }: { gaId?: string }) {
  const istemcide = useIstemcide();
  const onay = useCerezOnayi();
  const analitik = izinVar(onay, "analitik");
  const pazarlama = izinVar(onay, "pazarlama");

  useEffect(() => {
    const gtag = (window as unknown as { gtag?: Gtag }).gtag;
    gtag?.("consent", "update", {
      analytics_storage: analitik ? "granted" : "denied",
      ad_storage: pazarlama ? "granted" : "denied",
      ad_user_data: pazarlama ? "granted" : "denied",
      ad_personalization: pazarlama ? "granted" : "denied",
    });
  }, [analitik, pazarlama]);

  if (!gaId || !/^G-[A-Z0-9]+$/.test(gaId) || !istemcide || !analitik) return null;

  const reklam = pazarlama ? "granted" : "denied";
  return (
    <>
      <Script id="ga4-izin" strategy="afterInteractive">
        {`window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}window.gtag=gtag;` +
          `gtag('consent','default',{analytics_storage:'granted',ad_storage:'${reklam}',ad_user_data:'${reklam}',ad_personalization:'${reklam}'});` +
          `gtag('js',new Date());gtag('config','${gaId}');`}
      </Script>
      <Script id="ga4" src={`https://www.googletagmanager.com/gtag/js?id=${gaId}`} strategy="afterInteractive" />
    </>
  );
}
