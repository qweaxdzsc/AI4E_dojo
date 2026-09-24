"""外流结构图装配；平台视图参数与 AB-UPT 阶段适配由应用持有。"""

from pathlib import Path

DEFAULT_VIEW = "stage_trunk"
PLATFORM_VIEWS = (
    {
        "id": "stage_trunk",
        "label": "阶段主干",
        "member": "model.stage-trunk.html",
        "options": {
            "collapse_modules_after_depth": 1,
            "forced_module_tracing_depth": 0,
            "show_compressed_view": True,
            "show_module_attr_names": True,
            "show_non_gradient_nodes": False,
        },
    },
    {
        "id": "stage_blocks",
        "label": "阶段压缩块",
        "member": "model.stage-blocks.html",
        "options": {
            "collapse_modules_after_depth": 1,
            "forced_module_tracing_depth": 1,
            "show_compressed_view": True,
            "show_module_attr_names": True,
            "show_non_gradient_nodes": False,
        },
    },
)


def export_platform_views(network, inputs, output_dir, *, revision, input_source, predict=None):
    """组装真实网络及两档显示，交付固定文件与来源记录。"""
    from ai4e_core.abilities.modeling.inspection import preserve_model_state, trace_views

    from .abupt_stage_display import organize_for_display

    with preserve_model_state(network):
        organized = organize_for_display(network, inputs)
        model, values = organized if organized else (network, inputs)
        return trace_views(
            model,
            values,
            Path(output_dir),
            revision=revision,
            input_source=input_source,
            views=PLATFORM_VIEWS,
            default_view=DEFAULT_VIEW,
            predict=None if organized else predict,
            model_type=type(network).__module__ + "." + type(network).__name__,
        )
