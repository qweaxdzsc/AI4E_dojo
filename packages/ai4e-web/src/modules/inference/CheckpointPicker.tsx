import { Button, Checkbox, Empty, Input, InputNumber, Popover, Select, Tooltip } from "antd";
import { CaretDownOutlined, CaretRightOutlined, FilterOutlined, SearchOutlined, SortAscendingOutlined } from "@ant-design/icons";
import { useState } from "react";
import { compatibleIds, groupCheckpointsByRun } from "./checkpointTree";
import { compatible, statusLabel, type Checkpoint } from "./model";

function runMeta(status?: string, createdAt?: string) {
  const when = createdAt
    ? new Date(createdAt).toLocaleString("zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false })
    : "";
  return [status ? statusLabel(status) : "", when].filter(Boolean).join(" · ");
}

/** 权重快捷选择按训练运行收成树；缺证据不排名，全选只勾检查点叶子。 */
export function CheckpointPicker({items, selected, onChange, disabled}: {
  items: Checkpoint[]; selected: string[]; onChange: (ids: string[]) => void; disabled: boolean;
}) {
  const [query,setQuery]=useState(""), [sort,setSort]=useState("step"), [filter,setFilter]=useState("all"), [top,setTop]=useState(3), [collapsed,setCollapsed]=useState<string[]>([]);
  const usable=items.filter(compatible), ranked=usable.filter(c=>c.evaluation && Number.isFinite(c.evaluation.value));
  const same=ranked.length>0 && ranked.every(c=>c.evaluation!.protocol===ranked[0].evaluation!.protocol && c.evaluation!.direction===ranked[0].evaluation!.direction);
  const ranking=same ? [...ranked].sort((a,b)=>(a.evaluation!.value-b.evaluation!.value)*(a.evaluation!.direction==="max"?-1:1)) : [];
  const rows=items.filter(c=>(c.name+" "+c.run_id+" "+(c.run_id||"").slice(0,8)+" "+(c.aliases||[]).join(" ")).toLowerCase().includes(query.toLowerCase()))
    .filter(c=>filter==="all" || (filter==="compatible"?compatible(c):selected.includes(c.id)))
    .sort((a,b)=>sort==="name"?a.name.localeCompare(b.name):sort==="evaluation"?((ranking.findIndex(c=>c.id===a.id)<0?Infinity:ranking.findIndex(c=>c.id===a.id))-(ranking.findIndex(c=>c.id===b.id)<0?Infinity:ranking.findIndex(c=>c.id===b.id))):(b.updates??-1)-(a.updates??-1));
  const groups=groupCheckpointsByRun(rows);
  const toggleGroup=(key:string)=>setCollapsed(old=>old.includes(key)?old.filter(id=>id!==key):[...old,key]);
  const setLeaves=(leaves:Checkpoint[], checked:boolean)=>{
    const ids=compatibleIds(leaves);
    onChange(checked?[...new Set([...selected,...ids])]:selected.filter(id=>!ids.includes(id)));
  };
  return <section className="infer-card infer-picker" data-region="checkpoints">
    <h3>Checkpoint <small>已选择 {selected.length} / {items.length} 个</small></h3>
    <div className="infer-search"><Input prefix={<SearchOutlined/>} aria-label="搜索检查点" placeholder="搜索 checkpoint 或训练运行" value={query} onChange={e=>setQuery(e.target.value)}/>
      <Popover trigger="click" content={<Select aria-label="检查点排序方式" value={sort} onChange={setSort} options={[{value:"step",label:"Step 从大到小"},{value:"name",label:"名称"},{value:"evaluation",label:"评价值",disabled:!same}]}/>}><Button icon={<SortAscendingOutlined/>}>排序</Button></Popover>
      <Popover trigger="click" content={<Select aria-label="检查点筛选范围" value={filter} onChange={setFilter} options={[{value:"all",label:"全部"},{value:"compatible",label:"兼容权重"},{value:"selected",label:"已选择"}]}/>}><Button icon={<FilterOutlined/>}>筛选</Button></Popover>
    </div>
    <div className="infer-tabs">
      <Tooltip title={!same?"没有同口径评价证据，无法排名":"按记录的评价方向选择"}><Button disabled={disabled||!same} onClick={()=>onChange(ranking.slice(0,1).map(c=>c.id))}>Best</Button></Tooltip>
      <Button disabled={disabled||!usable.length} onClick={()=>onChange([...usable].sort((a,b)=>(b.created_at||"").localeCompare(a.created_at||"")||(b.updates??-1)-(a.updates??-1)).slice(0,1).map(c=>c.id))}>Latest</Button>
      <Popover trigger="click" content={<div className="infer-search"><InputNumber aria-label="Top N 数量" min={1} precision={0} value={top} onChange={v=>setTop(v||1)}/><Button disabled={!same} onClick={()=>onChange(ranking.slice(0,top).map(c=>c.id))}>选择前 {top} 个</Button></div>}><Button disabled={disabled||!same} title={!same?"缺少同口径评价证据":undefined}>Top N</Button></Popover>
      <Button aria-label="全选检查点" disabled={disabled||!rows.some(compatible)} onClick={()=>onChange(rows.filter(compatible).map(c=>c.id))}>全选</Button>
      {!!selected.length&&<Button type="text" onClick={()=>onChange([])} disabled={disabled}>清空</Button>}
    </div>
    <div className="infer-picker-list">{!items.length?<Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="尚无权重，请先训练"/>:groups.map(group=>{
      const leaves=compatibleIds(group.items);
      const picked=leaves.filter(id=>selected.includes(id)).length;
      const open=!!query||!collapsed.includes(group.key);
      const title=group.runId||"未归属运行";
      return <div key={group.key} className="infer-run-block">
        <div className="infer-run" data-run-parent={group.key} title={title}>
          <button type="button" className="infer-run-toggle" aria-label={`${open?"收起":"展开"}${group.label}`} aria-expanded={open} onClick={()=>toggleGroup(group.key)}>{open?<CaretDownOutlined/>:<CaretRightOutlined/>}</button>
          <Checkbox aria-label={`选择训练运行 ${title}`} disabled={disabled||!leaves.length} checked={!!leaves.length&&picked===leaves.length} indeterminate={picked>0&&picked<leaves.length} onChange={e=>setLeaves(group.items,e.target.checked)}><span>{group.label}</span></Checkbox>
          <small>{runMeta(group.status,group.createdAt)||`${group.items.length} 个检查点`}</small>
        </div>
        {open&&group.items.map(c=><div className="infer-choice" key={c.id} data-run-id={c.run_id||""} title={`${c.name} · ${c.run_id}\n${c.aliases?.join('、')||''}\n${c.compatibility.reason||''}`}>
          <Checkbox aria-label={`选择检查点 ${c.name} · ${c.run_id}`} disabled={disabled||!compatible(c)} checked={selected.includes(c.id)} onChange={e=>onChange(e.target.checked?[...selected,c.id]:selected.filter(id=>id!==c.id))}><span>{c.name}</span></Checkbox>
          <small>{compatible(c)?`step ${c.updates??"—"}${c.evaluation?` | ${c.evaluation.split} ${c.evaluation.value.toExponential(2)}`:""}`:c.compatibility.reason||"不可用"}</small>
        </div>)}
      </div>;
    })}</div>
  </section>;
}
