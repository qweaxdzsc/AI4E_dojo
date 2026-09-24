import { test, expect } from "@playwright/test";

/** 标签缺失保留原因且不能选择，多个有效候选不自动选最新。 */
test("训练候选显示缺标签原因并要求显式选择", async ({ page }) => {
  await page.route("**/api/v1/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path.endsWith("/configuration"))
      return route.fulfill({ json: {
        revision: "r1", stage: "train", values: { max_epochs: 2 },
        capabilities: { training_options: { optimizer: ["adamw"] }, official_combos: { current_model_id: "abupt", options: [] } },
      } });
    if (path.endsWith("/stage-inputs"))
      return route.fulfill({ json: [
        { binding: "inputs.train.preparation", name: "未标注数据", processed_name: "未标注数据", ref: { asset_id: "missing", revision: "1" }, compatibility: { status: "invalid", reason: "缺少类型／用途信息" } },
        ...["较早数据", "较新数据"].map((name, index) => ({
          binding: "inputs.train.preparation", name, processed_name: name,
          ref: { asset_id: `valid-${index}`, revision: "1" }, selected: false,
          compatibility: { status: "unchecked" },
        })),
      ] });
    return route.fulfill({ json: [] });
  });
  await page.goto("/");
  await page.evaluate(async () => {
    const React = (await import("/node_modules/.vite/deps/react.js" as any)).default;
    const { createRoot } = (await import("/node_modules/.vite/deps/react-dom_client.js" as any)).default;
    const { StageWorkbench } = await import("/src/modules/stages/StageWorkbench.tsx" as any);
    document.body.innerHTML = '<div id="fixture"></div>';
    createRoot(document.getElementById("fixture")).render(React.createElement(StageWorkbench, { project: "fixture", task: "fixture", stage: "train" }));
  });
  await expect(page.getByRole("button", { name: "开始训练", exact: true })).toBeDisabled();
  const selector = page.getByRole("combobox", { name: "已准备完成的数据集" });
  await selector.click();
  await expect(page.locator(".ant-select-item-option-disabled").filter({ hasText: "缺少类型／用途信息" })).toHaveCount(1);
  await expect(page.locator(".ant-select-item-option").filter({ hasText: "较早数据" })).toBeVisible();
  await expect(page.locator(".ant-select-item-option").filter({ hasText: "较新数据" })).toBeVisible();
  await expect(page.locator(".ant-select-item-option-selected")).toHaveCount(0);
});
