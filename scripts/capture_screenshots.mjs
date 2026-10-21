import { createRequire } from 'node:module';
import { resolve } from 'node:path';
import { execFileSync } from 'node:child_process';
import { setTimeout as delay } from 'node:timers/promises';

const require = createRequire(resolve(process.cwd(), 'frontend/package.json'));
const { chromium } = require('playwright');
const base = process.env.EVIDENCE_BASE_URL || 'http://127.0.0.1:8000';
const outputDir = resolve(process.cwd(), '..');
const browser = await chromium.launch({
  headless: false,
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--start-maximized', '--window-size=1600,1000']
});
const context = await browser.newContext({ viewport: null });
const page = await context.newPage();
page.setDefaultTimeout(20000);

async function snap(name) {
  await delay(900);
  execFileSync('scrot', ['-o', resolve(outputDir, name)]);
  console.log('Captured ' + name);
}

try {
  // Task 17: homepage before login.
  await page.goto(base + '/', { waitUntil: 'domcontentloaded' });
  await page.locator('.dealer-card').first().waitFor();
  await page.waitForFunction(() => Array.from(document.images).every(img => img.complete), { timeout: 15000 }).catch(() => {});
  await page.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all(Array.from(document.images, img => img.decode().catch(() => {})));
    window.scrollTo(0, 0);
  });
  await page.bringToFront();
  await delay(1800);
  await snap('get_dealers.png');

  // Task 18: homepage after logging in, with username and URL shown.
  await page.goto(base + '/login/', { waitUntil: 'domcontentloaded' });
  await page.locator('input[name="username"]').fill('demo');
  await page.locator('input[name="password"]').fill('DemoPass123!');
  await page.getByRole('button', { name: /log in/i }).click();
  await page.waitForURL(url => url.pathname === '/');
  await page.getByText('Hi, demo').waitFor();
  await snap('get_dealers_loggedin.png');

  // Task 19: filtered homepage.
  await page.locator('#state').selectOption({ label: 'Kansas' });
  await page.getByRole('button', { name: /apply filter/i }).click();
  await page.waitForURL(url => url.searchParams.get('state') === 'Kansas');
  await snap('dealersbystate.png');

  // Task 20: dealer page with persisted sample review.
  await page.goto(base + '/dealer/1/', { waitUntil: 'domcontentloaded' });
  await page.getByText('Fantastic services and a friendly team.').waitFor();
  await snap('dealer_id_reviews.png');

  // Task 21: review filled out before submission.
  await page.goto(base + '/dealer/1/review/', { waitUntil: 'domcontentloaded' });
  const reviewText = 'Fantastic services — the staff explained every option clearly.';
  await page.locator('textarea[name="review"]').fill(reviewText);
  await page.locator('select[name="rating"]').selectOption('5');
  await page.locator('select[name="purchase"]').selectOption('true');
  await page.locator('input[name="purchase_date"]').fill('2025-07-11');
  await page.locator('select[name="car_make"]').selectOption('Toyota');
  await page.locator('select[name="car_model"]').selectOption('Camry');
  await page.locator('input[name="car_year"]').fill('2025');
  await page.locator('textarea[name="review"]').fill(reviewText);
  await snap('dealership_review_submission.png');

  // Task 22: successful review submission, persisted on dealer details.
  await page.getByRole('button', { name: /post review/i }).click();
  await page.waitForURL(url => url.pathname === '/dealer/1/');
  await page.getByText(reviewText).waitFor();
  await snap('added_review.png');

  // Task 12: log into Django admin as root; account is created only in this CI run.
  await page.goto(base + '/admin/', { waitUntil: 'domcontentloaded' });
  await page.locator('#id_username').fill('root');
  await page.locator('#id_password').fill(process.env.CI_ADMIN_PASSWORD);
  await page.locator('input[type="submit"]').click();
  await page.locator('#user-tools').waitFor();
  await page.getByText('root', { exact: false }).waitFor();
  await snap('admin_login.png');

  // Task 13: use Django's actual admin logout flow.
  await page.getByRole('button', { name: /log out/i }).click();
  await page.goto(base + '/admin/', { waitUntil: 'domcontentloaded' });
  await page.locator('#id_username').waitFor();
  await snap('admin_logout.png');
} finally {
  await browser.close();
}
