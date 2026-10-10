# 将 ai-berkshire 接入 Kimi Work 的实施计划

## 目标

把 https://github.com/xbtlin/ai-berkshire 的全部 **21 个投资研究 skill** 安装到本机 **Kimi Work**（桌面 GUI Agent，注意不是 Kimi Code CLI），使其能在 Kimi Work 的技能面板中出现、可通过 `/` 调用或被自动触发，并抽样端到端验证可用。

## 已确认的关键事实（调查结论）

**ai-berkshire 仓库结构**
- `skills/*.md`：21 个 canonical workflow 源文件（Claude Code command 格式）
- `codex-skills/<name>/SKILL.md`：由 `scripts/sync-codex-skills.py` 从源文件生成，已是标准 Agent Skills 格式（YAML frontmatter + "Codex adapter note" 头部适配段）——**这是转换的直接参照样板**
- `tools/`：3 个 Python 精确计算/审计脚本（`financial_rigor.py`、`terminal_value.py`、`report_audit.py`），skill 文本中以 `python3 tools/xxx.py` 相对路径调用
- skill 之间存在交叉引用（如各 skill 引用 `skills/financial-data.md` 的数据源规范）

**Kimi Work 技能机制**
- 技能 = 标准 Agent Skills 格式（`<name>/SKILL.md`，frontmatter 含 name/description），与本仓库 codex-skills 格式同源
- 官方安装路径：技能面板 GUI 上传本地技能；输入 `/` 调用；Agent 按 description 自动触发
- 本机已装 Kimi Work：内置技能位于 `%APPDATA%\kimi-desktop\daimon-share\daimon\skills\`（由 daimon 的 manifest 管理，属内置区，不要直接写入）；**用户自定义技能的落盘位置未知，需第一步实测确认**
- 能力映射：Claude Code 的 Task/子 Agent → Kimi Work「Agent 集群」；WebSearch → 内置联网搜索 / WebBridge；Bash → 本地终端执行

**已确认的决策**：全部 21 个 skill；先做逐 skill 适配性分析，能最小适配的最小适配、必须重写的才重写；脚本化安装。

## 工作目录约定

不污染本机其他仓库与上游仓库，工作文件放在本项目根目录 `C:\Users\xdhui\CommonProjects\ai-berkshire-kimi-work-integration\`：
- 仓库克隆：`ai-berkshire/`（只读上游副本，内含 tools/ 脚本）
- 文档：`docs/`（PLAN、EXECUTOR_PROMPT、adaptation-matrix、verification、porting-brief）
- 脚本：`scripts/build_kimi_work_skills.py`、`scripts/install_skills.py`
- 产物：`dist/<name>/SKILL.md` × 21

本任务属本机环境接入，不改动任何既有代码仓库。

## 实施步骤

### 阶段 0：环境准备
1. `git clone https://github.com/xbtlin/ai-berkshire.git C:\Users\xdhui\ai-berkshire`
2. 验证本机 Python：检查 `python --version` 与 `python3 --version` 哪个可用；查看 `tools/*.py` 的 import，确认是否仅用标准库（若需第三方包则 `pip install`）；实跑 `python tools/financial_rigor.py calc` 类命令冒烟。

### 阶段 1：逐 skill 适配性分析
3. 通读 21 个 `skills/*.md` 源文件，逐个分类并产出《适配清单》（`adaptation-matrix.md`）：
   - **A 类·纯方法论**（如 dyp-ask、investment-checklist、financial-data）：只依赖搜索与写作 → 仅加 adapter note
   - **B 类·依赖 tools/ 脚本**（如 investment-research、earnings-review、quality-screen、industry-funnel、thesis-drift）：adapter note + 工具调用改绝对路径 + `python3`→`python` + 报告输出路径 Windows 化
   - **C 类·多 Agent 编排**（investment-team、earnings-team、wechat-article、deep-company-series 等）：除 B 类改动外，把"Task 工具启动 N 个子 Agent"的段落**重写**为 Kimi Work Agent 集群指令

   每个 skill 记录：类别、引用的外部文件、需改写的段落、预期风险。

