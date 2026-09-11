import { Alert } from "antd";
import React from "react";
/** 隔离页面异常，保留明确的恢复入口。 */
export class ErrorBoundary extends React.Component<
  React.PropsWithChildren,
  { error: string }
> {
  state = { error: "" };
  static getDerivedStateFromError(e: Error) {
    return { error: e.message };
  }
  render() {
    return this.state.error ? (
      <Alert
        type="error"
        message={this.state.error}
        description="请刷新页面重新读取服务记录"
      />
    ) : (
      this.props.children
    );
  }
}
