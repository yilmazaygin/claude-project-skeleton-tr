import { expect, test, type Page } from "@playwright/test";

// Google'a gerçek istek gitmez; gtag betiğinin yüklenip yüklenmediği sayfadaki <script> ile kontrol edilir.
async function googleuKapat(page: Page) {
  await page.route("**/www.googletagmanager.com/**", (r) => r.fulfill({ status: 200, contentType: "text/javascript", body: "" }));
}

const gtagBetigi = (page: Page) => page.locator('script[src*="googletagmanager.com/gtag/js"]');

async function onayCerezi(page: Page) {
  const cerez = (await page.context().cookies()).find((c) => c.name === "cerez_tercihi");
  return cerez ? JSON.parse(decodeURIComponent(cerez.value)) : null;
}

test("banner çıkar; onay yokken gtag yüklenmez", async ({ page }) => {
  await googleuKapat(page);
  await page.goto("/");
  await expect(page.getByRole("dialog", { name: "Çerez tercihleri" })).toBeVisible();
  await expect(gtagBetigi(page)).toHaveCount(0);
});

test("Reddet: onay çerezi yazılır, gtag yüklenmez, banner kapanır", async ({ page }) => {
  await googleuKapat(page);
  await page.goto("/");
  await page.getByRole("button", { name: "Reddet" }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  expect(await onayCerezi(page)).toMatchObject({ tercih: false, analitik: false, pazarlama: false });
  await expect(gtagBetigi(page)).toHaveCount(0);
  await page.reload();
  await expect(page.getByRole("dialog")).toHaveCount(0);
});

test("Kabul et: gtag yüklenir; 'Çerez ayarları' ile geri çekilince sayfa yenilenir ve gtag kalkar", async ({ page }) => {
  await googleuKapat(page);
  await page.goto("/");
  await page.getByRole("button", { name: "Kabul et" }).click();
  await expect(gtagBetigi(page)).toHaveCount(1);
  expect(await onayCerezi(page)).toMatchObject({ analitik: true, pazarlama: true });

  await page.evaluate(() => window.dispatchEvent(new Event("cerez-ayarlarini-ac")));
  await page.getByRole("button", { name: "Reddet" }).click();
  await page.waitForLoadState("load");
  await expect(gtagBetigi(page)).toHaveCount(0);
  expect(await onayCerezi(page)).toMatchObject({ analitik: false });
});
