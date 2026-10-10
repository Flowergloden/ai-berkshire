# -*- coding: utf-8 -*-
"""把 dist/ 下全部技能包批量安装到 Kimi Work 用户技能目录。

机制（由 GUI 上传探路实测确认）：
1. 技能文件夹拷贝到 %APPDATA%\\kimi-desktop\\daimon-share\\daimon\\skills\\<name>\\
2. 在 %APPDATA%\\kimi-desktop\\kimi-agent\\official-skill-origins.json 登记 {"<name>": {"kind": "custom"}}

幂等：已存在的技能先清除旧目录再拷贝；重复运行结果一致。
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
    if not DIST.is_dir():
        sys.exit("dist/ 不存在，请先运行 build_kimi_work_skills.py")
    packages = sorted(p for p in DIST.iterdir() if (p / "SKILL.md").is_file())
    if not packages:
        sys.exit("dist/ 下没有技能包")

    origins = {}
    if ORIGINS_JSON.is_file():
        origins = json.loads(ORIGINS_JSON.read_text(encoding="utf-8"))

    installed, skipped = [], []
    for pkg in packages:
        dest = SKILLS_DIR / pkg.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(pkg, dest)
        origins[pkg.name] = {"kind": "custom"}
        installed.append(pkg.name)

    ORIGINS_JSON.write_text(
        json.dumps(origins, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"已安装 {len(installed)} 个技能到 {SKILLS_DIR}：")
    for name in installed:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
