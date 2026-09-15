import { useEffect, useRef, useState } from "react";
import * as api from "./api";
import {
  compatible,
  terminal,
  type Batch,
  type BatchRequest,
  type Catalog,
  type Results,
  type Field, type Metric,
} from "./model";
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
      query_chunk_size: 16384,
    });
  const [batches, setBatches] = useState<Batch[]>([]),
    [active, setActive] = useState(""),
    [detail, setDetail] = useState<Batch>(),
    [result, setResult] = useState<Results>({ items: [], comparison: null });
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [loading, setLoading] = useState(true),
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
  useEffect(() => {
    let live = true;
    setPartitions({});
    setSelections({});
    setFields([]);
    setSelectionSupported(true);
    setMetrics([]);
    if (first)
      api
        .samples(project, task, first)
        .then((v) => {
          if (live) {
            setPartitions(v.partitions);
            setSelectionSupported(v.selection_supported !== false);
            setFields(v.fields || []); setMetrics(v.metrics || []);
            setFieldIds((v.fields || []).filter(f => f.default && f.available).map(f => f.id));
            setMetricIds((v.metrics || []).filter(m => m.default).map(m => m.id));
            setSplit(
              v.partitions.test ? "test" : Object.keys(v.partitions)[0] || "",
            );
          }
        })
        .catch((e) => live && setError(e.message));
    return () => {
      live = false;
    };
  }, [project, task, first, catalogTick]);
  useEffect(() => {
    let live = true;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const rows = await api.listBatches(project, task);
        if (live) {
          setBatches(rows);
          setActive(
            (old) =>
              old ||
              sessionStorage.getItem(`dojo.infer.${project}.${task}`) ||
              "",
          );
        }
      } catch (e: any) {
        if (live) setError(e.message);
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
    sessionStorage.setItem(`dojo.infer.${project}.${task}`, active);
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
        if (live) setError(e.message);
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
    (options.evaluate || options.save_predictions) &&
    (!options.export_vtk || options.save_predictions) &&
    !!device &&
    options.query_chunk_size > 0;
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
  function body(): BatchRequest {
    const data = {
      name: name.trim() || "批量推理",
      expected_revision: catalog.revision,
      checkpoints: chosen.map((c) => ({ id: c.id, revision: c.revision })),
      sample_selection: sampleSelection,
      ...(selectionSupported ? {fields: fieldIds, ...(options.evaluate && metricIds.length ? {metrics: metricIds} : {})} : {}),
      device,
      options,
    };
    const serialized = JSON.stringify(data);
    if (!identity.current) {
      try {
        identity.current = JSON.parse(
          sessionStorage.getItem(`dojo.infer.request.${project}.${task}`) ||
            "null",
        );
      } catch {}
    }
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
    batches,
    active,
    setActive,
    detail,
    result,
    error,
    busy,
    loading,
    notice,
    ready,
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
