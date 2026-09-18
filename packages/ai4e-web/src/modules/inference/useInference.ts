import { useEffect, useRef, useState } from "react";
import * as api from "./api";
import { remainingCatalogsMatch, type SampleCatalog } from "./catalog";
import {
  defaultInferenceBatchName,
  isInferBatchStamp,
} from "./batchName";
import {
  compatible,
  terminal,
  type Batch,
  type BatchRequest,
  type Catalog,
  type Results,
  type Field, type Metric,
} from "./model";
function storageKey(project: string, task: string) {
  return `dojo.infer.${project}.${task}`;
}
function isMissingBatch(error: { message?: string; code?: string; status?: number }) {
  const text = String(error?.message || "");
  return (
    error?.status === 404 ||
    error?.code === "inference_batch_not_found" ||
    /推理批次不存在或已被清理|文件不存在或数据根未配置/.test(text)
  );
}
/** 任务内选择草稿、服务轮询及幂等提交；迟到响应不能覆盖其他任务。 */
export function useInference(project: string, task: string) {
  const [catalog, setCatalog] = useState<Catalog>({
    items: [],
    device_options: [],
    revision: "",
  });
  const [selected, setSelected] = useState<string[]>([]),
    [partitions, setPartitions] = useState<Record<string, string[]>>({}),
    [split, setSplit] = useState("test"),
    [selections, setSelections] = useState<Record<string, string[]>>({}),
    [device, setDevice] = useState("");
  const [fields, setFields] = useState<Field[]>([]), [metrics, setMetrics] = useState<Metric[]>([]),
    [fieldIds, setFieldIds] = useState<string[]>([]), [metricIds, setMetricIds] = useState<string[]>([]);
  const [selectionSupported, setSelectionSupported] = useState(true);
  const sampleIds = selections[split] || [];
  const sampleSelection = Object.entries(selections).flatMap(([split, ids]) => ids.map(sample => ({split, sample})));
  const setSampleIds = (ids: string[]) => setSelections(old => ({...old, [split]: ids}));
  const [name, setName] = useState(""),
    [options, setOptions] = useState({
      evaluate: true,
      save_predictions: true,
      export_vtk: true,
      export_pointcloud: true,
      export_mesh: true,
      query_chunk_size: 16384,
    });
  const [meshExportAvailable, setMeshExportAvailable] = useState(false);
  const [meshExportReason, setMeshExportReason] = useState("");
  const [batches, setBatches] = useState<Batch[]>([]),
    [active, setActive] = useState(""),
    [detail, setDetail] = useState<Batch>(),
    [result, setResult] = useState<Results>({ items: [], comparison: null });
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [loading, setLoading] = useState(true),
    [samplesLoading, setSamplesLoading] = useState(false),
    [catalogMismatch, setCatalogMismatch] = useState(""),
    [perCheckpoint, setPerCheckpoint] = useState(false),
    [catalogTick, setCatalogTick] = useState(0),
    [tick, setTick] = useState(0),
    [notice, setNotice] = useState("");
  const alive = useRef(true),
    sending = useRef(false),
    identity = useRef<{ body: string; key: string }>(),
    retryIdentity = useRef<{ batch: string; key: string }>();
  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
    };
  }, []);
  useEffect(() => {
    let live = true;
    setLoading(true);
    api
      .checkpoints(project, task)
      .then((v) => {
        if (!live) return;
        setCatalog(v);
        setDevice((old) =>
          v.device_options.some((d) => d.id === old)
            ? old
            : v.device_options.find((d) => !d.busy && d.id !== "cpu")?.id ||
              v.device_options.find((d) => d.id === "cpu")?.id ||
              "",
        );
        setError("");
      })
      .catch((e) => live && setError(e.message))
      .finally(() => live && setLoading(false));
    return () => {
      live = false;
    };
  }, [project, task, catalogTick]);
  const first = selected[0] || "";
  const compatibleIds = catalog.items.filter(compatible).map((item) => item.id);
  function applyCatalog(value: SampleCatalog) {
    const rows = value.partitions || {};
    const next = {
      train: rows.train || [],
      test: rows.test || [],
      eval: rows.eval || (rows as Record<string, string[]>).validation || [],
      ...Object.fromEntries(
        Object.entries(rows).filter(
          ([key]) => !["train", "test", "eval", "validation"].includes(key),
        ),
      ),
    };
    setPartitions(next);
    setSelectionSupported(value.selection_supported !== false);
    setFields(value.fields || []);
    setMetrics(value.metrics || []);
    setFieldIds((value.fields || []).filter((item) => item.default && item.available).map((item) => item.id));
    setMetricIds((value.metrics || []).filter((item) => item.default).map((item) => item.id));
    setSplit(
      next.test.length ? "test" : next.eval.length ? "eval" : next.train.length ? "train" : "",
    );
    const mesh = value.vtk_exports?.mesh;
    const available = mesh?.available === true;
    setMeshExportAvailable(available);
    setMeshExportReason(mesh?.reason || (available ? "" : "训练集没有可还原的 VTK 网格"));
    setOptions((old) => ({
      ...old,
      export_mesh: available && old.export_mesh,
      export_vtk: available && old.export_mesh,
    }));
    setError("");
  }
  function fallbackToCheckpoint(message: string) {
    setPerCheckpoint(true);
    setCatalogMismatch(message);
    setPartitions({});
    setSelections({});
    setFields([]);
    setMetrics([]);
    setSelectionSupported(true);
    setMeshExportAvailable(false);
    setMeshExportReason("训练集没有可还原的 VTK 网格");
  }
  useEffect(() => {
    let live = true;
    setPartitions({});
    setSelections({});
    setFields([]);
    setMetrics([]);
    setSelectionSupported(true);
    setCatalogMismatch("");
    setPerCheckpoint(false);
    if (!compatibleIds.length) {
      setSamplesLoading(false);
      return;
    }
    setSamplesLoading(true);
    const ids = compatibleIds;
    const load = (id: string) => api.samples(project, task, id);
    load(ids[0])
      .then(async (first) => {
        if (!live) return;
        applyCatalog(first);
        setSamplesLoading(false);
        if (!(await remainingCatalogsMatch(load, ids, first)) && live) {
          fallbackToCheckpoint(
            "各 Checkpoint 的样本、物理量或指标不一致，请先选择一个 Checkpoint 再加载对应目录。",
          );
        }
      })
      .catch((e) => {
        if (!live) return;
        fallbackToCheckpoint(
          "未能读取全部检查点的共用目录，请先选择一个 Checkpoint 再加载对应目录。",
        );
        if (!isMissingBatch(e)) setError(e.message);
      })
      .finally(() => live && setSamplesLoading(false));
    return () => {
      live = false;
    };
  }, [project, task, catalogTick, compatibleIds.join("|")]);
  useEffect(() => {
    if (!perCheckpoint) return;
    let live = true;
    setPartitions({});
    setSelections({});
    setFields([]);
    setSelectionSupported(true);
    setMetrics([]);
    if (!first) {
      setSamplesLoading(false);
      return;
    }
    setSamplesLoading(true);
    api
      .samples(project, task, first)
      .then((value) => {
        if (live) applyCatalog(value);
      })
      .catch((e) => live && !isMissingBatch(e) && setError(e.message))
      .finally(() => live && setSamplesLoading(false));
    return () => {
      live = false;
    };
  }, [project, task, first, catalogTick, perCheckpoint]);
  useEffect(() => {
    let live = true;
    let timer: ReturnType<typeof setTimeout>;
    const key = storageKey(project, task);
    async function poll() {
      try {
        const rows = await api.listBatches(project, task);
        if (live) {
          setBatches(rows);
          setActive((old) => {
            const candidate = old || sessionStorage.getItem(key) || "";
            if (candidate && rows.some((row) => row.id === candidate)) return candidate;
            if (candidate) sessionStorage.removeItem(key);
            return "";
          });
        }
      } catch (e: any) {
        if (live && !isMissingBatch(e)) setError(e.message);
      } finally {
        if (live) timer = setTimeout(poll, 2500);
      }
    }
    void poll();
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [project, task, tick]);
  useEffect(() => {
    let live = true;
    let timer: ReturnType<typeof setTimeout>;
    setDetail(undefined);
    setResult({ items: [], comparison: null });
    if (!active) return;
    sessionStorage.setItem(storageKey(project, task), active);
    let finished = false,
      resultsVersion = "";
    async function poll() {
      try {
        const d = await api.getBatch(project, task, active);
        if (live) setDetail(d);
        const version = JSON.stringify([
          d.status,
          d.completed,
          d.children.map((c) => [c.run_id, c.status, c.progress?.completed]),
        ]);
        if (version !== resultsVersion) {
          const r = await api.results(project, task, active);
          if (live) setResult(r);
          resultsVersion = version;
        }
        finished = terminal(d.status);
      } catch (e: any) {
        if (!live) return;
        if (isMissingBatch(e)) {
          sessionStorage.removeItem(storageKey(project, task));
          setActive("");
          return;
        }
        setError(e.message);
      } finally {
        if (live && !finished) timer = setTimeout(poll, 2500);
      }
    }
    void poll();
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [project, task, active, tick]);
  const notifiedTerminal = useRef(new Set<string>());
  useEffect(() => {
    if (!detail || !terminal(detail.status)) return;
    const key = JSON.stringify([project, task, detail.id, detail.status]);
    if (notifiedTerminal.current.has(key)) return;
    notifiedTerminal.current.add(key);
    // 完成事实仍由服务提供；只通知应用壳重读任务，不能在页面内补造成功状态。
    window.dispatchEvent(
      new CustomEvent("dojo:task-updated", { detail: { project, task } }),
    );
  }, [project, task, detail]);
  const chosen = selected
    .map((id) => catalog.items.find((c) => c.id === id))
    .filter(Boolean) as Catalog["items"];
  const samePreparation =
    chosen.length < 2 ||
    chosen.every(
      (c) =>
        (c.preparation?.digest || c.preparation?.revision) ===
        (chosen[0].preparation?.digest || chosen[0].preparation?.revision),
    );
  const duplicate =
    chosen.length !== new Set(chosen.map((c) => c.revision)).size;
  const ready =
    !loading &&
    !!catalog.revision &&
    chosen.length === selected.length &&
    chosen.length > 0 &&
    chosen.every(compatible) &&
    samePreparation &&
    !duplicate &&
    sampleSelection.length > 0 &&
    (!selectionSupported || fieldIds.length > 0) &&
    (!selectionSupported || !options.evaluate || metricIds.length > 0) &&
    (options.evaluate || options.export_pointcloud || (meshExportAvailable && options.export_mesh)) &&
    !!device &&
    options.query_chunk_size > 0;
  const running = Boolean(detail && !terminal(detail.status));
  async function action(fn: () => Promise<void>) {
    if (sending.current) return;
    sending.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await fn();
    } catch (e: any) {
      if (alive.current) setError(e.message);
    } finally {
      sending.current = false;
      if (alive.current) setBusy(false);
    }
  }
  function resolveBatchName(core: object): string {
    if (name.trim()) return name.trim();
    if (identity.current?.body) {
      try {
        const previous = JSON.parse(identity.current.body) as { name?: string };
        const { name: previousName, ...previousCore } = previous;
        if (
          JSON.stringify(previousCore) === JSON.stringify(core) &&
          typeof previousName === "string" &&
          isInferBatchStamp(previousName)
        )
          return previousName;
      } catch {}
    }
    return defaultInferenceBatchName();
  }
  function body(): BatchRequest {
    const exportMesh = meshExportAvailable && options.export_mesh;
    const optionsPayload = {
      evaluate: options.evaluate,
      export_pointcloud: options.export_pointcloud,
      export_mesh: exportMesh,
      export_vtk: exportMesh,
      save_predictions: options.export_pointcloud || exportMesh,
      query_chunk_size: options.query_chunk_size,
    };
    const core = {
      expected_revision: catalog.revision,
      checkpoints: chosen.map((c) => ({ id: c.id, revision: c.revision })),
      sample_selection: sampleSelection,
      ...(selectionSupported ? {fields: fieldIds, ...(options.evaluate && metricIds.length ? {metrics: metricIds} : {})} : {}),
      device,
      options: optionsPayload,
    };
    if (!identity.current) {
      try {
        identity.current = JSON.parse(
          sessionStorage.getItem(`dojo.infer.request.${project}.${task}`) ||
            "null",
        );
      } catch {}
    }
    const data = {
      name: resolveBatchName(core),
      ...core,
    };
    const serialized = JSON.stringify(data);
    if (identity.current?.body !== serialized)
      identity.current = { body: serialized, key: crypto.randomUUID() };
    sessionStorage.setItem(
      `dojo.infer.request.${project}.${task}`,
      JSON.stringify(identity.current),
    );
    return { ...data, idempotency_key: identity.current.key };
  }
  async function run(checkOnly = false) {
    if (!ready) return;
    await action(async () => {
      const request = body();
      const validation = await api.check(project, task, request);
      if (
        validation?.valid === false ||
        validation?.ok === false ||
        ["invalid", "failed", "incompatible"].includes(validation?.status)
      )
        throw new Error(
          validation.reason ||
            validation.message ||
            JSON.stringify(validation.errors || "推理检查未通过"),
        );
      if (!alive.current) return;
      if (checkOnly) {
        setNotice("检查通过；尚未提交推理");
        return;
      }
      const created = await api.submit(project, task, request);
      if (alive.current) {
        setActive(created.id);
        setTick((v) => v + 1);
        setNotice("批次已提交，关闭页面不会停止计算");
      }
    });
  }
  return {
    catalog,
    selected,
    setSelected,
    partitions,
    split,
    changeSplit: setSplit,
    selections, sampleSelection, fields, metrics, fieldIds, setFieldIds, metricIds, setMetricIds,
    sampleIds,
    setSampleIds,
    device,
    setDevice,
    name,
    setName,
    options,
    setOptions,
    meshExportAvailable,
    meshExportReason,
    batches,
    active,
    setActive,
    detail,
    result,
    error,
    busy,
    loading,
    samplesLoading,
    catalogMismatch,
    notice,
    ready,
    running,
    samePreparation,
    selectionSupported,
    duplicate,
    refresh: () => {
      setCatalogTick((v) => v + 1);
      setTick((v) => v + 1);
    },
    run,
    cancel: () =>
      action(async () => {
        await api.cancel(project, task, active);
        if (alive.current) setTick((v) => v + 1);
      }),
    recover: () =>
      action(async () => {
        await api.recover(project, task, active);
        if (alive.current) setTick((v) => v + 1);
      }),
    retry: () =>
      action(async () => {
        if (retryIdentity.current?.batch !== active)
          retryIdentity.current = { batch: active, key: crypto.randomUUID() };
        const b = await api.retry(
          project,
          task,
          active,
          retryIdentity.current.key,
        );
        if (alive.current) {
          setActive(b.id);
          setTick((v) => v + 1);
        }
      }),
  };
}
