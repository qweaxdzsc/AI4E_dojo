import { Alert, Button, Checkbox, Input, Select, Space } from "antd";
import { useEffect, useState } from "react";
import { FilePreviewDialog } from "../previews";
import { download, list, roots } from "./api";
/** 刷新实际目录，保留有效选择；选择以登记根和相对路径表达。 */
export function FileBrowser({
  project,
  task,
  onSelection,
  compact=false,
  chrome,
}: {
  project: string;
  task?: string;
  onSelection?: (root: string, files: string[]) => void;
  compact?: boolean;
  chrome?: "project";
}) {
  const [root, setRoot] = useState(""),
    [options, setOptions] = useState<any[]>([]),
    [path, setPath] = useState(""),
    [rows, setRows] = useState<any[]>([]),
    [selected, setSelected] = useState<string[]>([]),
    [q, setQ] = useState(""),
    [kind, setKind] = useState("all"),
    [sort, setSort] = useState("name"),
    [error, setError] = useState(""),
    [preview, setPreview] = useState<any>();
  useEffect(() => {
    roots(project, task)
      .then((v) => {
        setOptions(v);
        setRoot(
          onSelection
            ? v.find((x: any) => x.id.startsWith("data"))?.id || v[0]?.id
            : v[0]?.id,
        );
      })
      .catch((e) => setError(e.message));
  }, [project, task]);
  async function refresh() {
    try {
      const v = await list(project, root, path, task);
      setRows(v);
      setError("");
      setSelected((old) =>
        old.filter((x) => {
          const parent = x.includes("/") ? x.slice(0, x.lastIndexOf("/")) : "";
          return parent !== path || v.some((r: any) => r.path === x);
        }),
      );
    } catch (e: any) {
      setError(e.message);
    }
  }
  useEffect(() => {
    if (root) void refresh();
  }, [project, task, root, path]);
  useEffect(() => onSelection?.(root, selected), [root, selected]);
  const shown = rows
    .filter(
      (r) =>
        r.name.toLowerCase().includes(q.toLowerCase()) &&
        (kind === "all" || (kind === "folder" ? r.directory : !r.directory)),
    )
    .sort((a, b) =>
      sort === "time"
        ? b.modified_at.localeCompare(a.modified_at)
        : sort === "size"
          ? b.size - a.size
          : a.name.localeCompare(b.name),
    );
  const filters = (
    <>
      {chrome === "project" ? (
        <>
          <label>
            文件搜索
            <Input.Search
              aria-label="搜索文件"
              placeholder="文件名 / 阶段 / 用途"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </label>
          <label>
            类型
            <Select
              aria-label="筛选文件类型"
              value={kind}
              onChange={setKind}
              options={[
                { value: "all", label: "全部类型" },
                { value: "folder", label: "目录" },
                { value: "file", label: "文件" },
              ]}
            />
          </label>
          <label>
            排序
            <Select
              aria-label="文件排序"
              value={sort}
              onChange={setSort}
              options={[
                { value: "name", label: "文件名 A–Z" },
                { value: "time", label: "更新时间 ↓" },
                { value: "size", label: "大小 ↓" },
              ]}
            />
          </label>
          <Button
            onClick={() => {
              setQ("");
              setKind("all");
              setSort("name");
            }}
          >
            重置筛选
          </Button>
        </>
      ) : (
        <>
          <Input.Search
            placeholder="搜索文件"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <Space>
            <Select
              aria-label="文件筛选"
              value={kind}
              onChange={setKind}
              options={[
                { value: "all", label: "全部类型" },
                { value: "folder", label: "目录" },
                { value: "file", label: "文件" },
              ]}
            />
            <Select
              aria-label="文件排序"
              value={sort}
              onChange={setSort}
              options={[
                { value: "name", label: "名称排序" },
                { value: "time", label: "最新修改" },
                { value: "size", label: "大小排序" },
              ]}
            />
          </Space>
        </>
      )}
    </>
  );
  return (
    <section className={"file-browser"+(compact?" compact":"")+(chrome==="project"?" project-chrome":"")}>
      {chrome!=="project"&&!compact&&<div className="panel-title">
        <b>数据文件</b>
        <Button onClick={refresh}>刷新</Button>
      </div>}
      {compact&&<div className="compact-file-tools"><Button onClick={refresh}>刷新</Button></div>}
      {chrome==="project"&&<Button onClick={refresh}>刷新</Button>}
      <Select
        aria-label="文件范围"
        value={root}
        options={options.map((o) => ({
          value: o.id,
          label: o.id + " · " + o.label,
        }))}
        onChange={(v) => {
          setRoot(v);
          setPath("");
          setSelected([]);
        }}
        style={{ width: chrome==="project" ? 220 : "100%" }}
      />
      {filters}
      <div className="breadcrumb">
        <Button
          disabled={!path}
          onClick={() => setPath(path.split("/").slice(0, -1).join("/"))}
        >
          ↑ 上级
        </Button>
        <span>{path || "根目录"}</span>
      </div>
      {error && <Alert type="error" message={error} />}
      <div className="scroll">
        <table>
          <thead>
            <tr>
              <th>文件名</th>
              {chrome==="project"&&<th>范围</th>}
              {chrome==="project"&&<th>类型</th>}
              {chrome==="project"&&<th>大小</th>}
              <th>更新时间</th>
              {chrome==="project"&&<th>操作</th>}
            </tr>
          </thead>
          <tbody>
            {shown.map((r) => (
              <tr key={r.path}>
                <td>
                  {!r.directory && onSelection && (
                    <Checkbox
                      aria-label={"选择 " + r.name}
                      checked={selected.includes(r.path)}
                      onChange={(e) =>
                        setSelected((old) =>
                          e.target.checked
                            ? [...old, r.path]
                            : old.filter((x) => x !== r.path),
                        )
                      }
                    />
                  )}
                  <button
                    className="link"
                    onClick={() =>
                      r.directory
                        ? setPath(r.path)
                        : setPreview({ root, path: r.path })
                    }
                  >
                    {r.directory ? "▸ " : ""}
                    {r.name}
                  </button>
                  {chrome!=="project"&&!r.directory && (
                    <a
                      aria-label={"下载 " + r.name}
                      href={download(project, root, r.path, task)}
                    >
                      {" "}
                      ↓
                    </a>
                  )}
                </td>
                {chrome==="project"&&<td>{root || "—"}</td>}
                {chrome==="project"&&<td>{r.directory ? "目录" : "文件"}</td>}
                {chrome==="project"&&<td>{r.directory ? "—" : ((r.size||0)/1024/1024).toFixed(2)}</td>}
                <td>
                  {new Date(r.modified_at).toLocaleString("zh-CN", {
                    year: "numeric",
                    month: "2-digit",
                    day: "2-digit",
                    hour: "2-digit",
                    minute: "2-digit",
                    hour12: false,
                  })}
                </td>
                {chrome==="project"&&<td>{r.directory ? "打开" : (<a aria-label={"下载 " + r.name} href={download(project, root, r.path, task)}>下载</a>)}</td>}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {onSelection && (
        <p>
          已选 {selected.length} 个文件{" "}
          <Button size="small" onClick={() => setSelected([])}>
            清空
          </Button>
        </p>
      )}
      {preview && (
        <FilePreviewDialog
          project={project}
          task={task}
          file={preview}
          onClose={() => setPreview(undefined)}
        />
      )}
    </section>
  );
}