### 阶段 2：编写转换脚本，生成 21 个技能包
4. 参照上游 `scripts/sync-codex-skills.py` 的思路，编写 `build_kimi_work_skills.py`，从 `skills/*.md` 生成 `dist/<name>/SKILL.md`：
   - frontmatter：`name` 用原 skill 名；`description` 用中文写清用途与触发场景（决定自动触发质量）
   - 正文头部注入「Kimi Work adapter note」，内容按阶段 1 的分类逐 skill 定制：
     - `$ARGUMENTS` → 当前会话中用户的请求
     - Task/子 Agent → 使用 Agent 集群并行执行（C 类整段重写）
     - WebSearch → 内置联网搜索，必要时 WebBridge 打开具体页面
     - `python3 tools/xxx.py` → `python C:/Users/xdhui/ai-berkshire/tools/xxx.py`
     - 交叉引用 `skills/financial-data.md` → "遵循 financial-data 技能中的数据源规范"
     - 报告输出 `~/xxx.md` → Windows 用户目录下的明确路径
5. 跑脚本生成全部 21 个 `dist/` 技能包；人工抽查 A/B/C 各 1 个，核对 frontmatter 合法、正文无残留 Claude 专有指令。

### 阶段 3：安装到 Kimi Work
6. **探路**：通过 Kimi Work GUI「技能 → 上传本地技能」手动上传 1 个技能包（选最简单的 A 类，如 dyp-ask），然后：
   - 用文件搜索确认用户技能实际落盘目录（对比上传前后 `daimon-share` 等目录变化）
   - 在 Kimi Work 输入 `/` 确认该技能可见、描述正确
7. **批量安装**：写 `install_skills.py`，把其余 20 个技能目录复制到第 6 步确认的用户技能目录；重启 Kimi Work（或刷新技能面板）后核对 21 个全部可见。
   - 回退方案：若用户技能必须经 GUI/内部注册、直接拷贝不生效，则改为把 21 个技能包整理好后由用户 GUI 逐个上传，并在交付说明中写清步骤。

### 阶段 4：端到端验证
8. 触发面检查：21 个技能全部出现在 `/` 列表，name/description 正确。
9. 每类抽 1 个做真实端到端测试（真实让 Kimi Work 执行，非仅检查加载）：
   - A 类：`/dyp-ask 拼多多的护城河在哪里？` —— 验证方法论文本生效
   - B 类：`/investment-checklist 茅台` 或 `/news-pulse 腾讯` —— 重点验证 Kimi Work 终端成功执行 `python C:/Users/xdhui/ai-berkshire/tools/financial_rigor.py ...`
   - C 类：`/investment-team 美团` —— 验证 Agent 集群编排段落可用、最终报告落盘
10. 把验证结果与未通过项记入 `verification.md`；未通过项给出修复并复测，或明确标注限制。

### 后续可维护性
- 上游更新流程：`git -C C:\Users\xdhui\ai-berkshire pull` → 重跑 `build_kimi_work_skills.py` → 重跑 `install_skills.py`（脚本幂等）。

## 主要风险与对策
- **用户技能目录不可脚本写入** → 第 6 步先实测，必要时回退 GUI 上传（已含回退方案）
- **Windows 上 `python3` 不存在或 tools 有第三方依赖** → 阶段 0 提前验证并适配命令
- **C 类多 Agent skill 在 Kimi Work 的 Agent 集群语义与 Claude Code Task 不完全等价** → 阶段 1 分析时逐段核对，重写时保守表述；阶段 4 用 investment-team 实测兜底
- **Kimi Work Beta 高频迭代导致技能机制变化** → 转换/安装脚本化，重跑成本低
