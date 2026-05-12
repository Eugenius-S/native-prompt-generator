const { test, expect } = require("@playwright/test");

async function selectOption(page, name, label) {
  const select = page.locator(`[data-select-name="${name}"]`);
  await select.locator(".select-trigger").click();
  const option = select.locator(".select-option").filter({ hasText: label }).first();
  await expect(option).toBeVisible();
  await option.click();
}

test("appearance custom-selects update labels and dependent inputs", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "women", exact: true }).click();

  const womenPhysicalTraits = page.locator('.sub-block').filter({ has: page.locator('h3', { hasText: 'Physical traits' }) }).first();
  const womenHairColorField = womenPhysicalTraits.locator('.field').filter({ has: page.locator('[data-select-name="hairColorControl"]') }).first();

  await expect(page.locator('input[name="age"]')).toHaveAttribute(
    "placeholder",
    "Random / 18 / 18-20 / 21-23 / 25-30 / 30+",
  );

  await selectOption(page, "hairLength", "Short hair");
  await expect(page.locator('[data-select-name="hairLength"] .select-trigger')).toContainText("Short hair");

  await selectOption(page, "hairstyle", "Custom");
  await expect(page.locator('input[name="customHair"]')).toBeEnabled();

  await expect(womenHairColorField).toContainText("Allow dyed hair");
  await expect(womenHairColorField.locator('input[name="allowDyedNaturalHairColors"]')).toBeVisible();
  await expect(womenHairColorField.locator('input[name="allowDyedNaturalHairColors"]')).toBeEnabled();
  const womenPhysicalTraitLabels = await womenPhysicalTraits.locator('.field-label').allTextContents();
  expect(womenPhysicalTraitLabels.indexOf("Custom hair color")).toBeLessThan(womenPhysicalTraitLabels.indexOf("Eye color"));

  await selectOption(page, "hairColorControl", "Custom");
  await expect(page.locator('input[name="customHairColor"]')).toBeEnabled();
  await expect(womenHairColorField.locator('input[name="allowDyedNaturalHairColors"]')).toBeDisabled();

  await selectOption(page, "hairColorControl", "Random");
  await expect(womenHairColorField.locator('input[name="allowDyedNaturalHairColors"]')).toBeEnabled();

  await selectOption(page, "breastSizeControl", "Small");
  await expect(page.locator('[data-select-name="breastSizeControl"] .select-trigger')).toContainText("Small");
});

test("custom-select supports keyboard navigation and default generate still works", async ({ page }) => {
  test.slow();
  await page.goto("/");

  const hairLengthTrigger = page.locator('[data-select-name="hairLength"] .select-trigger');
  await hairLengthTrigger.focus();
  await page.keyboard.press("ArrowDown");
  await expect(page.locator('[data-select-name="hairLength"]')).toHaveClass(/is-open/);
  await expect(hairLengthTrigger).toContainText("Random");
  await page.locator('[data-select-name="hairLength"] .select-option[data-value="short"]').focus();
  await page.keyboard.press("Enter");
  await expect(hairLengthTrigger).toContainText("Short hair");

  await page.getByRole("button", { name: /Generate/i }).click();
  await expect(page.locator(".preview-line").first()).toBeVisible({ timeout: 30_000 });
  await expect(page.locator('.preview-line .copy-button .button-icon').first()).toHaveCSS("width", "24px");
  await expect(page.locator('.preview-line .copy-button .button-icon').first()).toHaveCSS("height", "24px");
});

