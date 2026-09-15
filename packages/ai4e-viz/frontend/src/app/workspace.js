/** 应用壳展示的当前工作区和后台任务快照；不包含领域模块数据。 */

export const workspace = {
  id: 'ws-aero-07',
  name: '航空动力事业部',
  role: '管理员',
  user: '原力',
  storageUsedGB: 4.2,
  storageQuotaGB: 50,
};

export const runningTasks = [
  { id: 'task-8811', kind: '报告生成', target: 'rep-2026-0818-a', state: 'running' },
  { id: 'task-8813', kind: '导出（离线 HTML + PDF）', target: 'rep-2026-0814-b', state: 'running' },
  { id: 'task-8814', kind: '解析', target: 'heater_plate_v2.stl', state: 'queued' },
];
