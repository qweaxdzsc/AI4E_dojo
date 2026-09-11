import { Select } from "antd";
import { useState } from "react";
import { FileBrowser } from "./FileBrowser";
import "./project-files.css";
/** 项目文件通过任务筛选选择对应版本范围。 */
export function ProjectFiles({
  project,
  tasks,
}: {
  project: string;
  tasks: any[];
}) {
  const [t, setT] = useState<string>();
  return (
    <section className="project-files">
      <h2>项目文件</h2>
      <section className="panel files-panel">
        <div className="toolbar searchbar">
          <label className="versionfilter">
            任务版本
            <Select
              showSearch
              allowClear
              aria-label="筛选文件版本"
              placeholder="搜索任务 / 版本"
              onChange={setT}
              options={tasks.map((x) => ({
                value: x.id,
                label: x.version_id.slice(0, 8) + " / " + x.name,
              }))}
            />
          </label>
        </div>
        <FileBrowser key={t || "project"} project={project} task={t} chrome="project" />
      </section>
    </section>
  );
}
