# -*- coding: utf-8 -*-
"""把 plugin/personal/ai-berkshire 发布到 Kimi Work 个人市场（登记 ≠ 安装）。

流程：校验（validate_plugin）→ 升 +local 版本（cachebuster，--no-bump 跳过）→
登记（register_personal，走客户端官方 CLI kimi-daimon kimi-plugin register-personal）。
三步全部调用本机 Kimi Work 自带的 plugin-builder 官方脚本，本脚本只做编排与路径解析。

用法（在仓库根执行）：
    python kimi-work/scripts/release_plugin.py            # 校验 + 升版本 + 登记（日常更新）
    python kimi-work/scripts/release_plugin.py --no-bump  # 只校验 + 登记（首次登记）

登记成功后插件出现在 Kimi Work 插件页「个人」页签（未安装），点 ＋ 安装即可（免重启）；
已安装用户按版本号检出更新，点「更新」生效。

权利扫描（rights_scan）命中时 register 以 exit 7 中止——本脚本不代为确认，
请人工审阅后决定是否加 --confirm-rights 重跑（见 plugin-builder SKILL.md 规则）。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # kimi-work/ 目录（本文件位于 kimi-work/scripts/ 下）
PLUGIN_DIR = BASE / "plugin" / "personal" / "ai-berkshire"
KIMI_DESKTOP = Path(os.environ["APPDATA"]) / "kimi-desktop"
SHARE_DIR = KIMI_DESKTOP / "daimon-share"  # KIMI_SHARE_DIR 未设时官方脚本会错误回退 ~/.kimi，必须显式传
BUILDER_SCRIPTS = (
    SHARE_DIR / "daimon" / "skills" / "plugin-builder" / "scripts"
)
DEFAULT_DAIMON_BIN = KIMI_DESKTOP / "daimon-bundle" / "bin" / "kimi-daimon.cmd"


def run(cmd: list[str], label: str, capture: bool = False) -> subprocess.CompletedProcess:
    print(f"==> {label}")
    proc = subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        if capture:
            sys.stdout.write(proc.stdout or "")
            sys.stderr.write(proc.stderr or "")
        raise SystemExit(f"{label} 失败（exit {proc.returncode}）")
    return proc


def main() -> None:
    bump = "--no-bump" not in sys.argv[1:]
    daimon_bin = (
        os.environ.get("DAIMON_RUNTIME_BINARY_PATH", "").strip()
        or str(DEFAULT_DAIMON_BIN)
    )
    if not PLUGIN_DIR.is_dir():
        raise SystemExit(f"{PLUGIN_DIR} 不存在，先运行 build_kimi_work_skills.py")
    if not BUILDER_SCRIPTS.is_dir():
        raise SystemExit(f"plugin-builder 脚本目录不存在：{BUILDER_SCRIPTS}")
    if not Path(daimon_bin).exists():
        raise SystemExit(f"kimi-daimon 不存在：{daimon_bin}（可用 DAIMON_RUNTIME_BINARY_PATH 覆盖）")

    run(
        [sys.executable, str(BUILDER_SCRIPTS / "validate_plugin.py"), str(PLUGIN_DIR)],
        "校验插件（validate_plugin）",
    )
    if bump:
        run(
            [sys.executable, str(BUILDER_SCRIPTS / "cachebuster.py"), str(PLUGIN_DIR)],
            "升 +local 版本（cachebuster）",
        )
    proc = run(
        [
            sys.executable,
            str(BUILDER_SCRIPTS / "register_personal.py"),
            str(PLUGIN_DIR),
            "--share-dir",
            str(SHARE_DIR),
            "--daimon-bin",
            daimon_bin,
        ],
        "登记进个人市场（register_personal）",
        capture=True,
    )
    # register_personal.py stdout 为人类可读行 + 一行 "result -> {json}"，从该行提取结果
    result = None
    for line in proc.stdout.splitlines():
        if line.strip().startswith("result -> "):
            try:
                result = json.loads(line.split("->", 1)[1].strip())
            except json.JSONDecodeError:
                pass
    if result is None:
        sys.stdout.write(proc.stdout)
        raise SystemExit("登记输出中未找到 result JSON，请检查上面的原始输出")
    if not result.get("ok"):
        sys.stdout.write(proc.stdout)
        raise SystemExit(f"登记失败：{result.get('error', '未知错误')}")
    print(f"登记成功：{PLUGIN_DIR.name}")
    print(f"插件链接：{result.get('link')}（点击可打开插件详情）")
    print("下一步：到 Kimi Work 插件页「个人」页签点 ＋ 安装（已装则点「更新」），免重启。")


if __name__ == "__main__":
    main()
