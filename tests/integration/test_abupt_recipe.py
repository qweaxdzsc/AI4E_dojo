"""新模型经复制案例训练、恢复和缓存查询，默认声明不启用额外输入。"""

from pathlib import Path

import torch

from tests.integration.test_train_recipe import _fit_config, _run_script, prepared_case


def test_new_recipe_defaults():

    from tests.integration.test_dataset_recipe import load_internal

    cfg = load_internal(Path(__file__).parents[2] / "recipes/aero_cfd/config.yaml")
    assert cfg.train.batch_size == 1
    assert not cfg.model.data_specs.conditioning_dims
    for d in cfg.model.data_specs.domains:
        assert sum(cfg.model.data_specs.domains[d].feature_dim.values()) == 4
        assert not cfg.trainprep.domains[d].features
        assert cfg.sampling.domains[d].query.num_points == 0
    assert cfg.trainprep.use_physics_features is False
    assert cfg.model.parameters.require_features is False
    assert list(cfg.pipeline.stages) == ["rawprep", "trainprep", "train", "post"]
    assert "preparation" not in cfg.train
    assert cfg.post.checkpoint is None
    from omegaconf import OmegaConf

    assert (
        "checkpoint"
        not in OmegaConf.load(Path(__file__).parents[2] / "recipes/aero_cfd/config.yaml").post
    )
    assert "denormalization" not in cfg.post


def test_prepared_query_derives_output_mapping(tmp_path):
    """默认不启用物理特征，也不要求用户重复声明未来查询输出的反变换映射。"""
    from types import SimpleNamespace

    from omegaconf import OmegaConf

    from ai4e_contrib.ability.model.abupt.batch import collate
    from ai4e_contrib.ability.model.abupt.inference import InferenceContext
    from ai4e_contrib.ability.model.abupt.model import construct
    from ai4e_contrib.ability.model.abupt.sampling import prepare_inputs
    from ai4e_core.applications.aero_cfd.post.inference import query_prepared

    _, cfg = prepared_case(tmp_path)
    _fit_config(cfg)
    config = OmegaConf.to_container(cfg, resolve=True)
    model = construct(**config["model"]["parameters"], data_specs=config["model"]["data_specs"])
    result = query_prepared(
        config,
        SimpleNamespace(dry_run=False),
        model,
        prepare_inputs=prepare_inputs,
        collate=collate,
        context_factory=InferenceContext,
    )
    assert set(result["shapes"]) == {"query_surface_pressure", "query_volume_velocity"}
    for field, shape in result["shapes"].items():
        value = torch.load(Path(result["output"]) / f"{field}.pt", weights_only=True)
        assert list(value.shape) == shape


def test_real_recipe_cached_query(tmp_path):
    folder, cfg = prepared_case(tmp_path)
    _fit_config(cfg)
    cfg.train.max_epochs = 1
    result, directory, _ = _run_script(folder, cfg)
    assert result.returncode == 0, result.stderr
    cfg.post.checkpoint = str(directory / "checkpoints/last.pt")
    cfg.post.query_chunk_size = 1
    cfg.post.sample_indices = [0]
    cfg.post.evaluate = False
    cfg.post.save_predictions = False
    cfg.post.export_vtk = False
    result, _, summary = _run_script(folder, cfg, entry="post.py")
    assert result.returncode == 0, result.stderr
    report = summary["reports"]["post"]
    assert report["mode"] == "post"
    surface = Path(report["output"]) / "sample_0000_surface.vtp"
    volume = Path(report["output"]) / "sample_0000_volume.vtu"
    assert surface.is_file() and volume.is_file()
    from ai4e_core.abilities.postproc.export.mesh import verify_mesh_outputs

    verify_mesh_outputs(surface, volume, n_surface=4, n_volume=8)
    assert not (Path(cfg.paths.datasets.predictions) / "query").exists()
    cfg.post.overwrite = False
    result, _, summary = _run_script(folder, cfg, entry="post.py", extra=("--dry-run",))
    assert result.returncode == 0, result.stderr
    assert summary["reports"]["post"]["mode"] == "post_check"


def test_batch_two_recipe_resume(tmp_path):
    import shutil

    from tests.integration.test_dataset_recipe import execute_case, setup_case

    folder, cfg = setup_case(tmp_path)
    shutil.copytree(Path(cfg.dataset.root) / "a", Path(cfg.dataset.root) / "c")
    cfg.dataset.partition.train = ["a", "c"]
    cfg.statistics.mode = "reference"
    assert execute_case(folder, cfg) == 0
    cfg.normalization.execute = True
    cfg.sampling.supernodes.num_points = 2
    cfg.sampling.domains.surface.anchor.num_points = 2
    cfg.sampling.domains.volume.anchor.num_points = 1
    _fit_config(cfg)
    cfg.train.batch_size = 2
    result, full_dir, _ = _run_script(folder, cfg)
    assert result.returncode == 0, result.stderr
    full = torch.load(full_dir / "checkpoints/last.pt", weights_only=False)
    cfg.train.max_epochs = 1
    result, one_dir, _ = _run_script(folder, cfg)
    assert result.returncode == 0, result.stderr
    cfg.train.resume = str(one_dir / "checkpoints/last.pt")
    cfg.train.max_epochs = 2
    result, resumed_dir, _ = _run_script(folder, cfg)
    assert result.returncode == 0, result.stderr
    resumed = torch.load(resumed_dir / "checkpoints/last.pt", weights_only=False)
    assert full["updates"] == resumed["updates"] == 2
    for name, value in full["model"].items():
        torch.testing.assert_close(value, resumed["model"][name], rtol=1e-5, atol=1e-6)
