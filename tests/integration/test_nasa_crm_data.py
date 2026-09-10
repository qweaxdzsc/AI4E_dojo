"""B1—B3：真实 HDF5、完整点字段、来源身份与冻结准备。"""

import json

import h5py
import numpy as np
import pytest
from omegaconf import OmegaConf

from ai4e_contrib.application.datasets import nasa_crm
from ai4e_core.applications.aero_cfd.pointfield_workflow import datapre
from ai4e_core.applications.aero_cfd.trainprep.pointfields import open_preparation
from ai4e_core.run.dataset import execute
from tests.transolver_assets import configuration


class Reports:
    """单元装配测试只收报告，正式运行由真实会话验收。"""

    def report(self, *args, **kwargs):
        pass


def prepared(tmp_path):
    cfg, path = configuration(tmp_path)
    datapre(
        cfg, dataset_component=nasa_crm, model_component=None, executor=execute, session=Reports()
    )
    return cfg, path


def test_source_identity_and_train_statistics(tmp_path):
    """B1/B2/B3：跨来源重名不混读；只有训练数据参与统计。"""
    cfg, _ = prepared(tmp_path)
    view = nasa_crm.View(cfg.data_root)
    assert {k: len(v) for k, v in view.partitions.items()} == {
        "train": 4,
        "validation": 1,
        "test": 2,
    }
    m = view.manifest
    assert m["statistics"]["conditions"]["count"] == 4
    assert m["statistics"]["labels"]["count"] == 4 * 24
    assert m["statistics"]["conditions"]["mean"][0] < 10
    assert view.read("test", 0)["conditions"][0] > 100
    with h5py.File(cfg.dataset.train_h5, "r") as raw:
        name = view.partitions["train"][0]
        reconstructed = np.empty(24, dtype=np.float32)
        for part in range(4):
            values = view.read("train", 0, selection=part)
            reconstructed[values["point_ids"]] = values["points"][:, 0]
        np.testing.assert_array_equal(reconstructed, raw[name]["CoordinateX"][:])


def test_missing_fields_identify_sample(tmp_path):
    """B1：缺必需字段时明确报出样本和字段。"""
    cfg, _ = configuration(tmp_path)
    with h5py.File(cfg.dataset.train_h5, "a") as data:
        del data["Sample001"]["NormalX"]
    with pytest.raises(ValueError, match="Sample001.*NormalX"):
        nasa_crm.RawDataset(cfg.dataset)


def test_resume_and_preparation_content_guard(tmp_path):
    """B2/B3：完整样本复用，内容替换使冻结准备失效。"""
    from ai4e_contrib.ability.model.transolver3.component import resolve

    cfg, _ = prepared(tmp_path)
    config = resolve(OmegaConf.to_container(cfg, resolve=True))
    _, _, record = open_preparation(config, nasa_crm)
    path = tmp_path / "preparation.json"
    path.write_text(json.dumps(record))
    open_preparation(config, nasa_crm, path)
    target = next((tmp_path / "data/train").glob("*/labels_part0.npy"))
    value = np.load(target)
    value[0, 0] += 1
    np.save(target, value)
    with pytest.raises(ValueError, match="准备"):
        open_preparation(config, nasa_crm, path)
    cfg.dataset.resume = True
    datapre(
        cfg, dataset_component=nasa_crm, model_component=None, executor=execute, session=Reports()
    )
    open_preparation(config, nasa_crm, path)


@pytest.mark.parametrize("kind", ["shape", "empty", "attribute", "nonfinite"])
def test_source_failure_variants(tmp_path, kind):
    """B1：字段形状、空输入、缺工况和非有限值均能定位到样本。"""
    cfg, _ = configuration(tmp_path)
    with h5py.File(cfg.dataset.train_h5, "a") as source:
        group = source["Sample001"]
        if kind == "attribute":
            del group.attrs["Mach"]
        elif kind == "nonfinite":
            group["PressureCoefficient"][0] = np.nan
        else:
            del group["CoordinateX"]
            group.create_dataset("CoordinateX", data=np.empty((0,) if kind == "empty" else (2, 2)))
    with pytest.raises(ValueError, match="Sample001"):
        raw = nasa_crm.RawDataset(cfg.dataset)
        for split, names in raw.partitions.items():
            if "Sample001" in names and split != "test":
                raw.read(split, names.index("Sample001"))


