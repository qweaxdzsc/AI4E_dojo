import { test, expect, type Page } from "@playwright/test";
const cp = (id: string) => ({
  id,
  run_id: "training-" + id,
  name: id + ".pt",
  revision: "hash-" + id,
  epoch: 2,
  size: 4096,
  status: "running",
  compatibility: { status: "compatible" },
  preparation: { asset_id: "prep", revision: "prep-r1" },
});
/** 契约夹具覆盖真实页面和 API adapter，不代表模型或真实数据验收。 */
async function fixture(
  page: Page,
  { empty = false, fail = false, interrupted = false, duplicate = false } = {},
) {
  const submitted: any[] = [];
  let batch: any;
  let posts = 0;
  let cancelled = 0;
  let retry = 0;
  let recovered = 0;
  const result = {
    items: [
      {
        run_id: "run-a",
        checkpoint: cp("best"),
        sample: "car-a",
        files: [
          {
            name: "pressure.vtp",
            root: "task",
            path: "data/run-a/pressure.vtp",
            task_id: "t",
          },
        ],
        metrics: { pressure: { mse: 0.25, mae: 0.5, relative_l2: 0.1 } },
      },
    ],
    comparison: {
      status: "compatible",
      items: [
        {
          checkpoint: cp("best"),
          metrics: { pressure: { mse: 0.25, mae: 0.5, relative_l2: 0.1 } },
        },
      ],
    },
  };
  await page.route("**/api/v1/**", async (route) => {
    const req = route.request(),
      u = new URL(req.url()),
      path = u.pathname;
    let json: any = {};
    if (path === "/api/v1/projects") json = [{ id: "p", name: "项目" }];
    else if (path.endsWith("/tasks/t"))
      json = {
        id: "t",
        name: "任务",
        case_id: "shapenet_car_abupt",
        stage_summary: { train: { status: "succeeded" } },
      };
    else if (path.endsWith("/post/results")) json = {items:[],files:[],batches:[],errors:[]};
    else if (path.endsWith("/post/metrics/catalog")) json = {items:[]};
    else if (path.endsWith("/configuration")) json = {};
    else if (path.endsWith("/runs")) json = [];
    else if (path.endsWith("/tasks")) json = [{ id: "t", name: "任务" }];
    else if (path.endsWith("/inference/checkpoints"))
      json = {
        items: empty
          ? []
          : [
              cp("best"),
              {
                ...cp("latest"),
                ...(duplicate ? { revision: "hash-best" } : {}),
              },
              {
                ...cp("bad"),
                compatibility: {
                  status: "incompatible",
                  reason: "模型结构不匹配",
                },
              },
            ],
        revision: "config-r1",
        device_options: [
          { id: "mps", label: "Apple GPU", busy: true },
          { id: "cpu", label: "CPU", busy: false },
        ],
      };
    else if (path.endsWith("/inference/samples"))
      json = {
        preparation: { asset_id: "prep", revision: "prep-r1" },
        partitions: { test: ["car-a", "car-b"], validation: ["car-c"] },
        fields: [{id:"surface:pressure:scalar",label:"压力",domain:"surface",field:"pressure",component:"scalar",category:"流体",available:true,evaluable:true,default:true}],
        metrics: [{id:"relative_l2",label:"L2 Error",category:"误差指标",formula:"L2",default:true,scope:"field"}],
      };
    else if (path.endsWith("/inference/check")) json = { valid: true };
    else if (path.endsWith("/batches") && req.method() === "POST") {
      posts++;
      submitted.push(req.postDataJSON());
      if (fail && posts === 1) {
        await route.fulfill({
          status: 503,
          json: { detail: "暂时断连，请使用相同请求重试" },
        });
        return;
      }
      batch = {
        id: "batch-1",
        name: "对照批次",
        status: interrupted ? "interrupted" : "partial",
        total: 4,
        completed: 2,
        children: [
          {
            id: "child-a",
            run_id: "run-a",
            checkpoint: cp("best"),
            status: "succeeded",
            progress: { total: 2, completed: 2, operation: "保存" },
          },
          {
            id: "child-b",
            run_id: "run-b",
            checkpoint: cp("latest"),
            status: "failed",
            error: "样本读取失败",
          },
        ],
      };
      json = batch;
    } else if (path.endsWith("/batches"))
      json = { items: batch ? [batch] : [] };
    else if (path.endsWith("/results")) json = result;
    else if (path.endsWith("/cancel")) {
      cancelled++;
      json = {};
    } else if (path.endsWith("/recover")) {
      recovered++;
      batch = { ...batch, status: "running" };
      json = batch;
    } else if (path.endsWith("/retry")) {
      retry++;
      batch = { ...batch, id: "batch-2", status: "pending", completed: 0 };
      json = batch;
    } else if (/\/batches\/[^/]+$/.test(path)) json = batch;
    else if (path.endsWith("/assets") && req.method() === "POST")
      json = { asset_id: "result-file", revision: "fixed-r1" };
    else if (path.endsWith("/visualizations")) json = { items: [] };
    else if (
      path.endsWith("/visualizations/sessions") &&
      req.method() === "POST"
    ) {
      await route.fulfill({
        status: 503,
        json: { detail: "此用例仅验证宿主交接，不启动渲染进程" },
      });
      return;
    } else if (req.method() === "POST")
      throw new Error("Unexpected mutation: " + path);
    await route.fulfill({ json });
  });
  return {
    submitted,
    get posts() {
      return posts;
    },
    get cancelled() {
      return cancelled;
    },
    get retry() {
      return retry;
    },
    get recovered() {
      return recovered;
    },
  };
}
async function choose(page: Page) {
  await page.getByRole("checkbox", { name: "选择检查点 best.pt · training-best" }).check();
  await page.getByRole("checkbox", { name: "选择检查点 latest.pt · training-latest" }).check();
  await page
    .getByRole("checkbox", { name: "选择样本 car-a", exact: true })
    .check();
  await page
    .getByRole("checkbox", { name: "选择样本 car-b", exact: true })
    .check();
}

