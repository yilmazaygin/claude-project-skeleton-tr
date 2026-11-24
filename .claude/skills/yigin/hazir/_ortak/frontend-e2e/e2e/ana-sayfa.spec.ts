import { expect, test } from "@playwright/test";

test("ana sayfa açılır", async ({ page }) => {
  const yanit = await page.goto("/");
  expect(yanit?.status()).toBe(200);
  await expect(page.locator("body")).toBeVisible();
});
