import { test, expect } from '@playwright/test'

test('conversations -> new -> chat -> send', async ({ page }) => {
  await page.goto('/conversations')

  const cta = page.getByTestId('new-conversation-cta')
  await expect(cta).toBeVisible()
  await cta.click()

  // now at /chat/new -> select assistant and start
  await expect(page).toHaveURL(/\/chat\/new/, { timeout: 15000 })
  const select = page.getByTestId('assistant-select')
  await expect(select).toBeVisible({ timeout: 15000 })
  await select.selectOption({ index: 0 })
  await page.getByTestId('start-chat').click()

  // navigates to /chat/:id
  await expect(page).toHaveURL(/\/chat\/.+/, { timeout: 15000 })

  // send a message
  const input = page.getByPlaceholder(/Type message/i)
  await input.fill('Hello from E2E')
  await page.getByRole('button', { name: /^Send$/ }).click()

  // assert an assistant message bubble appears (WS or optimistic)
  const asstMsg = page.locator('[data-testid="assistant-msg"]').first()
  await expect(asstMsg.first()).toBeVisible({ timeout: 15000 })
})
