/** 实际视口录制；本地媒体流和远程图像合成共用输出协议。 */
import {physApi} from './api.js';
/** 创建与当前工作区绑定的录制控制器。 */
export function recordingController({frame,recorder,recordingAsset,model,setRecording,width=1280,height=720,fps=24}) {
  const toggleRecording = async () => {
    try {
      if (recorder.current) { recorder.current.stop(); recorder.current = null; setRecording(false); return; }
      if (!model.asset) throw new Error('请先保存配置，再开始录制');
      const canvases = [...frame.current.contentDocument.querySelectorAll('canvas')].filter((c) => c.width && c.height).sort((a, b) => (b.width * b.height - a.width * a.height) || b.toDataURL().length - a.toDataURL().length);
      if (!canvases.length) throw new Error('视口尚未连接');
      if (!MediaRecorder.isTypeSupported('video/webm')) throw new Error('当前浏览器不支持 WebM 录制');
      recordingAsset.current = model.asset;
      // 远程视口是2D图像画布，直接合成；本地WebGL通过媒体流保留实际合成帧。
      const direct = canvases[0].getContext('2d');
      const sourceStream = direct ? null : canvases[0].captureStream(fps);
      const video = direct ? null : document.createElement('video');
      if(video) {
        video.muted = true; video.srcObject = sourceStream;
        sourceStream.getVideoTracks()[0].requestFrame?.();
        const started=video.play();
        // 静止的 WebGL 画布未必产生媒体首帧；原相机重绘唤醒流，不改变视角。
        const snapshot=await model.snapshot();const view=snapshot.spec.views[0];
        await physApi.command(model.context,model.session.session_id,{operation:'camera',view:view.id,camera:view.camera});
        await started;
      }
      const canvas = document.createElement('canvas'); canvas.width = width; canvas.height = height;
      const ctx = canvas.getContext('2d');
      let animation;
      const draw = () => {
        ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, width, height);
        const remoteImage = direct ? canvases[0].parentElement.querySelector('img') : null;
        const source = video || (remoteImage?.complete && remoteImage.naturalWidth ? remoteImage : canvases[0]);
        const sw = video ? video.videoWidth : source.naturalWidth || source.width, sh = video ? video.videoHeight : source.naturalHeight || source.height;
        const scale = Math.min(width / sw, height / sh);
        const w = sw * scale, h = sh * scale;
        ctx.drawImage(source, (width - w) / 2, (height - h) / 2, w, h);
        if(remoteImage && source === remoteImage) ctx.drawImage(canvases[0], (width - w) / 2, (height - h) / 2, w, h);
        animation = requestAnimationFrame(draw);
      };
      draw();
      const stream = canvas.captureStream(fps), chunks = [];
      const active = new MediaRecorder(stream, { mimeType: 'video/webm' });
      active.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); };
      active.onstop = async () => {
        cancelAnimationFrame(animation); if(video) {video.pause(); video.srcObject = null;}
        [...stream.getTracks(), ...(sourceStream?.getTracks() || [])].forEach((track) => track.stop());
        const fixed = recordingAsset.current;
        try { model.setOutput(await physApi.record(model.context, fixed.visualization_id, fixed.revision, new Blob(chunks, { type: 'video/webm' }))); } catch (e) { model.fail(e); }
      };
      active.start(250); recorder.current = active; setRecording(true);
    } catch (e) { model.fail(e); }
  };
  return toggleRecording;
}
