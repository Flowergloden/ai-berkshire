# AGENTS.md — ai-berkshire-kimi-work-integration

把 [ai-berkshire](https://github.com/xbtlin/ai-berkshire)（21 个价值投资研究 Skill，原生 Claude Code / Codex）移植为本机 **Kimi Work**（桌面 GUI Agent，不是 Kimi Code CLI）可用的技能包，并持续维护：修正适配问题、跟随上游更新、评估与 Kimi Work 官方金融插件的取舍。

## 项目结构

- `ai-berkshire/` — 上游仓库的**只读**克隆（含 `skills/*.md` 源文件与 `tools/*.py` 计算脚本）。不要向它提交改动；该目录有自己的 `AGENTS.md`，进入前必读。
- `scripts/build_kimi_work_skills.py` — 转换脚本：从 `ai-berkshire/skills/*.md` 生成两类产物（幂等，可重跑；`--check` 只校验不写文件）：散装 `dist/<name>/SKILL.md`（tools 用项目绝对路径）与插件产物 `plugin/personal/ai-berkshire/`（skills ×21 + tools 拷贝，tools 引用用官方 `<plugin-root>` 占位约定）。adapter note 含取数路由段（优先本机官方数据插件，`DATA_ROUTED_EXCLUDE` 控制排除）。
- `scripts/install_skills.py` — 散装安装脚本：把 `dist/` 全部技能包拷贝到 `%APPDATA%\kimi-desktop\daimon-share\daimon\skills\` 并在 `official-skill-origins.json` 登记（幂等）。**插件形态验证通过后仅作回滚手段保留**。
- `scripts/release_plugin.py` — 插件发布：校验（validate_plugin）→ 升 `+local` 版本（cachebuster，`--no-bump` 跳过）→ 走官方 CLI 登记进个人市场（register_personal，显式传 `--share-dir` 与 `--daimon-bin`）。登记后用户到 Kimi Work 插件页「个人」页签点 ＋ 安装/更新，**免重启**。
- `scripts/uninstall_loose_skills.py` — 散装清理：删除 dist 名单 ∩ origins custom 登记的技能目录与登记（install_skills.py 的逆操作，`--yes` 跳过确认）。
- `dist/<name>/SKILL.md` — 生成的 21 个散装技能包。**不要手工编辑**，改转换逻辑后重跑生成脚本。
- `plugin/personal/ai-berkshire/` — Kimi 插件源目录（个人市场登记条目 sourcePath 指向它，**路径不能移动**）。`kimi.plugin.json`、`locales/` 由官方脚手架 create_plugin.py 一次性生成后入 git 手工维护（改元数据用 plugin-builder 的 update_plugin.py）；`skills/`、`tools/` 由生成脚本全量托管，**不要手工编辑**。
- `docs/` — 项目文档：
  - `PLAN.md` — 原始实施计划
  - `EXECUTOR_PROMPT.md` — 执行用 prompt
  - `adaptation-matrix.md` — 21 个 skill 的 A/B/C 适配分类矩阵
  - `verification.md` — 端到端验证记录（2026-10-10，含已知限制）
  - `porting-brief-ai-berkshire-vs-kimi-plugins.md` — 移植现状与官方插件对比的参考 prompt（**维护本移植的会话先读它**）

## 环境事实（Windows 本机）

- Python 命令名是 `python`（没有 `python3`）；主 tools（`financial_rigor.py`、`terminal_value.py`、`report_audit.py`）仅依赖标准库。
- 散装技能包内 tools 绝对路径由生成脚本自动取 `<项目根>/ai-berkshire/tools/`；插件内 tools 用 `<plugin-root>/tools/` 占位，运行时解析为插件安装根目录，不随项目位置变化。
- 报告统一输出到 `C:/Users/xdhui/reports/`。
- 散装安装后需**完全退出并重启 Kimi Work**（杀掉全部 Kimi.exe 进程）才生效；**插件安装/更新走 daemon 热更，无需重启**。
- 登记用官方 CLI：`%APPDATA%\kimi-desktop\daimon-bundle\bin\kimi-daimon.cmd`；`KIMI_SHARE_DIR`/`DAIMON_RUNTIME_BINARY_PATH` 在本机 shell 未注入，`release_plugin.py` 已内置正确路径（官方脚本在非 macOS 下会错误回退 `~/.kimi`，必须显式传 `--share-dir`）。
- plugin-builder 官方脚本目录：`%APPDATA%\kimi-desktop\daimon-share\daimon\skills\plugin-builder\scripts\`。

## 工作规则

- `ai-berkshire/skills/*.md` 是 canonical 源；上游 `git pull` 后依次运行：
  1. `python scripts/build_kimi_work_skills.py`
  2. `python scripts/release_plugin.py`（校验 + 升版本 + 重登记）
  3. 用户在 Kimi Work「个人」页签点「更新」验证（免重启）
  （散装回滚路径：`build` → `install_skills.py` → 完全重启 Kimi Work。）
- 改动转换脚本后必须跑 `python scripts/build_kimi_work_skills.py --check` 确认 dist 与插件产物均为最新。
- 技能适配分 A（纯方法论）/ B（依赖 tools 脚本）/ C（多 Agent 编排）三类，规则见 `docs/adaptation-matrix.md`；新增 skill 时先在矩阵中登记分类再改脚本。
- 验证纪律：如实记录通过/失败，不得把未验证项说成已完成（见 `docs/verification.md` 第 4 节的已知限制格式）。
- 本项目是学习研究用途，不构成投资建议。
