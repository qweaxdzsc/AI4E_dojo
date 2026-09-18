"""PI-BSNet 准备声明适配；保持原参数提取及冻结语义。"""


def preparation_parameters(config: dict) -> dict:
    """提取影响当前模型准备的参数，不要求其他模型采用样条配置。"""
    model = config["model"]
    return {
        "model": {
            key: model[key]
            for key in (
                "control_points",
                "degree",
                "hard_initial",
                "sampling",
                "boundary_conditions",
                "initial_conditions",
                "periodic_boundary_conditions",
            )
        },
        "boundary_enforcement": model["constraints"]["boundary_conditions"]["enforcement"],
    }
