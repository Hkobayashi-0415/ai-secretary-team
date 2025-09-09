import { test, expect } from '@playwright/test';

test('Assistants: Create → Edit → Delete (happy path)', async ({ page }) => {
  test.setTimeout(45_000); // ★ 少し余裕
  await page.goto('/assistants');

  const now = Date.now();
  const name = `E2E-${now}`;
  const desc = 'created by e2e';
  const updatedName = `${name}-updated`;
  const updatedDesc = 'updated by e2e';

  // Create
  await page.getByPlaceholder('例: Demo Assistant').fill(name);
  await page.getByPlaceholder('短い説明').fill(desc);
  await page.locator('select').first().selectOption('gemini-pro');
  await page.getByRole('button', { name: 'Create' }).click();

  // 作成された行（テキスト表示のまま）の確認
  const createdRow = page.locator('li', { hasText: name });
  await expect(createdRow).toBeVisible();

  // Edit
  await createdRow.getByRole('button', { name: 'Edit' }).click();

  // ★ 編集モードではテキストが input に変わるため、
  //   「Save ボタンがある li」を“編集中の行”として取り直す
  const editRow = page.locator('li', { has: page.getByRole('button', { name: 'Save' }) }).first();
  await expect(editRow).toBeVisible();

  // 入力欄に値を入れて保存
  await editRow.locator('input').first().fill(updatedName);
  await editRow.locator('input').nth(1).fill(updatedDesc);
  await editRow.locator('select').first().selectOption('gpt-4');
  await editRow.getByRole('button', { name: 'Save' }).click();

  // 更新結果の確認（表示に戻った行を再確認）
  const updatedRow = page.locator('li', { hasText: updatedName });
  await expect(updatedRow).toBeVisible();
  await expect(updatedRow).toContainText('(gpt-4)');

  // Delete
  page.once('dialog', (d) => d.accept()); // confirm を自動承認
  await updatedRow.getByRole('button', { name: 'Delete' }).click();
  await expect(page.locator('li', { hasText: updatedName })).toHaveCount(0);
});
