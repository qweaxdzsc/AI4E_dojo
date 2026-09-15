/** 可视化目录服务不可用时使用的确定性 5 家族、19 类型、23 方法快照。 */

const familyDefinitions = {
  PLT: ['分析图表', '比较、趋势、分布、不确定性与优化结果'],
  FLD: ['场与体数据', '规则栅格、三维体素或空间拓扑上的物理量'],
  ENT: ['实体与关系', '点集、轨迹以及节点—边关系'],
  GEO: ['几何与网格', '几何表面、边界与计算网格拓扑'],
  ASSET: ['报告资产', 'Markdown、静态图像与视频结果']
};

export const fallbackFamilies = Object.entries(familyDefinitions).map(([id, [label, description]]) => ({ id, label, description }));

const functionRows = [
  ['core.scalar-number@2.0.0', 'PLT', 'scalar', '数值指标', '直接显示一个关键值、单位和目标差异。', 'react', ['JSON', 'CSV', 'TSV', 'Parquet'], 'CASE-SCALAR-NUMBER', true, { precision: 2, unit: 'L/D', display_style: 'plain', value_color: '#1677FF', show_delta: true, show_target: true }],
  ['chart.echarts-scalar@2.1.0', 'PLT', 'scalar', '标量柱状图', '用单柱、目标线和标签比较当前值与基准。', 'echarts-svg', ['JSON', 'CSV', 'TSV', 'Parquet'], 'CASE-SCALAR-BAR', true, { precision: 2, unit: '%', orientation: 'vertical', bar_width: 48, baseline: 0, show_target: true, show_value_label: true }],
  ['table.perspective@2.0.0', 'PLT', 'table', '交互数据表', '筛选、排序和透视结构化记录。', 'perspective', ['CSV', 'TSV', 'JSON', 'Parquet', 'Arrow'], 'CASE-TABLE', true, { page_size: 50, density: 'normal', show_search: true, columns: [] }],
  ['chart.echarts-series@2.1.0', 'PLT', 'series', '序列趋势图', '比较时间、步数或坐标上的连续变化。', 'echarts-svg', ['CSV', 'TSV', 'JSON', 'Parquet'], 'CASE-SERIES', true, { x_scale: 'time', y_scale: 'linear', line_width: 2, show_symbols: false, zoom: true }],
  ['chart.echarts-distribution@2.1.0', 'PLT', 'distribution', '分布图', '显示集中区间、离散程度与长尾。', 'echarts-svg', ['CSV', 'JSON', 'Parquet', 'NPZ', 'NPY'], 'CASE-DISTRIBUTION', true, { bins: 24, orientation: 'vertical' }],
  ['chart.echarts-ensemble@2.1.0', 'PLT', 'ensemble', '集合带状图', '同时显示集合成员、均值和范围带。', 'echarts-svg', ['CSV', 'JSON', 'NPZ', 'NetCDF'], 'CASE-ENSEMBLE', true, { line_width: 2, show_legend: true }],
  ['chart.echarts-uncertainty@2.1.0', 'PLT', 'uncertainty', '不确定性区间图', '显示估计值、上下界与置信水平。', 'echarts-svg', ['CSV', 'JSON', 'NPZ'], 'CASE-UNCERTAINTY', true, { line_width: 2, show_symbols: true }],
  ['chart.echarts-matrix@2.1.0', 'PLT', 'matrix', '矩阵热力图', '用有序色阶读取二维矩阵结构。', 'echarts-svg', ['CSV', 'JSON', 'NPZ', 'NPY'], 'CASE-MATRIX', true, { colormap: 'coolwarm', aspect: 'equal' }],
  ['chart.echarts-tensor@2.1.0', 'PLT', 'tensor', '张量切片图', '选择分量和切片读取多维张量。', 'echarts-svg', ['NPZ', 'NPY', 'HDF5', 'NetCDF'], 'CASE-TENSOR', true, { slice_axis: 'z', slice_index: 0, colormap: 'viridis' }],
  ['chart.echarts-optimization@2.1.0', 'PLT', 'optimization', '优化候选图', '比较目标、约束和 Pareto 候选。', 'echarts-svg', ['CSV', 'JSON', 'Parquet'], 'CASE-OPTIMIZATION', true, { show_legend: true, show_tooltip: true }],
  ['scientific.raster-scalar@2.1.0', 'FLD', 'raster', '二维标量栅格', '用色图和等值线显示二维标量场。', 'trame-vtkjs', ['NPZ', 'NPY', 'VTI', 'TIFF', 'NetCDF'], 'CASE-RASTER-SCALAR', false, { scalar_field: 'pressure', representation: 'surface', colormap: 'viridis', contours: 12, show_colorbar: true }],
  ['scientific.raster-vector@2.1.0', 'FLD', 'raster', '二维矢量栅格', '用箭头、流线和幅值着色显示二维速度场。', 'trame-vtkjs', ['NPZ', 'NPY', 'VTI', 'NetCDF'], 'CASE-RASTER-VECTOR', false, { vector_components: ['u', 'v'], vector_style: 'streamlines', vector_density: 24, glyph_scale: 1, seed_count: 48 }],
  ['scientific.volume-scalar@2.1.0', 'FLD', 'volume', '三维标量体', '用体渲染、等值面和正交切片显示温度或压力。', 'trame-vtkjs', ['VTI', 'NRRD', 'NIfTI', 'NPZ', 'NetCDF'], 'CASE-VOLUME-SCALAR', false, { scalar_field: 'pressure', representation: 'volume', colormap: 'viridis', opacity: 0.72 }],
  ['scientific.volume-vector@2.1.0', 'FLD', 'volume', '三维矢量体', '用流线、箭头和幅值切片显示三维速度场。', 'trame-vtkjs', ['VTI', 'NPZ', 'NetCDF'], 'CASE-VOLUME-VECTOR', false, { vector_components: ['u', 'v', 'w'], vector_style: 'streamlines', vector_density: 20, glyph_scale: 0.8, seed_count: 64 }],
  ['scientific.field-scalar@2.1.0', 'FLD', 'field', '拓扑标量场', '在曲面或非规则网格上显示压力、温度、势场等标量。', 'trame-vtkjs', ['VTU', 'VTS', 'VTM', 'VTK', 'CGNS', 'NPZ'], 'CASE-FIELD-SCALAR', false, { scalar_field: 'pressure', representation: 'surface', colormap: 'coolwarm', show_edges: false }],
  ['scientific.field-vector@2.1.0', 'FLD', 'field', '拓扑矢量场', '在空间拓扑上显示速度矢量、流线与幅值。', 'trame-vtkjs', ['VTU', 'VTS', 'VTM', 'VTK', 'CGNS', 'NPZ'], 'CASE-FIELD-VECTOR', false, { vector_components: ['velocity_x', 'velocity_y', 'velocity_z'], vector_style: 'arrows', vector_density: 18, glyph_scale: 0.65, seed_count: 48 }],
  ['scientific.points@2.0.0', 'ENT', 'point_set', '三维点集', '按属性着色和缩放空间采样点。', 'trame-vtkjs', ['CSV', 'Parquet', 'PLY', 'VTU'], 'CASE-POINT-SET', false, { point_size: 4, colormap: 'viridis' }],
  ['scientific.trajectory@2.0.0', 'ENT', 'trajectory', '三维轨迹', '播放实体路径并按物理量着色。', 'trame-vtkjs', ['CSV', 'Parquet', 'JSON', 'VTU'], 'CASE-TRAJECTORY', false, { trail_length: 90, max_tracks: 64, playback_fps: 12 }],
  ['chart.echarts-graph@2.1.0', 'ENT', 'graph', '关系图', '显示节点、边、方向和依赖层级。', 'echarts-svg', ['JSON', 'CSV', 'GraphML'], 'CASE-GRAPH', true, { layout: 'force', node_size: 28, edge_width: 1.5, show_labels: true }],
  ['scientific.mesh@2.0.0', 'GEO', 'mesh', '三维几何查看', '旋转、缩放并检查几何表面、边线和装配部件。', 'o3dv', ['STL', 'PLY', 'OBJ', 'GLB', 'VTU→GLB', 'VTS→GLB', 'VTM→GLB'], 'CASE-MESH', true, { material_color: '#D6DEE8', show_edges: false, background_color: '#161A20', camera_projection: 'perspective', up_axis: 'y', auto_fit: true }],
  ['core.markdown@2.0.0', 'ASSET', 'text_document', '文档阅读', '安全渲染结构化文本和 Markdown。', 'browser-native', ['Markdown', 'TXT'], 'CASE-TEXT-DOCUMENT', true, { theme: 'report', show_toc: true, max_width: 820 }],
  ['media.image@2.0.0', 'ASSET', 'image', '图像查看', '显示原始图片、说明和替代文本。', 'browser-native', ['PNG', 'JPEG', 'SVG', 'WebP', 'TIFF'], 'CASE-IMAGE', true, { fit: 'contain', caption: '', alt_text: '' }],
  ['media.video@2.0.0', 'ASSET', 'video', '视频播放', '播放结果演化并保留 poster 与时间范围。', 'browser-native', ['MP4/H.264', 'WebM', 'MOV'], 'CASE-VIDEO', true, { controls: true, autoplay: false, loop: false, muted: true, start_time: 0 }]
];

