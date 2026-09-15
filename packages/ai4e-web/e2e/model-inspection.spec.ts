import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
/** 从平台选择冻结准备输入，执行正式模型的真实 CPU TorchVista 跟踪。 */
test("正式模型检查操作到沙箱图形渲染", async ({ page }, info) => {
  test.skip(
    Boolean(process.env.DOJO_MODEL_PICKER_EVIDENCE),
    "本次使用新换模真实证据",
  );
  test.setTimeout(300000);
  const e = JSON.parse(
    fs.readFileSync(
      path.resolve(
        "../../.context/mvp/web-integrated-results/shapenet_car_transolver3_surface.json",
      ),
      "utf8",
    ),
  );
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto(`/projects/${e.project}/tasks/${e.task}/3`);
  const generate = page.getByRole("button", { name: "生成真实模型结构", exact: true });
  test.skip(
    !(await generate.isVisible({ timeout: 15000 }).catch(() => false)),
    "需要已有真实任务证据",
  );
  await expect(page.getByRole("combobox", { name: "train.manifest" })).toHaveCount(0);
  await expect(page.getByRole("combobox", { name: "train.preparation" })).toHaveCount(0);
  await expect(page.locator(".execution-log")).toHaveCount(0);
  const submitted = page.waitForResponse(
    (r) =>
      r.url().endsWith("/model-inspections") && r.request().method() === "POST",
  );
  await page
    .getByRole("button", { name: "生成真实模型结构", exact: true })
    .click();
  const operation = await (await submitted).json();
  expect(operation.operation_id).toBeTruthy();
  const iframe = page.locator('iframe[title="真实模型结构"]');
  await expect(iframe).toBeVisible({ timeout: 270000 });
  await expect(iframe).toHaveAttribute("sandbox", "allow-scripts");
  const content = page.frameLocator('iframe[title="真实模型结构"]');
  await expect(content.locator("svg").first()).toBeVisible({ timeout: 30000 });
  await expect
    .poll(() => content.locator('svg g[class^="node_"]').count(), {
      timeout: 30000,
    })
    .toBeGreaterThan(0);
  expect(errors).toEqual([]);
  await page.screenshot({
    path: info.outputPath("real-torchvista.png"),
    fullPage: true,
  });
  await info.attach("operation", {
    body: JSON.stringify(operation, null, 2),
    contentType: "application/json",
  });
});

/** 换模后产生的新准备记录，通过真实服务生成正式目标网络并加载图形。 */
for (const [index, caseName] of [
  "shapenet_car_abupt",
  "nasa_crm_abupt",
].entries())
  test(caseName + " 换模后真实准备到模型结构", async ({ page }, info) => {
    test.skip(
      !process.env.DOJO_MODEL_PICKER_EVIDENCE,
      "需要本次真实换模证据目录",
    );
    test.setTimeout(300000);
    const e = JSON.parse(
      fs.readFileSync(
        path.join(process.env.DOJO_MODEL_PICKER_EVIDENCE!, caseName + ".json"),
        "utf8",
      ),
    );
    const origin =
      "http://127.0.0.1:" +
      (Number(process.env.DOJO_MODEL_PICKER_PORT || 8017) + index);
    await page.setViewportSize({ width: 1920, height: 1080 });
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(origin + `/projects/${e.project}/tasks/${e.task}/3`);
    const picker = page
      .locator(".ant-select")
      .filter({
        has: page.getByRole("combobox", { name: "模型类型", exact: true }),
      });
    await expect(picker).toContainText("Transolver-3", { timeout: 30000 });
    await expect(page.locator(".model-settings .input-bindings")).toHaveCount(
      0,
    );
    await expect(
      page.locator(".model-visualization .input-bindings"),
    ).toHaveCount(0);
    await expect(
      page.getByText("post.checkpoint：已绑定来源不可用"),
    ).toHaveCount(0);
    const submitted = page.waitForResponse(
      (r) =>
        r.url().endsWith("/model-inspections") &&
        r.request().method() === "POST",
    );
    await page
      .getByRole("button", { name: "生成真实模型结构", exact: true })
      .click();
    const response = await submitted;
    expect(response.status()).toBe(200);
    const operation = await response.json();
    const iframe = page.locator('iframe[title="真实模型结构"]');
    await expect(iframe).toBeVisible({ timeout: 270000 });
    await expect(iframe).toHaveAttribute("sandbox", "allow-scripts");
    const content = page.frameLocator('iframe[title="真实模型结构"]');
    await expect(content.locator("svg").first()).toBeVisible({
      timeout: 30000,
    });
    await expect
      .poll(() => content.locator('svg g[class^="node_"]').count())
      .toBeGreaterThan(0);
    expect(errors).toEqual([]);
    await page.screenshot({
      path: info.outputPath("model-picker-real.png"),
      fullPage: true,
    });
    await info.attach("operation", {
      body: JSON.stringify(operation, null, 2),
      contentType: "application/json",
    });
  });
