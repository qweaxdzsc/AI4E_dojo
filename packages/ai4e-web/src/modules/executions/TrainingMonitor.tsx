import { ActionButton as Button } from "../../infrastructure/components/ActionButton";
import { Alert, Card, Modal, Select, Space, Table, Tabs } from "antd";
import { SettingOutlined } from "@ant-design/icons";
import { useEffect, useState } from "react";
import { list, metrics } from "./api";
import "./executions.css";
import { ExecutionLog } from "./ExecutionLog";

function trainRuns(rows: any[]) {
  return rows.filter((item: any) =>
    (item.stages || Object.keys(item.summary?.reports || {})).includes("train"),
  );
}

function latestId(rows: any[]) {
  return [...rows].sort((a, b) =>
    String(b.created_at || b.created || "").localeCompare(
      String(a.created_at || a.created || ""),
    ),
  )[0]?.id;
}

function metricValue(value: unknown) {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (value && typeof value === "object" && typeof (value as any).value === "number")
    return Number.isFinite((value as any).value) ? (value as any).value : undefined;
  return undefined;
}

/** 最新一轮的在线分项与测试评估分开列出，不把训练批损失当成测试集结果。 */
function indicatorRows(last: any) {
  const rows: { key: string; source: string; name: string; value: number }[] = [];
  const online = last?.online && typeof last.online === "object" ? last.online : {};
  for (const [name, raw] of Object.entries(online)) {
    if (name === "loss") continue;
    const value = metricValue(raw);
    if (value === undefined) continue;
    rows.push({ key: "online:" + name, source: "在线", name, value });
  }
  const evaluation =
    last?.evaluation?.metrics && typeof last.evaluation.metrics === "object"
      ? last.evaluation.metrics
      : {};
  for (const [name, raw] of Object.entries(evaluation)) {
    const value = metricValue(raw);
    if (value === undefined) continue;
    rows.push({ key: "eval:" + name, source: "测试评估", name, value });
  }
  return rows;
}