test("九步稳定导航与旧数字地址；浏览不增加完成状态", async ({ page }) => {
  const state = await fixture(page);
  await page.goto("/projects/p/tasks/t/infer");
  await expect(
    page.getByRole("navigation", { name: "工作台步骤" }).getByRole("link"),
  ).toHaveCount(9);
  await expect(page.locator('[aria-current="step"]')).toHaveAttribute(
    "href",
    "/projects/p/tasks/t/infer",
  );
  await expect(
    page.getByRole("button", { name: "开始计算" }),
  ).toBeDisabled();
  await expect(
    page.getByRole("checkbox", { name: "选择检查点 bad.pt · training-bad" }),
  ).toBeDisabled();
  await page.goto("/projects/p/tasks/t/6");
  await expect(page.locator('[aria-current="step"]')).toHaveAttribute(
    "href",
    "/projects/p/tasks/t/post",
  );
  await expect(
    page.getByRole("button", { name: "运行后处理", exact: true }),
  ).toHaveCount(0);
  await page.goto("/projects/p/tasks/t/7");
  await expect(page.locator('[aria-current="step"]')).toHaveAttribute(
    "href",
    "/projects/p/tasks/t/report",
  );
  expect(state.posts).toBe(0);
  const summary = await page.evaluate(async () => {
    const m = await import("/src/modules/tasks/stages.ts");
    return {
      route: m.resolveStage("6"),
      status: m.stageDisplay(
        { stage_summary: { train: { status: "succeeded" } } },
        6,
      ),
    };
  });
  expect(summary.route).toBe("post");
  expect(summary.status.finished).toBe(false);
});

