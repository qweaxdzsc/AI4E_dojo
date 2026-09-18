import { Button, Checkbox, Empty, Input, Pagination, Popover, Select } from "antd";
import { SearchOutlined, SortAscendingOutlined, FilterOutlined } from "@ant-design/icons";
import { useEffect, useMemo, useState } from "react";
export const splitLabel=(split:string)=>({train:"训练集",validation:"验证集",eval:"验证集",test:"测试集"}[split]||split);
const SLICE_ORDER=["train","test","eval"];
function sliceNames(partitions:Record<string,string[]>){
  const extras=Object.keys(partitions).filter((key)=>!SLICE_ORDER.includes(key)&&key!=="validation");
  return [...SLICE_ORDER, ...extras];
}
/** 分片独立选择；分页全选只改当前页，筛选全选覆盖本分片筛选结果。 */
export function SamplePicker({partitions,split,onSplit,selected,onChange,disabled,totalSelected=selected.length,emptyHint="选择检查点后读取样本"}: {
 partitions:Record<string,string[]>;split:string;onSplit:(s:string)=>void;selected:string[];onChange:(ids:string[])=>void;disabled:boolean;totalSelected?:number;emptyHint?:string;
}) {
 const [query,setQuery]=useState(""),[sort,setSort]=useState(false),[filter,setFilter]=useState("all"),[page,setPage]=useState(1);
 useEffect(()=>setPage(1),[query,split,filter,sort]);
 const selection=useMemo(()=>new Set(selected),[selected]);
 const filtered=useMemo(()=>{const rows=(partitions[split]||[]).filter(id=>id.toLowerCase().includes(query.toLowerCase())&&(filter!=="selected"||selection.has(id)));return sort?rows.sort((a,b)=>b.localeCompare(a)):rows;},[partitions,split,query,filter,sort,selection]);
 const pages=Math.max(1,Math.ceil(filtered.length/50)), current=Math.min(page,pages), visible=filtered.slice((current-1)*50,current*50);
 const toggle=(ids:string[],on:boolean)=>onChange(on?[...new Set([...selected,...ids])]:selected.filter(id=>!new Set(ids).has(id)));
 const check=(ids:string[])=>({checked:!!ids.length&&ids.every(id=>selection.has(id)),indeterminate:ids.some(id=>selection.has(id))&&!ids.every(id=>selection.has(id))});
 return <section className="infer-card infer-picker" data-region="samples"><h3>样本 <small>已选择 {totalSelected} / {Object.values(partitions).reduce((n,v)=>n+v.length,0)} 个</small></h3>
 <div className="infer-search"><Input prefix={<SearchOutlined/>} aria-label="搜索推理样本" placeholder="搜索样本名称" value={query} onChange={e=>setQuery(e.target.value)}/><Button icon={<SortAscendingOutlined/>} onClick={()=>setSort(!sort)} title={sort?"当前降序，点击升序":"当前原顺序，点击降序"}>排序</Button><Popover trigger="click" content={<Select aria-label="样本筛选范围" value={filter} onChange={setFilter} options={[{value:"all",label:"全部"},{value:"selected",label:"已选择"}]}/>}><Button icon={<FilterOutlined/>}>筛选</Button></Popover></div>
 <div className="infer-tabs" role="tablist" aria-label="推理分片">{sliceNames(partitions).map(s=><Button key={s} role="tab" aria-selected={split===s} className={s===split?"active":""} onClick={()=>onSplit(s)} disabled={disabled}>{splitLabel(s)} ({(partitions[s]||[]).length.toLocaleString()})</Button>)}</div>
 {!!filtered.length&&<div className="infer-select-all"><Checkbox {...check(visible)} disabled={disabled} onChange={e=>toggle(visible,e.target.checked)}>全选当前页 ({visible.length})</Checkbox><Checkbox {...check(filtered)} disabled={disabled} onChange={e=>toggle(filtered,e.target.checked)}>全部筛选范围 ({filtered.length})</Checkbox></div>}
 <div className="infer-picker-list">{!partitions[split]?.length?<Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={emptyHint}/>:visible.map(id=><div className="infer-choice" key={id}><Checkbox aria-label={"选择样本 "+id} title={id} disabled={disabled} checked={selection.has(id)} onChange={e=>toggle([id],e.target.checked)}>{id}</Checkbox></div>)}</div>
 {!!filtered.length&&<Pagination aria-label="推理样本分页" simple size="small" current={current} pageSize={50} total={filtered.length} showSizeChanger={false} onChange={setPage}/>}
 </section>;
}
