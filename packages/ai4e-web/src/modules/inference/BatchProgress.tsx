import { Button, Empty, Progress, Select, Tag } from "antd";
import { statusLabel, terminal, type Batch } from "./model";
/** 只按服务已提交数量展示进度，不按时间插值。 */
export function BatchProgress({
  batches,
  active,
  onSelect,
  detail,
  busy,
  onCancel,
  onRetry,
  onRecover,
  onLog,
}: {
  batches: Batch[];
  active: string;
  onSelect: (id: string) => void;
  detail?: Batch;
  busy: boolean;
  onCancel: () => void;
  onRetry: () => void;
  onRecover: () => void;
  onLog: (run: string) => void;
}) {
  return (
    <section className="infer-card">
      <div className="infer-tools">
        <h3>推理批次</h3>
        <Select
          aria-label="推理批次"
          placeholder="选择已提交批次"
          value={active || undefined}
          onChange={onSelect}
          options={batches.map((b) => ({
            value: b.id,
            label: (b.name || b.id) + " · " + statusLabel(b.status),
          }))}
        />
        <Button
          disabled={!detail || terminal(detail.status) || busy}
          onClick={onCancel}
        >
          取消批次
        </Button>
        <Button
          disabled={
            !detail ||
            !terminal(detail.status) ||
            !detail.children.some((c) =>
              [
                "failed",
                "stopped",
                "interrupted",
                "canceled",
                "cancelled",
              ].includes(c.status),
            ) ||
            busy
          }
          onClick={onRetry}
        >
          重试失败子运行
        </Button>
        <Button
          disabled={detail?.status !== "interrupted" || busy}
          onClick={onRecover}
        >
          恢复中断批次
        </Button>
      </div>
      {detail ? (
        <>
          <div className="infer-tools">
            <Tag color={detail.status === "succeeded" ? "green" : "blue"}>
              {statusLabel(detail.status)}
            </Tag>
            <span>
              {detail.inherited_children?.length ? "本次重试样本完成" : "样本结果完成"} {detail.completed ?? "—"} / {detail.total ?? "—"}
            </span>
            {!!detail.inherited_children?.length && <span>保留原批次 {detail.inherited_children.length} 个成功子运行</span>}
            {detail.error && <span role="alert">{detail.error}</span>}
          </div>
          <div className="infer-table-scroll">
            <table className="infer-table">
              <thead>
                <tr>
                  <th>检查点 / 分片</th>
                  <th>状态</th>
                  <th>样本进度</th>
                  <th>当前操作</th>
                  <th>运行</th>
                </tr>
              </thead>
              <tbody>
                {[...(detail.inherited_children || []), ...detail.children].map((c, i) => {
                  const p = c.progress || {};
                  const done = p.completed ?? p.completed_samples;
                  const total = p.total ?? p.total_samples;
                  return (
                    <tr key={c.id || c.run_id || i}>
                      <td>
                        {c.checkpoint?.name || c.checkpoint?.id || "未记录"} · {c.split||"历史分片"}
                      </td>
                      <td>
                        {statusLabel(c.status)}{c.inherited && "（沿用固定结果）"}
                        {c.error && (
                          <div role="alert">
                            {typeof c.error === "string"
                              ? c.error
                              : JSON.stringify(c.error)}
                          </div>
                        )}
                      </td>
                      <td>
                        {done != null && total > 0 ? (
                          <>
                            <Progress
                              percent={Math.min(
                                100,
                                Math.round((100 * done) / total),
                              )}
                              size="small"
                            />
                            <small>
                              {done} / {total}
                            </small>
                          </>
                        ) : (
                          "尚无进度记录"
                        )}
                      </td>
                      <td>
                        {p.operation || p.stage || "—"}{" "}
                        {p.sample || p.sample_id || ""}
                      </td>
                      <td>
                        <Button
                          size="small"
                          disabled={!c.run_id}
                          onClick={() => onLog(c.run_id)}
                        >
                          查看日志
                        </Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        <Empty description="请选择批次查看进度与结果" />
      )}
    </section>
  );
}
