import { Alert, Button, Modal, Select, Space, Spin } from "antd";
import { useEffect, useState } from "react";
import { VisualizationWorkspace } from "../visualization";
import { preview, registerPreviewAsset } from "./api";
import "./preview-dialog.css";
/** 从真实文件读取字段、分页内容和网格；网格弹窗加高可视区并可放大到视口全屏。 */
export function FilePreviewDialog({
  project,
  task,
  file,
  onClose,
}: {
  project: string;
  task?: string;
  file: { root?: string; path?: string; name?: string; ref?: {asset_id?:string;revision?:string} };
  onClose: () => void;
}) {
  const [asset, setAsset] = useState<any>(),
    [info, setInfo] = useState<any>(),
    [data, setData] = useState<any>(),
    [error, setError] = useState(""),
    [field, setField] = useState<string>(),
    [offset, setOffset] = useState(0),
    [busy, setBusy] = useState(false),
    [expanded, setExpanded] = useState(false);
  const title = file.name || file.path?.split("/").pop() || "文件";
  const located = !!(file.root && file.path) || !!file.ref?.asset_id;
  const mesh = info?.kind === "mesh";
  useEffect(() => {
    let live = true;
    setInfo(undefined);
    setAsset(undefined);
    setError("");
    if (!located) {
      setError("缺少受控路径，无法预览");
      return;
    }
    if (file.root && file.path)
      registerPreviewAsset(project,file.root,file.path,task).then(v=>live&&setAsset(v)).catch(e=>live&&setError(e.message));
    else setAsset(file.ref);
    preview(project, file.root, file.path, task, "inspect", undefined, 0, file.ref)
      .then((v) => live && setInfo(v))
      .catch((e) => live && setError(e.message));
    return () => {
      live = false;
    };
  }, [project, task, file.root, file.path, file.ref?.asset_id, file.ref?.revision, located]);
  useEffect(() => {
    setExpanded(false);
  }, [file.root, file.path, file.ref?.asset_id, file.ref?.revision]);
  useEffect(() => {
    if(!info || info.kind === "mesh") return;
    let live = true;
    setBusy(true);
    setData(undefined);
    setError("");
    preview(project, file.root, file.path, task, "preview", field, offset, file.ref)
      .then((v) => live && setData(v))
      .catch((e) => live && setError(e.message))
      .finally(() => live && setBusy(false));
    return () => {
      live = false;
    };
  }, [project, task, file.root, file.path, file.ref?.asset_id, file.ref?.revision, field, offset, info]);
  return (
    <Modal
      title={<span className="file-preview-title"><span className="file-preview-title-text">文件预览 · {title}</span>{mesh && <Button size="small" aria-label={expanded ? "退出全屏幕" : "放大到全屏幕"} onClick={() => setExpanded((value) => !value)}>{expanded ? "退出全屏" : "放大"}</Button>}</span>}
      open
      width={expanded ? "100vw" : mesh ? "96vw" : 1000}
      style={mesh ? { top: expanded ? 0 : 16 } : undefined}
      wrapClassName={`file-preview-dialog${mesh ? " mesh" : ""}${expanded ? " fullscreen" : ""}`}
      styles={mesh ? {body: expanded ? {flex: 1, minHeight: 0, overflow: "hidden", padding: "8px 12px 12px"} : {minHeight: "min(780px, calc(100vh - 100px))", display: "flex", flexDirection: "column", overflow: "hidden"}, content: expanded ? {display: "flex", flexDirection: "column", height: "100vh", borderRadius: 0} : {display: "flex", flexDirection: "column", maxHeight: "calc(100vh - 24px)"}} : undefined}
      onCancel={() => {
        setExpanded(false);
        onClose();
      }}
      footer={null}
    >
      {error && <Alert type="error" message={error} />}
      {info?.kind !== "mesh" && <Space wrap>
        <Select
          aria-label="预览字段"
          placeholder="选择字段 / 成员"
          allowClear
          style={{ minWidth: 220 }}
          value={field}
          onChange={(v) => {
            setField(v);
            setOffset(0);
          }}
          options={(info?.fields || [])
            .filter(
              (f: any) =>
                ["point", "cell"].includes(f.association) ||
                info?.kind === "tensor",
            )
            .map((f: any) => ({
              label: f.association + " · " + f.name,
              value: info.kind === "tensor" ? f.name : f.id,
            }))}
        />
        <Button
          disabled={!offset || busy}
          onClick={() => setOffset(Math.max(0, offset - 100))}
        >
          上一页
        </Button>
        <Button
          disabled={
            busy ||
            data?.kind === "mesh" ||
            (data?.rows?.length ?? data?.lines?.length ?? 0) < 100
          }
          onClick={() => setOffset(offset + 100)}
        >
          下一页
        </Button>
      </Space>}
      {info?.kind === "mesh" ? (
        asset ? <div className="file-preview-mesh" style={expanded ? {height: "100%", minHeight: 0, flex: 1} : {height: "82vh", minHeight: 760}}><VisualizationWorkspace scope={{project_id:project,task_id:task}} sources={[{...asset,name:title}]} mode="preview" onError={e=>setError(e.message)} /></div> : <Spin/>
      ) : <Spin spinning={busy}>
        {data?.kind === "tensor" || data?.columns ? (
          <>
            <p>
              形状 {JSON.stringify(data.shape)} · {data.dtype} · 从第{" "}
              {offset + 1} 行开始
            </p>
            <div className="scroll">
              <table>
                <tbody>
                  {data.rows.map((r: any[], i: number) => (
                    <tr key={i}>
                      <th>{offset + i}</th>
                      {r.map((v, j) => (
                        <td key={j}>{v ?? "非有限值"}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ) : (
          <pre className="preview-text">{data?.lines?.join("\n")}</pre>
        )}
      </Spin>}
    </Modal>
  );
}
