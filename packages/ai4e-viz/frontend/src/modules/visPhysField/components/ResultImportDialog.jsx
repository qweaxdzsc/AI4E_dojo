/** 在任务产物、共享数据集和已挂数据根内选择可视化网格。 */
import {useEffect,useState} from 'react';
import {Modal,Tree,Alert,Upload,Button} from 'antd';

function toNode(item){
 return {
  ...item,
  key:item.id||`${item.root}:${item.path||item.name}`,
  title:item.name||item.filename||item.path,
  isLeaf:item.leaf===true,
 };
}

function replaceChildren(nodes,key,children){
 return nodes.map(node=>{
  if(node.key===key)return {...node,children};
  if(node.children)return {...node,children:replaceChildren(node.children,key,children)};
  return node;
 });
}

/** 目录必须展开到具体网格成员；非网格后缀不出现。 */
export function ResultImportDialog({open,items=[],onCancel,onImport,onBrowse,onUpload}) {
 const [tree,setTree]=useState([]);
 const [selected,setSelected]=useState();
 useEffect(()=>{if(open){setTree((items||[]).map(toNode));setSelected();}},[open,items]);
 const load=async node=>{
  if(!onBrowse||node.isLeaf||(node.children&&node.children.length))return;
  const result=await onBrowse(node.root,node.path||'');
  const children=(result.items||result||[]).map(toNode);
  setTree(current=>replaceChildren(current,node.key,children));
 };
 return <Modal open={open} title="导入结果" onCancel={onCancel} onOk={()=>selected&&onImport(selected)} okButtonProps={{disabled:!selected?.isLeaf}} destroyOnHidden maskClosable>
  <Alert type="info" message="只能从任务产物、共享数据集和已挂数据根里选择可视化网格，目录必须选到具体文件。"/>
  {onUpload&&<Upload showUploadList={false} beforeUpload={async file=>{const item=await onUpload(file);if(item)setSelected(toNode(item));return false;}}><Button style={{marginTop:12}}>上传本地结果</Button></Upload>}
  <Tree style={{marginTop:16}} treeData={tree} loadData={onBrowse?node=>load(node):undefined} onSelect={(_,info)=>setSelected(info.node)}/>
 </Modal>;
}
