"""物理场工作台查询导出控制；共享原工作台状态。"""


class ExportControls:
    """通过显式工作台引用访问共享场景，不创建第二份会话。"""

    def __init__(self, workbench):
        self.workbench = workbench

    def query(self, operation="probe"):
        """查询选定 Probe 的当前数值或时间曲线。"""
        node = self.workbench.object()
        if not node or "position" not in node:
            return
        result = self.workbench.command(
            {"operation": operation, "input": node["input"], "positions": [node["position"]]}
        )
        if result:
            self.workbench.show_rows(result["rows"])
            from ..modules.dataOverview.basicCharts import history_curve

            self.workbench.server.state.query_curve = (
                history_curve(result["rows"]) if operation == "temporal" else ""
            )

    def show_rows(self, rows):
        """展示可读字段表，保留域外与缺帧状态而不填零。"""
        node = self.workbench.object() or {}
        items = []
        for row in rows:
            prefix = f"t={row['time']:g} · " if "time" in row else ""
            values = row.get("fields") or row.get("values") or {}
            items.append(
                {
                    "field": prefix + "位置",
                    "value": ", ".join(f"{x:g}" for x in row.get("position", [])),
                }
            )
            items.append(
                {
                    "field": prefix + "状态",
                    "value": "有效"
                    if row.get("valid")
                    else "缺帧"
                    if row.get("status") == "missing_frame"
                    else "域外或来源不可用",
                }
            )
            selected = set(node.get("fields") or [])
            for key, value in values.items():
                if selected and key not in selected:
                    continue
                items.append(
                    {
                        "field": prefix + key,
                        "value": ", ".join(f"{v:.6g}" for v in value)
                        if isinstance(value, list)
                        else str(value),
                    }
                )
        self.workbench.server.state.query_table = items

    def export_probe(self):
        """Probe 导出当前点；线段提取导出当前折线图的 X + 所选 Y。"""
        node = self.workbench.object() or {}
        if node.get("type") == "plot_over_line":
            self.workbench.prepare_line_chart_export()
        else:
            self.workbench.query()
        self.workbench.request("export_csv")
