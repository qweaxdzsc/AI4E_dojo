"""前端构建产物按存在性打入 wheel；纯 Python 开发安装不依赖未生成目录。"""
from pathlib import Path
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """发布工作台前先构建前端，已有静态包会原样包含在安装包。"""
    def initialize(self, version, build_data):
        """仅包含实际生成的 dist，不收集 node_modules 或运行缓存。"""
        root = Path(self.root)
        dist = root/'frontend'/'dist'
        if dist.is_dir():
            build_data['force_include'][str(dist)] = 'ai4e_viz/frontend/dist'
