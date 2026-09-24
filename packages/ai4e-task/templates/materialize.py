"""展开普通 recipe 文件及显式输入路径；不导入用户代码。"""

from pathlib import Path

from ..storage.snapshots import snapshot


def recipe_entry(project: str | Path, task_id: str) -> dict:
    """读取任务当前 recipe 投影的入口；不使用创建时冻结的旧键快照。"""
    from ..storage.layout import task_dir
    from ..tasks.descriptions import described_entry

    folder = task_dir(project, task_id)
    return described_entry(folder / "recipe", cache_dir=folder / ".dojo/descriptions")


def read_entry(recipe: Path) -> dict:
    """按固定文件和公共配置发现入口；不读取逐案例任务描述。"""
    from omegaconf import OmegaConf

    from ai4e_core.base.config.conventions import input_bindings

    path = Path(recipe) / "config.yaml"
    if not path.is_file():
        return {}
    cfg = OmegaConf.to_container(OmegaConf.load(path), resolve=False)
    if not isinstance(cfg, dict):
        raise TypeError("configuration_must_be_mapping")
    inputs = dict.fromkeys(input_bindings(cfg), "other")
    # 这是从公共结构投影的内部查询结果，用户无需维护第二份声明。
    return {
        "script": "pipeline.py",
        "config": "config.yaml",
        "convention_version": 1,
        "inputs": inputs,
        "outputs": {"run_root": "{run_root}", "data_root": "{data_dir}"},
        "stage_inputs": {
            name: [{"key": key} for key in inputs if key.split(".")[1] == name]
            for name in cfg.get("inputs", {})
        },
        "components": cfg.get("components", {}),
        "stages": list(cfg.get("pipeline", {}).get("stages", [])),
        "shared_outputs": {},
    }


def materialize(source: Path | None, target: Path) -> dict:
    """复制代码，展开声明输入的相对路径，保持输出绑定由运行时分配。"""
    if source is None:
        target.mkdir(parents=True)
        return {}
    captured = snapshot(source, target)
    entry = read_entry(target)
    if entry and (target / entry["config"]).exists():
        from omegaconf import OmegaConf

        cfg = OmegaConf.load(target / entry["config"])
        base = (source / entry["config"]).parent
        for key in entry.get("inputs", {}):
            value = OmegaConf.select(cfg, key)
            if isinstance(value, str):
                path = Path(value).expanduser()
                OmegaConf.update(
                    cfg,
                    key,
                    str((base / path).resolve() if not path.is_absolute() else path.resolve()),
                )
        OmegaConf.save(cfg, target / entry["config"])
    return captured
