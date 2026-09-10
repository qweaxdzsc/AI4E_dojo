"""数值验收证据门禁：缺来源、数据身份或功能映射时拒绝宣布等价。"""

from ai4e_core.abilities.data.validate.fingerprint import file_fingerprint


def validate(baseline, coverage, *, reference_root, dataset_identity):
    """核对固定容差、来源内容与一百项映射；不读取历史目录猜测成功。"""
    if baseline.get("tolerance") != {"rtol": 1e-5, "atol": 1e-6}:
        raise ValueError("比较容差必须为固定协议值")
    if not dataset_identity or not baseline.get("files"):
        raise ValueError("缺少数据身份或参考来源")
    if len(coverage) != 100 or {row.get("id") for row in coverage} != set(range(1, 101)):
        raise ValueError("功能项必须恰好覆盖 1—100")
    if any(not row.get("leaf") or not row.get("dojo") for row in coverage):
        raise ValueError("缺少功能对应关系")
    for relative, expected in baseline["files"].items():
        path = reference_root / relative
        if not path.is_file() or file_fingerprint(path) != expected:
            raise ValueError(f"参考来源变化: {relative}")
    return {"reference_verified": True, "dataset_identity": dataset_identity, "mapped_items": 100}
