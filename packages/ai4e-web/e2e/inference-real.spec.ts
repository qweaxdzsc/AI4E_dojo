import { test, expect } from "@playwright/test";
/** 主任务提供隔离真实训练数据；不创建演示权重，不改用户训练任务。 */
test("真实批次：固定权重、多样本、下载及后处理 Trame", async ({
  page,
  request,
}, testInfo) => {
  const project = process.env.DOJO_INFER_PROJECT,
    task = process.env.DOJO_INFER_TASK;
  const checkpointIds = (process.env.DOJO_INFER_CHECKPOINTS || "")
      .split(",")
      .filter(Boolean),
    sampleIds = (process.env.DOJO_INFER_SAMPLES || "")
      .split(",")
      .filter(Boolean);
  test.skip(
    !project || !task || checkpointIds.length < 2 || sampleIds.length < 2,
    "需要隔离真实任务、至少两个检查点和两个真实准备样本；跳过不是验收",
  );
  test.setTimeout(1200000);
  await page.addInitScript(() => {
    (window as any).__inferenceTaskUpdates = [];
    window.addEventListener("dojo:task-updated", (event) => {
      (window as any).__inferenceTaskUpdates.push((event as CustomEvent).detail);
    });
  });
  await page.setViewportSize({ width: 1440, height: 1100 });
  const base = `/api/v1/projects/${project}/tasks/${task}/inference`;
  const catalogResponse = await request.get(base + "/checkpoints");
  expect(catalogResponse.ok()).toBeTruthy();
  const catalog = await catalogResponse.json();
  await page.goto(`/projects/${project}/tasks/${task}/infer`);
  for (const id of checkpointIds) {
    const cp = catalog.items.find((c: any) => c.id === id);
    expect(cp, `真实候选 ${id}`).toBeTruthy();
    await page
      .getByRole("checkbox", { name: "选择检查点 " + cp.name + " · " + cp.run_id, exact: true })
      .check();
  }
  for (const id of sampleIds)
    await page
      .getByRole("checkbox", { name: "选择样本 " + id, exact: true })
      .check();
  const submission = page.waitForResponse(
    (r) =>
      r.url().endsWith("/inference/batches") && r.request().method() === "POST",
  );
  await page.getByRole("button", { name: "开始计算" }).click();
  const response = await submission;
  expect(response.ok()).toBeTruthy();
  const submitted = await response.json(),
    id = submitted.id || submitted.batch?.id;
  expect(id).toBeTruthy();
  await page.reload();
  let batch: any;
  await expect
    .poll(
      async () => {
        const r = await request.get(base + "/batches/" + id);
        expect(r.ok()).toBeTruthy();
        batch = await r.json();
        return [
          "succeeded",
          "failed",
          "partial",
          "canceled",
          "interrupted",
        ].includes(batch.status)
          ? batch.status
          : "running";
      },
      { timeout: 1000000, intervals: [3000, 5000, 10000] },
    )
    .toBe("succeeded");
  const resultResponse = await request.get(
    base + "/batches/" + id + "/results",
  );
  expect(resultResponse.ok()).toBeTruthy();
  const results = await resultResponse.json();
  expect(results.items.length).toBeGreaterThanOrEqual(
    checkpointIds.length * sampleIds.length,
  );
  await testInfo.attach("real-batch", {
    body: JSON.stringify({ batch, results }, null, 2),
    contentType: "application/json",
  });
  await page.locator("#stage-handoff summary").click();
  await page.getByRole("button", { name: "在后处理中打开" }).first().waitFor();
  await page.locator(".infer-details").first().locator("summary").click();
  // 内部工作区独立滚动；整页截图不会展开它，须将每一组真实证据滚入视口。
  const batchCard = page.locator("section.infer-card").filter({
    has: page.getByRole("heading", { name: "推理批次", exact: true }),
  });
  await expect(batchCard).toContainText(`样本结果完成 ${checkpointIds.length * sampleIds.length} / ${checkpointIds.length * sampleIds.length}`);
  await expect.poll(() => page.evaluate(({ project, task }) =>
    (window as any).__inferenceTaskUpdates.filter((d: any) =>
      d.project === project && d.task === task).length, { project, task }),
  ).toBeGreaterThan(0);
  await expect(page.locator(".taskheading .statuspill")).not.toHaveText("运行中", { timeout: 15000 });
  await batchCard.evaluate((element) => element.scrollIntoView({ block: "start" }));
  await expect(batchCard.locator("tbody tr").last()).toBeInViewport();
  await page.screenshot({ path: testInfo.outputPath("inference-batch.png") });
  const filesTab = page.getByRole("tab", { name: "结果文件", exact: true });
  await filesTab.evaluate((element) => element.scrollIntoView({ block: "start" }));
  await expect(page.getByRole("button", { name: "在后处理中打开" }).first()).toBeInViewport();
  await page.screenshot({ path: testInfo.outputPath("inference-results.png") });
  await page.getByRole("tab", { name: "指标比较", exact: true }).click();
  const metricsPanel = page.getByRole("tabpanel", { name: "指标比较", exact: true });
  await expect(metricsPanel.locator("tbody tr")).toHaveCount(checkpointIds.length);
  await metricsPanel.evaluate((element) => element.scrollIntoView({ block: "start" }));
  await expect(metricsPanel.locator("tbody tr").last()).toBeInViewport();
  await page.screenshot({ path: testInfo.outputPath("inference-metrics.png") });
  await filesTab.click();
  const download = page
    .getByRole("link", { name: "下载", exact: true })
    .first();
  const target = await download.getAttribute("href");
  expect(target).toBeTruthy();
  const downloaded = await request.get(target!);
  expect(downloaded.ok()).toBeTruthy();
  expect((await downloaded.body()).length).toBeGreaterThan(0);
  await page.getByRole("button", { name: "在后处理中打开" }).first().click();
  await expect(page).toHaveURL(/\/post\?batch=/);
  const meshRow=page.locator('.post-result-files .filerow').filter({has:page.getByRole('button',{name:/\.vtp$/,exact:false})}).first();
  await meshRow.getByRole('button',{name:'可视化',exact:true}).click();
  const embed = page.frameLocator('iframe[title="独立可视化应用"]');
  const trame = embed.frameLocator("iframe").first();
  await expect(
    trame.locator(".phys-tree").getByText("基础显示", { exact: false }).first(),
  ).toBeVisible({ timeout: 120000 });
  await trame.getByRole("button",{name:"适窗",exact:true}).click();
  await page.waitForTimeout(1500);
  await page.screenshot({
    path: testInfo.outputPath("inference-trame.png"),
    fullPage: true,
  });
  await page.getByRole("menuitem", { name: "项目管理", exact: true }).click();
});
