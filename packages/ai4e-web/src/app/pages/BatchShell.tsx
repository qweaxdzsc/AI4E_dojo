import { UnavailablePanel } from "../../infrastructure/components/UnavailablePanel";
import "../../modules/reports/report-shell.css";

/** 批量页只保留整合 HTML 两栏外壳，不生成假计划或排队。 */
export function BatchShell() {
  return (
    <div className="cols batch-shell">
      <section className="panel">
        <h2>批量派生计划</h2>
        <p className="muted">先选择 base 和改动，再检查每一行，最后批量创建任务。本轮入口未开放。</p>
        <UnavailablePanel />
      </section>
      <aside className="panel">
        <h3>运行策略</h3>
        <p className="muted">单任务继续使用真实执行门面。不创建假运行记录，也不模拟排队。</p>
      </aside>
    </div>
  );
}
