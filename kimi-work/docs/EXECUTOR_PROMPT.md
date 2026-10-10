# 执行 Prompt：将 ai-berkshire 接入 Kimi Work

> 把下面整段内容作为任务指令交给负责实现的 agent。该 agent 没有任何前置上下文，所有需要的事实都已包含在内。

---

## 任务

把 GitHub 仓库 https://github.com/xbtlin/ai-berkshire 的全部 **21 个投资研究 skill** 安装到本机的 **Kimi Work**（月之暗面的桌面 GUI Agent，**不是** Kimi Code CLI），使其出现在 Kimi Work 的技能面板中、可通过 `/` 调用或被自动触发，并完成抽样端到端验证。

完整实施计划见 `docs/PLAN.md`（项目根下），先读它再动手。本 prompt 与其不一致时以 PLAN.md 为准，但如果你发现 PLAN.md 中的前提与实际情况不符（例如目录不存在、命令不可用），如实记录并按最合理方式推进，不要死磕计划原文。本 prompt 与其不一致时以 PLAN.md 为准，但如果你发现 PLAN.md 中的前提与实际情况不符（例如目录不存在、命令不可用），如实记录并按最合理方式推进，不要死磕计划原文。

## 运行环境

- Windows 10+，shell 为 Git Bash（用 Unix 语法，`/dev/null` 而非 `NUL`）
- 本机已安装 Kimi Work（`%APPDATA%\kimi-desktop` 存在）
- 用户语言：中文；所有产出文档用中文，编码 UTF-8

## 已调查确认的关键事实（不要重复调查，直接使用）

1. ai-berkshire 仓库结构：
   - `skills/*.md` — 21 个 canonical workflow 源文件（Claude Code command 格式）
   - `codex-skills/<name>/SKILL.md` — 由 `scripts/sync-codex-skills.py` 生成的标准 Agent Skills 格式（YAML frontmatter + adapter note），**这是你写转换脚本时的直接参照样板**
   - `tools/financial_rigor.py`、`tools/terminal_value.py`、`tools/report_audit.py` — skill 文本中以 `python3 tools/xxx.py` 调用的精确计算脚本
   - skill 间有交叉引用（多个 skill 引用 `skills/financial-data.md` 的数据源规范）
2. Kimi Work 技能 = 标准 Agent Skills 格式（`<name>/SKILL.md`，frontmatter 含 name、description），支持技能面板 GUI 上传本地技能，输入 `/` 调用。
3. Kimi Work 内置技能位于 `%APPDATA%\kimi-desktop\daimon-share\daimon\skills\`，由 daimon manifest 管理，**不要往里写**。用户自定义技能的落盘位置未知，需要你在阶段 3 实测确认。
4. 能力映射：Claude Code 的 Task/子 Agent → Kimi Work「Agent 集群」；WebSearch → Kimi Work 内置联网搜索 / WebBridge；Bash → Kimi Work 本地终端执行。

## 工作目录约定（严格遵守）

- 仓库克隆到固定路径：`C:\Users\xdhui\ai-berkshire\`（skill 中的 Python 工具将以此绝对路径引用）
- 所有工作文件放在本项目根目录 `C:\Users\xdhui\CommonProjects\ai-berkshire-kimi-work-integration\`（文档在 `docs/`、脚本在 `scripts/`、产物在 `dist/`）
- **不要**修改本项目以外的其他仓库；**不要**向 ai-berkshire 克隆仓库提交改动

## 执行步骤（四阶段）

### 阶段 0：环境准备
1. `git clone https://github.com/xbtlin/ai-berkshire.git C:/Users/xdhui/ai-berkshire`
2. 确认本机 Python：`python --version` / `python3 --version` 哪个可用；检查 `tools/*.py` 的 import 是否仅用标准库（有第三方依赖则 `pip install`）；实跑一次 `financial_rigor.py` 的子命令做冒烟，记录可用的 Python 命令名（后续转换脚本要用）。