/** 训练运行只监控已提交运行，不在此页选择数据或开训。 */
export function TrainingMonitor({
  project,
  task,
  initialRun,
}: {
  project: string;
  task: string;
  initialRun?: string;
}) {
  const [dimension, setDimension] = useState("loss");
  const [lossAxis, setLossAxis] = useState<"epoch" | "updates">("epoch");
  const [chartSettings, setChartSettings] = useState(false);
  const chartLabel = { loss: "Loss", learning_rate: "学习率" }[dimension] || "Loss";
  const [runs, setRuns] = useState<any[]>([]);
  const [run, setRun] = useState<string | undefined>(initialRun);
  const [value, setValue] = useState<any>();
  const [error, setError] = useState("");
  useEffect(() => {
    let live = true;
    list(project, task)
      .then((rows) => {
        if (!live) return;
        const candidates = trainRuns(rows);
        setRuns(candidates);
        setRun((current) => {
          if (initialRun && candidates.some((item) => item.id === initialRun))
            return initialRun;
          if (current && candidates.some((item) => item.id === current)) return current;
          return latestId(candidates);
        });
      })
      .catch((e) => live && setError(e.message));
    return () => {
      live = false;
    };
  }, [project, task, initialRun]);
  useEffect(() => {
    setValue(undefined);
    setError("");
    if (!run) return;
    let live = true;
    const read = () =>
      metrics(project, run)
        .then((v) => live && setValue(v))
        .catch((e) => live && setError(e.message));
    void read();
    const timer = setInterval(read, 1500);
    return () => {
      live = false;
      clearInterval(timer);
    };
  }, [project, run]);
  const history = value?.history || [];
  const curves = value?.curves || {};
  const curveRows = dimension === "loss" ? curves.loss : curves.learning_rate;
  const series = (Array.isArray(curveRows) && curveRows.length ? curveRows : history)
    .map((row: any) => ({ ...row, value: row.value ?? row[dimension] }))
    .filter((row: any) => Number.isFinite(row.value));
  const axis = dimension === "loss" ? lossAxis : "updates";
  const plotted = series.filter((row: any) => Number.isFinite(row[axis]));
  const xs = plotted.map((r: any) => r[axis]),
    ys = plotted.map((r: any) => r.value);
  const xmin = Math.min(...xs),
    xmax = Math.max(...xs),
    ymin = Math.min(...ys),
    ymax = Math.max(...ys);
  const x = (v: number) =>
    xs.length === 1 || xmin === xmax ? 420 : 50 + ((v - xmin) / (xmax - xmin)) * 740;
  const y = (v: number) =>
    ymin === ymax ? 125 : 220 - ((v - ymin) / (ymax - ymin)) * 180;
  const points = plotted.map((row: any) => x(row[axis]) + "," + y(row.value)).join(" ");
  const last = history.at(-1),
    indicators = indicatorRows(last);
  return (
    <div className="training-monitor">
      <section className="run-summary">
        <div className="run-summary-header">
          <h2>训练运行监控</h2>
          <span className="run-badge">{value?.status || "尚无运行"}</span>
        </div>
        <Space wrap id="stage-handoff" align="center">
          <Select
            aria-label="查看运行"
            style={{ width: 300 }}
            placeholder="查看运行"
            value={run}
            options={runs.map((item) => ({
              value: item.id,
              label: item.id.slice(0, 8) + " · " + item.status,
            }))}
            onChange={setRun}
          />
        </Space>
        <div className="monitor-kpis run-numbers">
          {[
            ["当前 epoch", last?.epoch ?? "尚无记录"],
            ["优化步数", last?.updates ?? "尚无记录"],
            [
              "开始时间",
              value?.created_at ? new Date(value.created_at).toLocaleString() : "—",
            ],
            [
              "进程 CPU",
              value?.resources ? value.resources.cpu_percent + "%" : "尚无记录",
            ],
            [
              "进程常驻内存",
              value?.resources
                ? (value.resources.resident_bytes / 1024 / 1024).toFixed(1) + " MB"
                : "尚无记录",
            ],
          ].map(([label, v]) => (
            <div key={label} className="run-number">
              <small>{label}</small>
              <strong>{v}</strong>
            </div>
          ))}
        </div>
      </section>
      <div className="run-grid monitor-grid">
        <div className="run-left">
          <Card title="训练曲线">
            <Space style={{ marginBottom: 8 }}>
              <span>Loss 横轴</span>
              <Select
                aria-label="Loss 横轴"
                value={lossAxis}
                options={[{ value: "epoch", label: "epoch" }, { value: "updates", label: "更新步" }]}
                onChange={setLossAxis}
              />
            </Space>
            <Tabs
              activeKey={dimension}
              onChange={(key) => { setDimension(key); setChartSettings(false); }}
              items={[
                { key: "loss", label: "Loss" },
                { key: "learning_rate", label: "学习率" },
              ]}
              tabBarExtraContent={<Button type="text" aria-label={`${chartLabel}曲线配置`} icon={<SettingOutlined />} onClick={() => setChartSettings(true)} />}
            />
            {plotted.length ? (
              <svg role="img" aria-label={`真实训练 ${chartLabel} 曲线`} viewBox="0 0 840 270">
                <path d="M50 25V220H800" stroke="#cddcf1" fill="none" />
                {[0, 0.5, 1].map((t) => (
                  <g key={t}>
                    <line
                      x1="50"
                      x2="800"
                      y1={40 + t * 180}
                      y2={40 + t * 180}
                      stroke="#edf2fa"
                    />
                    <text x="4" y={44 + t * 180} fontSize="10">
                      {(ymax - t * (ymax - ymin)).toPrecision(3)}
                    </text>
                    <text
                      x={50 + t * 740}
                      y="245"
                      fontSize="10"
                      textAnchor={t === 1 ? "end" : "start"}
                    >
                      {(xmin + t * (xmax - xmin)).toLocaleString()}
                    </text>
                  </g>
                ))}
                <polyline
                  points={points}
                  fill="none"
                  stroke="#1677ff"
                  strokeWidth="2"
                />
                {plotted.map((row: any, i: number) => (
                  <circle
                    key={i}
                    data-coordinate={row[axis]}
                    data-value={row.value}
                    cx={x(row[axis])}
                    cy={y(row.value)}
                    r="3"
                    fill="#1677ff"
                  >
                    <title>
                      {axis} {row[axis]} · {chartLabel} {row.value}
                    </title>
                  </circle>
                ))}
                <text x="400" y="265" fontSize="11">
                  {axis === "updates" ? "优化步数" : "epoch"}
                </text>
                <text x="680" y="18" fontSize="11" fill="#1677ff">
                  ● {chartLabel}
                </text>
              </svg>
            ) : (
              <div className="empty-record">
                {dimension === "loss" ? "尚无已记录的训练曲线" : `尚无已记录的${chartLabel}曲线`}
                <br />
                <small>只展示运行实际记录的数据</small>
              </div>
            )}
          </Card>
          <Card title="在线诊断与测试评估">
            {indicators.length ? (
              <Table
                rowKey="key"
                pagination={false}
                dataSource={indicators}
                columns={[
                  { title: "来源", dataIndex: "source" },
                  { title: "指标", dataIndex: "name" },
                  { title: "最新值", dataIndex: "value" },
                ]}
              />
            ) : (
              <div className="empty-record">
                尚无在线分项或测试评估
                <br />
                <small>不从日志拼数；关闭测试评估时仍可在本轮后看到在线分项</small>
              </div>
            )}
          </Card>
        </div>
        <div className="run-right">
          <ExecutionLog project={project} run={run} />
          <Card title="快捷操作">
            <Space>
              <Button disabled>生成评估报告（未开放）</Button>
            </Space>
          </Card>
        </div>
      </div>
      <Modal title={`${chartLabel}曲线配置`} open={chartSettings} onCancel={() => setChartSettings(false)} footer={null}>
        <div style={{ minHeight: 120 }} />
      </Modal>
      {error && <Alert type="error" message={error} />}
    </div>
  );
}