export const fallbackFunctions = functionRows.map(([id, family, kind, label, description, renderer, accepted_formats, example_id, offline, default_parameters]) => {
  const [function_id, version] = id.split('@');
  return {
    id, function_id, version, family, label, description, compatible_kinds: [kind], renderer,
    accepted_formats, example_id, status: 'available', capabilities: { interactive: true, static: true, offline },
    schema_revision: '2026-08-25.2', default_parameters,
    parameter_schema: { $schema: 'https://json-schema.org/draft/2020-12/schema', type: 'object', additionalProperties: true, properties: Object.fromEntries(Object.keys(default_parameters).map((key) => [key, { title: key, default: default_parameters[key] }])) },
    ui_schema: { groups: [] }
  };
});

const functionById = new Map(fallbackFunctions.map((item) => [item.id, item]));
const kindRows = [
  ['scalar', 'PLT', '标量', '单个工程数值、目标比例或离散状态。', ['core.scalar-number@2.0.0', 'chart.echarts-scalar@2.1.0'], []],
  ['table', 'PLT', '表格', '共享字段结构的记录集合。', ['table.perspective@2.0.0'], ['A-1024', 'A-1032']],
  ['series', 'PLT', '序列', '按时间、step 或有序坐标排列的数据。', ['chart.echarts-series@2.1.0'], ['A-1025']],
  ['distribution', 'PLT', '分布', '原始样本或频数数据。', ['chart.echarts-distribution@2.1.0'], []],
  ['ensemble', 'PLT', '集合', '同一坐标系中的多个成员。', ['chart.echarts-ensemble@2.1.0'], []],
  ['uncertainty', 'PLT', '不确定性', '估计值及误差或区间。', ['chart.echarts-uncertainty@2.1.0'], []],
  ['matrix', 'PLT', '矩阵', '带行列标签的二维数值矩阵。', ['chart.echarts-matrix@2.1.0'], []],
  ['tensor', 'PLT', '张量', '带命名轴或分量的多维数组。', ['chart.echarts-tensor@2.1.0'], ['A-1026']],
  ['optimization', 'PLT', '优化', '目标、约束与候选方案。', ['chart.echarts-optimization@2.1.0'], []],
  ['raster', 'FLD', '栅格场', '二维规则网格上的标量或矢量物理量。', ['scientific.raster-scalar@2.1.0', 'scientific.raster-vector@2.1.0'], []],
  ['volume', 'FLD', '体数据', '三维体素网格上的标量或矢量物理量。', ['scientific.volume-scalar@2.1.0', 'scientific.volume-vector@2.1.0'], ['A-1028']],
  ['field', 'FLD', '物理场', '空间拓扑上的标量或矢量场。', ['scientific.field-scalar@2.1.0', 'scientific.field-vector@2.1.0'], ['A-1108']],
  ['point_set', 'ENT', '点集', '没有连续时间关系的空间采样点。', ['scientific.points@2.0.0'], []],
  ['trajectory', 'ENT', '轨迹', '实体或粒子的空间路径。', ['scientific.trajectory@2.0.0'], ['A-1029']],
  ['graph', 'ENT', '关系图', '节点与边组成的关系结构。', ['chart.echarts-graph@2.1.0'], []],
  ['mesh', 'GEO', '几何网格', '表面、边界或装配几何。', ['scientific.mesh@2.0.0'], ['A-1027', 'A-1031', 'A-1033', 'A-1114']],
  ['text_document', 'ASSET', '文本文档', '报告说明、方法与结论。', ['core.markdown@2.0.0'], []],
  ['image', 'ASSET', '静态图像', '图片或快照。', ['media.image@2.0.0'], []],
  ['video', 'ASSET', '视频', '结果演化或实验过程回放。', ['media.video@2.0.0'], []]
];

