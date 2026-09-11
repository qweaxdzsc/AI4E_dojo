import { ActionButton as Button } from "../../infrastructure/components/ActionButton";
import {Alert, Checkbox, Modal, Select, Space, Table} from "antd";
import { useEffect, useState } from "react";
import { inspectFile } from "../previews";
/** 草稿在弹窗内独立；每个输出对应现有案例中的固定字段，取消不修改工作台。 */
export function ExtractionDialog({
  project,
  task,
  root,
  files,
  source,
  outputs,
  mapping,
  onSave,
  onCancel,
}: {
  project: string;
  task: string;
  root: string;
  files: string[];
  source: string;
  outputs: string[];
  mapping: Record<string, string[]>;
  onSave: (source: string, outputs: string[]) => void;
  onCancel: () => void;
}) {
  const [s, setS] = useState(source),
    [file, setFile] = useState<string>(),
    [fields, setFields] = useState<any[]>([]),
    [draft, setDraft] = useState(outputs),
    [active, setActive] = useState(outputs[0]),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [unchecked, setUnchecked] = useState<string[]>([]);
  const available = Object.keys(mapping).filter((k) => mapping[k][0] === s);
  useEffect(() => {
    setFile(undefined);
    setFields([]);
  }, [s]);
  async function read() {
    if (!file) return;
    setBusy(true);
    try {
      const v = await inspectFile(project, root, file, task);
      setFields(v.fields);
      setError("");
    } catch (e: any) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  const expected = active ? mapping[active]?.[1] : undefined;
  return (
    <Modal
      open
      title="字段提取"
      width={1100}
      okText="保存提取条目"
      onCancel={onCancel}
      onOk={() => {
        if (draft.some((k) => unchecked.includes(k))) {
          setError("请勾选每个输出对应的字段");
          return;
        }
        if (!draft.length) {
          setError("请添加至少一个输出");
          return;
        }
        onSave(s, draft);
      }}
    >
      <div className="extraction-grid">
        <section>
          <h3>输入文件与字段</h3>
          <Space>
            <Select
              aria-label="提取来源"
              disabled
              value={s}
              onChange={(v) => {
                setS(v);
                setDraft([]);
                setActive(undefined as any);
              }}
              options={[
                { value: "surface", label: "表面数据" },
                { value: "volume", label: "体积数据" },
              ]}
            />
            <Select
              style={{ width: 300 }}
              aria-label="读取文件"
              placeholder="从已选择的文件中打开"
              value={file}
              onChange={setFile}
              options={files
                .filter((f) =>
                  f.endsWith(
                    s === "surface" ? "quadpress_smpl.vtk" : "hexvelo_smpl.vtk",
                  ),
                )
                .map((f) => ({ value: f, label: f }))}
            />
            <Button loading={busy} disabled={!file} onClick={read}>
              读取字段
            </Button>
          </Space>
          <Table
            rowKey="id"
            pagination={false}
            dataSource={fields}
            columns={[
              {
                title: "选择",
                render: (_, f) => (
                  <Checkbox
                    aria-label={"字段 " + f.id}
                    disabled={!active || expected !== f.id}
                    checked={
                      expected === f.id &&
                      draft.includes(active) &&
                      !unchecked.includes(active)
                    }
                    onChange={(e) => {
                      setUnchecked(
                        e.target.checked
                          ? unchecked.filter((k) => k !== active)
                          : [...unchecked, active],
                      );
                    }}
                  />
                ),
              },
              { title: "字段", dataIndex: "name" },
              { title: "归属", dataIndex: "association" },
              { title: "形状", render: (_, f) => JSON.stringify(f.shape) },
              { title: "类型", dataIndex: "dtype" },
            ]}
          />
          <p>
            选择右侧输出后，勾选同步到其对应字段。派生场来自处理设置，源文件中不存在该场。
          </p>
        </section>
        <section>
          <h3>输出条目</h3>
          <Select<string>
            aria-label="添加输出"
            placeholder="添加案例支持的输出"
            value={undefined}
            style={{ width: "100%" }}
            onChange={(v) => {
              setDraft([...draft, v]);
              setActive(v);
            }}
            options={available
              .filter((k) => !draft.includes(k))
              .map((k) => ({ value: k, label: k }))}
          />
          {draft.map((k) => (
            <div
              className={"output-row " + (active === k ? "active" : "")}
              key={k}
            >
              <button className="link" onClick={() => setActive(k)}>
                {k}
              </button>
              <Button
                aria-label={"删除输出 " + k}
                size="small"
                onClick={() => {
                  setDraft(draft.filter((x) => x !== k));
                  if (active === k) setActive(undefined as any);
                }}
              >
                删除
              </Button>
            </div>
          ))}
          <Alert
            type="info"
            message="沿用案例输出约定"
            description="当前为具名字段输出。不支持任意重命名、多字段打包或单元场提取；输出目录由任务执行绑定。"
          />
        </section>
      </div>
      {error && <Alert type="error" message={error} />}
    </Modal>
  );
}
