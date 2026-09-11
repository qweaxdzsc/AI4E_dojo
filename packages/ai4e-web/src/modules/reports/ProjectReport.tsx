import { useEffect, useState } from "react";
import { UnavailablePanel } from "../../infrastructure/components/UnavailablePanel";
import { read } from "./api";
import "./report-shell.css";

/** 新整合入口未开放；只读展示既有历史正文，不提供编辑或发布。 */
export function ProjectReport({ project }: { project: string; runs?: any[] }) {
  const [value, setValue] = useState<any>({ title: "", text: "" });
  useEffect(() => {
    read(project)
      .then(setValue)
      .catch(() => setValue({ title: "", text: "" }));
  }, [project]);
  const history = Boolean(value.title || value.text);
  return (
    <div className="cols report-shell">
      <section className="panel">
        <div className="hint">PROJECT REPORT</div>
        <h2>项目报告</h2>
        <UnavailablePanel />
        {history && (
          <details className="history">
            <summary>历史报告记录</summary>
            <p>{value.title || "未命名"}</p>
            <pre>{value.text}</pre>
          </details>
        )}
      </section>
      <aside className="panel">
        <h3>证据资产</h3>
        <p className="muted">本轮不开放编辑、生成、审批或导出。既有记录保留，研究证据继续通过固定运行和比较保存。</p>
      </aside>
    </div>
  );
}
