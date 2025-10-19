import { test, expect } from '@playwright/test'

test('conversations -> new -> chat -> send', async ({ page }) => {
  await page.goto('/conversations')

  // assistant select may or may not exist yet (rendered after load)
  const newBtn = page.getByRole('button', { name: /New Conversation/i })
  await expect(newBtn).toBeVisible()
  await newBtn.click()

  // navigates to /chat/:id
  await expect(page).toHaveURL(/\/chat\/.+/)

  // send a message
  const input = page.getByPlaceholder(/Type message/i)
  await input.fill('Hello from E2E')
  await page.getByRole('button', { name: /^Send$/ }).click()

  // expect assistant stream result to include 'You said'
  await expect(page.getByText('You said', { exact: false })).toBeVisible()
})

