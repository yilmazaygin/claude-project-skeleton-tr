"use client";

import { useSyncExternalStore } from "react";

import { DEGISTI_OLAYI, onayiOku, type Onay } from "./cerez-onayi";

let onbellek: { cerez: string; onay: Onay | null } | null = null;

function anlikDurum(): Onay | null {
  const cerez = document.cookie;
  if (!onbellek || onbellek.cerez !== cerez) {
    onbellek = { cerez, onay: onayiOku() };
  }
  return onbellek.onay;
}

function abone(degisti: () => void): () => void {
  window.addEventListener(DEGISTI_OLAYI, degisti);
  return () => window.removeEventListener(DEGISTI_OLAYI, degisti);
}

const bosAbone = () => () => {};

/** Ziyaretçinin güncel onayı. Sunucuda ve ilk çizimde null'dır. */
export function useCerezOnayi(): Onay | null {
  return useSyncExternalStore(abone, anlikDurum, () => null);
}

/** Bileşen tarayıcıda mı? Sunucu çiziminde false; böylece hiçbir izleme betiği HTML'e girmez. */
export function useIstemcide(): boolean {
  return useSyncExternalStore(bosAbone, () => true, () => false);
}
