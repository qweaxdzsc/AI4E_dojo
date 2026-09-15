/** 物理场二维表格概览组件；分页数据由一级Hook提供。 */

import { Table } from 'antd';

/** 渲染已由Hook准备好的二维表格数据。 */
export default function DataOverviewTable({ columns = [], rows = [] }) {
  return <Table columns={columns} dataSource={rows} pagination={{ pageSize: 200 }} />;
}
