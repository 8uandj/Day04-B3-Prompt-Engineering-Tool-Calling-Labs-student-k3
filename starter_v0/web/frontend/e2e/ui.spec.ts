import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => { await page.goto("/"); });

test("sidebar hides and has a persistent bottom-left reveal control", async ({ page }) => {
  await page.getByTitle("Ẩn sidebar").click();
  const reveal = page.getByRole("button", { name: "Mở sidebar" });
  await expect(reveal).toBeVisible();
  const box = await reveal.boundingBox();
  const viewport = page.viewportSize();
  expect(box).not.toBeNull(); expect(viewport).not.toBeNull();
  expect(box!.x).toBeLessThan(30);
  expect(viewport!.height - box!.y - box!.height).toBeLessThan(30);
  await reveal.click();
  await expect(page.getByLabel("Application sidebar")).toBeVisible();
});

test("history opens as a focused modal", async ({ page }) => {
  await page.getByRole("button", { name: "Lịch sử" }).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.getByPlaceholder("Tìm trong lịch sử…")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toBeHidden();
});

test("chat composer keeps white typing text on navy", async ({ page }) => {
  const input = page.getByPlaceholder("Nhập câu hỏi nghiên cứu…");
  await input.fill("Kiểm tra màu chữ");
  await expect(input).toHaveCSS("color", "rgb(255, 255, 255)");
  await expect(input.locator("..")).toHaveCSS("background-color", "rgb(0, 38, 76)");
});
