import { Checkbox, Input, InputNumber, Select } from 'antd';
/** 无业务语义的标量编辑器；对象不会被错误转换成文本框字符串。 */
export function ConfigurationField({label,value,onChange,options,disabled,help}:{label:string;value:any;onChange:(v:any)=>void;help?:string;disabled?:boolean;options?:string[]}){
 return <div className="configuration-field"><label title={help}>{label}</label>{options?<Select disabled={disabled} value={value} options={options.map(v=>({value:v,label:v}))} onChange={onChange}/>:typeof value==='boolean'?<Checkbox disabled={disabled} checked={value} onChange={e=>onChange(e.target.checked)}/>:typeof value==='number'||value===null?<InputNumber disabled={disabled} value={value} onChange={onChange}/>:typeof value==='string'?<Input disabled={disabled} value={value} onChange={e=>onChange(e.target.value)}/>:<span>此项为复合配置，请在对应配置区域修改</span>}</div>
}
