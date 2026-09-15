import { test, expect, type Page } from "@playwright/test";

/** 只验证界面与传输故障的契约夹具；真实准备和模型跟踪另有实际服务验收。 */
async function fixture(page: Page, dataset = "shapenet_car") {
  const ab = {
    id: "abupt",
    model_id: "abupt",
    name: "AB-UPT",
    structure_version: { id: "default", name: "案例默认" },
    variants: [],
    model: {
      parameters: { dim: 192 },
      sampling: { supernodes: { num_points: 512 } },
      supervision: [
        { name: "pressure", target: "pressure", loss: "mse", weight: 1 },
      ],
    },
    capabilities: {
      losses: { configurable: true },
      sampling: { configurable: true },
    },
  };
  const transolverCaps = {
    losses: {
      configurable: false,
      reason: "参考固定损失",
      terms: [
        {
          name: "surface/pressure",
          target: "surface_pressure",
          loss: "mse",
          weight: 1,
        },
      ],
    },
    sampling: {
      configurable: true,
      constraints: { stride: { allowed: [4], readOnly: true } },
    },
  };
  const surface = {
    parameters: { n_hidden: 256, space_dim: 6, out_dim: 1, slice_num: 64 },
    sampling: { seed: 2, stride: 4, chunk_count: 20, random_stream: "independent" },
  };
  const volume = {
    parameters: { n_hidden: 256, space_dim: 3, out_dim: 3, slice_num: 64 },
    sampling: { seed: 2, stride: 4, chunk_count: 20, random_stream: "independent" },
  };
  const tr = {
    id: "transolver3",
    model_id: "transolver3",
    name: "Transolver-3",
    structure_version: { id: "default", name: "案例默认" },
    variants:
      dataset === "shapenet_car"
        ? [
            { id: "surface", name: "表面" },
            { id: "volume", name: "体场" },
          ]
        : [],
    variant_defaults:
      dataset === "shapenet_car"
        ? {
            surface: {
              id: "transolver3",
              model_id: "transolver3",
              model: surface,
              capabilities: transolverCaps,
            },
            volume: {
              id: "transolver3",
              model_id: "transolver3",
              model: volume,
              capabilities: transolverCaps,
            },
          }
        : {},
    model: surface,
    capabilities: transolverCaps,
  };
  const state: any = {
    revision: "r1",
    values: structuredClone(ab.model),
    current: ab.id,
    variant: undefined,
    options: [ab, tr],
    presets: [],
    saves: [],
    posts: [],
    exports: [],
    conflict: false,
    optionsFailed: false,
  };
  await page.route("**/api/v1/**", async (route) => {
    const req = route.request(),
      url = new URL(req.url());
    if (url.pathname.endsWith("/model-options"))
      return route.fulfill(
        state.optionsFailed
          ? { status: 503, json: { detail: "选项暂不可用" } }
          : {
              json: {
                revision: state.revision,
                current_model_id: state.current,
                current_variant: state.variant,
                current_preset_id: undefined,
                options: state.options,
                presets: state.presets,
                trace_available: true,
              },
            },
      );
    if (url.pathname.endsWith("/model-presets")) {
      const body = req.postDataJSON();
      state.exports.push(body);
      return route.fulfill({ json: { id: "preset-1", name: body.name } });
    }
    if (url.pathname.endsWith("/configuration")) {
      if (req.method() === "PUT") {
        const body = req.postDataJSON();
        state.saves.push(body);
        if (state.conflict)
          return route.fulfill({
            status: 409,
            json: { detail: "configuration_revision_conflict" },
          });
        state.values = body.values;
        state.current = body.target_model || state.current;
        state.variant = body.target_variant;
        state.revision = "r" + (state.saves.length + 1);
        return route.fulfill({
          json: { revision: state.revision, config: { model: state.values } },
        });
      }
      return route.fulfill({
        json: {
          revision: state.revision,
          stage: "model",
          values: state.values,
          capabilities: state.options.find((o: any) => o.id === state.current)
            .capabilities,
        },
      });
    }
    if (url.pathname.endsWith("/stage-inputs"))
      return route.fulfill({
        json: [
          {
            binding: "train.manifest",
            selected: false,
            ref: null,
            compatibility: { status: "invalid", reason: "path_outside_root" },
          },
          {
            binding: "post.checkpoint",
            ref: null,
            compatibility: {
              status: "invalid",
              reason: "binding_file_missing",
            },
          },
        ],
      });
    if (url.pathname.endsWith("/operations")) {
      state.posts.push(req.postDataJSON());
      return route.fulfill({
        json: { status: "succeeded", result: { valid: true } },
      });
    }
    return route.fulfill({ json: [] });
  });
  return state;
}

