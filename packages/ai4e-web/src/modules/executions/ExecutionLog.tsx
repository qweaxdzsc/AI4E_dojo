import { Alert, Button, Checkbox, Input, Select, Tag } from "antd";
import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { readLog, stop, subscribe } from "./api";
import "./executions.css";
import {
  LOG_WINDOW,
  clampStart,
  filterLogLines,
  lineLevel,
  olderStart,
  tailStart,
} from "./logWindow";

/** 事件重连只同步日志；筛选和清空仅作用于显示，下载始终读取完整运行日志。页面操作说明只在发生时写入一行普通日志，不钉在底部。默认只渲染最近 500 行，其余留在内存，向上滚动再展开。 */
export function ExecutionLog({
  project,
  run,
  accumulate,
  onSnapshot,
  activity,
}: {
  project: string;
  run?: string;
  accumulate?: boolean;
  onSnapshot?: (value: any) => void;
  activity?: { status: string; text?: string };
}) {
  const [value, setValue] = useState<any>(),
    [connection, setConnection] = useState("等待运行"),
    [error, setError] = useState("");
  const [search, setSearch] = useState(""),
    [level, setLevel] = useState("全部"),
    [follow, setFollow] = useState(true),
    [cleared, setCleared] = useState(""),
    [history, setHistory] = useState(""),
    [start, setStart] = useState(0);
  const output = useRef<HTMLPreElement>(null);
  const latest = useRef("");
  const notify = useRef(onSnapshot);
  const followRef = useRef(follow);
  const ignoreScroll = useRef(false);
  const allowFollowOnBottom = useRef(true);
  const restore = useRef<{ height: number; top: number } | null>(null);
  const pending = useRef<any>(null);
  const flush = useRef<number>(0);
  const lastNote = useRef("");
  notify.current = onSnapshot;
  followRef.current = follow;
  latest.current = value?.text || "";

  useEffect(() => {
    if (accumulate && latest.current)
      setHistory((old) =>
        old ? old + "\n\n—— 下一次运行 ——\n\n" + latest.current : latest.current,
      );
    setValue(undefined);
    setError("");
    setConnection("等待运行");
    setCleared("");
    setStart(0);
    setFollow(true);
    allowFollowOnBottom.current = true;
    if (!accumulate) {
      setHistory("");
      lastNote.current = "";
      setSearch("");
      setLevel("全部");
    }
    notify.current?.(undefined);
    if (!run) return;
    const stream = subscribe(project, run);
    stream.onopen = () => setConnection("已连接");
    const apply = (v: any, immediate = false) => {
      pending.current = v;
      const publish = () => {
        flush.current = 0;
        const next = pending.current;
        if (!next) return;
        setValue(next);
        if (followRef.current) setStart(0);
      };
      if (immediate) {
        if (flush.current) window.clearTimeout(flush.current);
        publish();
        return;
      }
      if (flush.current) return;
      flush.current = window.setTimeout(publish, 80);
    };
    stream.onmessage = (e) => {
      try {
        const v = JSON.parse(e.data);
        notify.current?.(v);
        const ended = ["succeeded", "failed", "stopped"].includes(v.status);
        apply(v, ended);
        if (ended) {
          stream.close();
          setConnection("运行已结束");
        }
      } catch {
        setError("日志响应格式无效，请重新打开此运行");
      }
    };
    stream.onerror = () => setConnection("连接中断，正在重连（运行状态待核对）");
    return () => {
      stream.close();
      if (flush.current) window.clearTimeout(flush.current);
    };
  }, [project, run]);

  useEffect(() => {
    const line = activity?.text?.trim();
    if (!line || line === lastNote.current) return;
    lastNote.current = line;
    setHistory((old) => (old ? old + "\n" + line : line));
  }, [activity?.text]);

  const text = [history, value?.text].filter(Boolean).join("\n");
  const visible = cleared && text.startsWith(cleared) ? text.slice(cleared.length) : text;
  const lines = useMemo(() => (visible ? visible.split("\n") : []), [visible]);
  const filteredLines = useMemo(
    () => filterLogLines(lines, level, search),
    [lines, level, search],
  );
  const windowStart = follow
    ? tailStart(filteredLines.length)
    : clampStart(start, filteredLines.length);
  const shown = filteredLines.slice(windowStart, windowStart + LOG_WINDOW);
  const hiddenAbove = windowStart;
  const hiddenBelow = Math.max(0, filteredLines.length - windowStart - shown.length);
  const filtered = shown.join("\n");
  const levels = useMemo(
    () => [...new Set((text ? text.split("\n") : []).map(lineLevel))],
    [text],
  );
  const empty =
    filtered ||
    (!run && !history
      ? "运行开始后显示真实日志"
      : !text
        ? "等待运行日志"
        : "无匹配日志");

  useLayoutEffect(() => {
    const el = output.current;
    if (!el) return;
    ignoreScroll.current = true;
    if (restore.current) {
      const { height, top } = restore.current;
      restore.current = null;
      el.scrollTop = top + (el.scrollHeight - height);
    } else if (follow) {
      el.scrollTop = el.scrollHeight;
    }
    const frame = window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => {
        ignoreScroll.current = false;
      });
    });
    return () => window.cancelAnimationFrame(frame);
  }, [filtered, follow, windowStart]);

  function changeFollow(next: boolean) {
    setFollow(next);
    allowFollowOnBottom.current = next;
    setStart(tailStart(filteredLines.length));
  }

  function onScroll() {
    const el = output.current;
    if (!el || ignoreScroll.current) return;
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 24;
    const atTop = el.scrollTop < 24;
    if (!atBottom) {
      allowFollowOnBottom.current = true;
      if (followRef.current) setFollow(false);
      setStart(windowStart);
    } else if (allowFollowOnBottom.current && !followRef.current) {
      setFollow(true);
      setStart(tailStart(filteredLines.length));
    }
    if (atTop && hiddenAbove > 0) {
      restore.current = { height: el.scrollHeight, top: el.scrollTop };
      setFollow(false);
      allowFollowOnBottom.current = true;
      setStart(olderStart(windowStart));
    }
  }

  async function download() {
    if (!run) return;
    try {
      const result = await readLog(project, run);
      const url = URL.createObjectURL(new Blob([result.text], { type: "text/plain;charset=utf-8" }));
      const link = document.createElement("a");
      link.href = url;
      link.download = `run-${run}.log`;
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (e: any) {
      setError(e.message);
    }
  }

  const tag = activity?.status || value?.status || connection;
  return (
    <section className="execution-log">
      <div className="panel-title">
        <b>执行日志</b>
        <Tag>{tag}</Tag>
        {connection !== tag && <span>{connection}</span>}
        <Button
          disabled={!run || ["succeeded", "failed", "stopped"].includes(value?.status)}
          onClick={() => run && stop(project, run).catch((e) => setError(e.message))}
        >
          停止运行
        </Button>
      </div>
      <div className="log-tools">
        <Input
          aria-label="搜索日志"
          placeholder="搜索日志"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Select
          aria-label="日志级别"
          value={level}
          options={["全部", ...levels].map((item) => ({ value: item, label: item }))}
          onChange={setLevel}
        />
        <Checkbox
          checked={follow}
          onChange={(e) => changeFollow(e.target.checked)}
        >
          自动滚动
        </Checkbox>
        <Button disabled={!text} onClick={() => setCleared(text)}>
          清空显示
        </Button>
        <Button disabled={!run} onClick={download}>
          下载日志
        </Button>
      </div>
      {(hiddenAbove > 0 || hiddenBelow > 0) && (
        <p className="log-window-hint" aria-label="日志窗口提示">
          {hiddenAbove > 0 ? `更早 ${hiddenAbove} 行已存储，向上滚动展开` : ""}
          {hiddenAbove > 0 && hiddenBelow > 0 ? "；" : ""}
          {hiddenBelow > 0 ? `下方还有 ${hiddenBelow} 行` : ""}
        </p>
      )}
      {error && <Alert type="error" message={error} />}
      <pre ref={output} aria-label="运行日志内容" onScroll={onScroll}>
        {empty}
      </pre>
    </section>
  );
}
