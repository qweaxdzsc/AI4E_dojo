import { Empty } from "antd";
/** 尚未交付的阶段没有执行按钮。 */
export function UnavailablePanel() {
  return <Empty description="本轮未开放 · 入口保留，不提供示意执行" />;
}
