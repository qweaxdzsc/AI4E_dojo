import { Alert, Button, Tag } from "antd";
import { useEffect, useState } from "react";
import { stop, subscribe } from "./api";
/** 事件重连只同步日志，绝不重复提交运行。 */
export function ExecutionLog({
  project,
  run,
}: {
  project: string;
  run?: string;
}) {
  const [value, setValue] = useState<any>(),
    [connection, setConnection] = useState("等待运行"),
    [error, setError] = useState("");
  useEffect(() => {
    setValue(undefined);
    if (!run) return;
    const stream = subscribe(project, run);
    stream.onopen = () => setConnection("已连接");
    stream.onmessage = (e) => {
      const v = JSON.parse(e.data);
      setValue(v);
      if (["succeeded", "failed", "stopped"].includes(v.status)) {
        stream.close();
        setConnection("运行已结束");
      }
    };
    stream.onerror = () =>
      setConnection("连接中断，正在重连（运行状态待核对）");
    return () => stream.close();
  }, [project, run]);
  return (
    <section className="execution-log">
      <div className="panel-title">
        <b>执行日志</b>
        <Tag>{value?.status || connection}</Tag>
        <span>{connection}</span>
        <Button
          disabled={
            !run || ["succeeded", "failed", "stopped"].includes(value?.status)
          }
          onClick={() =>
            run && stop(project, run).catch((e) => setError(e.message))
          }
        >
          停止运行
        </Button>
      </div>
      {error && <Alert type="error" message={error} />}
      <pre>{value?.text || "运行开始后显示真实日志"}</pre>
    </section>
  );
}
