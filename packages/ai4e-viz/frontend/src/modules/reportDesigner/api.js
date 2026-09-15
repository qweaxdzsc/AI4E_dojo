/** 报告草稿、冻结和编排导出API。 */

import { requestJson } from '../../infrastructure/http/client.js';

export const apiReportDraft = (reportId) => requestJson(`/api/reports/${encodeURIComponent(reportId)}/draft`);
export const apiSaveReportDraft = (reportId, payload) => requestJson(`/api/reports/${encodeURIComponent(reportId)}/draft`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
export const apiFreezeReport = (reportId, payload = {}) => requestJson(`/api/reports/${encodeURIComponent(reportId)}/versions`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
export const apiQuartoHealth = () => requestJson('/api/quarto/health');
