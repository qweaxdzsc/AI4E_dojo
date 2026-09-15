import { Alert, Button, Empty, Spin } from "antd";
import { useEffect, useState } from "react";
import { FilePreviewDialog } from "../previews";
import { ArtifactFileTree } from "./ArtifactFileTree";
import { fileDownload, stageFiles } from "./api";
import type { ArtifactTreeFile } from "./artifactTree";

function toFile(row: any): ArtifactTreeFile {
  return {
    ...row,
    id: row.directory ? "dir:" + row.path : (row.root || "") + ":" + (row.source_path || row.path),
    tree_path: String(row.path || row.name),
    directory: !!row.directory,
  };
}
function merge(old: ArtifactTreeFile[], next: ArtifactTreeFile[]) {
  const seen = new Map(old.map((row) => [row.id, row]));
  for (const row of next) seen.set(row.id, row);
  return [...seen.values()];
}

/** 固定清单或运行限定浏览范围；没有来源时不回退项目文件。emptyHint 只改无来源空态说明，不自动选定清单。 */
export function StageFiles({
  project,
  task,
  role,
  run,
  asset,
  onSelection,
  emptyHint,
  query = "",
  compact = false,
}: {
  project: string;
  task: string;
  role: "inputs" | "preparation" | "post";
  run?: string;
  asset?: any;
  onSelection?: (refs: any[]) => void;
  emptyHint?: string;
  query?: string;
  compact?: boolean;
}) {
  const [rows, setRows] = useState<ArtifactTreeFile[]>([]);
  const [searchRows, setSearchRows] = useState<ArtifactTreeFile[] | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [preview, setPreview] = useState<any>();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState<string[]>([]);
  const [generation, setGeneration] = useState(0);
  useEffect(() => {
    let live = true;
    setError("");
    setSearchRows(null);
    if (!run && !asset) {
      setRows([]);
      setBusy(false);
      return;
    }
    setBusy(true);
    stageFiles(project, task, role, run, asset, "", query)
      .then((value) => {
        if (!live) return;
        const files = value.map(toFile);
        if (query) setSearchRows(files);
        else {
          setRows(files);
          setSearchRows(null);
        }
        setSelected((old) => old.filter((id) => files.some((r) => r.id === id)));
      })
      .catch((e) => live && setError(e.message))
      .finally(() => live && setBusy(false));
    return () => {
      live = false;
    };
  }, [project, task, role, run, asset?.asset_id, asset?.revision, generation, query]);
  useEffect(() => {
    setSelected([]);
    setRows([]);
    setSearchRows(null);
    setPreview(undefined);
    onSelection?.([]);
  }, [project, task, role, run, asset?.asset_id, asset?.revision]);
  async function expand(path: string) {
    setLoading((old) => [...old, path]);
    try {
      const value = (await stageFiles(project, task, role, run, asset, path)).map(toFile);
      setRows((old) => merge(old, value));
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading((old) => old.filter((item) => item !== path));
    }
  }
  const files = searchRows ?? rows;
  return (
    <div className="stage-files" data-role={role}>
      {!compact && (
        <Button size="small" disabled={busy || (!run && !asset)} onClick={() => setGeneration((g) => g + 1)}>
          刷新阶段文件
        </Button>
      )}
      {error && <Alert type="error" message={error} />}
      {busy && !files.length ? (
        <Spin />
      ) : !files.length ? (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={run || asset ? "该来源尚无对应阶段文件" : emptyHint || "请选择固定输入或运行"}
        />
      ) : (
        <ArtifactFileTree
          files={files}
          query={query}
          selected={onSelection ? selected : []}
          onSelection={
            onSelection
              ? (ids) => {
                  setSelected(ids);
                  onSelection(
                    files
                      .filter((r) => ids.includes(r.id) && !r.directory)
                      .map((r) => ({ root: r.root, path: r.source_path || r.path, name: r.name })),
                  );
                }
              : undefined
          }
          onPreview={(file) => setPreview(file)}
          onExpand={query ? undefined : expand}
          loadingPaths={loading}
          download={(file) => fileDownload(project, file.root || "project", file.source_path || file.path || "", task)}
        />
      )}
      {preview && (
        <FilePreviewDialog
          project={project}
          task={task}
          file={{ ...preview, path: preview.source_path || preview.path }}
          onClose={() => setPreview(undefined)}
        />
      )}
    </div>
  );
}
