import { test, expect } from '@playwright/test';

test('Assistants: Create → Edit → Delete (happy path)', async ({ page }) => {
  test.setTimeout(45_000);

  // 1) 一覧ページへ
  await page.goto('/assistants');

  // 一意な値を用意
  const now = Date.now();
  const name = `E2E-${now}`;
  const desc = 'created by e2e';
  const updatedName = `${name}-updated`;
  const updatedDesc = 'updated by e2e';

  // 2) Create
  await page.getByPlaceholder('例: Demo Assistant').fill(name);
  await page.getByPlaceholder('短い説明').fill(desc);
  await page.locator('select').first().selectOption('gemini-pro');
  await page.getByRole('button', { name: 'Create' }).click();

  const createdRow = page.locator('[data-testid^="assistant-row-"]', { hasText: name }).first();
  await expect(createdRow).toBeVisible();

  // 3) Edit
  await createdRow.getByTestId('assistant-edit').click();
  const editRow = page.locator('[data-testid^="assistant-row-"]', { has: page.getByTestId('assistant-save') }).first();
  await expect(editRow).toBeVisible();
  await editRow.getByTestId('assistant-edit-name').fill(updatedName);
  await editRow.getByTestId('assistant-edit-description').fill(updatedDesc);
  await editRow.getByTestId('assistant-edit-model').selectOption('gpt-4');
  await editRow.getByTestId('assistant-save').click();

  const updatedRow = page.locator('[data-testid^="assistant-row-"]', { hasText: updatedName }).first();
  await expect(updatedRow).toBeVisible();
  await expect(updatedRow).toContainText('(gpt-4)');

  // 4) Delete（クリック後に行の消滅を待つ）
  page.once('dialog', d => d.accept());
  await updatedRow.getByTestId('assistant-delete').click();
  await expect(page.locator('[data-testid^="assistant-row-"]', { hasText: updatedName })).toHaveCount(0, { timeout: 15000 });
});
