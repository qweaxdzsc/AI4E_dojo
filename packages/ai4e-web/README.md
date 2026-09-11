# Dojo Web

React / TypeScript / Vite / Ant Design 正式平台，以 docs/prototypes/dojo-web-integrated.html 为唯一交互布局基准。项目任务管理、原始处理、准备、模型、训练设置、运行监控、后处理和固定比较接入真实服务；报告发布与批量研究执行尚未开放，历史报告记录保留。

```bash
npm ci --prefix packages/ai4e-web
npm run --prefix packages/ai4e-web dev
npm run --prefix packages/ai4e-web build
npm run --prefix packages/ai4e-web check:architecture
```

先按 ai4e-server/README.md 启动 API，默认8000，再打开 http://127.0.0.1:5173。`DOJO_API_URL=http://127.0.0.1:8002` 可指定开发代理目标。生产 dist 用服务 --web-dist 同源托管。

新建任务只选择服务实际登记的数据集与模型案例；ShapeNet 目录和 NASA 三个来源文件在原始处理页用受控浏览绑定，创建和编辑弹窗不接受数据路径。字段提取容器支持增删条目、多个独立输出和实际字段成员；输出 PT/Zarr 格式位于阶段配置，弹窗不保存目录或格式。准备统计只读，模型采样位于模型页面，实际能力约束不可编辑。检查、试跑、正式运行分开；训练与后处理选择既有正式产物。监控和图表只显示真实记录，缺失耗时/峰值显存明确不可用。

统一预览/三维工作区通过受控资产和辅助操作接口使用 viz；保存场景固定源修订。服务取消和重启状态均可查询。保留 server 启动 root 才能恢复项目、场景与比较；刷新浏览器不丢失已保存配置。

自动化浏览器使用已安装 Chrome，不需要人工手点：

```bash
DOJO_API_URL=http://127.0.0.1:8002 DOJO_WEB_URL=http://127.0.0.1:5174 npm run --prefix packages/ai4e-web test:e2e -- platform-integrated.spec.ts
uv run packages/ai4e-web/scripts/generate-contracts.py
```

platform-integrated 用例消费总链路记录中的真实汽车案例，要求 `.context/mvp/web-integrated-results/shapenet_car_transolver3_surface.json` 对应服务数据仍存在。它验证正式产物选择、配置保存恢复、真实后处理指标、提取取消，并记录同视口原型结构差异；不将局部几何检查宣称逐像素验收。visualization-views 用例的真实来源由 DOJO_VIZ_ROOT/DOJO_VIZ_FILE 指定。rawprep.spec 已迁移为真实字段多输出、正式页面处理与网格预览；model-inspection.spec 通过页面选择冻结准备输入并检查 TorchVista 沙箱图节点。

实际范围与待验收项见 ../../.context/mvp/web-integrated-acceptance.md，历史首期证据保留不改写。

请求按钮统一使用 `infrastructure/components/ActionButton.tsx`：进行中以原生禁用和 `aria-busy` 表示，加载图标只作装饰且结束直接移除。快速保存不会因图标离场动画改变按钮名称。`platform-integrated.spec.ts` 包含持有真实服务器响应的进行中断言和连续快速保存回归；该回归须在不启用 trace 的正常速度下通过。

项目首页沿用整合原型的范围筛选、工具栏、两列封面卡和进入项目入口。`public/project-covers` 保留原型装饰封面字节；项目任务数与基线读取真实任务记录，未记录负责人/领域明确显示缺失状态。`/workbench` 提供项目选择、真实任务列表、新建任务和经服务核对的最近任务继续入口；侧边菜单整行可点击并根据当前页面标记选中。任务表的八步入口对应真实任务身份。
