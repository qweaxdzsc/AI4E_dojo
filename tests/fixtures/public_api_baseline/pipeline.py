"""自由组件流程；公开运行入口只管理执行外围。"""
from configuration import load_configuration
from user_steps import read_mesh, encode_points, save_features
from user_wiring import mesh_to_points
from ai4e_core import run


def pipeline(cfg):
    """普通阶段立即执行，原样返回自定义对象与结果。"""
    mesh = run.stage("read", read_mesh, cfg.input_path)
    points = run.stage("connect", mesh_to_points, mesh)
    features = run.stage("encode", encode_points, points, radius=cfg.radius)
    path = run.stage("save", save_features, features, cfg.output_path)
    run.TrainingRun().report({"output": str(path), "count": len(features)}, stage="features")
    return path


if __name__ == "__main__":
    raise SystemExit(run.launch(pipeline, script=__file__, config_loader=load_configuration))
