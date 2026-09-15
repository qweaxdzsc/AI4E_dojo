---
name: html-to-react
description: Converts HTML/CSS prototypes or UI mockups into production React + Ant Design 5.x code. Use when migrating HTML to React, converting UI prototypes or screenshots to React components, or when the user provides HTML/CSS files or design specs for React + antd implementation.
---

# HTML 转 React（Ant Design 5.x）

将 UI 原型（HTML+CSS 文件或截图）还原为生产级 React + Ant Design 5.x 代码时，按本技能执行。

## 核心原则

1. **原型当设计稿**：不直接迁移原型中的 HTML/CSS，用 antd 组件重新实现，仅在必要时补充自定义样式。
2. **优先 antd 组件**：使用 Button、Table、Form、Modal、Card、Flex、Space、Grid 等，不用原生 HTML 标签造轮子。
3. **体验一致、实现规范**：保留原型视觉效果和交互，代码结构符合 React + antd 最佳实践。

## 样式调整优先级（严格按顺序）

| 优先级 | 方式 | 说明 |
|--------|------|------|
| 第一 | ConfigProvider 的 `theme.token` | 全局 Design Token（颜色、圆角、间距、字体等） |
| 第二 | 组件 API + `className` / `styles` | `size`、`variant`、`type` 及组件级样式 |
| 第三 | CSS Modules | 局部样式覆盖。**禁止**直接覆盖 antd 内部类名（如 `.ant-btn-xxx`），antd 5.x 的 CSS-in-JS 会导致类名不稳定 |

## 何时写自定义组件

仅当 antd 无对应组件时（如高度定制的动画卡片、独特可视化模块），才用原生 HTML+CSS 写 React 组件。要求：

- 放在独立文件中
- 用 CSS Modules 管理样式
- props 接口清晰

## 代码规范

- 函数式组件 + Hooks
- 组件拆分合理，单文件不超过 200 行
- 布局优先用 antd 的 Flex、Grid，不手写 flexbox（除非 antd 无法满足）
- 文案抽成常量或 i18n key，不硬编码在 JSX
- TypeScript 类型完整

## 输出格式

对每个页面/组件，输出：

1. **Theme 配置**：若需调整 token，给出 ConfigProvider 的 `theme` 配置
2. **组件代码**：React 组件实现
3. **CSS Module**：若需要，给出对应 `.module.css` 文件
4. **设计说明**：简要说明还原决策、与原型差异及原因
