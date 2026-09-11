import { Alert, Button, Modal, Select, Space, Spin } from "antd";
import { useEffect, useState } from "react";
import { VisualizationWorkspace } from "../visualization";
import { preview, registerPreviewAsset } from "./api";
/** 从真实文件读取字段、分页内容和网格；切换文件清除上次结果。 */
export function FilePreviewDialog({
  project,
  task,
  file,
  onClose,
}: {
  project: string;
  task?: string;
  file: { root: string; path: string };
  onClose: () => void;
}) {
  const [asset, setAsset] = useState<any>(),
    [info, setInfo] = useState<any>(),
    [data, setData] = useState<any>(),
    [error, setError] = useState(""),
    [field, setField] = useState<string>(),
    [offset, setOffset] = useState(0),
    [busy, setBusy] = useState(false);
  useEffect(() => {
    let live = true;
    setInfo(undefined);
    setAsset(undefined);
    registerPreviewAsset(project,file.root,file.path,task).then(v=>live&&setAsset(v)).catch(e=>live&&setError(e.message));
    preview(project, file.root, file.path, task)
      .then((v) => live && setInfo(v))
      .catch((e) => live && setError(e.message));
    return () => {
      live = false;
    };
  }, [project, task, file.root, file.path]);
  useEffect(() => {
    let live = true;
    setBusy(true);
    setData(undefined);
    setError("");
    preview(project, file.root, file.path, task, "preview", field, offset)
      .then((v) => live && setData(v))
      .catch((e) => live && setError(e.message))
      .finally(() => live && setBusy(false));
    return () => {
      live = false;
    };
  }, [project, task, file.root, file.path, field, offset]);
  return (
    <Modal
      title={"文件预览 · " + file.path}
      open
      width={1000}
      onCancel={onClose}
      footer={null}
    >
      {error && <Alert type="error" message={error} />}
      <Space wrap>
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
      </Space>
      <Spin spinning={busy}>
        {data?.kind === "mesh" ? (
          asset ? <VisualizationWorkspace scope={{project_id:project,task_id:task}} sources={[asset]} mode="preview" onError={e=>setError(e.message)} /> : <Spin/>
        ) : data?.kind === "tensor" || data?.columns ? (
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
      </Spin>
    </Modal>
  );
}
