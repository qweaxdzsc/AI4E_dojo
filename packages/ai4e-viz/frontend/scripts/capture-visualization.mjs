import { chromium } from 'playwright';

const [url, output, widthRaw = '960', heightRaw = '620'] = process.argv.slice(2);
if (!url || !output) {
  throw new Error('usage: node scripts/capture-visualization.mjs <url> <output.png> [width] [height]');
}

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({
    viewport: { width: Number(widthRaw), height: Number(heightRaw) },
    deviceScaleFactor: 1,
    reducedMotion: 'reduce',
    locale: 'zh-CN',
    timezoneId: 'Asia/Shanghai',
  });
  // O3DV streams a large GLB through an iframe. Waiting for networkidle is
  // incorrect here: the viewer can keep requests/connections alive after the
  // document is ready, which made otherwise healthy exports time out.
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60_000 });
  const evidence = page.locator('.evidence-canvas').first();
  await evidence.waitFor({ state: 'visible', timeout: 45_000 });
  const o3dvIframe = evidence.locator('iframe[data-component="o3dv-viewer-iframe"]');
  if (await o3dvIframe.count()) {
    const handle = await o3dvIframe.elementHandle();
    const frame = await handle?.contentFrame();
    if (!frame) throw new Error('O3DV_FRAME_UNAVAILABLE: viewer iframe has no content frame');
    await frame.locator('#viewer canvas').waitFor({ state: 'visible', timeout: 60_000 });
    // embed.html hides #overlay only from onModelLoaded, so this proves the
    // captured pixels belong to the requested GLB and configured O3DV camera.
    await frame.locator('#overlay').waitFor({ state: 'hidden', timeout: 60_000 });
  } else {
    await page.waitForFunction(() => {
      const root = document.querySelector('.evidence-canvas');
      return Boolean(root?.querySelector('svg, canvas, perspective-viewer, .plot-container, .react-flow__viewport, .scalar-evidence, article, img, video'));
    }, undefined, { timeout: 45_000 });
  }
  await page.waitForTimeout(900);
  await evidence.screenshot({ path: output, animations: 'disabled' });
} finally {
  await browser.close();
}
