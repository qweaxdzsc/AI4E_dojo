import { Button, Checkbox, Empty, Input, Popover, Select } from "antd";
import { SearchOutlined, SortAscendingOutlined, FilterOutlined } from "@ant-design/icons";
import { useState } from "react";
import type { Metric } from "./model";
/** 指标公式由后台目录提供，分组仅影响浏览而不清空已选指标。 */
export function MetricPicker({items,selected,onChange,disabled}:{items:Metric[];selected:string[];onChange:(v:string[])=>void;disabled:boolean}) {
 const [query,setQuery]=useState(""),[category,setCategory]=useState(""),[sorted,setSorted]=useState(false),[filter,setFilter]=useState("all");
 const categories=[...new Set(items.map(m=>m.category))];
 const rows=items.filter(m=>(!category||m.category===category)&&(m.label+m.id).toLowerCase().includes(query.toLowerCase())&&(filter!=="selected"||selected.includes(m.id)));
 if(sorted)rows.sort((a,b)=>a.label.localeCompare(b.label));
 return <section className="infer-card infer-picker" data-region="metrics"><h3>4. 指标 <small>已选择 {selected.length} / {items.length} 个</small></h3>
 <div className="infer-search"><Input prefix={<SearchOutlined/>} aria-label="搜索指标" placeholder="搜索指标名称" value={query} onChange={e=>setQuery(e.target.value)}/><Button icon={<SortAscendingOutlined/>} onClick={()=>setSorted(!sorted)}>排序</Button><Popover trigger="click" content={<Select aria-label="指标筛选范围" value={filter} onChange={setFilter} options={[{value:"all",label:"全部"},{value:"selected",label:"已选择"}]}/>}><Button icon={<FilterOutlined/>}>筛选</Button></Popover></div>
 <div className="infer-tabs">{categories.map(c=><Button key={c} className={category===c?"active":""} onClick={()=>setCategory(category===c?"":c)} title="再次点击显示全部指标">{c} ({items.filter(m=>m.category===c).length})</Button>)}</div>
 <div className="infer-picker-list">{!items.length?<Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="等待指标目录"/>:rows.map(m=><div className="infer-choice" key={m.id} title={`${m.formula}\n零分母及常量真值保留不可定义原因`}><Checkbox aria-label={"选择指标 "+m.label} checked={selected.includes(m.id)} disabled={disabled} onChange={e=>onChange(e.target.checked?[...selected,m.id]:selected.filter(id=>id!==m.id))}>{m.label}</Checkbox><small className="infer-field-badge">{m.category}</small></div>)}</div>
 </section>;
}