export const fallbackKinds = kindRows.map(([id, family, label, definition, method_ids, reference_example_ids]) => {
  const examples = method_ids.map((methodId) => {
    const method = functionById.get(methodId);
    return { id: method.example_id, name: method.label, method_id: methodId, case_type: 'open-source-reconstruction', case_type_label: '开源算例轻量重建' };
  });
  return { id, family, label, definition, method_ids, default_function: method_ids[0], reference_example_ids, example_ids: examples.map((item) => item.id), examples };
});

export const fallbackCatalog = {
  revision: 'visual-report-engine-v2.2026-08-25-method-catalog',
  counts: { families: 5, kinds: 19, functions: 23 },
  families: fallbackFamilies,
  kinds: fallbackKinds,
  updated_at: '2026-08-25T00:00:00+08:00'
};

export const fallbackSpecs = {
  ...fallbackCatalog,
  functions: fallbackFunctions,
  renderer_bindings: {
    'scientific.mesh@2.0.0': { owner: 'o3dv', label: 'Online3DViewer', formats: ['STL', 'PLY', 'OBJ', 'GLB'], converted_formats: ['VTU', 'VTS', 'VTM'], static_fallback: 'o3dv-fixed-camera-snapshot' },
    'scientific.raster-scalar@2.1.0': { owner: 'trame-vtkjs', label: 'Trame + vtk.js' },
    'scientific.raster-vector@2.1.0': { owner: 'trame-vtkjs', label: 'Trame + vtk.js' },
    'scientific.volume-scalar@2.1.0': { owner: 'trame-vtkjs', label: 'Trame + vtk.js' },
    'scientific.volume-vector@2.1.0': { owner: 'trame-vtkjs', label: 'Trame + vtk.js' },
    'scientific.field-scalar@2.1.0': { owner: 'trame-vtkjs', label: 'Trame + vtk.js' },
    'scientific.field-vector@2.1.0': { owner: 'trame-vtkjs', label: 'Trame + vtk.js' }
  }
};
