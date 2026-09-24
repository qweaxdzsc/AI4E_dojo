"""参数化 PDE 案例显式资源生成；数据算法由数据集 application 提供。"""


def generate_smoke_data(request: dict) -> dict:
    """按案例资源声明生成最小数据，非空目录由生产者拒绝覆盖。"""
    from ai4e_contrib.application.datasets.parametric import generate_dataset

    options = request["options"]
    manifest = generate_dataset(request["case"], {**options, "output": request["output"]})
    return {"case": request["case"], "manifest": manifest, **options, "device": "cpu"}
