"""把经过清单筛选的研究资源加入 ai4e-task wheel。

recipes、.context、缓存和本机路径不会进入资源目录；skill 正文仍只来自仓库唯一源文件。
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """构建时生成纯资源 staging 目录，再由 Hatch force-include。"""

    def initialize(self, version, build_data):
        package_root = Path(self.root)
        repo_root = package_root.parents[1]
        source_examples = repo_root / "examples"
        manifest = source_examples / "case-manifest.json"
        guide = repo_root / "DOJO_AGENT_GUIDE.md"
        skill = repo_root / ".agents/skills/dojo-research/SKILL.md"
        help_center = repo_root / "docs/agent-help"
        if (
            not manifest.is_file()
            or not guide.is_file()
            or not skill.is_file()
            or not (help_center / "manifest.json").is_file()
        ):
            raise FileNotFoundError(
                "构建资源缺少 case-manifest.json、DOJO_AGENT_GUIDE.md、skill 或 Agent Help Center"
            )
        staging = package_root / ".hatch-resources"
        if staging.exists():
            shutil.rmtree(staging)
        (staging / "examples").mkdir(parents=True)
        data = json.loads(manifest.read_text(encoding="utf-8"))
        shutil.copy2(manifest, staging / "examples/case-manifest.json")
        examples_readme = source_examples / "README.md"
        if examples_readme.is_file():
            shutil.copy2(examples_readme, staging / "examples/README.md")
        for case in data["cases"]:
            source = source_examples / case["path"]
            target = staging / "examples" / case["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            if case["type"] == "standalone":
                shutil.copytree(
                    source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
                )
            else:
                shutil.copytree(
                    source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
                )
        shutil.copy2(guide, staging / "DOJO_AGENT_GUIDE.md")
        skill_target = staging / ".agents/skills/dojo-research/SKILL.md"
        skill_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill, skill_target)
        help_target = staging / "docs/agent-help"
        shutil.copytree(
            help_center,
            help_target,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        )
        build_data["force_include"][str(staging / "examples")] = "ai4e_task/resources/examples"
        build_data["force_include"][str(staging / "DOJO_AGENT_GUIDE.md")] = (
            "ai4e_task/resources/DOJO_AGENT_GUIDE.md"
        )
        build_data["force_include"][str(staging / ".agents")] = "ai4e_task/resources/.agents"
        build_data["force_include"][str(staging / "docs")] = "ai4e_task/resources/docs"
