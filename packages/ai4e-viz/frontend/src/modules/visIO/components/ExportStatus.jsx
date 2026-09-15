/** 输出状态来自已提交清单，失败不展示成功下载。 */
import { Button, Alert } from 'antd';

/** 通用输出交付展示，不实现物理场算法。 */
export default function ExportStatus({ output, fileUrl, onCancel }) {
  if (!output) return null;
  return <div role="status">导出：{({running:'正在生成',succeeded:'已完成',failed:'失败',canceled:'已取消'})[output.status] || output.status}{output.progress && ` · ${output.progress.completed}/${output.progress.total} 帧`}{output.status === 'running' && <Button onClick={onCancel}>取消</Button>}{output.error && <Alert type="error" message={output.error} />}{output.status === 'succeeded' && output.files.map((file) => <a key={file.name} href={fileUrl(file.name)} download style={{ marginLeft: 12 }}>{file.name}</a>)}</div>;
}
