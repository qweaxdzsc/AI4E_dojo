"""静态外流 MeshGraphNet 单域、多域、核心监督和完整拼回契约。"""

import torch

from ai4e_contrib.application.aero_cfd import meshgraphnet


class IdentityNormalization:
    """测试用恒等变换。"""

    def apply(self, fields):
        return dict(fields)

    def inverse(self, _name, value):
        return value


def config(domains, *, partitioned=False):
    specs = {}
    bindings = {}
    supervision = []
    sampling = {}
    for domain, output in domains.items():
        specs[domain] = {"feature_dim": {"normal": 3}, "output_dims": {output: 1}}
        bindings[domain] = {
            "position": f"{domain}_position",
            "features": {"normal": f"{domain}_normal"},
            "targets": {output: f"{domain}_{output}"},
        }
        supervision.append(
            {
                "name": f"{domain}_{output}",
                "prediction": f"{domain}_{output}",
                "target": f"{domain}_{output}_target",
                "normalization": f"{domain}_{output}",
                "loss": "mse",
                "weight": 1.0,
            }
        )
        method = (
            {"method": "core_halo", "core_nodes": 2, "halo_hops": 2}
            if partitioned
            else {"method": "full"}
        )
        sampling[domain] = {"train": method, "infer": method}
    return meshgraphnet.resolve(
        {
            "model": {
                "parameters": {"hidden_dim": 8, "processor_layers": 2},
                "data_specs": {"position_dim": 3, "domains": specs, "conditioning_dims": {}},
                "supervision": supervision,
            },
            "trainprep": {"domains": bindings, "conditioning": {}},
            "sampling": {"seed": 42, "domains": sampling},
            "train": {},
        }
    )


def sample(domains):
    result = {
        "identity": {"sample": "s", "partition": "train", "index": 0},
        "fields": {},
        "domains": {},
        "conditions": {},
    }
    edge_index = torch.tensor([[0, 1, 1, 2, 2, 3, 3, 4], [1, 0, 2, 1, 3, 2, 4, 3]])
    for domain, output in domains.items():
        result["fields"][f"{domain}_position"] = torch.tensor(
            [[float(i), 0.0, 0.0] for i in range(5)]
        )
        result["fields"][f"{domain}_normal"] = torch.tensor([[0.0, 1.0, 0.0]] * 5)
        result["fields"][f"{domain}_{output}"] = torch.arange(5, dtype=torch.float32)[:, None]
        result["domains"][domain] = {
            "graph": {
                "edge_index": edge_index,
                "source_ids": torch.arange(5),
                "topology_digest": domain,
            },
            "ids": torch.arange(5),
            "position": f"{domain}_position",
            "identity_basis": "source",
        }
    return result


def test_static_single_and_multi_domain_networks_use_core_supervision():
    domains = {"surface": "pressure", "volume": "speed"}
    cfg = config(domains, partitioned=True)
    model = meshgraphnet.construct(**meshgraphnet.training_parameters(cfg))
    assert set(model.networks) == {"surface", "volume"}
    assert model.networks["surface"] is not model.networks["volume"]
    batch = meshgraphnet.prepare_sample(sample(domains), cfg, IdentityNormalization())
    report = meshgraphnet.loss(model, batch, cfg)
    assert torch.isfinite(report["loss"])
    assert batch["targets"]["surface_pressure_target"].shape == (2, 1)


def test_partitioned_prediction_matches_full_graph_with_sufficient_halo():
    domains = {"surface": "pressure"}
    full_cfg = config(domains)
    part_cfg = config(domains, partitioned=True)
    model = meshgraphnet.construct(**meshgraphnet.training_parameters(full_cfg)).eval()
    data = sample(domains)
    normalization = IdentityNormalization()
    full = meshgraphnet.predict_sample(model, data, full_cfg, normalization, preparation_id="x")
    partitioned = meshgraphnet.predict_sample(
        model, data, part_cfg, normalization, preparation_id="x"
    )
    assert torch.allclose(full["surface_pressure"], partitioned["surface_pressure"], atol=1e-6)


def test_nasa_conditions_are_broadcast_to_every_surface_node():
    cfg = config({"surface": "cp"})
    cfg["model"]["data_specs"]["conditioning_dims"] = {"conditions": 6}
    cfg["trainprep"]["conditioning"] = {"conditions": {"field": "conditions"}}
    data = sample({"surface": "cp"})
    data["conditions"]["conditions"] = torch.arange(6, dtype=torch.float32)[None]

    class Transform:
        def apply(self, value):
            return value

    normalization = IdentityNormalization()
    normalization.transforms = {"conditions": Transform()}
    batch = meshgraphnet.prepare_sample(data, cfg, normalization, evaluation=True)
    features = batch["inputs"]["graphs"]["surface"]["node_features"]
    assert features.shape == (5, 12)
    assert torch.equal(features[:, -6:], data["conditions"]["conditions"].expand(5, -1))