async function mount(page: Page, task = "fixture") {
  await page.goto("/");
  await page.evaluate(async (task) => {
    const React = (await import("/node_modules/.vite/deps/react.js" as any))
      .default;
    const { createRoot } = (
      await import("/node_modules/.vite/deps/react-dom_client.js" as any)
    ).default;
    const { StageWorkbench } = await import(
      "/src/modules/stages/StageWorkbench.tsx" as any
    );
    document.body.innerHTML = '<div id="fixture"></div>';
    (window as any).modelFixtureRoot = createRoot(
      document.getElementById("fixture"),
    );
    (window as any).modelFixtureRoot.render(
      React.createElement(StageWorkbench, {
        project: "fixture",
        task,
        stage: "model",
      }),
    );
  }, task);
}
async function choose(page: Page, name: string) {
  await page
    .locator(".ant-select")
    .filter({
      has: page.getByRole("combobox", { name: "模型类型", exact: true }),
    })
    .click();
  await page
    .locator(".ant-select-dropdown:visible .ant-select-item-option")
    .filter({ hasText: name })
    .click();
}
function hidden(page: Page) {
  return page
    .locator(".configuration-field")
    .filter({ has: page.locator("label", { hasText: "隐藏层宽度" }) })
    .getByRole("spinbutton");
}

for (const dataset of ["shapenet_car", "nasa_crm"])
  test(
    dataset + " 同数据集切换、编辑保存、刷新与告警分区",
    async ({ page }) => {
      const state = await fixture(page, dataset);
      await mount(page);
      const picker = page.getByRole("combobox", {
        name: "模型类型",
        exact: true,
      });
      await expect(picker).toBeEnabled();
      await page.locator(".ant-select").filter({ has: picker }).click();
      await expect(page.getByRole("option")).toHaveCount(2);
      await page.keyboard.press("Escape");
      await expect(
        page.getByRole("combobox", { name: "结构版本" }),
      ).toBeDisabled();
      await expect(
        page.locator(".model-settings").getByText("path_outside_root"),
      ).toHaveCount(0);
      await expect(
        page.locator(".model-visualization").getByText("path_outside_root"),
      ).toHaveCount(0);
      await expect(page.getByRole("combobox", { name: "train.manifest" })).toHaveCount(
        0,
      );
      await expect(page.getByText("binding_file_missing")).toHaveCount(0);
      await expect(page.locator("summary", { hasText: "权重加载" })).toHaveCount(0);
      await expect(page.getByText("从检查点继续请进入训练运行")).toHaveCount(0);
      await expect(page.locator("summary", { hasText: "模型采样" })).toBeVisible();
      await expect(page.getByText("supernodes / num_points")).toBeVisible();
      await choose(page, "Transolver-3");
      await expect(hidden(page)).toHaveValue("256");
      await expect(page.locator("summary", { hasText: "模型采样" })).toBeVisible();
      await expect(page.getByText("supernodes / num_points")).toHaveCount(0);
      await expect(
        page
          .locator(".configuration-field")
          .filter({ has: page.locator("label", { hasText: "采样步长" }) })
          .getByRole("spinbutton"),
      ).toHaveValue("4");
      await expect(
        page
          .locator(".configuration-field")
          .filter({ has: page.locator("label", { hasText: "查询分块数" }) })
          .getByRole("spinbutton"),
      ).toHaveValue("20");
      await expect(
        page
          .locator(".configuration-field")
          .filter({ has: page.locator("label", { hasText: "切片数量" }) })
          .getByRole("spinbutton"),
      ).toHaveValue("64");
      await expect(page.getByText("surface_pressure")).toBeVisible();
      if (dataset === "shapenet_car") {
        await expect(
          page.getByRole("combobox", { name: "应用变体" }),
        ).toBeVisible();
      } else {
        await expect(
          page.getByRole("combobox", { name: "应用变体" }),
        ).toHaveCount(0);
      }
      await expect(
        page
          .locator(".configuration-field")
          .filter({ has: page.locator("label", { hasText: "特征维度" }) }),
      ).toHaveCount(0);
      await expect(page.getByText(/固定等权 MSE/)).toBeVisible();
      expect(state.saves).toHaveLength(0);
      await hidden(page).fill("128");
      await page.getByRole("button", { name: "保存配置", exact: true }).click();
      await expect(
        page.getByRole("button", { name: "保存配置", exact: true }),
      ).toBeDisabled();
      expect(state.saves[0].target_model).toBe("transolver3");
      if (dataset === "shapenet_car")
        expect(state.saves[0].target_variant).toBe("surface");
      else expect(state.saves[0].target_variant).toBeUndefined();
      expect(state.values.parameters.n_hidden).toBe(128);
      await mount(page);
      await expect(hidden(page)).toHaveValue("128");
      await hidden(page).fill("96");
      await page.getByRole("button", { name: "保存配置", exact: true }).click();
      await expect(
        page.getByRole("button", { name: "保存配置", exact: true }),
      ).toBeDisabled();
      expect(state.saves[1].target_model).toBeUndefined();
      await choose(page, "AB-UPT");
      await expect(page.locator("summary", { hasText: "模型采样" })).toBeVisible();
      await expect(page.getByText("supernodes / num_points")).toBeVisible();
      await choose(page, "Transolver-3");
      await expect(hidden(page)).toHaveValue("256");
      await expect(page.locator("summary", { hasText: "模型采样" })).toBeVisible();
      await expect(page.getByText("supernodes / num_points")).toHaveCount(0);
      await choose(page, "Transolver-3");
      await expect(hidden(page)).toHaveValue("256");
    },
  );

