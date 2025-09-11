// frontend/tests/assistants-happy.spec.ts
import { test, expect } from '@playwright/test';

test('Assistants: Create → Edit → Delete (happy path)', async ({ page }) => {
  await page.goto('/assistants');

  // Create: 入力待ち
  await page.getByTestId('assistant-create-name').waitFor({ state: 'visible' });

  const name = `E2E-${Date.now()}`;
  await page.getByTestId('assistant-create-name').fill(name);
  await page.getByTestId('assistant-create-description').fill('e2e desc');
  await page.getByTestId('assistant-create-model').selectOption('gemini-pro');

  // 作成送信とAPI完了待ち（POSTと、その後の一覧GET）
  const waitPost = page.waitForResponse(r => {
    try {
      const u = new URL(r.url());
      return /\/api\/v1\/assistants\/?$/.test(u.pathname) && r.request().method() === 'POST' && r.ok();
    } catch { return false; }
  });
  const waitGetAfterCreate = page.waitForResponse(r => {
    try {
      const u = new URL(r.url());
      return /\/api\/v1\/assistants\/?$/.test(u.pathname) && r.request().method() === 'GET' && r.ok();
    } catch { return false; }
  });

  await page.getByTestId('assistant-create-submit').click();
  const postRes = await waitPost;
  await waitGetAfterCreate;

  // 作成IDを取得して、その行をピンポイントで取る
  const created = await postRes.json();
  const id: string = created.id;
  const row = page.getByTestId(`assistant-row-${id}`);

  await expect(row).toBeVisible();
  await expect(row).toContainText(name);

  // --- Edit ---
  await row.getByTestId('assistant-edit').click();

  // 編集フィールドが出るまで待つ（この待ちが超重要）
  await row.getByTestId('assistant-edit-name').waitFor({ state: 'visible' });

  const edited = `${name}-edited`;
  await row.getByTestId('assistant-edit-name').fill(edited);
  await row.getByTestId('assistant-edit-description').fill('e2e desc edited');
  await row.getByTestId('assistant-edit-model').selectOption('gpt-4');

  // 保存とAPI完了待ち（PUT or PATCH、対象IDに限定）
  const waitUpdate = page.waitForResponse(r => {
    try {
      const u = new URL(r.url());
      return new RegExp(`/api/v1/assistants/${id}/?$`).test(u.pathname)
        && ['PUT', 'PATCH'].includes(r.request().method())
        && r.ok();
    } catch { return false; }
  });

  await row.getByTestId('assistant-save').click();
  await waitUpdate;

  // 表示が更新されたことを確認
  await expect(row).toBeVisible();
  await expect(row).toContainText(edited);
  await expect(row).toContainText('gpt-4');

  // --- Delete ---
  // confirm を自動承認
  page.once('dialog', d => d.accept());

  const waitDelete = page.waitForResponse(r => {
    try {
      const u = new URL(r.url());
      return new RegExp(`/api/v1/assistants/${id}/?$`).test(u.pathname)
        && r.request().method() === 'DELETE'
        && r.ok();
    } catch { return false; }
  });

  await row.getByTestId('assistant-delete').click();
  await waitDelete;

  // 行が消えたことを確認
  await expect(row).toHaveCount(0);
});
