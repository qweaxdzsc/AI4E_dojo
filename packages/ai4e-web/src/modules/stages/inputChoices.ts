/** 阶段输入候选的展示规则，不改变资产身份或服务数据。 */
/** 同一清单只作为一条选项；平台名称优先并按登记时间倒序，避免与任务历史共用 asset_id 导致点一项选中多项。 */
export function bindingOptionKey(item: any) {
  return [
    item.origin || "run",
    item.source_project || "",
    item.shared_asset_id || "",
    item.ref?.asset_id,
    item.processed_name || item.run_id || "",
    item.name,
  ].join(":");
}

function choiceTime(item: any) {
  return String(item.created_at || "");
}

function byNewest(left: any, right: any) {
  return (
    choiceTime(right).localeCompare(choiceTime(left)) ||
    String(left.name || "").localeCompare(String(right.name || ""))
  );
}

/** 已准备完成的数据集只展示用户登记的名称，不显示运行短号或 JSON 文件名。 */
export function preparedDatasetLabel(item: any) {
  const name = String(item?.processed_name || "").trim();
  if (name) return name;
  const fallback = String(item?.name || "").trim();
  if (fallback && !/\.json$/i.test(fallback) && fallback !== "已绑定来源不可用")
    return fallback;
  return "未命名数据集";
}

/** 只有当前绑定失效才报警；目录里空的共享名或未选用的坏项不冒充已绑定来源。 */
export function unavailableBindingItems(inputs: any[], bindingKeys: string[]) {
  const alerts: any[] = [];
  for (const binding of bindingKeys) {
    const items = inputs.filter((item) => item.binding === binding);
    const selected = items.find((item) => item.selected);
    if (selected) {
      if (!selected.ref || selected.compatibility?.status === "invalid") {
        alerts.push(selected);
      }
      continue;
    }
    if (
      items.some((item) => item.ref && item.compatibility?.status !== "invalid")
    ) {
      continue;
    }
    const broken = items.find(
      (item) => !item.ref && item.compatibility?.status === "invalid",
    );
    if (broken) alerts.push(broken);
  }
  return alerts;
}

export function uniqueManifestChoices(items: any[]) {
  const valid = items.filter(
    (item) => item.ref && item.compatibility?.status !== "invalid",
  );
  const platform = valid
    .filter((item) => item.origin === "platform")
    .slice()
    .sort(byNewest);
  const used = new Set(platform.map((item) => item.ref.asset_id));
  return [
    ...platform,
    ...valid
      .filter(
        (item) => item.origin !== "platform" && !used.has(item.ref.asset_id),
      )
      .slice()
      .sort(byNewest),
  ];
}
