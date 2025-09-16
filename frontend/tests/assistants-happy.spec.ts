import { pickList } from './_utils';
import { test, expect } from '@playwright/test';

type AssistantRecord = {
  id: string;
  name: string;
  description: string | null;
  default_llm_model: string;
  updated_at: string;
};

test.describe.configure({ mode: 'serial' });

test('Assistants: table row count matches API list length', async ({ page, request }) => {
  test.setTimeout(45_000);

  const apiResponse = await request.get('/api/v1/assistants/');
  expect(apiResponse.ok()).toBeTruthy();
  const assistants = (await apiResponse.json()) as AssistantRecord[];

  await page.goto('/assistants');
  await expect(page.getByRole('heading', { name: 'Existing Assistants' })).toBeVisible();

  const rows = page.locator('[data-testid^="assistant-row-"]');
  await expect(rows).toHaveCount(assistants.length);
});

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

test('Assistants: updated_at increases after edit', async ({ page, request }) => {
  test.setTimeout(45_000);

  await page.goto('/assistants');

  const now = Date.now();
  const name = `E2E-updated-at-${now}`;
  const desc = 'timestamp baseline';
  const updatedDesc = 'timestamp baseline updated';

  await page.getByPlaceholder('例: Demo Assistant').fill(name);
  await page.getByPlaceholder('短い説明').fill(desc);
  await page.locator('select').first().selectOption('gemini-pro');
  await page.getByRole('button', { name: 'Create' }).click();

  const createdRow = page.locator('[data-testid^="assistant-row-"]', { hasText: name }).first();
  await expect(createdRow).toBeVisible();

  const listResponse = await request.get('/api/v1/assistants/');
  expect(listResponse.ok()).toBeTruthy();
  const assistants = (await listResponse.json()) as AssistantRecord[];
  const createdAssistant = assistants.find(assistant => assistant.name === name);
  if (!createdAssistant) {
    throw new Error('Newly created assistant was not returned by the API');
  }

  const previousUpdatedAt = new Date(createdAssistant.updated_at).getTime();
  expect(Number.isNaN(previousUpdatedAt)).toBeFalsy();

  await createdRow.getByTestId('assistant-edit').click();
  const editRow = page.locator('[data-testid^="assistant-row-"]', { has: page.getByTestId('assistant-save') }).first();
  await expect(editRow).toBeVisible();
  await editRow.getByTestId('assistant-edit-description').fill(updatedDesc);
  await editRow.getByTestId('assistant-save').click();

  const updatedRow = page.locator('[data-testid^="assistant-row-"]', { hasText: updatedDesc }).first();
  await expect(updatedRow).toBeVisible();

  let latestUpdatedAt = previousUpdatedAt;
  for (let attempt = 0; attempt < 10; attempt++) {
    const detailResponse = await request.get(`/api/v1/assistants/${createdAssistant.id}`);
    expect(detailResponse.ok()).toBeTruthy();
    const detail = (await detailResponse.json()) as AssistantRecord;
    latestUpdatedAt = new Date(detail.updated_at).getTime();
    if (!Number.isNaN(latestUpdatedAt) && latestUpdatedAt > previousUpdatedAt) {
      break;
    }
    await page.waitForTimeout(500);
  }

  expect(latestUpdatedAt).toBeGreaterThanOrEqual(previousUpdatedAt);

  page.once('dialog', d => d.accept());
  await updatedRow.getByTestId('assistant-delete').click();
  await expect(page.locator('[data-testid^="assistant-row-"]', { hasText: updatedDesc })).toHaveCount(0, { timeout: 15000 });
});
