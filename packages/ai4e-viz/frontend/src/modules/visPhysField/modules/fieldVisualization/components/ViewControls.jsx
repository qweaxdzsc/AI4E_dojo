/** 旋转、平移、缩放、标准视图和适合窗口控制组件。 */

import { Button, Space } from 'antd';
import useFieldView from '../hooks/useFieldView.js';

/** 渲染最小视图控制入口，具体相机参数由一级状态编排。 */
export default function ViewControls() {
  const setView = useFieldView();
  return <Space><Button onClick={() => setView({ preset: 'front' })}>前视</Button><Button onClick={() => setView({ fit: true })}>适合窗口</Button></Space>;
}