test("ShapeNet 可改选体场变体", async ({ page }) => {
  await fixture(page);
  await mount(page);
  await choose(page, "Transolver-3");
  await page
    .locator(".ant-select")
    .filter({
      has: page.getByRole("combobox", { name: "应用变体", exact: true }),
    })
    .click();
  await page
    .locator(".ant-select-dropdown:visible .ant-select-item-option")
    .filter({ hasText: "体场" })
    .click();
  await expect(
    page
      .locator(".configuration-field")
      .filter({ has: page.locator("label", { hasText: "空间输入维度" }) })
      .getByRole("spinbutton"),
  ).toHaveValue("3");
});

test("导出当前模型配置", async ({ page }) => {
  const state = await fixture(page);
  await mount(page);
  await page.getByLabel("导出模型名称").fill("我的汽车表面");
  await page.getByRole("button", { name: "导出模型", exact: true }).click();
  await expect.poll(() => state.exports.length).toBe(1);
  expect(state.exports[0].name).toBe("我的汽车表面");
});

test("换模保存冲突保留草稿，不启动检查", async ({ page }) => {
  const state = await fixture(page);
  await mount(page);
  await choose(page, "Transolver-3");
  await hidden(page).fill("128");
  state.conflict = true;
  await page
    .getByRole("button", { name: "检查配置与交接", exact: true })
    .click();
  await expect(
    page.getByText("configuration_revision_conflict", { exact: false }),
  ).toBeVisible();
  await expect(hidden(page)).toHaveValue("128");
  expect(state.posts).toHaveLength(0);
  state.conflict = false;
  await page
    .getByRole("button", { name: "检查配置与交接", exact: true })
    .click();
  await expect(
    page.getByText("配置与交接检查通过", { exact: true }),
  ).toBeVisible();
  expect(state.posts).toHaveLength(1);
  expect(state.posts[0].expected_revision).toBe(state.revision);
});

test("选项加载失败可重试，原参数不丢失", async ({ page }) => {
  const state = await fixture(page);
  state.optionsFailed = true;
  await mount(page);
  await expect(
    page.getByText("模型选项加载失败", { exact: true }),
  ).toBeVisible();
  await expect(
    page
      .locator(".configuration-field")
      .filter({ has: page.locator("label", { hasText: "特征维度" }) })
      .getByRole("spinbutton"),
  ).toHaveValue("192");
  state.optionsFailed = false;
  await page.getByRole("button", { name: "重试模型选项" }).click();
  await expect(
    page.getByRole("combobox", { name: "模型类型", exact: true }),
  ).toBeEnabled();
  await choose(page, "Transolver-3");
  await expect(hidden(page)).toHaveValue("256");
});

/** 任务切换时旧选项响应不能覆盖新任务，选择本身使用已加载默认值不发请求。 */
test("迟到模型选项不覆盖新任务", async ({ page }) => {
  const state = await fixture(page);
  let release!: () => void;
  const delayed = new Promise<void>((resolve) => (release = resolve));
  let requested = false;
  await page.route("**/tasks/old/model-options", async (route) => {
    requested = true;
    await delayed;
    await route.fulfill({
      json: {
        current_model_id: "stale",
        options: [
          {
            id: "stale",
            name: "旧任务模型",
            structure_version: { id: "default", name: "案例默认" },
          },
        ],
      },
    });
  });
  await mount(page, "old");
  await expect.poll(() => requested).toBe(true);
  await page.evaluate(async () => {
    const React = (await import("/node_modules/.vite/deps/react.js" as any))
      .default;
    const { StageWorkbench } = await import(
      "/src/modules/stages/StageWorkbench.tsx" as any
    );
    (window as any).modelFixtureRoot.render(
      React.createElement(StageWorkbench, {
        project: "fixture",
        task: "new",
        stage: "model",
      }),
    );
  });
  const picker = page
    .locator(".ant-select")
    .filter({
      has: page.getByRole("combobox", { name: "模型类型", exact: true }),
    });
  await expect(picker).toContainText("AB-UPT");
  const late = page.waitForResponse((r) =>
    r.url().endsWith("/tasks/old/model-options"),
  );
  release();
  await late;
  await choose(page, "Transolver-3");
  await expect(hidden(page)).toHaveValue("256");
  await expect(picker).toContainText("Transolver-3");
  expect(state.saves).toHaveLength(0);
});
