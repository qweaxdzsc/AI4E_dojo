"""外流点流分块预测、具名解码与物理反变换。"""

from ai4e_core.abilities.inference.indexed_prediction import predict_indexed
from ai4e_core.abilities.sampling.points import point_indices
from ai4e_core.applications.aero_cfd.trainprep.point_inputs import prepare_point_sample


def predict_point_sample(model, sample, config, normalization, *, predict_stream):
    """完整预测各物理域；predict_stream 接收点流编号和模型具名输入。

    全部块共享几何选择；学习后的上下文不跨模型更新缓存。输出只反变换一次。
    """
    batch = prepare_point_sample(sample, config, normalization, evaluation=True)
    inputs = batch["inputs"]
    device = next(model.parameters()).device
    context = {k: v.to(device) for k, v in inputs.items() if k != "local_embedding"}
    output = {}
    key = f"{sample['identity'].get('partition', '')}/{sample['identity']['sample']}"
    for index, (domain, spec) in enumerate(config["model"]["data_specs"]["domains"].items()):
        points = inputs["local_embedding"][index]
        count = points.shape[1]
        order = point_indices(
            count, count, seed=config["infer"]["seed"], sample=key, operation=domain + ":infer"
        )

        def operation(ids, *, points=points, index=index):
            return predict_stream(model, points[:, ids].to(device), stream_index=index, **context)[
                0
            ]

        values, _ = predict_indexed(
            count, order, chunk_size=config["infer"]["query_chunk_size"], operation=operation
        )
        offset = 0
        for name, width in spec["output_dims"].items():
            source = config["trainprep"]["domains"][domain]["targets"][name]
            output[source] = normalization.inverse(source, values[:, offset : offset + width])
            offset += width
        if offset != values.shape[1]:
            raise ValueError("预测字段宽度不符")
    return output
