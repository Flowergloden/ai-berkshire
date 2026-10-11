# AI Berkshire Codex Guide

This repository contains investment research workflows, reports, and shared
validation tools. Keep compatibility with both Claude Code and Codex users.

## Project Layout

- `skills/*.md`: Claude Code slash-command source files.
- `codex-skills/*/SKILL.md`: Codex skill packages. Most are generated from
  `skills/*.md`; Codex-only hand-written packages are allowed when clearly
  marked and no same-named `skills/*.md` source exists.
- `codex-prompts/*.md`: generated Codex custom prompts for slash-command
  style entry points. These are a compatibility layer; skills remain preferred.
- `tools/*.py`: shared financial validation and data tools used by both systems.
- `reports/`: research outputs. Do not rewrite unrelated reports while changing
  tooling or skills.
- `scripts/sync-codex-skills.py`: regenerates Codex skills from `skills/*.md`.
- `scripts/install-codex-skills.sh` / `scripts/install-codex-skills.bat`:
  installs Codex skills locally.
- `scripts/install-codex-prompts.sh` / `scripts/install-codex-prompts.bat`:
  installs generated Codex slash prompts locally.
- `scripts/install-claude-commands.sh` / `scripts/install-claude-commands.bat`:
  installs Claude Code commands locally.

## Compatibility Rules

- Treat `skills/*.md` as the canonical workflow source.
- After changing any file in `skills/`, run:
  `python3 scripts/sync-codex-skills.py`
- If slash prompt compatibility is needed, also run:
  `python3 scripts/sync-codex-prompts.py`
- Do not manually edit generated `codex-skills/*/SKILL.md` unless also updating
  the corresponding source in `skills/`.
- For Codex-only hand-written packages under `codex-skills/`, keep them clearly
  marked as Codex-only and do not create a same-named `skills/*.md` file unless
  intentionally adopting the workflow for Claude Code too.
- Keep tool paths compatible with the documented checkout path:
  `~/ai-berkshire/tools/...`
- Keep `CLAUDE.md` for Claude Code behavior and this `AGENTS.md` for Codex
  behavior.

## Research Quality Rules

- Before starting any research, run the `date` command to confirm today's
  date. Treat that date as the baseline for "latest" data (prices, market cap,
  most recent filings), and state the data cutoff date in the report header.
  Never assume the current date from training data.
- Financial data must come from at least two independent sources when the skill
  requires verification.
- Use exact arithmetic tools for market cap, valuation, cross-source checks, and
  scenario analysis:
  `python3 tools/financial_rigor.py ...`
- Use report audit tooling before treating generated research as publishable:
  `python3 tools/report_audit.py ...`
- Clearly label low-confidence conclusions, incomplete data, and source gaps.
- This project is for learning and research, not investment advice.

## Editing Rules

- Preserve existing report files unless the task specifically asks to change
  them.
- Keep changes scoped to the requested skill, tool, script, or documentation.
- Before finishing a skill/tool change, run the relevant syntax or generation
  check. For compatibility changes, run:
  `python3 scripts/sync-codex-skills.py`
- To verify generated Codex artifacts are current without rewriting files, run:
  `python3 scripts/sync-codex-skills.py --check`
  and, when slash prompts are relevant:
  `python3 scripts/sync-codex-prompts.py --check`

---

## Kimi Work 移植层（fork 仓库 kimi-work 分支）

