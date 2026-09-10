"""仅供参考验收的参数名称映射，不是运行时检查点兼容接口。"""


def mapped_state(reference, model):
    """只用于对照的权重名称映射；不作为生产 checkpoint 导入 API。"""
    origin = reference.state_dict()
    mapping = {}
    for key in model.state_dict():
        source = key
        if key.startswith("biases."):
            domain, suffix = key[len("biases.") :].split(".", 1)
            source = f"domain_biases.{domain}.mlp.{suffix}"
        elif key.startswith("feature_projections."):
            domain, suffix = key[len("feature_projections.") :].split(".", 1)
            source = f"domain_feature_projs.{domain}.mlp.{suffix}"
        elif key.startswith("readouts."):
            domain, part, suffix = key[len("readouts.") :].split(".", 2)
            module = "norm_final" if part == "norm" else "linear.project"
            source = f"domain_decoder_projections.{domain}.{module}.{suffix}"
        elif key.startswith("encoder.message."):
            prefix, suffix = key.rsplit(".", 1)
            source = prefix + ".project." + suffix
        elif key.startswith("encoder.proj."):
            source = key.replace("encoder.proj.", "encoder.proj.project.")
        elif key.startswith(("blocks.", "geometry_blocks.", "decoders.")):
            if key.startswith("decoders."):
                _, domain, i, rest = key.split(".", 3)
                prefix = f"domain_decoder_blocks.{domain}.{i}"
                attention = "attention_block.mixed_attention"
                perceiver = False
            else:
                group, i, rest = key.split(".", 2)
                perceiver = group == "blocks" and model.block_types[int(i)] == "p"
                prefix = f"{'physics_blocks' if group == 'blocks' else group}.{i}"
                attention = (
                    "attn"
                    if perceiver
                    else "attention_block.mixed_attention"
                    if group == "blocks"
                    else "attention_block"
                )
            part, suffix = rest.split(".", 1)
            if part.startswith("norm_"):
                name = {
                    "norm_q": "norm1q" if perceiver else "norm1",
                    "norm_kv": "norm1kv" if perceiver else "norm1",
                    "norm_mlp": "norm2",
                }[part]
                source = f"{prefix}.{name}.{suffix}"
            elif part in ("q", "proj"):
                source = f"{prefix}.{attention}.{part}.{suffix}"
            elif part == "kv":
                source = f"{prefix}.{attention}.{suffix}"
            else:
                source = f"{prefix}.{rest}"
        mapping[key] = origin[source]
    return mapping
