import { ActionButton as Button } from "../../infrastructure/components/ActionButton";
import { Alert, Modal, Select, Space, Table } from "antd";
import { useEffect, useMemo, useState } from "react";
import { inspectFile } from "../previews";
import { sourceFiles } from "./api";

export type FieldChoice = { name: string; source_field: string; components: number };

function fieldSource(path: string) {
  return /\.(vtk|vtu|vtp|vtm|vti|vts|vtr|hdf5|h5|pt|pth|npy|npz|zarr)$/i.test(
    path.split("/").pop() || path,
  );
}

function fileName(path: string) {
  return (path.split("::").pop() || path).split("/").pop() || path;
}

function isAbsolute(path: string) {
  return path.startsWith("/") || /^[A-Za-z]:[\\/]/.test(path);
}

function listingRef(path: string, fallbackRoot: string) {
  const split = path.indexOf("::");
  return {
    root: split < 0 ? fallbackRoot : path.slice(0, split),
    relative: split < 0 ? path : path.slice(split + 2),
  };
}

function parentDir(path: string) {
  const parts = path.split("/").filter(Boolean);
  parts.pop();
  return parts.join("/");
}

function mergeFiles(paths: string[]) {
  const byName = new Map<string, string>();
  for (const path of paths.filter((item) => item && fieldSource(item))) {
    const name = fileName(path).toLowerCase();
    const previous = byName.get(name);
    if (!previous || (path.includes("/") && !previous.includes("/")))
      byName.set(name, path);
  }
  return [...byName.values()];
}

function identity(field: any) {
  return field.field_id || field.id || `${field.association}/${field.name}`;
}

function kind(field: any) {
  return /coord|points?$|position/i.test(field.name || "") ? "坐标" : "物理量";
}

function outputOf(profile: any, entry?: FieldChoice) {
  return (profile?.outputs || []).find(
    (item: any) =>
      item.name === entry?.name ||
      item.name === entry?.source_field ||
      item.source_field === entry?.source_field,
  );
}

function representativeSample(catalog: any) {
  return (
    catalog?.samples?.find((item: any) =>
      catalog?.inspection?.checked_samples?.includes(item.key),
    ) || catalog?.samples?.[0]
  );
}

/** 只列已检查代表样本的 VTK 目录；889 份汽车样本不能逐个打开。 */
function sourceFolders(catalog: any, basePath: string) {
  const sample = representativeSample(catalog);
  const sampleId = typeof sample?.sample_id === "string" ? sample.sample_id : "";
  const folders = new Set<string>();
  for (const source of catalog?.sources || []) {
    const ref = source.relative_path || "";
    if (
      sampleId &&
      !ref.includes(sampleId) &&
      !String(source.source_id || "").includes(sampleId)
    )
      continue;
    if (!ref.includes("::")) continue;
    const { root, relative } = listingRef(ref, "");
    if (!relative || isAbsolute(relative)) continue;
    const folder = parentDir(relative);
    if (folder) folders.add(`${root}::${folder}`);
  }
  if (folders.size) return [...folders];
  if (sampleId && /[\\/]/.test(sampleId) && !isAbsolute(sampleId)) {
    folders.add([basePath, sampleId].filter(Boolean).join("/"));
  }
  return [...folders];
}

function declaredPaths(profile: any, catalog: any, folders: string[]) {
  const folder = folders[0] || "";
  const { root, relative } = listingRef(folder, "");
  const sample = representativeSample(catalog);
  const sampleId = typeof sample?.sample_id === "string" ? sample.sample_id : "";
  return [
    ...Object.values(profile?.source_files || {}),
    ...(profile?.outputs || []).map((item: any) => item.filename),
    ...(catalog?.sources || [])
      .filter(
        (item: any) =>
          !sampleId ||
          String(item.relative_path || "").includes(sampleId) ||
          String(item.source_id || "").includes(sampleId),
      )
      .flatMap((item: any) => [item.relative_path, item.path]),
  ]
    .filter(Boolean)
    .map((name) => {
      const value = String(name);
      if (value.includes("/") || value.includes("::") || !relative) return value;
      const joined = `${relative}/${value}`;
      return root ? `${root}::${joined}` : joined;
    });
}

