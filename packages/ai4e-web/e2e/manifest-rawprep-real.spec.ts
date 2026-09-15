import { test, expect } from "@playwright/test";
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { resolve } from "node:path";
const api = (process.env.DOJO_API_URL || "http://127.0.0.1:8037") + "/api/v1";
/** 使用真实已绑定样本从首页进入并执行；不拦截请求或伪造数值产物。 */
for (const nasa of [false, true])
  test(`manifest 页面真实执行 ${nasa ? "NASA" : "ShapeNet"}`, async ({
    page,
    request,
  }, info) => {
    test.setTimeout(360000);
    page.setDefaultTimeout(25000);
    const input = JSON.parse(
      readFileSync(
        process.env.DOJO_MANIFEST_REAL_ROOT + "/inputs.json",
        "utf8",
      ),
    );
    const name = "声明驱动浏览器 " + Date.now();
    const project = await (
      await request.post(api + "/projects", { data: { name } })
    ).json();
    const created = await request.post(`${api}/projects/${project.id}/tasks`, {
      data: {
        name: nasa ? "NASA" : "ShapeNet",
        case_id: nasa ? "nasa_crm_abupt" : "shapenet_car_abupt",
      },
    });
    expect(created.ok(), await created.text()).toBeTruthy();
    const task = await created.json(),
      url = `${api}/projects/${project.id}/tasks/${task.id}`;
    const binding = await (await request.get(url + "/dataset")).json();
    const sources = nasa
      ? {
          train_h5: { root: "data1", path: "trainingData_NASA-CRM.h5" },
          test_h5: { root: "data2", path: "testData_NASA-CRM.h5" },
          connectivity_h5: { root: "data2", path: "connectivity_NASA-CRM.h5" },
        }
      : { root: { root: "data0", path: "" } };
    const bound = await request.put(url + "/dataset", {
      data: { expected_revision: binding.revision, sources },
    });
    expect(bound.ok(), await bound.text()).toBeTruthy();
    await page.goto("/projects");
    await page
      .getByRole("textbox", { name: "搜索项目", exact: true })
      .fill(name);
    await page
      .locator(".taskcard")
      .filter({ hasText: name })
      .getByRole("link", { name: "进入项目", exact: true })
      .click();
    await page.getByRole("link", { name: "进入工作台", exact: true }).click();
    await expect(
      page.getByText((nasa ? "surface_cp" : "surface_pressure") + ".pt", {
        exact: true,
      }),
    ).toBeVisible();
    await expect(
      page.getByText("每个输出是一个 .pt；一次只提取一个物理量或坐标。"),
    ).toBeVisible();
    // 样本选择取适配器产生的身份，而非文件树勾选。
    await page
      .getByRole("combobox", { name: "执行范围", exact: true })
      .press("ArrowDown");
    await page
      .locator(".ant-select-item-option")
      .filter({ hasText: "指定样本" })
      .click();
    await expect(page.locator(".ant-select-dropdown:visible")).toHaveCount(0);
    const selected = nasa ? input.nasa_samples : input.car_samples;
    let selectedCount = 0;
    for (const [split, names] of Object.entries(selected) as [
      string,
      string[],
    ][]) {
      const combo = page.getByRole("combobox", {
        name: "执行样本选择",
        exact: true,
      });
      await combo.focus();
      await combo.press("ArrowDown");
      await expect(combo).toBeFocused();
      await combo.fill(names[0]);
      await page
        .locator(".ant-select-item-option")
        .filter({ hasText: names[0] })
        .click({ timeout: 30000 });
      selectedCount++;
      await expect(
        page.getByText(`处理样本：${selectedCount} 个`),
      ).toBeVisible();
      await page.keyboard.press("Escape");
    }
    if (nasa) {
      await page
        .getByRole("button", { name: "删除 surface_area", exact: true })
        .click();
    } else {
      await page.getByRole("checkbox", { name: "体积法向", exact: true }).uncheck();
    }
    await page
      .getByRole("combobox", { name: "统计策略", exact: true })
      .press("ArrowDown");
    await page
      .locator(".ant-select-item-option")
      .filter({ hasText: "不生成统计" })
      .click();
    await page.getByRole("button", { name: "保存配置", exact: true }).click();
    await expect(page.getByText("配置已保存，未创建新版本")).toBeVisible();
    const saved = await (await request.get(url + "/rawprep")).json();
    expect(saved.rawprep.save_fields).not.toContain(
      nasa ? "surface_area" : "volume_normals",
    );
    const responsePromise = page.waitForResponse(
      (r) =>
        r.url().endsWith("/rawprep/execute") && r.request().method() === "POST",
      { timeout: 180000 },
    );
    await page.getByRole("button", { name: "执行", exact: true }).click();
    const response = await responsePromise;
    expect(response.ok(), await response.text()).toBeTruthy();
    const run = await response.json();
    await expect
      .poll(
        async () =>
          (
            await (
              await request.get(`${api}/projects/${project.id}/runs/${run.id}`)
            ).json()
          ).status,
        { timeout: 180000 },
      )
      .toBe("succeeded");
    await page.reload();
    await expect(
      page.getByText((nasa ? "surface_area" : "volume_normals") + ".pt", {
        exact: true,
      }),
    ).toHaveCount(0);
    await page
      .locator(".bound-dataset-files")
      .getByRole("tab", { name: "处理结果", exact: true })
      .click();
    await page
      .getByRole("button", {
        name: "预览 " + (nasa ? "surface_cp.pt" : "surface_pressure.pt"),
        exact: true,
      })
      .click();
    await expect(page.getByRole("dialog")).toBeVisible();
    await expect(
      page.getByRole("dialog").locator("table tbody tr").first(),
    ).toBeVisible({ timeout: 30000 });
    await page.screenshot({
      path: info.outputPath((nasa ? "nasa" : "shapenet") + "-real.png"),
      fullPage: true,
    });
    // 用公开任务 API 设置显式的两样本声明；页面“全部”必须跑声明名单，不看文件树。
    execFileSync(
      "uv",
      [
        "run",
        "--no-sync",
        "python",
        "-c",
        'import sys,json; from pathlib import Path; import ai4e_task as t; p=next(p for p in Path(sys.argv[1]).iterdir() if p.is_dir() and t.open_project(p)["id"]==sys.argv[4]); i=sys.argv[2]; c=t.read_configuration(p,i); t.save_configuration(p,i,{"dataset":json.loads(sys.argv[3])},revision=c["revision"])',
        resolve(process.env.DOJO_MANIFEST_REAL_ROOT!, "browser/projects"),
        task.id,
        JSON.stringify(
          nasa
            ? { samples: selected }
            : { partition: selected, samples: "all" },
        ),
        project.id,
      ],
      {
        cwd: resolve("..", ".."),
        env: {
          ...process.env,
          UV_CACHE_DIR: resolve(
            process.env.DOJO_MANIFEST_REAL_ROOT!,
            "../../.uv-cache",
          ),
        },
      },
    );
    await page.reload();
    await expect(page.getByText("处理样本：2 个")).toBeVisible({
      timeout: 30000,
    });
    const allResponse = page.waitForResponse(
      (r) =>
        r.url().endsWith("/rawprep/execute") && r.request().method() === "POST",
      { timeout: 180000 },
    );
    await page.getByRole("button", { name: "执行", exact: true }).click();
    const allStarted = await allResponse;
    expect(allStarted.ok(), await allStarted.text()).toBeTruthy();
    const allRun = await allStarted.json();
    await expect
      .poll(
        async () =>
          (
            await (
              await request.get(
                `${api}/projects/${project.id}/runs/${allRun.id}`,
              )
            ).json()
          ).status,
        { timeout: 180000 },
      )
      .toBe("succeeded");
    await expect(page.locator(".execution-log .ant-tag")).toHaveText(
      "succeeded",
      { timeout: 30000 },
    );
    writeFileSync(
      info.outputPath("evidence.json"),
      JSON.stringify({
        project: project.id,
        task: task.id,
        run: run.id,
        all_run: allRun.id,
        samples: selected,
        all_samples: 2,
      }),
    );
    await page.screenshot({
      path: info.outputPath("all-complete.png"),
      fullPage: true,
    });
    await info.attach("真实执行身份", {
      body: JSON.stringify({
        project: project.id,
        task: task.id,
        run: run.id,
        samples: 2,
      }),
      contentType: "application/json",
    });
  });

test("完成状态与产物证据", async ({ page }, info) => {
  const directory =
    process.env.DOJO_MANIFEST_BROWSER_EVIDENCE || info.project.outputDir;
  let verified = 0;
  for (const folder of readdirSync(directory)) {
    if (
      !folder.startsWith("manifest-rawprep") ||
      !existsSync(resolve(directory, folder, "evidence.json"))
    )
      continue;
    verified++;
    const record = JSON.parse(
      readFileSync(resolve(directory, folder, "evidence.json"), "utf8"),
    );
    await page.goto(`/projects/${record.project}/tasks/${record.task}/1`);
    await expect(page.locator(".execution-log .ant-tag")).toHaveText(
      "succeeded",
      { timeout: 30000 },
    );
    await expect(
      page.locator(".execution-log").getByText("运行已结束", { exact: true }),
    ).toBeVisible();
    await page.screenshot({
      path: info.outputPath(
        folder.includes("NASA")
          ? "nasa-completed.png"
          : "shapenet-completed.png",
      ),
      fullPage: true,
    });
  }
  expect(verified).toBe(2);
});
