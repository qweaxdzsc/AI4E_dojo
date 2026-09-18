import { test, expect } from "@playwright/test";

for (const race of [false, true])
  test(`共享覆盖取消及单次确认 ${race ? "提交时冲突" : "已有名称"}`, async ({
    page,
  }) => {
    page.setDefaultTimeout(15000);
    const submitted: any[] = [];
    let revision = "r1";
    await page.route("**/api/v1/**", async (route) => {
      const req = route.request(),
        url = new URL(req.url());
      let value: any = [];
      if (url.pathname.endsWith("/dataset"))
        value = {
          revision,
          dataset_id: "shapenet_car",
          status: "valid",
          sources: { root: { root: "data0", path: "cars" } },
          binding_schema: { root_key: "root", slots: [] },
          errors: [],
        };
      else if (url.pathname.endsWith("/rawprep")) {
        if (req.method() === "PUT") revision = "r2";
        value = {
          revision,
          processed_name: "shared_cars",
          processed_name_status: {
            status: race ? "available" : "conflict",
            message: "同名项目共享数据已存在，继续会覆盖物理文件。",
          },
          profile: {
            dataset_id: "shapenet_car",
            outputs: [],
            geometry: [],
            filters: [],
            formats: ["pt"],
            vtkhdf: false,
            statistics_modes: ["none"],
            defaults: {},
          },
          rawprep: {
            format: "pt",
            geometry: [],
            filters: {},
            statistics: { mode: "none" },
            sources: [],
          },
        };
      } else if (url.pathname.endsWith("/rawprep/catalog"))
        value = {
          revision: "catalog",
          samples: [{ key: "train::a", partition: "train", sample_id: "a" }],
          fields: [],
          sources: [],
          errors: [],
        };
      else if (url.pathname.endsWith("/rawprep/execute")) {
        submitted.push(req.postDataJSON());
        if (race && !req.postDataJSON().overwrite_processed_name) {
          await route.fulfill({
            status: 409,
            json: {
              detail: "shared_dataset_exists: shared_cars",
              error: {
                code: "shared_dataset_exists",
                message: "同名项目共享数据已存在",
              },
            },
          });
          return;
        }
        value = { id: "running", status: "running" };
      } else if (url.pathname.endsWith("/runs/running"))
        value = { id: "running", status: "running" };
      else if (url.pathname.endsWith("/log")) value = { text: "" };
      await route.fulfill({ json: value });
    });
    await page.goto("/");
    await page.evaluate(async () => {
      const React = (await import("/node_modules/.vite/deps/react.js" as any))
        .default;
      const { createRoot } = (
        await import("/node_modules/.vite/deps/react-dom_client.js" as any)
      ).default;
      const { RawprepWorkbench } = await import(
        "/src/modules/rawprep/RawprepWorkbench.tsx" as any
      );
      document.body.innerHTML = '<div id="shared-test"></div>';
      createRoot(document.getElementById("shared-test")).render(
        React.createElement(RawprepWorkbench, {
          project: "shared-project",
          task: "consumer",
        }),
      );
    });
    await page.getByRole("button", { name: "执行", exact: true }).click();
    const dialog = page.getByRole("dialog");
    await expect(dialog).toContainText("覆盖已有共享数据集");
    await dialog.getByRole("button", { name: /取\s*消/ }).click();
    expect(submitted.filter((x) => x.overwrite_processed_name)).toHaveLength(0);
    if (!race) expect(submitted).toHaveLength(0);
    await page.getByRole("button", { name: "执行", exact: true }).click();
    await dialog.getByRole("button", { name: "覆盖并执行" }).click();
    await expect
      .poll(() => submitted.filter((x) => x.overwrite_processed_name).length)
      .toBe(1);
    expect(submitted.at(-1).overwrite_processed_name).toBe(true);
  });

test("真实服务离线共享可见与文件浏览", async ({ page, request }) => {
  test.skip(
    !process.env.DOJO_SHARED_PROJECT || !process.env.DOJO_SHARED_TASK,
    "需要明确的验收项目与任务",
  );
  const p = process.env.DOJO_SHARED_PROJECT!,
    t = process.env.DOJO_SHARED_TASK!;
  const listed = await request.get("/api/v1/datasets");
  expect(listed.ok()).toBeTruthy();
  expect(
    (await listed.json()).some(
      (x: any) =>
        x.name === "shapenet_car4" &&
        x.shared_asset_id &&
        x.status === "available",
    ),
  ).toBeTruthy();
  await page.goto("/");
  await page.evaluate(
    async ({ p, t }) => {
      const React = (await import("/node_modules/.vite/deps/react.js" as any))
        .default;
      const { createRoot } = (
        await import("/node_modules/.vite/deps/react-dom_client.js" as any)
      ).default;
      const { BoundDatasetFiles } = await import(
        "/src/modules/rawprep/BoundDatasetFiles.tsx" as any
      );
      document.body.innerHTML = '<div id="shared-real"></div>';
      createRoot(document.getElementById("shared-real")).render(
        React.createElement(BoundDatasetFiles, {
          project: p,
          task: t,
          onBinding: () => {},
          onSelection: () => {},
        }),
      );
    },
    { p, t },
  );
  await page.getByRole("tab", { name: "处理结果", exact: true }).click();
  const select = page.getByRole("combobox", {
    name: "平台数据集",
    exact: true,
  });
  await select.click();
  const option = page
    .locator(".ant-select-item-option")
    .filter({ hasText: "shapenet_car4" });
  await expect(option).toHaveCount(1);
  await option.click();
  await expect(
    page.getByRole("button", { name: "train", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "train", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "param1", exact: true }),
  ).toBeVisible();
});
