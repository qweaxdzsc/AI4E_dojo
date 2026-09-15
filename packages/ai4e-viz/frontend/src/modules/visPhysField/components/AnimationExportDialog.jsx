/** 固定实际时间步的导出表单，帧率不改变物理时间。 */
import {useEffect,useState} from 'react';
import {Modal, Form, InputNumber, Select, Alert} from 'antd';
/** 统一配置时序动画与显式图片、数据输出。 */
export function AnimationExportDialog({open, animation, formatHint='png', times=[], views=[], activeView, onCancel, onExport}) {
  const [start,setStart]=useState(0),[end,setEnd]=useState(0),[stride,setStride]=useState(1),[reverse,setReverse]=useState(false),[width,setWidth]=useState(1280),[height,setHeight]=useState(720),[fps,setFps]=useState(24),[view,setView]=useState('all'),[format,setFormat]=useState('mp4');
  useEffect(()=>{if(open){setEnd(Math.max(0,times.length-1));setStart(0);setView(activeView ?? 'all');setFormat(animation?'mp4':formatHint);}},[open,animation,formatHint]);
  const submit=()=>{const selected=times.filter((_,i)=>i>=start&&i<=end&&(i-start)%stride===0);if(reverse)selected.reverse();onExport({format,width,height,fps,...(view!=='all'?{view}:{}),...(['mp4','png_sequence'].includes(format)?{times:selected}:{})});};
  return <Modal open={open} title={animation?'生成时序动画':'导出图片 / 数据'} onCancel={onCancel} onOk={submit} okText="生成" okButtonProps={{disabled:(animation&&!times.length)||start>end}} destroyOnHidden maskClosable>
    <Alert message="输出使用已保存配置修订；每个选定时间步生成一帧。" type="info"/>
    <Form layout="vertical">
      <Form.Item label="格式"><Select value={format} onChange={setFormat} options={(animation?['mp4','png_sequence']:['png','csv']).map(value=>({value,label:value}))}/></Form.Item>
      <Form.Item label="输出视图"><Select value={view} onChange={setView} options={[{value:'all',label:'整个布局'},...views.map(v=>({value:v.id,label:v.name}))]}/></Form.Item>
      {animation&&<><Form.Item label="开始时间步"><InputNumber aria-label="开始时间步" min={0} max={times.length-1} value={start} onChange={v=>setStart(v??0)}/><span> t={times[start]}</span></Form.Item><Form.Item label="结束时间步"><InputNumber aria-label="结束时间步" min={0} max={times.length-1} value={end} onChange={v=>setEnd(v??0)}/><span> t={times[end]}</span></Form.Item><Form.Item label="时间步间隔"><InputNumber min={1} value={stride} onChange={v=>setStride(v||1)}/></Form.Item><Form.Item label="方向"><Select value={reverse} onChange={setReverse} options={[{value:false,label:'正向'},{value:true,label:'反向'}]}/></Form.Item></>}
      {format!=='csv'&&<><Form.Item label="输出宽度"><InputNumber min={64} max={4096} value={width} onChange={v=>setWidth(v||1280)}/></Form.Item><Form.Item label="输出高度"><InputNumber min={64} max={4096} value={height} onChange={v=>setHeight(v||720)}/></Form.Item>{animation&&<Form.Item label="帧率 fps"><InputNumber min={1} max={60} value={fps} onChange={v=>setFps(v||24)}/></Form.Item>}</>}
    </Form>
  </Modal>;
}
