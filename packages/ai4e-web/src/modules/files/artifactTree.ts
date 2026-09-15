/** 固定产物的展示层级；路径仅用于显示，操作始终使用受控文件引用或根+相对路径。 */
export interface ArtifactTreeFile {
  id: string;
  name: string;
  tree_path: string;
  directory?: boolean;
  size?: number;
  modified_at?: string;
  visualizable?: boolean;
  root?: string;
  source_path?: string;
  path?: string;
  ref?: any;
  [key: string]: any;
}
export interface ArtifactNode {
  key: string;
  name: string;
  path: string;
  children?: ArtifactNode[];
  file?: ArtifactTreeFile;
}
function ensureDir(nodes: ArtifactNode[], path: string, name: string): ArtifactNode {
  let node = nodes.find((item) => item.path === path && !item.file);
  if (!node) {
    node = { key: "dir:" + path, name, path, children: [] };
    nodes.push(node);
  }
  return node;
}
/** 搜索保留祖先，目录身份不受分页或展开状态影响。 */
export function artifactTree(files: ArtifactTreeFile[], query = ""): ArtifactNode[] {
  const roots: ArtifactNode[] = [];
  for (const file of files) {
    const hay = (file.tree_path + " " + file.name).toLocaleLowerCase();
    if (query && !hay.includes(query.toLocaleLowerCase())) continue;
    const parts = file.tree_path.split("/").filter(Boolean);
    let nodes = roots;
    let path = "";
    parts.forEach((name, index) => {
      path = path ? path + "/" + name : name;
      const last = index === parts.length - 1;
      if (last && !file.directory) {
        nodes.push({ key: file.id, name, path, file });
        return;
      }
      const node = ensureDir(nodes, path, name);
      nodes = node.children!;
    });
  }
  return roots;
}
/** 目录勾选仅作用于可加入的真实成员。 */
export function selectableFiles(
  node: ArtifactNode,
  accept: (file: ArtifactTreeFile) => boolean = (file) => !!file.visualizable && !file.directory,
): ArtifactTreeFile[] {
  return node.file
    ? accept(node.file)
      ? [node.file]
      : []
    : (node.children || []).flatMap((child) => selectableFiles(child, accept));
}
/** 已展开路径：至少有一条更深的子项。 */
export function loadedDirectories(files: ArtifactTreeFile[]): string[] {
  const loaded = new Set<string>([""]);
  for (const file of files) {
    const parts = file.tree_path.split("/").filter(Boolean);
    if (file.directory) {
      if (files.some((item) => item.tree_path !== file.tree_path && item.tree_path.startsWith(file.tree_path + "/")))
        loaded.add(file.tree_path);
    } else if (parts.length > 1) loaded.add(parts.slice(0, -1).join("/"));
    else loaded.add("");
  }
  return [...loaded];
}
