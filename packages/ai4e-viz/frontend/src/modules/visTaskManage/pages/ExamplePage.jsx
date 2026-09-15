/** 可视化案例页面：展示单个数据资产的可运行表现。 */

import { Button } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { Link, useParams } from 'react-router-dom';
import ExamplePreview from '../components/ExamplePreview.jsx';
import PageTitle from '../../../infrastructure/components/PageTitle.jsx';

export default function ExamplePage() {
  const { artifactId } = useParams();
  return <div className="workspace-page"><PageTitle title="默认参数预览" description="使用数据资产与系统推荐方法的默认参数生成；该页面不是已保存的可视化结果。" actions={<Link to="/recommendations"><Button icon={<ArrowLeftOutlined />}>返回推荐目录</Button></Link>} /><ExamplePreview artifactId={artifactId} /></div>;
}
