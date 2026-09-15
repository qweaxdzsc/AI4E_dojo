import { Button, Tag } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';

const states = {
  live: ['success', 'LIVE', '实时服务'],
  stale: ['warning', 'STALE', '最近快照'],
  offline: ['default', 'OFFLINE', '离线'],
  partial: ['warning', 'PARTIAL', '部分完成'],
  error: ['error', 'ERROR', '失败']
};

export default function ConnectionStatus({ state = 'offline', updatedAt, onRetry, compact = false }) {
  const [color, code, label] = states[state] ?? states.offline;
  return (
    <div className="connection-status" role="status" aria-live="polite">
      <Tag color={color} bordered={false}>{code}</Tag>
      {compact ? null : <span>{label}{updatedAt ? ` · 更新于 ${new Date(updatedAt).toLocaleString('zh-CN', { hour12: false })}` : ''}</span>}
      {onRetry && state !== 'live' ? <Button type="text" size="small" icon={<ReloadOutlined />} onClick={onRetry}>重试</Button> : null}
    </div>
  );
}
