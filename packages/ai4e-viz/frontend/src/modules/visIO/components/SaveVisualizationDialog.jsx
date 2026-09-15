/** 保存表单只选择名称，目标任务由上下文明确提供。 */
import { useState } from 'react';
import { Modal, Input } from 'antd';

/** 显示保存目标并提交配置，冲突由上层保留旧资产处理。 */
export default function SaveVisualizationDialog({ open, target, initialName, onSave, onCancel }) {
  const [name, setName] = useState(initialName || '三维物理场');
  return <Modal title="保存可视化配置" open={open} onCancel={onCancel} onOk={() => onSave(name)} okButtonProps={{ disabled: !name.trim() }} destroyOnClose><p>目标任务：{target?.task_id}</p><p>保存来源引用、处理与显示配置。</p><Input aria-label="可视化名称" value={name} onChange={(e) => setName(e.target.value)} /></Modal>;
}
