/** 几何可视化模块的 O3DV 资源地址与嵌入参数适配。 */

const O3DV_EMBED = `${import.meta.env.BASE_URL}3dviewer/embed.html`;

/** 把几何模型地址和视角参数转换为自托管 O3DV 嵌入地址。 */
export function o3dvEmbedUrl(modelUrl, parameters = {}) {
  const entries = new URLSearchParams();
  entries.set('model', modelUrl);
  const copy = (key, value) => {
    if (value !== undefined && value !== null && value !== '') {
      entries.set(key, Array.isArray(value) ? value.join(',') : String(value));
    }
  };
  copy('background', parameters.background_color);
  copy('material', parameters.material_color);
  copy('edges', parameters.show_edges);
  copy('projection', parameters.camera_projection);
  copy('camera', parameters.camera_position);
  copy('target', parameters.camera_target);
  copy('up', parameters.up_axis);
  copy('fit', parameters.auto_fit);
  return `${O3DV_EMBED}#${entries.toString()}`;
}