function declaredFields(output: any, catalog: any, entry?: FieldChoice) {
  if (!output && !entry) return [];
  const raw = output?.raw_field;
  const fromCatalog = (catalog?.fields || []).filter(
    (field: any) =>
      field.field_id === raw ||
      field.semantic_key === output?.domain ||
      (output?.domain && String(field.field_id || "").startsWith(output.domain + "/")),
  );
  if (fromCatalog.length) return fromCatalog;
  return [
    {
      field_id: raw || entry?.source_field || output?.name,
      name: output?.label || entry?.name || output?.name,
      association: output?.association || "",
      components: output?.components || entry?.components || 1,
      shape: undefined,
    },
  ];
}

function matchField(fields: any[], output: any, entry?: FieldChoice) {
  const raw = output?.raw_field;
  const rawName = raw ? String(raw).split("/").pop() : "";
  return (
    fields.find((field) => identity(field) === raw) ||
    fields.find((field) => field.field_id === entry?.source_field) ||
    fields.find((field) => field.name === rawName) ||
    fields.find((field) => field.name === entry?.name || field.name === output?.name) ||
    (/position|coord/i.test(entry?.name || output?.name || "")
      ? fields.find((field) => /points?$|coord|position/i.test(field.name || ""))
      : undefined)
  );
}

function preferredFile(listed: string[], output: any, profile: any, catalog: any) {
  const declared =
    output?.filename || (output?.domain && profile?.source_files?.[output.domain]);
  if (declared) {
    const found = listed.find((path) => fileName(path) === declared);
    if (found) return found;
  }
  const source = (catalog?.sources || []).find(
    (item: any) =>
      item.exists !== false &&
      (String(item.source_id || "").endsWith("/" + output?.domain) ||
        fileName(item.relative_path || item.path || "") === declared),
  );
  if (source?.relative_path || source?.path) {
    const path = source.relative_path || source.path;
    const name = fileName(path);
    return listed.find((item) => item === path || fileName(item) === name) || path;
  }
  return listed[0];
}

