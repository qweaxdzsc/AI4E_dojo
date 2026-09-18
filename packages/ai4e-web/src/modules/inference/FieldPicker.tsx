import { Button, Checkbox, Empty, Input, Popover, Select } from "antd";
import { SearchOutlined, SortAscendingOutlined, FilterOutlined } from "@ant-design/icons";
import { useState } from "react";
import type { Field } from "./model";
/** 真实输出目录，未接入的物理分类明确不可用；单位不推测。 */
export function FieldPicker({items,selected,onChange,disabled}:{items:Field[];selected:string[];onChange:(v:string[])=>void;disabled:boolean}) {
 const [query,setQuery]=useState(""),[category,setCategory]=useState("流体"),[sorted,setSorted]=useState(false),[filter,setFilter]=useState("all");
 const categories=[...new Set(["流体","热","结构",...items.map(f=>f.category)])];
 const rows=items.filter(f=>f.category===category&&(f.label+f.domain+f.field).toLowerCase().includes(query.toLowerCase())&&(filter!=="selected"||selected.includes(f.id)));
 if(sorted)rows.sort((a,b)=>a.label.localeCompare(b.label));
 const available=rows.filter(f=>f.available);
 const allOn=!!available.length&&available.every(f=>selected.includes(f.id));
 const some=available.some(f=>selected.includes(f.id));
 return <section className="infer-card infer-picker" data-region="fields"><h3>物理量 <small>已选择 {selected.length} / {items.length} 个</small></h3>
 <div className="infer-search"><Input prefix={<SearchOutlined/>} aria-label="搜索物理量" placeholder="搜索物理量名称" value={query} onChange={e=>setQuery(e.target.value)}/><Button icon={<SortAscendingOutlined/>} onClick={()=>setSorted(!sorted)}>排序</Button><Popover trigger="click" content={<Select aria-label="物理量筛选范围" value={filter} onChange={setFilter} options={[{value:"all",label:"全部"},{value:"selected",label:"已选择"}]}/>}><Button icon={<FilterOutlined/>}>筛选</Button></Popover></div>
 <div className="infer-tabs">{categories.map(c=><Button key={c} className={category===c?"active":""} disabled={!items.some(f=>f.category===c)} title={!items.some(f=>f.category===c)?"当前模型未提供此类输出":undefined} onClick={()=>setCategory(c)}>{c} ({items.filter(f=>f.category===c).length})</Button>)}</div>
 {!!available.length&&<div className="infer-select-all"><Checkbox aria-label="全选物理量" checked={allOn} indeterminate={some&&!allOn} disabled={disabled} onChange={e=>onChange(e.target.checked?[...new Set([...selected,...available.map(f=>f.id)])]:selected.filter(id=>!available.some(f=>f.id===id)))}>全选当前分类 ({available.length})</Checkbox></div>}
 <div className="infer-picker-list">{!items.length?<Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="等待模型输出目录"/>:rows.map(f=><div className="infer-choice" key={f.id} title={`${f.domain} / ${f.field} / ${f.component} · ${f.unit||'单位未声明'}${f.reason?' · '+f.reason:''}`}><Checkbox aria-label={"选择物理量 "+f.label} checked={selected.includes(f.id)} disabled={disabled||!f.available} onChange={e=>onChange(e.target.checked?[...selected,f.id]:selected.filter(id=>id!==f.id))}>{f.label}</Checkbox><small className="infer-field-badge">{f.domain}</small></div>)}</div>
 </section>;
}
