/** 外部声明式配置在应用前经过服务端完整校验。 */
import {useState} from 'react';
import {Modal,Input,Alert} from 'antd';
/** 配置编辑是显式操作，不覆盖已保存的修订文件。 */
export function ConfigurationDialog({open,onCancel,onApply}) {
 const [text,setText]=useState(''),[error,setError]=useState('');
 return <Modal open={open} title="应用外部配置" onCancel={onCancel} onOk={async()=>{try{await onApply(JSON.parse(text));setError('');}catch(e){setError(e.message);}}} okText="校验并应用" width={700} destroyOnHidden maskClosable>
 <Input.TextArea aria-label="外部配置 JSON" rows={16} value={text} onChange={e=>setText(e.target.value)}/>{error&&<Alert type="error" message={error}/>}</Modal>;
}
