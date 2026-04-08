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
  await page.waitForLoadState('networkidle', { timeout: 3000 }).catch(() => {});
  await page.waitForTimeout(800);
}

async function captureClip(page, clip, filename) {
  await page.screenshot({
    path: path.join(outputDir, filename),
    type: 'png',
    clip: {
      x: Math.max(0, Math.floor(clip.x)),
      y: Math.max(0, Math.floor(clip.y)),
      width: Math.ceil(clip.width),
      height: Math.ceil(clip.height),
    },
  });
}

function logStep(message) {
  console.log(`[capture] ${message}`);
}

async function navigateWithinApp(page, route) {
  await page.evaluate((nextRoute) => {
    window.history.pushState({}, '', nextRoute);
    window.dispatchEvent(new PopStateEvent('popstate'));
  }, route);
}

async function captureSectionByText(page, text, filename) {
  const clip = await page.evaluate((needle) => {
    const normalizedNeedle = needle.toLowerCase();
    const section = [...document.querySelectorAll('section')].find((node) =>
      node.innerText.toLowerCase().includes(normalizedNeedle),
    );
    if (!section) return null;
    const rect = section.getBoundingClientRect();
    return {
      x: rect.left + window.scrollX,
      y: rect.top + window.scrollY,
      width: rect.width,
      height: rect.height,
    };
  }, text);
  if (!clip) {
    throw new Error(`Failed to find section containing "${text}"`);
  }
  await captureClip(page, clip, filename);
}

async function captureSelectorBox(page, selector, filename) {
  const clip = await page.evaluate((query) => {
    const node = document.querySelector(query);
    if (!node) return null;
    const rect = node.getBoundingClientRect();
    return {
      x: rect.left + window.scrollX,
      y: rect.top + window.scrollY,
      width: rect.width,
      height: rect.height,
    };
  }, selector);
  if (!clip) {
    throw new Error(`Failed to find selector "${selector}"`);
  }
  await captureClip(page, clip, filename);
}

async function captureSmallestBoxByText(page, text, filename) {
  const handle = await page.evaluateHandle((needle) => {
    const normalizedNeedle = needle.toLowerCase();
    const candidates = [...document.querySelectorAll('section, div')]
      .filter((node) => node.innerText.toLowerCase().includes(normalizedNeedle))
      .filter((node) => {
        const rect = node.getBoundingClientRect();
        return rect.width >= 260 && rect.height >= 140;
      });

    if (!candidates.length) return null;
    candidates.sort((left, right) => {
      const leftRect = left.getBoundingClientRect();
      const rightRect = right.getBoundingClientRect();
      return leftRect.width * leftRect.height - rightRect.width * rightRect.height;
    });
    return candidates[0];
  }, text);
  const element = handle.asElement();
  if (!element) {
    await handle.dispose();
    throw new Error(`Failed to find focused block containing "${text}"`);
  }
  await element.screenshot({
    path: path.join(outputDir, filename),
    type: 'png',
  });
  await handle.dispose();
}

async function preparePage(context, draftSnapshot, resultSnapshot, route = '/') {
  const page = await context.newPage();
  page.setDefaultTimeout(45000);
  await page.addInitScript(({ draft, snapshot }) => {
    const apply = () => {
      window.sessionStorage.setItem('catprice_calculator_draft', JSON.stringify(draft));
      window.sessionStorage.setItem('catprice_calculator_result', JSON.stringify(snapshot));
    };
    apply();
    const startedAt = Date.now();
    const timer = window.setInterval(() => {
      apply();
      if (Date.now() - startedAt > 4000) {
        window.clearInterval(timer);
      }
    }, 50);
  }, { draft: draftSnapshot, snapshot: resultSnapshot });
  await page.goto(baseUrl, { waitUntil: 'domcontentloaded' });
  if (route !== '/') {
    await navigateWithinApp(page, route);
  }
  await waitForAppReady(page);
  return page;
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
  const draftSnapshot = {
    rows: [
      {
        id: 'draft-active-ni',
        role: 'active_metal',
        name: 'Ni',
        wt_pct: 20,
        price_per_lb: 16.83,
        source_type: 'manual',
        source: 'Manual input',
      },
      {
        id: 'draft-support-alumina',
        role: 'support',
        name: 'Al2O3',
        wt_pct: 80,
        price_per_lb: 1.1,
        source_type: 'manual',
        source: 'Manual input',
      },
    ],
    steps: ['mixer_slurry', 'incipient_wetness', 'dryer_rotary_100_300C'],
    catalystDomain: 'thermal',
    applicationFamily: 'general',
    orderSize: 20,
    pricesUpdatedAt: new Date().toISOString(),
    includeSpentValue: false,
    reactorType: 'fixed',
    catalystBulkDensity: 50,
    electrocatalystConfig: null,
    benchmarkCandidate: null,
  };
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
  await context.route('**/api/**', async (route) => {
    const requestUrl = new URL(route.request().url());
    const nextUrl = `${apiBaseUrl}${requestUrl.pathname.replace(/^\/api/, '')}${requestUrl.search}`;
    const response = await route.fetch({ url: nextUrl });
    await route.fulfill({ response });
  });

  logStep('cost estimate');
  {
    const page = await preparePage(context, draftSnapshot, resultSnapshot, '/?estimate=composition');
    await page.waitForSelector('text=Define the catalyst recipe.');
    await captureSectionByText(page, 'Define the catalyst recipe.', 'screen-cost-estimate.png');
    await page.close();
  }

  logStep('result');
  {
    const page = await preparePage(context, draftSnapshot, resultSnapshot, '/calculator/result?result=summary');
    await page.waitForTimeout(1200);
    await captureSectionByText(page, 'Estimated selling price', 'readme-hero.png');
    await page.close();
  }
  {
    const page = await preparePage(context, draftSnapshot, resultSnapshot, '/calculator/result?result=manufacturing');
    await page.waitForTimeout(1200);
    await captureSmallestBoxByText(page, 'Materials versus processing', 'screen-result.png');
    await page.close();
  }

  logStep('live metal prices');
  {
    const page = await preparePage(context, draftSnapshot, resultSnapshot, '/prices?feed=history');
    await page.waitForSelector('text=Selected Metal');
    await captureSectionByText(page, 'Selected Metal', 'screen-live-metal-prices.png');
    await page.close();
  }

  logStep('literature benchmarks');
  {
    const page = await preparePage(context, draftSnapshot, resultSnapshot, '/benchmarks?reference=routes');
    await page.waitForTimeout(1500);
    await captureSectionByText(page, 'How do these routes compare right now?', 'screen-literature-benchmarks.png');
    await page.close();
  }

  logStep('source library');
  {
    const page = await preparePage(context, draftSnapshot, resultSnapshot, '/library?library=materials');
    await page.waitForSelector('text=Inspect material sources, step rates, and route templates.');
    await captureSelectorBox(page, '.cp-split-workspace > div:first-child', 'screen-source-library.png');
    await page.close();
  }

  logStep('estimate range');
  {
    const page = await preparePage(context, draftSnapshot, resultSnapshot, '/uncertainty');
    await page.waitForSelector('text=Read the uncertainty around the same estimate case.');
    await page.getByRole('button', { name: /Run estimate range/ }).click();
    await page.waitForSelector('text=Percentile-weighted price spread');
    await waitForAppReady(page);
    await captureSectionByText(page, 'Percentile-weighted price spread', 'screen-estimate-range.png');
    await page.close();
  }

  logStep('done');
  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
