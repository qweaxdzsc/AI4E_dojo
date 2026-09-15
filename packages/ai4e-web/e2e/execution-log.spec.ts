import { test, expect } from "@playwright/test";

function lines(count: number) {
  return Array.from({ length: count }, (_, i) => `[INFO] line ${i + 1}`).join("\n");
}

/** 日志栏只渲染最近 500 行；自动滚动开关与向上展开必须有效。 */
test("长日志默认最近500行，取消跟随后不抢滚动，向上展开更早行", async ({ page }) => {
  page.setDefaultTimeout(15000);
  await page.route("**/api/v1/**", async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname.endsWith("/events")) {
      await route.fulfill({
        status: 200,
        contentType: "text/event-stream",
        body:
          "data: " +
          JSON.stringify({ status: "running", text: lines(600) }) +
          "\n\n",
      });
      return;
    }
    if (url.pathname.endsWith("/log")) {
      await route.fulfill({ json: { text: lines(600) } });
      return;
    }
    await route.fulfill({ json: [] });
  });
  await page.goto("/");
  await page.evaluate(async () => {
    const React = (await import("/node_modules/.vite/deps/react.js" as any)).default;
    const { createRoot } = (await import("/node_modules/.vite/deps/react-dom_client.js" as any))
      .default;
    const { ExecutionLog } = await import("/src/modules/executions/ExecutionLog.tsx" as any);
    document.body.innerHTML = '<div id="fixture"></div>';
    createRoot(document.getElementById("fixture")!).render(
      React.createElement(ExecutionLog, { project: "fixture", run: "run-1" }),
    );
  });
  const { tailStart, olderStart, LOG_WINDOW } = await page.evaluate(async () => {
    const mod = await import("/src/modules/executions/logWindow.ts" as any);
    return { tailStart: mod.tailStart(600), olderStart: mod.olderStart(100), LOG_WINDOW: mod.LOG_WINDOW };
  });
  expect(LOG_WINDOW).toBe(500);
  expect(tailStart).toBe(100);
  expect(olderStart).toBe(0);

  const log = page.getByLabel("运行日志内容");
  await expect.poll(async () => (await log.innerText()).split("\n").at(-1)).toBe("[INFO] line 600");
  await expect.poll(async () => (await log.innerText()).split("\n")).not.toContain("[INFO] line 1");
  await expect.poll(async () => (await log.innerText()).split("\n")[0]).toBe("[INFO] line 101");
  await expect(page.getByLabel("日志窗口提示")).toHaveText("更早 100 行已存储，向上滚动展开");
  await expect(page.getByRole("checkbox", { name: "自动滚动" })).toBeChecked();

  await page.getByRole("checkbox", { name: "自动滚动" }).click();
  await expect(page.getByRole("checkbox", { name: "自动滚动" })).not.toBeChecked();
  const frozen = await log.evaluate((el) => el.scrollTop);
  await page.waitForTimeout(200);
  expect(await log.evaluate((el) => el.scrollTop)).toBe(frozen);

  await log.evaluate((el) => {
    el.scrollTop = 0;
    el.dispatchEvent(new Event("scroll"));
  });
  await expect.poll(async () => (await log.innerText()).split("\n")).toContain("[INFO] line 1");
  await expect(page.getByRole("checkbox", { name: "自动滚动" })).not.toBeChecked();
  await expect(page.getByLabel("日志窗口提示")).toHaveText("下方还有 100 行");

  await page.waitForTimeout(50);
  await log.evaluate((el) => {
    el.scrollTop = el.scrollHeight;
    el.dispatchEvent(new Event("scroll"));
  });
  await expect(page.getByRole("checkbox", { name: "自动滚动" })).toBeChecked();
  await expect.poll(async () => (await log.innerText()).split("\n").at(-1)).toBe("[INFO] line 600");
});

test("提交运行说明只写入一行，不钉在日志底部", async ({ page }) => {
  page.setDefaultTimeout(15000);
  await page.route("**/api/v1/**", async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname.endsWith("/events")) {
      await route.fulfill({
        status: 200,
        contentType: "text/event-stream",
        body:
          "data: " +
          JSON.stringify({ status: "running", text: lines(20) }) +
          "\n\n",
      });
      return;
    }
    await route.fulfill({ json: [] });
  });
  await page.goto("/");
  await page.evaluate(async () => {
    const React = (await import("/node_modules/.vite/deps/react.js" as any)).default;
    const { createRoot } = (await import("/node_modules/.vite/deps/react-dom_client.js" as any))
      .default;
    const { ExecutionLog } = await import("/src/modules/executions/ExecutionLog.tsx" as any);
    document.body.innerHTML = '<div id="fixture"></div>';
    createRoot(document.getElementById("fixture")!).render(
      React.createElement(ExecutionLog, {
        project: "fixture",
        run: "run-1",
        activity: { status: "处理中", text: "[INFO] 已提交运行 abc" },
      }),
    );
  });
  const log = page.getByLabel("运行日志内容");
  await expect(log).toContainText("[INFO] 已提交运行 abc");
  await expect(log).not.toContainText("—— 操作 ——");
  await expect.poll(async () => (await log.innerText()).split("\n").at(-1)).toBe("[INFO] line 20");
  await expect.poll(async () => (await log.innerText()).split("\n")[0]).toBe("[INFO] 已提交运行 abc");
});
