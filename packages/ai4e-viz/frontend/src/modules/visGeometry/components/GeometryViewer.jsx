/** ============================================================
   AI4E VizReport — GEOViewer：Online3DViewer 三维查看容器
   GEO 纯几何（STL/PLY/OBJ）走全新 Online3DViewer 引擎：
   查看器资产自托管（public/3dviewer/embed.html + o3dv.min.js），
   模型经 API 文件端点跨源提供（/api/artifact/{id}/file/{name}）。
   加载策略与 EmbedFrame 一致：先 no-cors 探测，再挂载 iframe。
   ============================================================ */
import { useEffect, useState } from 'react';
import { Button, Space, Spin, Tag } from 'antd';
import { ReloadOutlined, WarningOutlined, AimOutlined } from '@ant-design/icons';
import { o3dvEmbedUrl } from '../api.js';

const PROBE_TIMEOUT = 6000;

export default function GEOViewer({ modelUrl, title, height = 480, fallbackUrl, parameters = {}, ...qoderProps }) {
  const [status, setStatus] = useState('probing'); // probing | online | offline
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setStatus('probing');
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), PROBE_TIMEOUT);

    fetch(modelUrl, { mode: 'no-cors', cache: 'no-store', signal: controller.signal })
      .then(() => !cancelled && setStatus('online'))
      .catch(() => !cancelled && setStatus('offline'))
      .finally(() => clearTimeout(timer));

    return () => {
      cancelled = true;
      clearTimeout(timer);
      controller.abort();
    };
  }, [modelUrl, attempt]);

  const retry = () => setAttempt((a) => a + 1);

  const frame = (
    <iframe
      title={title}
      src={o3dvEmbedUrl(modelUrl, parameters)}
      style={{
        width: '100%',
        height,
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        background: parameters.background_color || '#161a20',
        display: 'block'
      }}
      allow="fullscreen"
      data-component="o3dv-viewer-iframe"
     data-qoder-id="qel-o3dv-viewer-iframe-5c4fb8a2" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-o3dv-viewer-iframe-5c4fb8a2&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;o3dv-viewer-iframe&quot;,&quot;loc&quot;:{&quot;line&quot;:40,&quot;column&quot;:5}}"/>
  );

  return (
    <div data-component="geo-viewer" style={qoderProps?.style} className={qoderProps?.className} data-qoder-id="qel-geo-viewer-33e2540a" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-geo-viewer-33e2540a&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;geo-viewer&quot;,&quot;loc&quot;:{&quot;line&quot;:57,&quot;column&quot;:5}}">
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }} data-qoder-id="qel-div-add242c0" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-div-add242c0&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;div&quot;,&quot;loc&quot;:{&quot;line&quot;:58,&quot;column&quot;:7}}">
        <Tag color="cyan" style={{ marginInlineEnd: 0 }} data-qoder-id="qel-tag-eed4e549" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-tag-eed4e549&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;tag&quot;,&quot;loc&quot;:{&quot;line&quot;:59,&quot;column&quot;:9}}">Online3DViewer</Tag>
        <span style={{ fontSize: 13, fontWeight: 600 }} data-qoder-id="qel-span-37ea2ede" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-span-37ea2ede&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;span&quot;,&quot;loc&quot;:{&quot;line&quot;:60,&quot;column&quot;:9}}">{title}</span>
        {status === 'online' && (
          <span style={{ fontSize: 11.5, color: 'var(--ok)' }} data-qoder-id="qel-span-36ea2d4b" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-span-36ea2d4b&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;span&quot;,&quot;loc&quot;:{&quot;line&quot;:62,&quot;column&quot;:11}}">● 查看器就绪</span>
        )}
        {status === 'probing' && (
          <span style={{ fontSize: 11.5, color: 'var(--fg-3)' }} data-qoder-id="qel-span-35ea2bb8" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-span-35ea2bb8&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;span&quot;,&quot;loc&quot;:{&quot;line&quot;:65,&quot;column&quot;:11}}">
            <Spin size="small" style={{ marginInlineEnd: 6 }}  data-qoder-id="qel-spin-c280a185" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-spin-c280a185&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;spin&quot;,&quot;loc&quot;:{&quot;line&quot;:66,&quot;column&quot;:13}}"/>
            正在探测模型文件端点…
          </span>
        )}
        {status === 'offline' && (
          <span style={{ fontSize: 11.5, color: 'var(--warn)' }} data-qoder-id="qel-span-33ea2892" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-span-33ea2892&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;span&quot;,&quot;loc&quot;:{&quot;line&quot;:71,&quot;column&quot;:11}}">
            <WarningOutlined style={{ marginInlineEnd: 4 }}  data-qoder-id="qel-warningoutlined-bd854276" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-warningoutlined-bd854276&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;warningoutlined&quot;,&quot;loc&quot;:{&quot;line&quot;:72,&quot;column&quot;:13}}"/>
            模型文件端点未连接
          </span>
        )}
      </div>

      {status === 'online' && frame}

      {status === 'probing' && (
        <div
          style={{
            height,
            display: 'grid',
            placeItems: 'center',
            border: '1px dashed var(--border-2)',
            borderRadius: 'var(--radius)',
            background: 'var(--surface-2)',
            color: 'var(--fg-3)',
            fontSize: 12.5
          }}
         data-qoder-id="qel-div-9f03f175" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-div-9f03f175&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;div&quot;,&quot;loc&quot;:{&quot;line&quot;:81,&quot;column&quot;:9}}">
          <Space direction="vertical" align="center" size={6} data-qoder-id="qel-space-59fec25c" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-space-59fec25c&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;space&quot;,&quot;loc&quot;:{&quot;line&quot;:93,&quot;column&quot;:11}}">
            <Spin  data-qoder-id="qel-spin-ee8fe73b" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-spin-ee8fe73b&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;spin&quot;,&quot;loc&quot;:{&quot;line&quot;:94,&quot;column&quot;:13}}"/>
            <span data-qoder-id="qel-span-6fb19e3a" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-span-6fb19e3a&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;span&quot;,&quot;loc&quot;:{&quot;line&quot;:95,&quot;column&quot;:13}}">正在探测 API 文件服务…</span>
          </Space>
        </div>
      )}

      {status === 'offline' && (
        <div
          style={{
            border: '1px dashed var(--border-2)',
            borderRadius: 'var(--radius)',
            background: 'var(--surface-2)',
            padding: 16,
            display: 'flex',
            flexDirection: 'column',
            gap: 12
          }}
          data-component="geo-viewer-offline"
         data-qoder-id="qel-geo-viewer-offline-2aac9430" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-geo-viewer-offline-2aac9430&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;geo-viewer-offline&quot;,&quot;loc&quot;:{&quot;line&quot;:101,&quot;column&quot;:9}}">
          {fallbackUrl ? <figure style={{ margin: 0 }}><img src={fallbackUrl} alt={`${title} 的 Online3DViewer 固定相机快照`} style={{ width: '100%', maxHeight: height, objectFit: 'contain', display: 'block', borderRadius: 6, background: '#161a20' }} /><figcaption style={{ marginTop: 6, color: 'var(--fg-3)', fontSize: 11.5 }}>交互服务不可达，保留由同一 O3DV 模型和固定相机生成的最近快照。</figcaption></figure> : null}
          <div style={{ fontSize: 12.5, color: 'var(--fg-2)', lineHeight: 1.7 }} data-qoder-id="qel-div-9803e670" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-div-9803e670&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;div&quot;,&quot;loc&quot;:{&quot;line&quot;:113,&quot;column&quot;:11}}">
            模型文件由解析 API 提供，当前不可达。请在终端执行：
            <div
              style={{
                margin: '8px 0',
                padding: '8px 12px',
                background: 'var(--surface)',
                border: '1px solid var(--border)',
                borderRadius: 6,
                fontFamily: 'var(--font-mono)',
                fontSize: 12
              }}
             data-qoder-id="qel-div-9903e803" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-div-9903e803&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;div&quot;,&quot;loc&quot;:{&quot;line&quot;:115,&quot;column&quot;:13}}">
              cd backend && ./.venv/bin/python run.py
            </div>
            启动后 API 位于 <b data-qoder-id="qel-b-e36fd9ee" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-b-e36fd9ee&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;b&quot;,&quot;loc&quot;:{&quot;line&quot;:128,&quot;column&quot;:24}}">127.0.0.1:8091</b>，模型经 <b data-qoder-id="qel-b-e46fdb81" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-b-e46fdb81&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;b&quot;,&quot;loc&quot;:{&quot;line&quot;:128,&quot;column&quot;:50}}">/api/artifact/&#123;id&#125;/file/&#123;name&#125;</b> 跨源提供，前端查看器资产已自托管，无需外网。
          </div>
          <Space data-qoder-id="qel-space-d5fbb3f9" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-space-d5fbb3f9&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;space&quot;,&quot;loc&quot;:{&quot;line&quot;:130,&quot;column&quot;:11}}">
            <Button size="small" icon={<ReloadOutlined  data-qoder-id="qel-reloadoutlined-1312aee5" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-reloadoutlined-1312aee5&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;reloadoutlined&quot;,&quot;loc&quot;:{&quot;line&quot;:131,&quot;column&quot;:40}}"/>} onClick={retry} data-qoder-id="qel-button-6add43ee" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-button-6add43ee&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;button&quot;,&quot;loc&quot;:{&quot;line&quot;:131,&quot;column&quot;:13}}">
              重新连接
            </Button>
          </Space>
        </div>
      )}

      {status === 'online' && (
        <div style={{ marginTop: 6, fontSize: 11.5, color: 'var(--fg-3)', display: 'flex', alignItems: 'center', gap: 6 }} data-qoder-id="qel-div-9501a320" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-div-9501a320&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;div&quot;,&quot;loc&quot;:{&quot;line&quot;:139,&quot;column&quot;:9}}">
          <AimOutlined  data-qoder-id="qel-aimoutlined-718e6815" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-aimoutlined-718e6815&quot;,&quot;filePath&quot;:&quot;frontend/src/components/GEOViewer.jsx&quot;,&quot;componentName&quot;:&quot;GEOViewer&quot;,&quot;elementRole&quot;:&quot;aimoutlined&quot;,&quot;loc&quot;:{&quot;line&quot;:140,&quot;column&quot;:11}}"/>
          手势归属：单指旋转、双指平移/缩放；键盘和工具栏提供缩放、视角复位、边线、背景与全屏替代操作。
        </div>
      )}
    </div>
  );
}
