import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { chromium } from 'playwright';

const baseUrl = process.env.CATPRICE_CAPTURE_BASE_URL ?? 'http://127.0.0.1:4173';
const outputDir = path.resolve(process.cwd(), 'docs', 'assets');
const apiBaseUrl = process.env.CATPRICE_CAPTURE_API_URL ?? 'http://127.0.0.1:8765/api';

async function ensureOutputDir() {
  await mkdir(outputDir, { recursive: true });
}

async function waitForAppReady(page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(800);
}

async function captureViewport(page, filename) {
  await page.screenshot({
    path: path.join(outputDir, filename),
    type: 'png',
  });
}

function logStep(message) {
  console.log(`[capture] ${message}`);
}

async function main() {
  await ensureOutputDir();

  const [pricesResponse, resultResponse] = await Promise.all([
    fetch(`${apiBaseUrl}/prices`),
    fetch(`${apiBaseUrl}/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        catalyst_domain: 'thermal',
        application_family: 'general',
        order_size_tons: 20,
        steps: ['mixer_slurry', 'incipient_wetness', 'dryer_rotary_100_300C'],
        components: [
          { role: 'active_metal', name: 'Ni', wt_pct: 20, price_per_lb: 16.83 },
          { role: 'support', name: 'Al2O3', wt_pct: 80, price_per_lb: 1.1 },
        ],
      }),
    }),
  ]);

  if (!pricesResponse.ok) {
    throw new Error(`Failed to fetch prices for README capture: ${pricesResponse.status}`);
  }
  if (!resultResponse.ok) {
    throw new Error(`Failed to fetch calculation result for README capture: ${resultResponse.status}`);
  }

  const prices = await pricesResponse.json();
  const result = await resultResponse.json();
  const liveFeedCount = prices.filter((row) => row.source_type === 'live').length;
  const indexedFeedCount = prices.filter((row) => row.source_type === 'indexed').length;
  const resultSnapshot = {
    result,
    orderSize: 20,
    steps: ['mixer_slurry', 'incipient_wetness', 'dryer_rotary_100_300C'],
    stepLabels: ['Slurry Mixer', 'Incipient Wetness', 'Rotary Dryer 100-300 C'],
    selectedSupportName: 'Al2O3',
    activeMetalCount: 1,
    liveFeedCount,
    indexedFeedCount,
    nonSupportWt: 20,
    supportWtPct: 80,
    generatedAt: new Date().toISOString(),
    benchmarkCandidate: null,
  };

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1500, height: 1120 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  page.setDefaultTimeout(45000);

  await page.goto(baseUrl, { waitUntil: 'domcontentloaded' });
  await page.evaluate((snapshot) => {
    window.sessionStorage.setItem('catprice_calculator_result', JSON.stringify(snapshot));
  }, resultSnapshot);

  logStep('cost estimate');
  await page.goto(`${baseUrl}/?estimate=composition`, { waitUntil: 'domcontentloaded' });
  await waitForAppReady(page);
  await page.waitForSelector('text=Define the catalyst recipe.');
  await captureViewport(page, 'screen-cost-estimate.png');

  logStep('result');
  await page.goto(`${baseUrl}/calculator/result`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('text=Estimated selling price');
  await waitForAppReady(page);
  await captureViewport(page, 'readme-hero.png');
  await captureViewport(page, 'screen-result.png');

  logStep('live metal prices');
  await page.goto(`${baseUrl}/prices`, { waitUntil: 'domcontentloaded' });
  await waitForAppReady(page);
  await page.waitForSelector('text=Quote Status');
  await captureViewport(page, 'screen-live-metal-prices.png');

  logStep('literature benchmarks');
  await page.goto(`${baseUrl}/benchmarks?reference=detail`, { waitUntil: 'domcontentloaded' });
  await waitForAppReady(page);
  await page.waitForSelector('text=Selected reference route');
  await captureViewport(page, 'screen-literature-benchmarks.png');

  logStep('source library');
  await page.goto(`${baseUrl}/library?library=materials`, { waitUntil: 'domcontentloaded' });
  await waitForAppReady(page);
  await page.waitForSelector('text=Inspect material sources, step rates, and route templates.');
  await captureViewport(page, 'screen-source-library.png');

  logStep('uncertainty range');
  await page.goto(`${baseUrl}/uncertainty`, { waitUntil: 'domcontentloaded' });
  await waitForAppReady(page);
  await page.waitForSelector('text=Stress-test the estimate');
  await page.getByRole('button', { name: /Run range check/ }).click();
  await page.waitForSelector('text=Percentile-weighted spread');
  await waitForAppReady(page);
  await captureViewport(page, 'screen-uncertainty-range.png');

  logStep('done');
  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
