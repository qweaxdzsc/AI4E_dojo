"""透明最小参考修正：屏蔽黏度公式未选分支，原源码文件保持不变。"""

import ast


def repair_vis(node):
    """只给原分段公式的未激活分支输入安全值；激活公式保持不变。"""
    for item in node.body:
        if isinstance(item, ast.FunctionDef) and item.name == "vis":

            class Input(ast.NodeTransformer):
                def __init__(self, name):
                    self.name = name

                def visit_Name(self, n):
                    return (
                        ast.copy_location(ast.Name(id=self.name, ctx=n.ctx), n)
                        if n.id == "T"
                        else n
                    )

            body = []
            for statement in item.body:
                if isinstance(statement, ast.Assign) and isinstance(statement.targets[0], ast.Name):
                    name = statement.targets[0].id
                    if name in ["val1", "val2", "val3"]:
                        i = name[-1]
                        safe = {"1": "0.0", "2": "40.0", "3": "100.0"}[i]
                        body.extend(ast.parse(f"T{i} = torch.where(cond{i}, T, {safe})").body)
                        statement.value = Input("T" + i).visit(statement.value)
                body.append(statement)
            # Group the three masks before the original formula assignments.
            masks = [
                s
                for s in body
                if isinstance(s, ast.Assign)
                and getattr(s.targets[0], "id", "") in ["T1", "T2", "T3"]
            ]
            body = [s for s in body if s not in masks]
            first = next(
                i
                for i, s in enumerate(body)
                if isinstance(s, ast.Assign) and getattr(s.targets[0], "id", "") == "val1"
            )
            item.body = body[:first] + masks + body[first:]
    return ast.fix_missing_locations(node)


def apply_to_source_module(module):
    """在已导入原模块中替换这一个函数，并保留其他源码行为。"""
    import inspect

    tree = repair_vis(ast.parse(inspect.getsource(module.PDE_F)).body[0])
    namespace = dict(vars(module))
    exec(  # noqa: S102 -- 执行已固定的用户本地源码及显式AST修正
        compile(ast.Module(body=[tree], type_ignores=[]), "explicit-vis-repair", "exec"), namespace
    )
    module.PDE_F.vis = staticmethod(namespace["PDE_F"].vis)
