"""参数化物理数据的读取与校验；数据生成在独立入口完成。"""


def rawprep(cfg, *, dataset_component, session, **components):
    """逐个核验清单中的完整物理数据，报告来源而不改配置。"""
    dataset = dataset_component.Dataset(cfg["dataset"]["manifest"])

    def check(record):
        dataset.read(record)
        return {"id": record["id"]}

    session.execute_samples(dataset.manifest["samples"], check, stage="rawprep")
    result = {
        "manifest": str(dataset.path),
        "content_id": dataset.manifest["content_id"],
        "samples": len(dataset.manifest["samples"]),
    }
    session.report(result, stage="dataset")
    return result
