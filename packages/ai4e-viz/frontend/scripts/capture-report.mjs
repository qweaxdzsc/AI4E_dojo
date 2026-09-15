import { readFile, writeFile } from 'node:fs/promises';
import { chromium } from 'playwright';

const [url, output, format = 'html'] = process.argv.slice(2);
if (!url || !output || !['html', 'pdf'].includes(format)) {
  throw new Error('usage: node scripts/capture-report.mjs <report-url> <output> <html|pdf>');
}

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({
    viewport: { width: 1440, height: 960 },
    deviceScaleFactor: 1,
    reducedMotion: 'reduce',
    locale: 'zh-CN',
    timezoneId: 'Asia/Shanghai',
  });
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 90_000 });
  const reader = page.locator('.report-reader').first();
  await reader.waitFor({ state: 'visible', timeout: 60_000 });
  await page.waitForFunction(() => !document.querySelector('.report-reader .ant-spin-spinning'), undefined, { timeout: 45_000 });
  await page.waitForTimeout(1400);

  // Remote vtk.js/O3DV views cannot remain live in a single-file report.
  // Capture the exact visible pixels and replace only the iframe, preserving
  // every title, conclusion, source label and surrounding report block.
  const frames = reader.locator('iframe');
  for (let index = 0; index < await frames.count(); index += 1) {
    const frame = frames.nth(index);
    if (!await frame.isVisible()) continue;
    const png = await frame.screenshot({ type: 'png', animations: 'disabled' });
    const dataUrl = `data:image/png;base64,${png.toString('base64')}`;
    await frame.evaluate((element, source) => {
      const image = document.createElement('img');
      image.src = source;
      image.alt = element.title || '交互可视化的当前静态画面';
      image.className = 'exported-interactive-snapshot';
      element.replaceWith(image);
    }, dataUrl);
  }

  // Read report images through Playwright's request context. This avoids
  // browser CORS/lazy-loading edge cases while still freezing the exact URLs
  // present in the immutable report snapshot (not alternate placeholder art).
  const reportImages = reader.locator('img');
  for (let index = 0; index < await reportImages.count(); index += 1) {
    const image = reportImages.nth(index);
    const source = await image.getAttribute('src');
    if (!source || source.startsWith('data:')) continue;
    try {
      const absolute = new URL(source, page.url()).href;
      const response = await page.request.get(absolute, { timeout: 30_000 });
      if (!response.ok()) throw new Error(`HTTP ${response.status()}`);
      const mimeType = (response.headers()['content-type'] || 'application/octet-stream').split(';')[0];
      const dataUrl = `data:${mimeType};base64,${(await response.body()).toString('base64')}`;
      await image.evaluate((element, embedded) => {
        element.src = embedded;
        element.removeAttribute('srcset');
        element.loading = 'eager';
      }, dataUrl);
    } catch (error) {
      await image.evaluate((element, message) => {
        element.alt = `${element.alt || '图像'}（资源未能嵌入：${message}）`;
      }, error instanceof Error ? error.message : String(error));
    }
  }

  await page.evaluate(async () => {
    for (const canvas of document.querySelectorAll('.report-reader canvas')) {
      try {
        const image = document.createElement('img');
        image.src = canvas.toDataURL('image/png');
        image.alt = canvas.getAttribute('aria-label') || '图表画面';
        image.className = canvas.className;
        canvas.replaceWith(image);
      } catch { /* SVG renderers remain unchanged; protected canvases keep their fallback text. */ }
    }
    const css = [];
    for (const sheet of document.styleSheets) {
      try { css.push([...sheet.cssRules].map((rule) => rule.cssText).join('\n')); } catch { /* ignore cross-origin sheets */ }
    }
    const report = document.querySelector('.report-reader').cloneNode(true);
    report.querySelectorAll('.page-title-actions, button, .connection-status').forEach((node) => node.remove());
    document.head.innerHTML = '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>报告导出</title>';
    const style = document.createElement('style');
    style.textContent = `${css.join('\n')}
      html,body{margin:0;background:#fff;color:#182230;overflow:visible!important}
      body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans CJK SC",sans-serif}
      .report-reader{width:min(1120px,100%);max-width:1120px!important;margin:0 auto!important;padding:38px 48px 64px!important;overflow:visible!important}
      .exported-interactive-snapshot{display:block;width:100%;height:auto;max-height:640px;object-fit:contain;background:#111827;border-radius:6px}
      .report-chart svg,.report-chart img,.gs-image-gallery img{max-width:100%;height:auto}
      a{color:#1677ff;text-decoration:none}
      @media print{
        .report-reader{width:auto;max-width:none!important;padding:0!important}
        .report-section{break-inside:auto}
        .report-section>header{break-after:avoid-page;page-break-after:avoid;break-inside:avoid-page}
        .report-section>header+.report-block{break-before:avoid-page;page-break-before:avoid}
        .report-block,.report-chart,table,figure{break-inside:avoid-page;page-break-inside:avoid}
      }
      @media(max-width:720px){.report-reader{padding:22px 16px 42px!important}}
    `;
    document.head.append(style);
    document.body.replaceChildren(report);
  });

  await page.emulateMedia({ media: 'print' });
  if (format === 'pdf') {
    await page.pdf({ path: output, format: 'A4', printBackground: true, preferCSSPageSize: false, margin: { top: '14mm', right: '13mm', bottom: '16mm', left: '13mm' } });
  } else {
    const html = await page.content();
    await writeFile(output, `<!doctype html>\n${html.replace(/^<!DOCTYPE html>/i, '')}`, 'utf8');
    // Prove the file no longer references the running application.
    const saved = await readFile(output, 'utf8');
    if (/127\.0\.0\.1|localhost|<script[^>]+src=/i.test(saved)) throw new Error('REPORT_HTML_NOT_SELF_CONTAINED');
  }
} finally {
  await browser.close();
}
