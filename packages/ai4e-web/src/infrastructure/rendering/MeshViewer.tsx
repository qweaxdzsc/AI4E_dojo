import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
/** 浏览器只展示预览进程返回的网格与数值，不进行物理计算。 */
export function MeshViewer({ data }: { data: any }) {
  const host = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!host.current) return;
    const el = host.current;
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setClearColor("#e9eef5");
    el.appendChild(renderer.domElement);
    const scene = new THREE.Scene(),
      camera = new THREE.PerspectiveCamera(45, 1, 0.001, 100000);
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(data.positions, 3),
    );
    if (data.indices.length) geometry.setIndex(data.indices);
    geometry.computeVertexNormals();
    geometry.computeBoundingSphere();
    const sphere = geometry.boundingSphere!;
    let material: THREE.Material;
    const hasValues = !!data.values;
    if (hasValues) {
      const finite = data.values.filter((x: any) => x !== null);
      let lo = Infinity,
        hi = -Infinity;
      for (const v of finite) {
        lo = Math.min(lo, v);
        hi = Math.max(hi, v);
      }
      const colors = data.values.flatMap((v: any) => {
        const c =
          v === null
            ? new THREE.Color("#999")
            : new THREE.Color().setHSL(
                0.67 * (1 - (v - lo) / (hi - lo || 1)),
                0.8,
                0.5,
              );
        return [c.r, c.g, c.b];
      });
      geometry.setAttribute(
        "color",
        new THREE.Float32BufferAttribute(colors, 3),
      );
    }
    material = data.indices.length
      ? new THREE.MeshStandardMaterial({
          color: hasValues ? 0xffffff : 0x5688bb,
          vertexColors: hasValues,
          side: THREE.DoubleSide,
        })
      : new THREE.PointsMaterial({
          color: hasValues ? 0xffffff : 0x5688bb,
          vertexColors: hasValues,
          size: Math.max(sphere.radius / 200, 0.001),
        });
    scene.add(
      data.indices.length
        ? new THREE.Mesh(geometry, material)
        : new THREE.Points(geometry, material),
    );
    scene.add(new THREE.HemisphereLight(0xffffff, 0x778899, 3));
    camera.position
      .copy(sphere.center)
      .add(new THREE.Vector3(0, 0, Math.max(sphere.radius * 3, 0.1)));
    camera.lookAt(sphere.center);
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.copy(sphere.center);
    const resize = () => {
      renderer.setSize(el.clientWidth, 400);
      camera.aspect = el.clientWidth / 400;
      camera.updateProjectionMatrix();
    };
    const observer = new ResizeObserver(resize);
    observer.observe(el);
    let frame = 0;
    const draw = () => {
      controls.update();
      renderer.render(scene, camera);
      frame = requestAnimationFrame(draw);
    };
    resize();
    draw();
    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      controls.dispose();
      geometry.dispose();
      material.dispose();
      renderer.dispose();
      el.replaceChildren();
    };
  }, [data]);
  return <div ref={host} aria-label="三维网格" data-field={data.field||""} />;
}
