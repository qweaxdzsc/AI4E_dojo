/** 可选来源由宿主或独立数据资产模块提供，不接受机器路径。 */
import {useState} from 'react';
import {Modal,Select,Input,Alert,Upload,Button} from 'antd';
/** 选择已登记结果以及可选文件成员。 */
export function ResultImportDialog({open,items=[],onCancel,onImport,onUpload}) {
 const [selected,setSelected]=useState(),[member,setMember]=useState('');
 return <Modal open={open} title="导入结果" onCancel={onCancel} onOk={()=>onImport(selected,member)} okButtonProps={{disabled:!selected}} destroyOnHidden maskClosable>
 <Alert type="info" message="追加到当前工作区，已有对象和相机保持不变。"/>
 {onUpload&&<Upload showUploadList={false} beforeUpload={async file=>{const item=await onUpload(file);if(item)setSelected(item.id);return false;}}><Button style={{marginTop:12}}>上传本地结果</Button></Upload>}
 <Select showSearch optionFilterProp="label" aria-label="结果资产" style={{width:'100%',marginTop:16}} value={selected} onChange={setSelected} options={items.map(a=>({value:a.id||a.asset_id,label:a.name||a.filename||a.id||a.asset_id}))}/>
 <Input aria-label="文件成员" value={member} onChange={e=>setMember(e.target.value)} placeholder="目录资产中的相对文件名（单文件留空）" style={{marginTop:12}}/>
 </Modal>;
}
