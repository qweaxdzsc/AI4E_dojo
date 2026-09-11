import { ActionButton as Button } from "../../infrastructure/components/ActionButton";
import {Alert, Select, Space, Table} from "antd";
import { useState, useEffect, useRef } from "react";
import { DifferencePanel } from "./DifferencePanel";
import { compare, listSaved, saveComparison } from "./api";
import "./comparison.css";

const RAILS = [
  ["表格", "参数与结果逐列查看"],
  ["趋势", "观察参数随版本变化"],
  ["三维可视化", "管线、属性与多视图"],
] as const;

/** 比较目标显式区分创建版本、当前目录和固定运行。 */
export function ComparisonView({
  project,
  tasks,
  runs, initialSelection,
}: {
  project: string;
  tasks: any[];
  runs: any[]; initialSelection?:any;
}) {
  const generation=useRef(0);const [comparing,setComparing]=useState(false),[saving,setSaving]=useState(false);
  const [parameter,setParameter]=useState<string>();
  const [saved,setSaved]=useState<any[]>([]),[currentSaved,setCurrentSaved]=useState<any>();
  useEffect(()=>{listSaved(project).then(setSaved).catch(e=>setError(e.message))},[project]);
  const [mode, setMode] = useState("versions"),
    [left, setLeft] = useState<string>(),
    [right, setRight] = useState<string>(),
    [result, setResult] = useState<any>(),
    [error, setError] = useState(""),
    [rail, setRail] = useState<(typeof RAILS)[number][0]>("表格");
  useEffect(()=>{if(initialSelection){generation.current++;setComparing(false);setParameter(initialSelection.parameter);setMode(initialSelection.mode);setLeft(initialSelection.left);setRight(initialSelection.right);setResult(undefined);setCurrentSaved(undefined)}},[initialSelection]);
  const options = (mode === "runs" ? runs : tasks).map((v) => ({
    value: mode === "versions" ? v.version_id : v.id,
    label: v.name || v.id,
  }));
  function invalidate(){generation.current++;setComparing(false);setResult(undefined);setCurrentSaved(undefined)}
  async function execute() {
    const current=++generation.current;setComparing(true);setError('');
    try {const value=await compare(project,{mode,left,right,parameter});if(current===generation.current)setResult(value)}
    catch(e:any){if(current===generation.current)setError(e.message)}
    finally{if(current===generation.current)setComparing(false)}
  }
  async function persist(){if(!result||comparing||saving)return;const current=generation.current;setSaving(true);try{const record=await saveComparison(project,{mode,left,right,parameter});if(current===generation.current)setCurrentSaved(record);setSaved(await listSaved(project))}catch(e:any){if(current===generation.current)setError(e.message)}finally{setSaving(false)}}
  const table = (
    <>
      {parameter&&<Alert type="info" message={"已加入比较参数："+parameter+"（创建快照）"}/>}
      <Space>
        <Select
          value={mode}
          onChange={(v) => {
            invalidate();setMode(v);setParameter(undefined);setCurrentSaved(undefined);
            setLeft(undefined);
            setRight(undefined);
            setResult(undefined);
          }}
          options={[
            { value: "versions", label: "版本创建记录" },
            { value: "worktree", label: "当前工作目录" },
            { value: "runs", label: "固定运行" },
          ]}
        />
        <Select
          placeholder="比较对象 A"
          value={left}
          onChange={value=>{invalidate();setLeft(value);setResult(undefined);setCurrentSaved(undefined)}}
          options={options}
          style={{ width: 260 }}
        />
        {mode !== "worktree" && (
          <Select
            placeholder="比较对象 B"
            value={right}
            onChange={value=>{invalidate();setRight(value);setResult(undefined);setCurrentSaved(undefined)}}
            options={options}
            style={{ width: 260 }}
          />
        )}
        <Button
          onClick={execute}
          disabled={comparing || !left || (mode !== "worktree" && !right)}
        >
          比较
        </Button>
      </Space>
      <Space style={{margin:'14px 0'}}><Select style={{width:320}} placeholder="打开固定比较" options={saved.map(v=>({value:v.comparison_id,label:v.created_at+' · '+v.selection.mode}))} onChange={id=>{const record=saved.find(v=>v.comparison_id===id);invalidate();setCurrentSaved(record);setParameter(record.selection.parameter);setMode(record.selection.mode);setLeft(record.selection.left);setRight(record.selection.right);setResult(record.result)}}/><Button disabled={!result||comparing||saving} loading={saving} onClick={persist}>保存固定比较</Button></Space>
      {error && <Alert type="error" message={error} />}
      {result ? (
        <>
          <p>
            来源：{result.kind} · {result.left || result.version_id}{" "}
            {result.right ? "→ " + result.right : ""}
          </p>
          {result.parameter_comparison&&<Table pagination={false} rowKey="path" dataSource={[result.parameter_comparison]} columns={[{title:'固定参数',dataIndex:'path'},{title:'对象 A 创建值',render:(_,r)=>r.left.available?JSON.stringify(r.left.value):'缺失'},{title:'对象 B 创建值',render:(_,r)=>r.right.available?JSON.stringify(r.right.value):'缺失'},{title:'来源',dataIndex:'source'}]}/>}
          <Table<any>
            rowKey="path"
            dataSource={result.files || []}
            columns={[
              { title: "文件 / 配置", dataIndex: "path" },
              { title: "变化", dataIndex: "status" },
              {
                title: "差异",
                render: (_, r) => <pre>{r.diff || "二进制文件变化"}</pre>,
              },
            ]}
          />
          {result.metrics && (
            <Table<any>
              rowKey="name"
              dataSource={Object.entries(result.metrics).map(([name, v]) => ({
                name,
                ...(v as any),
              }))}
              columns={[
                { title: "指标", dataIndex: "name" },
                { title: "对象 A", render: (_, v) => v.left?.value ?? "缺失" },
                { title: "对象 B", render: (_, v) => v.right?.value ?? "缺失" },
                { title: "可比状态", dataIndex: "status" },
                { title: "说明", dataIndex: "reason" },
              ]}
            />
          )}
        </>
      ) : (
        <p>选择明确对象后比较；缺失值不会被当作零。</p>
      )}
    </>
  );
  return (
    <div className="workspacewithrail comparison-workspace">
      <nav className="viewrail">
        <div className="hint">版本比较</div>
        {RAILS.map(([label, desc], i) => (
          <button key={label} type="button" className={rail === label ? "active" : ""} onClick={() => setRail(label)}>
            <strong>0{i + 1}</strong>
            <b>{label}</b>
            <small>{desc}</small>
          </button>
        ))}
      </nav>
      <section className="panel comparemain">
        <h2>{rail}</h2>
        <div className="comparetools">
          <div>
            <h3>对比参数 {parameter ? <span className="badge">1</span> : null}</h3>
            <div className="parameterchips">
              {parameter ? <span className="badge">{parameter}（创建快照）</span> : <span className="muted">从版本树勾选真实创建参数加入；缺失值不按零绘制。</span>}
            </div>
          </div>
        </div>
        {rail === "表格" && table}
        {rail === "趋势" && (
          result?.parameter_comparison?.left?.available && typeof result.parameter_comparison.left.value === "number" && result.parameter_comparison.right?.available && typeof result.parameter_comparison.right.value === "number" ? (
            <p>对象 A {result.parameter_comparison.left.value}　/　对象 B {result.parameter_comparison.right.value}。不同分支不自动连成演化曲线。</p>
          ) : (
            <div className="compare-placeholder">该参数为文本、资产或尚无数值，请使用表格查看真实创建值。</div>
          )
        )}
        {rail === "三维可视化" && (currentSaved?.selection.mode === "runs" ? <DifferencePanel project={project} saved={currentSaved} runs={runs}/> : <div className="compare-placeholder">三维比较只接受已保存的固定运行；版本创建记录请留在表格。</div>)}
        <div className="compare-note">创建版本、当前工作目录与固定运行是三种来源，不能互相冒充。加入项目报告尚未开放。</div>
      </section>
    </div>
  );
}
