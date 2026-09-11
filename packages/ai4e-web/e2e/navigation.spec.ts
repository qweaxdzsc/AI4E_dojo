import { test, expect } from "@playwright/test";
test("六个项目页签和八个工作台阶段", async ({ page, request }) => {
  const p = (
    await (
      await request.post((process.env.DOJO_API_URL || "http://127.0.0.1:8000") + "/api/v1/projects", {
        data: { name: "导航验收" },
      })
    ).json()
  ).id;
  const t = (
    await (
      await request.post(`${process.env.DOJO_API_URL || "http://127.0.0.1:8000"}/api/v1/projects/${p}/tasks`, {
        data: { name: "nav" },
      })
    ).json()
  ).id;
  try {
  await page.goto(`/projects/${p}/tasks`);
  await expect(page.getByRole("tab")).toHaveCount(6);
  for (const tab of ["lineage", "compare", "report", "files", "batch"]) {
    await page.goto(`/projects/${p}/${tab}`);
    await expect(page.getByRole("tab")).toHaveCount(6);
  }
  for (let i = 0; i < 8; i++) {
    await page.goto(`/projects/${p}/tasks/${t}/${i}`);
    await expect(page.locator(".workbench-steps .topstep")).toHaveCount(8);
    if (i === 0 || i === 7) {
      await expect(page.getByText(/未开放/).first()).toBeVisible();
      await expect(
        page.getByRole("button", { name: "开始处理", exact: true }),
      ).toHaveCount(0);
    }
  }
  await page.goto("/projects");
  await expect(page.getByRole("menuitem")).toHaveCount(2);
  } finally {
    await request.patch(`${process.env.DOJO_API_URL || "http://127.0.0.1:8000"}/api/v1/projects/${p}`, {data: {archived: true}});
  }
});
