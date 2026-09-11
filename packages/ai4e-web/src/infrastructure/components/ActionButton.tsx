import { LoadingOutlined } from '@ant-design/icons';
import { Button, type ButtonProps } from 'antd';

/** 请求状态使用原生禁用和独立装饰图标，快速响应也不会留下加载图标的可访问名称。 */
export function ActionButton({loading=false, disabled, children, icon, ...props}: Omit<ButtonProps, 'loading'> & {loading?: boolean}) {
  return <Button {...props} aria-label={props['aria-label'] ?? (typeof children==='string'?children:undefined)} aria-busy={loading} disabled={disabled || loading} icon={loading ? <LoadingOutlined aria-hidden="true" /> : icon}>{children}</Button>;
}
