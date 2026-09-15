/** 可视化任务管理模块路由和导航元数据。 */

export const visTaskManageModule = Object.freeze({ name: 'visTaskManage', navigation: { key: 'recommendations', label: '可视化推荐', mobileLabel: '推荐', to: '/recommendations/scalar' }, routes: ['/recommendations/:kind', '/examples/:artifactId', '/specs', '/specs/:specId/v/:version', '/assets/:artifactId/visualizations/new/:recommendationId', '/visualizations/:visualizationId', '/visualizations/:visualizationId/edit'] });