把 [ai-berkshire](https://github.com/xbtlin/ai-berkshire)（上游 21 个价值投资研究 Skill，原生 Claude Code / Codex；插件现交付 15 个，6 个被裁见下）移植为本机 **Kimi Work**（桌面 GUI Agent，不是 Kimi Code CLI）可用的技能包，并持续维护：修正适配问题、跟随上游更新、评估与 Kimi Work 官方金融插件的取舍。

本工作副本是 fork 仓库（`Flowergloden/ai-berkshire`）`kimi-work` 分支的 checkout；移植层位于 `kimi-work/` 子目录；上游原貌在 `main` 分支（纯镜像，零自有 commit）。本指南原在 `kimi-work/AGENTS.md`，2026-10-11 上移至仓库根并与上游指南合并为一份，适用于整个工作副本。

### 项目结构（fork 仓库内）

- `main` 分支 — 上游（xbtlin/ai-berkshire）的**纯镜像**，Sync fork 永远 fast-forward，禁止任何自有 commit。
- `kimi-work` 分支 — **默认分支**，承载全部移植内容（`kimi-work/` 子目录）；本地 clone 固定停在此分支。
- `openspec/` — 位于仓库根（2026-10-11 由 `kimi-work/openspec/` 上移），OpenSpec 配置与 change 档案（`fork-integration`）。
- `kimi-work/scripts/build_kimi_work_skills.py` — 转换脚本：以**仓库根**为上游源（`REPO = parents[2]`，读 `skills/*.md`、`tools/*.py`）生成两类产物（幂等，可重跑；`--check` 先跑规则命中断言再校验产物）：散装 `kimi-work/dist/<name>/SKILL.md`（tools 用检出路径绝对路径）与插件产物 `kimi-work/plugin/personal/ai-berkshire/`（skills ×15 + tools 拷贝，tools 引用用官方 `<plugin-root>` 占位约定）。`PRUNED_SKILLS` 排除集（6 个被裁技能）只约束生成范围，`check_rule_hits` 仍扫描全部上游源文件（断言哨兵与生成范围解耦，期望计数不因裁剪调整）。`transform_body` 的每条改写规则登记期望命中语义（`*` 至少一次 / 精确次数），上游改写原文导致命中数不符时构建非零退出（CI 适配哨兵）；改规则后须同步校准期望。
- `kimi-work/scripts/release_plugin.py` — 插件发布：校验（validate_plugin）→ 升 `+local` 版本（cachebuster，`--no-bump` 跳过）→ 走官方 CLI 登记进个人市场（register_personal，显式传 `--share-dir` 与 `--daimon-bin`）。登记后用户到 Kimi Work 插件页「个人」页签点「更新」，**免重启**。
- `kimi-work/scripts/install_skills.py` / `uninstall_loose_skills.py` — 散装安装/清理（插件形态的回滚手段；散装安装后需完全重启 Kimi Work 生效）。
- `kimi-work/dist/` — 生成的 15 个散装技能包（`.gitignore` 排除，内嵌本机绝对路径）。**不要手工编辑**，改转换逻辑后重跑生成脚本。
- `kimi-work/plugin/personal/ai-berkshire/` — Kimi 插件源目录（个人市场登记条目 sourcePath 指向它，**路径不能移动**）。`kimi.plugin.json`、`locales/` 手工维护（改元数据用 plugin-builder 的 update_plugin.py）；`skills/`、`tools/` 由生成脚本全量托管并**提交入库**（clone 本分支即可登记，无需先构建），**不要手工编辑**。
- `kimi-work/docs/` — 项目文档：`PLAN.md`、`EXECUTOR_PROMPT.md`、`adaptation-matrix.md`（A/B/C 适配分类矩阵）、`verification.md`（端到端验证记录）、`porting-brief-ai-berkshire-vs-kimi-plugins.md`（**维护本移植的会话先读它**）。
- `.github/workflows/kimi-work.yml`（仓库根）— `main` 收到 push（上游 sync 发生）或手动 dispatch 时：merge `main` 到 `kimi-work` → 跑构建（含断言）→ 产物有变化则推 `bot/kimi-work-sync-*` 分支并向 `kimi-work` 开 PR（人工把关，PR diff 即适配审计）；构建失败则 workflow 红且不开 PR。

### 环境事实（Windows 本机）

- 本地唯一工作副本：`C:\Users\xdhui\CommonProjects\ai-berkshire`（fork clone，**固定 `kimi-work` 分支**，勿切走；登记 sourcePath 盯着它）。
- remotes：`origin` = Flowergloden fork，`upstream` = xbtlin。上游 sync 用 GitHub Sync fork 按钮（fast-forward `main`）或 `git fetch upstream && git merge --ff-only`。
- fork 的**默认分支是 `kimi-work`**（GitHub 只从默认分支发现 workflows；这同时让 PR 默认指向 `kimi-work`）。`main` 仍保持纯镜像。
- Python 命令名是 `python`（没有 `python3`）；主 tools（`financial_rigor.py`、`terminal_value.py`、`report_audit.py`）仅依赖标准库。
- 报告统一输出到 `C:/Users/xdhui/reports/`（`REPORTS_DIR` 在构建脚本中写死，标有 TODO 可移植性欠账，个人专用 fork 定位下不改）。
- 散装安装后需**完全退出并重启 Kimi Work**（杀掉全部 Kimi.exe 进程）才生效；**插件安装/更新走 daemon 热更，无需重启**。
- 登记用官方 CLI：`%APPDATA%\kimi-desktop\daimon-bundle\bin\kimi-daimon.cmd`；`KIMI_SHARE_DIR`/`DAIMON_RUNTIME_BINARY_PATH` 在本机 shell 未注入，`release_plugin.py` 已内置正确路径（官方脚本在非 macOS 下会错误回退 `~/.kimi`，必须显式传 `--share-dir`）。
- plugin-builder 官方脚本目录：`%APPDATA%\kimi-desktop\daimon-share\daimon\skills\plugin-builder\scripts\`。

### 工作规则

- **日常更新（跟随上游）**：
  1. GitHub 上 Sync fork（`main` fast-forward）→ CI `kimi-work-sync` 自动 merge + 构建 + 有变化开 PR → 人工 review PR diff（适配审计）后合并。
  2. 本地 `git pull`（停在 `kimi-work` 分支）。
  3. CI 已把产物提交入库时本地无需再跑构建；本地手动改动转换脚本后才需要：
     `python kimi-work/scripts/build_kimi_work_skills.py && python kimi-work/scripts/build_kimi_work_skills.py --check`（在仓库根执行）。
  4. 插件产物有变化时 `python kimi-work/scripts/release_plugin.py`（校验 + 升版本 + 重登记，登记条目 sourcePath 不变），用户在 Kimi Work「个人」页签点「更新」（免重启）。
- **断言纪律**：转换规则命中断言失败 = 上游改写了原文。读构建输出中列出的失效规则与实际命中数，人工核对上游改动后更新规则或期望（改期望是显式决定，不许静默改规则绕过）。
- `ai-berkshire/skills/*.md`（仓库根 `skills/`，main 分支镜像）是 canonical 源；**不要直接改动**（上游内容只通过 sync 进入）。
- 技能适配分 A（纯方法论）/ B（依赖 tools 脚本）/ C（多 Agent 编排）三类，规则见 `kimi-work/docs/adaptation-matrix.md`；上游新增 skill 时 CI 会断言失败提醒——在矩阵登记分类、给 `CATEGORY`/`DESCRIPTIONS` 补条目、校准规则期望。
- **裁剪纪律**（2026-10-11 起）：被裁技能由构建脚本 `PRUNED_SKILLS` 排除集管理（现 6 个：news-pulse / financial-data / earnings-review / deep-company-series / industry-research / portfolio-review，理由见 `kimi-work/docs/adaptation-matrix.md` 与 `kimi-work/README.md`）。增删排除集时必须同步：manifest `skillOverrides` 与计数文案（`update_plugin.py`）、`locales/en-US.json`、adaptation-matrix 标注，然后重跑构建 + `--check` + `release_plugin.py`；断言扫描范围（全部上游源文件）与期望计数不因裁剪改动。上游删除被裁技能源文件导致断言失败是期望的哨兵行为，届时人工核对。
- 本文件前半部分是上游指南（Codex 指南与 `CLAUDE.md` 同属上游），遵循"只 add 不动"：不改上游内容，不与上游路径撞名（`kimi-work/` 子目录 + `kimi-work.yml` workflow 名）。
- 改动转换脚本后必须跑 `--check` 确认 dist 与插件产物均为最新，并提交插件产物入库。
- 验证纪律：如实记录通过/失败，不得把未验证项说成已完成（见 `kimi-work/docs/verification.md` 的已知限制格式）。
- 本项目是学习研究用途，不构成投资建议。
