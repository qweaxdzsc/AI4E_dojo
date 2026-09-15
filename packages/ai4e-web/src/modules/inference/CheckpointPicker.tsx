import { Button, Checkbox, Empty, Input, InputNumber, Popover, Select, Tooltip } from "antd";
import { SearchOutlined, SortAscendingOutlined, FilterOutlined } from "@ant-design/icons";
import { useState } from "react";
import { compatible, type Checkpoint } from "./model";
/** 权重快捷选择只使用同口径的真实评价记录；缺证据不排名。 */
export function CheckpointPicker({items, selected, onChange, disabled}: {
  items: Checkpoint[]; selected: string[]; onChange: (ids: string[]) => void; disabled: boolean;
}) {
  const [query,setQuery]=useState(""), [sort,setSort]=useState("step"), [filter,setFilter]=useState("all"), [top,setTop]=useState(3);
  const usable=items.filter(compatible), ranked=usable.filter(c=>c.evaluation && Number.isFinite(c.evaluation.value));
  const same=ranked.length>0 && ranked.every(c=>c.evaluation!.protocol===ranked[0].evaluation!.protocol && c.evaluation!.direction===ranked[0].evaluation!.direction);
  const ranking=same ? [...ranked].sort((a,b)=>(a.evaluation!.value-b.evaluation!.value)*(a.evaluation!.direction==="max"?-1:1)) : [];
  const rows=items.filter(c=>(c.name+" "+c.run_id+" "+(c.aliases||[]).join(" ")).toLowerCase().includes(query.toLowerCase()))
    .filter(c=>filter==="all" || (filter==="compatible"?compatible(c):selected.includes(c.id)))
    .sort((a,b)=>sort==="name"?a.name.localeCompare(b.name):sort==="evaluation"?((ranking.findIndex(c=>c.id===a.id)<0?Infinity:ranking.findIndex(c=>c.id===a.id))-(ranking.findIndex(c=>c.id===b.id)<0?Infinity:ranking.findIndex(c=>c.id===b.id))):(b.updates??-1)-(a.updates??-1));
  return <section className="infer-card infer-picker" data-region="checkpoints">
    <h3>1. Checkpoint <small>已选择 {selected.length} / {items.length} 个</small></h3>
    <div className="infer-search"><Input prefix={<SearchOutlined/>} aria-label="搜索检查点" placeholder="搜索 checkpoint 名称" value={query} onChange={e=>setQuery(e.target.value)}/>
      <Popover trigger="click" content={<Select aria-label="检查点排序方式" value={sort} onChange={setSort} options={[{value:"step",label:"Step 从大到小"},{value:"name",label:"名称"},{value:"evaluation",label:"评价值",disabled:!same}]}/>}><Button icon={<SortAscendingOutlined/>}>排序</Button></Popover>
      <Popover trigger="click" content={<Select aria-label="检查点筛选范围" value={filter} onChange={setFilter} options={[{value:"all",label:"全部"},{value:"compatible",label:"兼容权重"},{value:"selected",label:"已选择"}]}/>}><Button icon={<FilterOutlined/>}>筛选</Button></Popover>
    </div>
    <div className="infer-tabs">
      <Tooltip title={!same?"没有同口径评价证据，无法排名":"按记录的评价方向选择"}><Button disabled={disabled||!same} onClick={()=>onChange(ranking.slice(0,1).map(c=>c.id))}>Best</Button></Tooltip>
      <Button disabled={disabled||!usable.length} onClick={()=>onChange([...usable].sort((a,b)=>(b.created_at||"").localeCompare(a.created_at||"")||(b.updates??-1)-(a.updates??-1)).slice(0,1).map(c=>c.id))}>Latest</Button>
      <Popover trigger="click" content={<div className="infer-search"><InputNumber aria-label="Top N 数量" min={1} precision={0} value={top} onChange={v=>setTop(v||1)}/><Button disabled={!same} onClick={()=>onChange(ranking.slice(0,top).map(c=>c.id))}>选择前 {top} 个</Button></div>}><Button disabled={disabled||!same} title={!same?"缺少同口径评价证据":undefined}>Top N</Button></Popover>
      {!!selected.length&&<Button type="text" onClick={()=>onChange([])} disabled={disabled}>清空</Button>}
    </div>
    <div className="infer-picker-list">{!items.length?<Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="尚无权重，请先训练"/>:rows.map(c=><div className="infer-choice" key={c.id} title={`${c.name} · ${c.run_id}\n${c.aliases?.join('、')||''}\n${c.compatibility.reason||''}`}>
      <Checkbox aria-label={`选择检查点 ${c.name} · ${c.run_id}`} disabled={disabled||!compatible(c)} checked={selected.includes(c.id)} onChange={e=>onChange(e.target.checked?[...selected,c.id]:selected.filter(id=>id!==c.id))}><span>{c.name}</span></Checkbox>
      <small>{compatible(c)?`step ${c.updates??"—"}${c.evaluation?` | ${c.evaluation.split} ${c.evaluation.value.toExponential(2)}`:""}`:c.compatibility.reason||"不可用"}</small>
    </div>)}</div>
  </section>;
}
