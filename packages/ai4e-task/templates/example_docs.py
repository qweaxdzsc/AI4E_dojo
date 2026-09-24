"""案例说明的构建副本：保留来源摘要，并把链接限制到实际交付文件。"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from urllib.parse import unquote

DOC_DIRECTORY = ".dojo-docs"
_LINK = re.compile(r"(!?)\[([^\]\n]+)\]\((<[^>]+>|[^)\n]+)\)")


def render_document(
    text: str, source: Path, destination: Path, mappings: list[tuple[Path, Path]]
) -> str:
    """转换指向已交付文件的链接；外部参考保留，未交付本机路径改为明示文本。

    mappings按优先级给出来源目录与目标目录，不访问未映射的外部文件。
    这不是通用Markdown解析器；支持案例正文中的内联链接与图像。
    """

    def link(match):
        marker, label, raw = match.groups()
        raw = raw.strip().removeprefix("<").removesuffix(">")
        if raw.startswith(("https://", "http://", "mailto:", "#")):
            return match.group(0)
        path, separator, anchor = raw.partition("#")
        resolved = (source.parent / unquote(path)).resolve()
        for origin, target in mappings:
            if resolved.is_relative_to(origin.resolve()):
                mapped = target / resolved.relative_to(origin.resolve())
                if mapped.is_file():
                    relative = Path(os.path.relpath(mapped, destination.parent)).as_posix()
                    suffix = separator + anchor if separator else ""
                    return f"{marker}[{label}](<{relative}{suffix}>)"
        return f"{label}（原参考 `{raw}` 未随此说明交付）"

    return _LINK.sub(link, text)


def write_example_documents(destination: Path, sources: dict[str, Path]) -> dict:
    """从原README生成可搬移副本；根README与用户脚本不作隐式改写。"""
    directory = destination / DOC_DIRECTORY
    directory.mkdir()
    metadata = {}
    for role, root in sources.items():
        source = root / "README.md"
        target = directory / f"{role}.md"
        original = source.read_bytes()
        text = render_document(original.decode("utf-8"), source, target, [(root, destination)])
        target.write_text(text, encoding="utf-8")
        metadata[role] = {
            "path": target.relative_to(destination).as_posix(),
            "source_sha256": hashlib.sha256(original).hexdigest(),
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        }
    lines = [
        "# 案例改写说明",
        "",
        "本目录是由案例README生成的副本；修改研究代码前先核对两层说明。",
        "",
    ]
    for role, entry in metadata.items():
        label = {"base": "基案例完整说明", "extension": "本次扩展的变化", "case": "完整案例说明"}[
            role
        ]
        lines.append(f"- [{label}]({Path(entry['path']).name})")
    (directory / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"entry": f"{DOC_DIRECTORY}/index.md", "sources": metadata}
