/** 报告中心查询、版本、复制和导出API。 */

import { currentStorageContext } from '../visIO/index.js';
import { requestJson, resourceUrl } from '../../infrastructure/http/client.js';

export const apiReports = () => requestJson('/api/reports');
export const apiReport = (reportId) => requestJson(`/api/reports/${encodeURIComponent(reportId)}`);
export const apiReportSnapshot = (reportId, version) => requestJson(`/api/report-snapshots/${encodeURIComponent(reportId)}/versions/${encodeURIComponent(version)}`);
export const apiCreateReport = (payload) => requestJson('/api/reports', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
export const apiDuplicateReport = (reportId, payload = {}) => requestJson(`/api/reports/${encodeURIComponent(reportId)}/duplicate`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
export const apiCreateReportExport = (reportId, payload) => requestJson(`/api/reports/${encodeURIComponent(reportId)}/exports`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({...payload, context_id: currentStorageContext() || undefined}) });
export const apiReportExport = (exportId) => requestJson(`/api/report-exports/${encodeURIComponent(exportId)}`);
export const apiRetryReportExport = (exportId) => requestJson(`/api/report-exports/${encodeURIComponent(exportId)}/retry`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({context_id: currentStorageContext() || undefined}) });
export const reportExportDownloadUrl = (exportId) => resourceUrl(`/api/report-exports/${encodeURIComponent(exportId)}/download`);