test("men and couples expose expanded male appearance controls", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "men", exact: true }).click();
  await selectOption(page, "bodyMixPreset", "Athletic");
  await expect(page.locator('[data-select-name="bodyMixPreset"] .select-trigger')).toContainText("Athletic");
  await selectOption(page, "maleHairLength", "Random");
  await expect(page.locator('[data-select-name="maleHairLength"] .select-trigger')).toContainText("Random");
  await selectOption(page, "maleHairstyle", "Custom");
  await expect(page.locator('input[name="maleCustomHair"]')).toBeEnabled();
  await selectOption(page, "maleGroomingControl", "Clean-shaven");
  await expect(page.locator('[data-select-name="maleGroomingControl"] .select-trigger')).toContainText("Clean-shaven");
  await selectOption(page, "maleOutfitControl", "Luxury");
  await expect(page.locator('[data-select-name="maleOutfitControl"] .select-trigger')).toContainText("Luxury");

  await page.getByRole("button", { name: "couples", exact: true }).click();
  await expect(page.locator('[data-select-name="maleHairstyle"] .select-trigger')).toBeVisible();
  await expect(page.locator('input[name="maleAge"]')).toHaveAttribute(
    "placeholder",
    "Random / 18 / 18-20 / 21-23 / 25-30 / 30+",
  );
  const couplesHairColorField = page.locator('.field').filter({ has: page.locator('[data-select-name="hairColorControl"]') }).first();
  await expect(couplesHairColorField).toContainText("Allow dyed hair");
  await expect(couplesHairColorField.locator('input[name="allowDyedNaturalHairColors"]')).toBeVisible();
  await selectOption(page, "maleHairstyle", "Textured crop");
  await expect(page.locator('[data-select-name="maleHairstyle"] .select-trigger')).toContainText("Textured crop");
  await selectOption(page, "maleOutfitControl", "Coastal");
  await expect(page.locator('[data-select-name="maleOutfitControl"] .select-trigger')).toContainText("Coastal");
});

test("exact theme shortcut syncs with location strategy", async ({ page }) => {
  await page.goto("/");

  const shortcut = page.locator('input[name="exactThemeShortcut"]');
  const sceneFocusTrigger = page.locator('[data-select-name="sceneFocus"] .select-trigger');
  const womenSceneFamilyTrigger = page.locator('[data-select-name="womenSceneFamily"] .select-trigger');
  const locationStrategyTrigger = page.locator('[data-select-name="locationStrategy"] .select-trigger');

  await expect(shortcut).not.toBeChecked();
  await expect(locationStrategyTrigger).toContainText("Fresh only");
  await expect(sceneFocusTrigger).toBeEnabled();
  await expect(womenSceneFamilyTrigger).toBeEnabled();

  await shortcut.check();
  await expect(shortcut).toBeChecked();
  await expect(locationStrategyTrigger).toContainText("Exact theme");
  await expect(sceneFocusTrigger).toBeDisabled();
  await expect(womenSceneFamilyTrigger).toBeEnabled();

  await shortcut.uncheck();
  await expect(shortcut).not.toBeChecked();
  await expect(locationStrategyTrigger).toContainText("Fresh only");
  await expect(sceneFocusTrigger).toBeEnabled();

  await selectOption(page, "locationStrategy", "Exact theme");
  await expect(shortcut).toBeChecked();
  await expect(sceneFocusTrigger).toBeDisabled();
});

test("race preset quick-picks expose curated exact presets", async ({ page }) => {
  await page.goto("/");

  const racePreset = page.locator('[data-select-name="racePreset"]');
  await racePreset.locator('.select-trigger').click();

  const optionTexts = await racePreset.locator('.select-option span').allTextContents();
  expect(optionTexts).toContain("Japanese");
  expect(optionTexts).toContain("Other");
  expect(optionTexts.indexOf("Japanese")).toBeLessThan(optionTexts.indexOf("Other"));
  expect(optionTexts).toEqual(
    expect.arrayContaining([
      "White American",
      "Ukrainian",
      "Russian",
      "Polish",
      "Italian",
      "Spanish",
      "English",
      "Black American",
      "Black British",
      "Black Nigerian",
      "Mexican Latina",
      "Colombian Latina",
      "Brazilian Latina",
      "Chinese",
      "Thai",
      "Vietnamese",
      "Filipina",
      "Arab",
      "Indian",
    ]),
  );
});
