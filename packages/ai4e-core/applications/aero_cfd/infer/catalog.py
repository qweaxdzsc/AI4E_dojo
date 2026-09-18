"""从模型输出和物理准备生成目录；不在网页猜测字段和单位。"""

from ai4e_core.abilities.eval.catalog import metric_catalog


def describe_fields(config: dict, *, dataset_component=None) -> list[dict]:
    """按有序域和目标声明列出分量，单位未知保留空值。"""
    metadata = (
        dataset_component.inference_fields()
        if dataset_component and hasattr(dataset_component, "inference_fields")
        else {}
    )
    units = config.get("dataset", {}).get("field_units", {})
    result = []
    domains = config.get("trainprep", {}).get("domains", {})
    dimensions = config.get("model", {}).get("data_specs", {}).get("domains", {})
    for domain, declaration in domains.items():
        for name, source in declaration["targets"].items():
            info = metadata.get(source, {})
            count = (
                dimensions.get(domain, {}).get("output_dims", {}).get(name, info.get("components"))
            )
            if count is None:
                raise ValueError(f"推理字段缺少分量声明: {domain}/{name}")
            parts = ["scalar"] if count == 1 else [*map(str, range(count)), "magnitude"]
            for component in parts:
                label = info.get("label", name)
                if component != "scalar":
                    names = info.get("component_labels", [])
                    label += (
                        " · 模长"
                        if component == "magnitude"
                        else "-"
                        + (
                            names[int(component)]
                            if int(component) < len(names)
                            else str(int(component) + 1)
                        )
                    )
                result.append(
                    {
                        "id": f"{domain}:{name}:{component}",
                        "domain": domain,
                        "field": name,
                        "source": source,
                        "component": component,
                        "components": count,
                        "label": label,
                        "category": info.get("category", "流体"),
                        "unit": units.get(source, info.get("unit")),
                        "association": "point",
                        "available": True,
                        "evaluable": True,
                        "default": component != "magnitude",
                    }
                )
    return result


def describe_catalog(config, *, dataset_component=None) -> dict:
    """共享目录供预检和管理端消费。"""
    from ai4e_core.applications.aero_cfd.infer.vtk_capability import describe_vtk_exports

    return {
        "fields": describe_fields(config, dataset_component=dataset_component),
        "metrics": metric_catalog(),
        "vtk_exports": describe_vtk_exports(config, dataset_component=dataset_component),
    }