test("多检查点批次、刷新恢复、固定结果、指标与失败重试取消", async ({
  page,
}) => {
  const state = await fixture(page);
  await page.goto("/projects/p/tasks/t/infer");
  await choose(page);
  await expect(
    page.locator(".infer-budget"),
  ).toContainText("2 个 Checkpoint × 2 个样本");
  await page.getByRole("button", { name: "开始计算" }).click();
  await expect(
    page.getByText("批次已提交，关闭页面不会停止计算"),
  ).toBeVisible();
  expect(state.submitted[0].name).toMatch(/^infer-\d{8}-\d{6}$/);
  expect(state.submitted[0]).toMatchObject({
    expected_revision: "config-r1",
    checkpoints: [
      { id: "best", revision: "hash-best" },
      { id: "latest", revision: "hash-latest" },
    ],
    sample_selection: [{split:"test",sample:"car-a"},{split:"test",sample:"car-b"}],
    device: "cpu",
  });
  await page.locator("#stage-handoff summary").click();
  await expect(page.getByRole("button", { name: "在后处理中打开" })).toBeVisible();
  await page.reload();
  await page.locator("#stage-handoff summary").click();
  await expect(page.getByRole("button", { name: "在后处理中打开" })).toBeVisible();
  expect(state.posts).toBe(1);
  await page.getByRole("tab", { name: "聚合" }).click();
  await expect(page.getByText("0.25", { exact: true })).toBeVisible();
  await page.getByRole("tab", { name: "结果文件" }).click();
  await page.getByRole("button", { name: "在后处理中打开" }).click();
  await expect(page).toHaveURL(
    /\/post\?batch=batch-1&run=run-a&sample=car-a&result=0/,
  );
  expect(state.posts).toBe(1);
  await expect(page.locator(".post-file-location")).toContainText("run-a");
  await page.goto("/projects/p/tasks/t/infer");
  await page.locator(".infer-details").first().locator("summary").click();
  await page.getByRole("button", { name: "重试失败子运行" }).click();
  await expect.poll(() => state.retry).toBe(1);
  await expect(page.getByRole("button", { name: "取消批次" })).toBeEnabled();
  await page.getByRole("button", { name: "取消批次" }).click();
  await expect.poll(() => state.cancelled).toBe(1);
});

test("提交失败保留幂等身份与选择；换分片保留样本", async ({ page }) => {
  const state = await fixture(page, { fail: true });
  await page.goto("/projects/p/tasks/t/infer");
  await choose(page);
  await page.getByRole("button", { name: "开始计算" }).click();
  await expect(page.getByRole("alert")).toContainText("暂时断连");
  await page.getByRole("button", { name: "开始计算" }).click();
  await expect(
    page.getByText("批次已提交，关闭页面不会停止计算"),
  ).toBeVisible();
  expect(state.submitted[0].idempotency_key).toBe(
    state.submitted[1].idempotency_key,
  );
  await page.getByRole("tab", {name:/评价集/}).click();
  await expect(page.getByRole("checkbox",{name:"选择样本 car-c"})).not.toBeChecked();
  await page.getByRole("tab", {name:/测试集/}).click();
  await expect(page.getByRole("checkbox",{name:"选择样本 car-a",exact:true})).toBeChecked();
  await expect(page.getByRole("button",{name:"开始计算"})).toBeEnabled();
});

test("没有检查点时不制造候选、样本和运行", async ({ page }) => {
  const state = await fixture(page, { empty: true });
  await page.goto("/projects/p/tasks/t/infer");
  await expect(
    page.getByText("尚无权重，请先训练"),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "开始计算" }),
  ).toBeDisabled();
  expect(state.posts).toBe(0);
});

test("中断批次显式恢复；重复内容标签不允许提交", async ({ page }) => {
  const state = await fixture(page, { interrupted: true });
  await page.goto("/projects/p/tasks/t/infer");
  await choose(page);
  await page.getByRole("button", { name: "开始计算" }).click();
  await page.locator(".infer-details").first().locator("summary").click();
  await expect(
    page.getByRole("button", { name: "恢复中断批次" }),
  ).toBeEnabled();
  await page.getByRole("button", { name: "恢复中断批次" }).click();
  await expect.poll(() => state.recovered).toBe(1);
  await page.unroute("**/api/v1/**");
  await fixture(page, { duplicate: true });
  await page.goto("/projects/p/tasks/t/infer");
  await choose(page);
  await expect(
    page.getByText("所选检查点含相同内容，请保留一个标签"),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "开始计算" }),
  ).toBeDisabled();
});

test("1440和1920宽度工作区保留九步及可操作选择区", async ({ page }, info) => {
  await fixture(page);
  for (const width of [1440, 1920]) {
    await page.setViewportSize({ width, height: 1100 });
    await page.goto("/projects/p/tasks/t/infer");
    await expect(
      page.getByRole("checkbox", { name: "选择检查点 best.pt · training-best" }),
    ).toBeVisible();
    await page.screenshot({
      path: info.outputPath(`inference-${width}.png`),
      fullPage: true,
    });
    const viewport = await page.locator(".inference-workspace").boundingBox();
    expect(viewport!.x + viewport!.width).toBeLessThanOrEqual(width);
  }
});
