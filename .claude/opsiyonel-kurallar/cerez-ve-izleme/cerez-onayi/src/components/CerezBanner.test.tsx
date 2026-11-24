import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import CerezBanner from "./CerezBanner";
import { CEREZ_ADI, ayarlariAc, onayiOku } from "@/lib/cerez-onayi";

function cerezleriTemizle() {
  for (const parca of document.cookie.split(";")) {
    const ad = parca.split("=")[0].trim();
    if (ad) document.cookie = `${ad}=; Max-Age=0; Path=/`;
  }
}

beforeEach(cerezleriTemizle);
afterEach(() => {
  cleanup();
  cerezleriTemizle();
});

describe("CerezBanner", () => {
  it("onay yokken çıkar; üç düğme de var", () => {
    render(<CerezBanner />);
    expect(screen.getByRole("dialog", { name: "Çerez tercihleri" })).toBeTruthy();
    for (const ad of ["Reddet", "Ayarlar", "Kabul et"]) expect(screen.getByRole("button", { name: ad })).toBeTruthy();
  });

  it("Reddet: onay çerezi yazılır, seçmeli kategoriler kapalı, banner kapanır", () => {
    render(<CerezBanner />);
    fireEvent.click(screen.getByRole("button", { name: "Reddet" }));
    expect(document.cookie).toContain(`${CEREZ_ADI}=`);
    expect(onayiOku()).toMatchObject({ tercih: false, analitik: false, pazarlama: false });
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("Ayarlar: yalnızca analitik seçilip kaydedilir", () => {
    render(<CerezBanner />);
    fireEvent.click(screen.getByRole("button", { name: "Ayarlar" }));
    fireEvent.click(screen.getByRole("checkbox", { name: /Analitik/ }));
    fireEvent.click(screen.getByRole("button", { name: "Seçimi kaydet" }));
    expect(onayiOku()).toMatchObject({ tercih: false, analitik: true, pazarlama: false });
  });

  it("onay varken çıkmaz; 'Çerez ayarları' ile yeniden açılır", () => {
    render(<CerezBanner />);
    fireEvent.click(screen.getByRole("button", { name: "Kabul et" }));
    expect(screen.queryByRole("dialog")).toBeNull();
    act(() => ayarlariAc());
    expect(screen.getByRole("dialog", { name: "Çerez tercihleri" })).toBeTruthy();
  });
});