/** 一次只勾选一个物理量或坐标，固定保存为一个 .pt。 */
export function FieldExtractionEditor({
  project,
  task,
  root,
  basePath = "",
  files,
  catalog,
  catalogBusy,
  profile,
  entry,
  onSave,
  onCancel,
}: {
  project: string;
  task: string;
  root: string;
  basePath?: string;
  files: string[];
  catalog?: any;
  catalogBusy?: boolean;
  profile?: any;
  entry?: FieldChoice;
  onSave: (v: FieldChoice) => void;
  onCancel: () => void;
}) {
  const output = outputOf(profile, entry);
  const folders = useMemo(
    () => sourceFolders(catalog, basePath),
    [catalog, basePath],
  );
  const declared = useMemo(
    () => declaredPaths(profile, catalog, folders),
    [profile, catalog, folders],
  );
  const [discovered, setDiscovered] = useState<string[]>([]);
  const listed = useMemo(
    () => mergeFiles([...discovered, ...files, ...declared]),
    [discovered, files, declared],
  );
  const [file, setFile] = useState<string>();
  const [fields, setFields] = useState<any[]>([]);
  const [selected, setSelected] = useState<string>();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [loadingFiles, setLoadingFiles] = useState(true);
  function asChoice(field: any): FieldChoice {
    const mapped = (profile?.outputs || []).find(
      (item: any) =>
        item.raw_field === field.field_id ||
        item.raw_field === identity(field) ||
        item.name === field.name ||
        (item.raw_field && String(item.raw_field).split("/").pop() === field.name),
    );
    if (mapped)
      return {
        name: mapped.name,
        source_field: mapped.name,
        components: mapped.components || field.components || 1,
      };
    return {
      name: (field.field_id || identity(field)).replaceAll("/", "_"),
      source_field: field.field_id || identity(field),
      components: field.components || 1,
    };
  }
  function applyFields(next: any[], keep = entry) {
    const current = outputOf(profile, keep);
    const matched = matchField(next, current, keep);
    setFields(next);
    setSelected(matched ? identity(matched) : undefined);
  }
  async function inspect(path: string, keep = entry) {
    const { root: sourceRoot, relative } = listingRef(path, root);
    const info = await inspectFile(project, sourceRoot, relative, task);
    const next = info.fields || [];
    applyFields(
      next.length ? next : declaredFields(outputOf(profile, keep), catalog, keep),
      keep,
    );
    setError("");
  }
  async function read() {
    if (!file) return;
    setBusy(true);
    try {
      await inspect(file);
    } catch (e: any) {
      applyFields(declaredFields(output, catalog, entry));
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  useEffect(() => {
    if (!file && listed.length) {
      setFile(entry ? preferredFile(listed, output, profile, catalog) : listed[0]);
    } else if (file && listed.length) {
      const current = listed.find(
        (item) => item === file || fileName(item) === fileName(file),
      );
      if (current && current !== file) setFile(current);
    }
  }, [listed, entry, output, profile, catalog, file]);
  useEffect(() => {
    let live = true;
    (async () => {
      let next: string[] = [];
      if (folders.length) {
        try {
          const groups = await Promise.all(
            folders.map(async (folder) => {
              const { root: sourceRoot, relative } = listingRef(folder, root);
              if (!sourceRoot || !relative || isAbsolute(relative)) return [];
              const rows: any[] = await sourceFiles(
                project,
                task,
                sourceRoot,
                relative,
              );
              return rows
                .filter((row) => !row.directory && fieldSource(row.path || row.name))
                .map((row) => {
                  const path = row.path || `${relative}/${row.name}`;
                  return sourceRoot === root ? path : `${sourceRoot}::${path}`;
                });
            }),
          );
          next = groups.flat();
        } catch {
          next = [];
        }
      }
      if (!live) return;
      setDiscovered(next);
      setLoadingFiles(false);
    })();
    return () => {
      live = false;
    };
  }, [project, task, root, folders]);
  useEffect(() => {
    if (!file) {
      if (!catalogBusy && !loadingFiles)
        applyFields(declaredFields(output, catalog, entry), entry);
      return;
    }
    if (!root && !file.includes("::")) {
      applyFields(declaredFields(output, catalog, entry), entry);
      return;
    }
    let live = true;
    setBusy(true);
    inspect(file, entry)
      .catch((e: any) => {
        if (!live) return;
        applyFields(declaredFields(output, catalog, entry), entry);
        if (entry) setError("");
        else setError(e.message);
      })
      .finally(() => {
        if (live) setBusy(false);
      });
    return () => {
      live = false;
    };
  }, [file, root]);
  const current = selected
    ? asChoice(fields.find((field) => identity(field) === selected) || {})
    : entry;
  const waiting = loadingFiles || (!listed.length && !!catalogBusy);
  return (
    <Modal
      open
      title={entry?.name ? "编辑字段提取" : "添加字段提取"}
      width={920}
      onCancel={onCancel}
      okText="保存字段提取"
      onOk={() => {
        const field = fields.find((item) => identity(item) === selected);
        if (!field) {
          setError("请勾选一个物理量或坐标");
          return;
        }
        onSave(asChoice(field));
      }}
    >
      <h3>1. 打开源文件</h3>
      {!waiting && !listed.length && (
        <Alert type="info" message="数据集声明和已检查样本里没有 VTK 或场文件" />
      )}
      <Space wrap style={{ width: "100%" }}>
        <Select
          style={{ minWidth: 280, width: 420, maxWidth: "100%" }}
          aria-label="读取文件"
          placeholder={waiting ? "正在读取样本目录" : "选择源文件"}
          showSearch
          optionFilterProp="label"
          loading={waiting}
          getPopupContainer={(node) =>
            (node.closest(".ant-modal-body") as HTMLElement) || document.body
          }
          value={file}
          onChange={(value) => {
            setFile(value);
            setSelected(undefined);
          }}
          options={listed.map((value) => ({
            value,
            label: fileName(value),
          }))}
        />
        <Button disabled={!file} loading={busy} onClick={read}>
          读取字段
        </Button>
      </Space>
      <h3>2. 勾选一个字段</h3>
      <Table
        rowKey={identity}
        pagination={false}
        size="small"
        loading={busy || waiting}
        dataSource={fields}
        locale={{ emptyText: busy || waiting ? "正在读取字段" : "暂无字段" }}
        rowSelection={{
          type: "radio",
          selectedRowKeys: selected ? [selected] : [],
          onChange: (keys) => setSelected(String(keys[0] || "")),
        }}
        columns={[
          { title: "字段", dataIndex: "name" },
          { title: "归属", dataIndex: "association" },
          { title: "类型", render: (_, field) => kind(field) },
          {
            title: "形状",
            render: (_, field) =>
              Array.isArray(field.shape) ? field.shape.join(" × ") : "",
          },
        ]}
      />
      <p>
        将保存为 <b>{current?.name || "…"}.pt</b> · 一个物理量或坐标 → 一个 .pt
      </p>
      {error && <Alert type="error" message={error} />}
    </Modal>
  );
}