def test_resume_does_not_trust_incomplete_commit_manifest(tmp_path):
    """B2：即使来源摘要合法，缺少文件项目的完成标记也必须重建。"""
    cfg, _ = prepared(tmp_path)
    directory = next((tmp_path / "data/train").iterdir())
    marker = directory / ".commit.json"
    record = json.loads(marker.read_text())
    record["files"] = {}
    marker.write_text(json.dumps(record))
    broken = directory / "labels_part0.npy"
    broken.write_bytes(b"broken")
    cfg.dataset.resume = True
    datapre(
        cfg, dataset_component=nasa_crm, model_component=None, executor=execute, session=Reports()
    )
    assert np.load(broken).shape == (6, 4)
    assert len(json.loads(marker.read_text())["files"]) == 18


@pytest.mark.parametrize("invalid", ["constant", "nan", "inf"])
def test_invalid_statistics_cannot_be_frozen(invalid):
    """B3：常量与非有限训练统计不能进入可消费的冻结变换。"""
    from ai4e_core.abilities.data.stats.population import PopulationMoments
    from ai4e_core.abilities.transform.pointfields import FieldNormalization

    values = np.ones((2, 4))
    if invalid != "constant":
        values[0, 0] = float(invalid)
    moments = PopulationMoments(4)
    with pytest.raises(ValueError):
        moments.update(values)
        moments.finalize()
    record = {
        k: {"mean": [0.0], "std": [0.0 if invalid == "constant" else float(invalid)]}
        for k in ("conditions", "labels")
    }
    with pytest.raises(ValueError, match="统计"):
        FieldNormalization(record)


def test_field_order_and_cross_source_point_count_guard(tmp_path):
    """B1/B3：字段排列变化和来源点数不一致不能作为合法数据消费。"""
    cfg, _ = prepared(tmp_path)
    path = tmp_path / "data/manifest.json"
    record = json.loads(path.read_text())
    record["fields"]["labels"].reverse()
    record["fingerprint"] = nasa_crm.manifest_digest(record)
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="顺序"):
        nasa_crm.View(path)
    with h5py.File(cfg.dataset.test_h5, "a") as source:
        for group in source.values():
            for key in list(group):
                values = group[key][:]
                del group[key]
                group.create_dataset(key, data=values[:-1])
    with pytest.raises(ValueError, match="点数"):
        nasa_crm.RawDataset(cfg.dataset)


def test_consumer_uses_only_public_dataset_view(tmp_path):
    """B3：只实现公开读取/描述协议的视图可以准备与遍历，不暴露存储内部属性。"""
    from types import SimpleNamespace

    from ai4e_contrib.ability.model.transolver3.component import resolve
    from ai4e_core.applications.aero_cfd.trainprep.pointfields import PointDataset

    cfg, _ = prepared(tmp_path)

    class PublicView:
        def __init__(self, path):
            self._delegate = nasa_crm.View(path)
            self.partitions = self._delegate.partitions

        def read(self, *args, **kwargs):
            return self._delegate.read(*args, **kwargs)

        def describe(self):
            return self._delegate.describe()

        def content_digest(self):
            return self._delegate.content_digest()

    settings = resolve(OmegaConf.to_container(cfg, resolve=True))
    view, normalization, record = open_preparation(settings, SimpleNamespace(View=PublicView))
    assert record["split_counts"]["validation"] == 1
    dataset = PointDataset(view, normalization, "validation")
    assert len(dataset) == 4 and dataset[0]["inputs"]["features"].shape == (6, 12)
