# -*- coding: utf-8 -*-
"""清理本项目安装的 21 个散装技能（插件形态验证通过后的迁移收尾）。

动作（install_skills.py 的逆操作，幂等）：
1. 以 dist/ 下的技能包名单为准（即本项目安装的那批），删除
   %APPDATA%\\kimi-desktop\\daimon-share\\daimon\\skills\\<name>\\ 目录；
2. 从 official-skill-origins.json 移除对应登记（仅删本项目名单内的条目，不碰其他）。

安全约束：
- 只删除同时在 dist/ 名单与 origins 登记（kind=custom）中的技能；其他目录/条目一律不动；
- 默认打印清单并等待确认，--yes 跳过确认；
- 回滚：重跑 install_skills.py 即可恢复散装技能。

前提：插件（plugin/personal/ai-berkshire）已在 Kimi Work「个人」页签安装并验证可用。
"""
import json
import os
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # kimi-work/ 目录（本文件位于 kimi-work/scripts/ 下）
DIST = BASE / "dist"
KIMI_DESKTOP = Path(os.environ["APPDATA"]) / "kimi-desktop"
SKILLS_DIR = KIMI_DESKTOP / "daimon-share" / "daimon" / "skills"
ORIGINS_JSON = KIMI_DESKTOP / "kimi-agent" / "official-skill-origins.json"


def main():
    assume_yes = "--yes" in sys.argv[1:]
    if not DIST.is_dir():
        sys.exit("dist/ 不存在，无法确定本项目安装的技能名单")
    names = sorted(p.name for p in DIST.iterdir() if (p / "SKILL.md").is_file())
    if not names:
        sys.exit("dist/ 下没有技能包")

    origins = {}
    if ORIGINS_JSON.is_file():
        origins = json.loads(ORIGINS_JSON.read_text(encoding="utf-8"))

    # 只处理“dist 名单 ∩ origins custom 登记”的技能
    targets = [n for n in names if origins.get(n, {}).get("kind") == "custom"]
    skipped = [n for n in names if n not in targets]

    print(f"将清理 {len(targets)} 个散装技能：")
    for n in targets:
        exists = (SKILLS_DIR / n).is_dir()
        print(f"  - {n}（skills 目录{'存在' if exists else '已不存在'}，origins 登记将移除）")
    if skipped:
        print(f"跳过 {len(skipped)} 个（无 custom 登记，可能已被清理或属其他来源）：")
        for n in skipped:
            print(f"  - {n}")
    if not targets:
        print("没有需要清理的技能。")
        return

    if not assume_yes:
        answer = input("确认删除以上散装技能目录与登记？[y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print("已取消。")
            return

    removed_dirs, removed_entries = 0, 0
    for n in targets:
        dest = SKILLS_DIR / n
        if dest.is_dir():
            shutil.rmtree(dest)
            removed_dirs += 1
        if origins.pop(n, None) is not None:
            removed_entries += 1

    ORIGINS_JSON.write_text(
        json.dumps(origins, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"完成：删除 {removed_dirs} 个技能目录、移除 {removed_entries} 条 origins 登记。")
    print("回滚方式：python kimi-work/scripts/install_skills.py（在仓库根执行）")


if __name__ == "__main__":
    main()