### 阶段 1：逐 skill 适配性分析
3. 通读全部 21 个 `skills/*.md`，逐个分类，产出 `C:\Users\xdhui\CommonProjects\ai-berkshire-kimi-work-integration\adaptation-matrix.md`：
   - **A 类·纯方法论**：只依赖搜索与写作 → 仅加 adapter note
   - **B 类·依赖 tools/ 脚本**：adapter note + `python3 tools/xxx.py` 改为 `python C:/Users/xdhui/ai-berkshire/tools/xxx.py`（用阶段 0 确认的 Python 命令）+ 报告输出路径 Windows 化
   - **C 类·多 Agent 编排**（含"Task 工具/子 Agent 并行"的 skill，如 investment-team、earnings-team、wechat-article、deep-company-series）：除 B 类改动外，把多 Agent 编排段落**重写**为 Kimi Work Agent 集群指令
   每个 skill 记录：类别、引用的外部文件、需改写的段落、预期风险。

### 阶段 2：转换脚本与技能包生成
4. 参照上游 `scripts/sync-codex-skills.py` 的思路，编写 `C:\Users\xdhui\CommonProjects\ai-berkshire-kimi-work-integration\build_kimi_work_skills.py`，从 `skills/*.md` 生成 `dist/<name>/SKILL.md`：
   - frontmatter：`name` = 原 skill 名；`description` = 中文、写清用途与触发场景（决定 Kimi Work 自动触发质量）
   - 正文头部注入「Kimi Work adapter note」，按阶段 1 的分类逐 skill 定制：
     - `$ARGUMENTS` → 当前会话中用户的请求
     - Task/子 Agent → Agent 集群并行执行（C 类整段重写）
     - WebSearch → 内置联网搜索，必要时 WebBridge 打开具体页面
     - `python3 tools/xxx.py` → `python C:/Users/xdhui/ai-berkshire/tools/xxx.py`
     - `skills/financial-data.md` 交叉引用 → "遵循 financial-data 技能中的数据源规范"
     - `~/xxx.md` 输出路径 → Windows 用户目录明确路径
5. 跑脚本生成 21 个技能包；人工抽查 A/B/C 各 1 个，核对 frontmatter 合法、正文无残留的 Claude Code 专有指令。

### 阶段 3：安装到 Kimi Work
6. **探路（可能需要 GUI 操作）**：通过 Kimi Work「技能 → 上传本地技能」上传 1 个 A 类技能包（建议 dyp-ask）。如果你有桌面 GUI 自动化能力可自行操作；没有就明确指导用户完成这一步，然后你接手验证：
   - 对比上传前后 `%APPDATA%\kimi-desktop` 下各目录变化，确认用户技能实际落盘目录
   - 在 Kimi Work 输入 `/` 确认该技能可见、描述正确
7. **批量安装**：写 `install_skills.py`，把其余 20 个技能目录复制到确认的用户技能目录（脚本幂等）；重启/刷新 Kimi Work 后核对 21 个全部可见。
   - 回退：若直接拷贝不生效（例如必须经 GUI/内部注册），整理好 21 个技能包并在交付说明中写清 GUI 逐个上传的步骤，如实告知用户。

### 阶段 4：端到端验证
8. 触发面检查：21 个技能全部出现在 `/` 列表，name/description 正确。
9. 每类抽 1 个真实执行（不是只检查加载）：
   - A 类：`/dyp-ask 拼多多的护城河在哪里？`
   - B 类：`/investment-checklist 茅台` 或 `/news-pulse 腾讯` —— 重点验证 Kimi Work 终端成功执行了 `python C:/Users/xdhui/ai-berkshire/tools/financial_rigor.py ...`
   - C 类：`/investment-team 美团` —— 验证 Agent 集群编排段落可用、报告最终落盘
10. 结果记入 `docs/verification.md`：每个验证项的通过/失败、失败原因、修复动作；无法修复的明确标注限制，**不得把未验证项说成已完成**。

## 交付物清单（项目根下）

- `docs/adaptation-matrix.md` — 21 个 skill 的适配分类清单
- `scripts/build_kimi_work_skills.py` — 转换脚本（幂等，上游 git pull 后可重跑）
- `scripts/install_skills.py` — 安装脚本（幂等）
- `dist/<name>/SKILL.md` × 21 — 技能包
- `docs/verification.md` — 端到端验证记录

## 约束

- 全程用中文汇报；文件编码 UTF-8
- 每个阶段完成后向用户汇报一次进展；阶段 3 的 GUI 操作如无法自行完成，停下来给用户清晰的操作指引，不要假装完成
- 遇到计划外 blocker，先尝试合理解决；解决不了就停下来说明，不要绕过验证直接交付
