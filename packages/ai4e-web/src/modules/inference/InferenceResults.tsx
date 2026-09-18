import { Button, Empty, Select, Tabs, Alert } from "antd";
import { useState } from "react";
import { FilePreviewDialog } from "../previews";
import { download } from "./api";
import type { ResultFile, Results } from "./model";
const METRICS: Record<string, string> = {
  mse: "MSE",
  mae: "MAE",
  relative_l2: "Relative L2",
};
/** 仅整理服务的指标叶子，累计量不进入产品表格，不重算数值。 */
function metrics(value: any, prefix = ""): Record<string, number | null> {
  if (!value || typeof value !== "object") return {};
  return Object.fromEntries(
    Object.entries(value).flatMap(([key, v]): [string, number | null][] => {
      const name = prefix
        ? prefix + " / " + (METRICS[key] || key)
        : METRICS[key] || key;
      if (key in METRICS)
        return [[name, typeof v === "number" && Number.isFinite(v) ? v : null]];
      return Object.entries(metrics(v, name));
    }),
  );
}
/** 文件预览共用 Trame；指标仅展示及排序服务返回的值，后处理携带固定来源。 */
export function InferenceResults({
  project,
  task,
  value,
  onOpen,
}: {
  project: string;
  task: string;
  value: Results;
  onOpen?: (run: string, sample: string, index: number) => void;
}) {
  const [preview, setPreview] = useState<ResultFile>(),
    [scope, setScope] = useState("all"),
    [sort, setSort] = useState("");
  const comparison = value.comparison,
    aggregate = scope === "all";
  const comparable = ["comparable", "compatible"].includes(comparison?.status);
  const raw = aggregate
    ? comparison?.items || comparison?.rows || []
    : value.items.filter((r) => JSON.stringify([r.split, r.sample]) === scope);
  const rows = raw.map((r: any) => ({
    ...r,
    display: metrics(r.metrics || r.values),
  }));
  const fields = [
    ...new Set<string>(rows.flatMap((r: any) => Object.keys(r.display))),
  ];
  if (sort && comparable && aggregate)
    rows.sort((a: any, b: any) => {
      const x = a.display[sort],
        y = b.display[sort];
      return x == null ? 1 : y == null ? -1 : x - y;
    });
  const vtkSkipReasons = (vtk: any) => {
    if (!vtk) return [];
    const reasons: string[] = [];
    if (vtk.pointcloud && vtk.pointcloud.exported === false)
      reasons.push(vtk.pointcloud.reason || "该次推理未写出点云");
    if (vtk.mesh && vtk.mesh.exported === false)
      reasons.push(vtk.mesh.reason || "该次推理未写出网格化");
    if (!reasons.length && vtk.exported === false)
      reasons.push(vtk.reason || "该次推理未写出点云或网格化");
    return reasons;
  };
  const missingVtk = value.items.filter((r) => vtkSkipReasons(r.vtk).length > 0);
  const checkpointName = (r: any) =>
    typeof r.checkpoint === "string"
      ? r.checkpoint
      : r.checkpoint?.name ||
        value.items.find((i) => i.run_id === r.run_id)?.checkpoint?.name ||
        r.checkpoint?.id ||
        r.run_id ||
        r.id;
  return (
    <section className="infer-card">
      <Tabs
        items={[
          {
            key: "files",
            label: "结果文件",
            children: !value.items.some((r) => r.files.length) ? (
              <Empty description="尚无已提交结果文件" />
            ) : (
              <div className="infer-table-scroll">
                {missingVtk.length > 0 && (
                  <Alert
                    type="warning"
                    showIcon
                    style={{ marginBottom: 12 }}
                    message="有样本未写出点云或网格化"
                    description={missingVtk
                      .map((r) => `${r.sample_id || r.sample}：${vtkSkipReasons(r.vtk).join("；")}`)
                      .join("；")}
                  />
                )}
                <table className="infer-table">
                  <thead>
                    <tr>
                      <th>检查点 / 样本</th>
                      <th>结果文件</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    {value.items.flatMap((r, i) =>
                      r.files.map((f, j) => (
                        <tr key={r.run_id + ":" + r.sample + ":" + i + ":" + j}>
                          <td>
                            {checkpointName(r)}
                            <small>{r.split} · {r.sample}</small>
                          </td>
                          <td>{f.name || f.path}</td>
                          <td>
                            <Button size="small" onClick={() => setPreview(f)}>
                              预览
                            </Button>{" "}
                            {download(project, task, f) && (
                              <a
                                href={download(project, task, f)}
                                download={f.name}
                              >
                                下载
                              </a>
                            )}{" "}
                            {onOpen && (
                              <Button
                                size="small"
                                onClick={() => onOpen(r.run_id, r.sample, i)}
                              >
                                在后处理中打开
                              </Button>
                            )}
                          </td>
                        </tr>
                      )),
                    )}
                  </tbody>
                </table>
              </div>
            ),
          },
          {
            key: "metrics",
            label: "聚合",
            children: (
              <>
                <div className="infer-tools">
                  <Select
                    aria-label="指标样本范围"
                    value={scope}
                    onChange={(s) => {
                      setScope(s);
                      setSort("");
                    }}
                    options={[
                      { value: "all", label: "历史全元素累计指标（独立口径）" },
                      ...value.items.map(r => ({value:JSON.stringify([r.split,r.sample]),label:`${r.split || "历史分片"} · ${r.sample}`})).filter((v,i,a)=>a.findIndex(w=>w.value===v.value)===i),
                    ]}
                  />
                  <Select
                    aria-label="指标排序"
                    value={sort}
                    disabled={!aggregate || !comparable}
                    onChange={setSort}
                    options={[
                      { value: "", label: "保持检查点顺序" },
                      ...fields.map((f) => ({
                        value: f,
                        label: f + " 从小到大",
                      })),
                    ]}
                  />
                </div>
                <Alert
                  type={comparable ? "info" : "warning"}
                  message={
                    comparison?.reason ||
                    (comparable
                      ? "服务确认比较口径一致。总体指标来自完整结果累计；未定义指标不补零。"
                      : "尚无完整比较结论；部分结果仅供查看。")
                  }
                />
                {rows.length && fields.length ? (
                  <div className="infer-table-scroll">
                    <table className="infer-table">
                      <thead>
                        <tr>
                          <th>检查点</th>
                          {fields.map((f) => (
                            <th key={f}>{f}</th>
                          ))}
                          <th>比较状态</th>
                        </tr>
                      </thead>
                      <tbody>
                        {rows.map((r: any, i: number) => (
                          <tr key={r.run_id || r.id || i}>
                            <td>
                              {checkpointName(r)}
                              <small>{r.run_id}</small>
                            </td>
                            {fields.map((f) => (
                              <td key={f}>
                                {r.display[f] == null
                                  ? "不可计算"
                                  : String(r.display[f])}
                              </td>
                            ))}
                            <td>
                              {aggregate
                                ? r.reason ||
                                  comparison?.reason ||
                                  (comparable ? "可比" : "尚不可比")
                                : "单样本结果"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <Empty
                    description={
                      aggregate
                        ? "尚无可用总体比较；可切换样本查看已完成指标"
                        : "该样本尚无指标"
                    }
                  />
                )}
              </>
            ),
          },
        ]}
      />
      {preview && (
        <FilePreviewDialog
          project={project}
          task={preview.task_id || task}
          file={
            preview.ref ? { name: preview.name, ref: preview.ref } : preview
          }
          onClose={() => setPreview(undefined)}
        />
      )}
    </section>
  );
}
