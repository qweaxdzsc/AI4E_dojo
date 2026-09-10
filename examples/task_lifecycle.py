"""从本地已配置 recipe 建立研究项目，并派生第二个正式版本。"""

import argparse

from ai4e_task import (
    compare_versions,
    create_project,
    fork_task,
    get_lineage,
    new_task,
    submit_run,
    wait_run,
)


def main() -> None:
    """执行显式指定的案例目录；不自动下载或修改原始数据。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("project")
    parser.add_argument("recipe")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    create_project(args.project)
    first = new_task(args.project, "baseline", source=args.recipe)
    child = fork_task(args.project, first["id"], name="candidate")
    print(get_lineage(args.project))
    print(compare_versions(args.project, first["version_id"], child["version_id"]))
    if args.execute:
        for item in (first, child):
            run = submit_run(args.project, item["id"])
            print(wait_run(args.project, run["id"], timeout=60))


if __name__ == "__main__":
    main()
