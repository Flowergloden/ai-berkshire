# ai-berkshire 21 个投资研究 Skill → Kimi Work 适配性分析矩阵

- 生成日期：2026-10-10
- 源仓库（只读）：`C:/Users/xdhui/CommonProjects/ai-berkshire-kimi-work-integration/ai-berkshire/skills/*.md`
- 生成产物（由 `scripts/build_kimi_work_skills.py` 幂等生成）：散装 `dist/<name>/SKILL.md`（tools 用项目绝对路径）+ 插件 `plugin/personal/ai-berkshire/`（skills ×21 用官方 `<plugin-root>/tools/` 占位路径，另拷贝 tools ×12）
- 环境事实：Windows 上 `python3` 不存在，统一用 `python`；3 个主 tools（`financial_rigor.py`、`terminal_value.py`、`report_audit.py`）仅用标准库，冒烟已通过。

## 分类定义

- **A 类·纯方法论**：只依赖联网搜索与写作，仅注入通用 adapter note。
- **B 类·依赖 tools/ 脚本**：adapter note + 正文 `python3 tools/xxx.py` 机械改写为 `python <tools 前缀>/xxx.py`（散装产物的前缀是项目绝对路径 `C:/Users/xdhui/CommonProjects/ai-berkshire-kimi-work-integration/ai-berkshire/tools`，插件产物的前缀是 `<plugin-root>/tools`），输出路径 Windows 化。
- **C 类·多 Agent 编排**：在 B 类改动基础上，adapter note 中追加「多 Agent 编排的 Kimi Work 执行方式」整段说明（角色拆解 → 并行子任务独立执行 → 主 Agent 汇总），并声明忽略 TeamCreate/TaskCreate/SendMessage 等 Claude Code 专有工具调用。

## 全局改写规则（脚本 `transform_body` 实现）

| 原文 | 改写后 |
|---|---|
| `$ARGUMENTS` | 保留在正文，adapter note 首条声明其=当前会话中用户的请求 |
| `python3 tools/xxx.py` / `` `tools/xxx.py` `` | `python <tools 前缀>/xxx.py`（散装=项目绝对路径；插件=`<plugin-root>/tools`，官方占位约定，运行时解析） |
| `~/ai-berkshire/tools/xxx.py` | 同上，按产物类型取前缀 |
| `` `skills/financial-data.md` `` | "financial-data 技能（同一 ai-berkshire 技能包/插件内的 `financial-data` 技能）中的数据源规范" |
| `` `~/xxx.md` ``（报告输出） | `` `C:/Users/xdhui/reports/xxx.md` `` |
| `` `reports/...` ``（仓库相对输出路径） | `` `C:/Users/xdhui/reports/...` `` |
| `/tmp/...` | `C:/Users/xdhui/AppData/Local/Temp/...` |
| WebSearch / WebFetch | adapter note 声明：Kimi Work 内置联网搜索；读具体页面全文用 WebBridge 打开 |
| Team/Task/SendMessage 编排 | C 类 adapter note 整段覆盖：保守的「Agent 集群」指令（并行子任务、各自独立、主 Agent 汇总；不支持并行时串行降级） |
| 取数路由（2026-10-10 新增） | 除 dyp-ask / wechat-article 外的 19 个技能，adapter note 注入「数据获取路由」段：优先本机官方数据插件（ifind / yahoo_finance / sec_edgar / tianyancha / imf / world_bank / FRED / scholar），通用搜索作第二来源，双源交叉验证纪律不变（脚本 `DATA_ROUTED_EXCLUDE` 控制范围） |

报告输出目录统一约定为 `C:/Users/xdhui/reports/`（Windows 用户目录下，agent 可自行创建），已在每个 adapter note 中说明。

## 逐 Skill 分类明细

### A 类（6 个）

| Skill | 引用的外部文件 | 需改写的段落 | 预期风险 |
|---|---|---|---|
| deep-company-series | 无（样本目录 `reports/腾讯/...` 已 Windows 化） | 无实质改写，仅 note | 低：纯写作流程 |
| dyp-ask | 无 | 无 | 低：纯问答框架 |
| era-alpha | 无 | 无 | 低 |
| financial-data | `tools/twstock_data.py`（引用，已改绝对路径） | 数据源规范正文不改 | 低：本身是规范文档，被其他技能交叉引用 |
| income-investment | `financial_rigor.py`、`report_audit.py`、`reports/...`（已改写） | 取数指令为英文原文，保留 | 低 |
| thesis-drift | `financial_rigor.py`（可选）、`reports/{公司名}-thesis*.md` 快照 | 快照查找路径已 Windows 化 | 低-中：依赖历史快照文件是否存在于约定目录 |

注：income-investment / thesis-drift 虽引用 tools，但均为辅助性单点调用，无编排，故归 A 偏 B；脚本按统一规则对其做了 B 类同款路径改写（adapter note 注：A 类 note 未含工具段，但正文路径已被全局规则改写，不影响使用）。

### B 类（5 个）

| Skill | 引用的外部文件 | 需改写的段落 | 预期风险 |
|---|---|---|---|
| bottleneck-hunter | `twstock_data.py`、`financial-data.md`、`reports/bottleneck-map/*` | 台股取数段落、扫描产物目录 | 中：日更扫描依赖 `C:/Users/xdhui/reports/bottleneck-map/` 目录持续性 |
| industry-funnel | `report_audit.py` | 准出抽检段 | 低 |
| portfolio-review | `financial_rigor.py`、`reports/portfolio-latest.md` | 组合文件读写路径 | 中：依赖既有组合文件，首跑需从无到有 |
| quality-screen | 无 tools，仅用 WebSearch | 无 | 低 |
| thesis-tracker | `financial_rigor.py`、既有 investment-research 报告 | 估值锚点取数段 | 中：依赖先前报告是否存在于约定目录 |

### C 类（10 个）

| Skill | 引用的外部文件 | 需改写的段落 | 预期风险 |
|---|---|---|---|
| earnings-review | `financial_rigor.py`、`report_audit.py`、`twstock_data.py`、`financial-data.md` | "使用 Task 工具启动多个后台 Agent 并行获取原始材料"段 | 中：并行取数降级为串行/集群子任务 |
| earnings-team | `financial_rigor.py`、`report_audit.py` | 四大师并行 + 编辑/读者评审共 6 Agent 的全文编排 | 中 |
| industry-research | `report_audit.py`、`financial-data.md` | Task 后台 Agent 全上市公司扫描段、`~/` 输出路径 | 中 |
| investment-checklist | `financial_rigor.py` | "每家公司一个后台 Agent"段、`~/` 输出路径 | 中 |
| investment-research | `financial_rigor.py`、`report_audit.py`、`terminal_value.py`、`financial-data.md`、历史横评报告引用 | Task 取数段、`~/` 输出路径 | 中：引用的历史报告 `reports/7公司10年投资价值横评...` 不在交付环境 |
| investment-team | `financial_rigor.py`、`report_audit.py`、`twstock_data.py`、`financial-data.md` | 全文 Team/Task/SendMessage 编排（第一步¾ WebSearch 权限预检段为 Claude 专有，note 已声明忽略） | 高：编排最复杂；权限预检段无对应物，Kimi Work 联网由平台保证 |
| management-deep-dive | `financial_rigor.py` | Task 并行收集段 | 中 |
| news-pulse | `xueqiu_scraper.py`（雪球爬虫） | TeamCreate + 4 侦察 Agent 编排、`/tmp/` 输出 | 高：雪球爬虫依赖网络与反爬，非标准库冒烟范围；10 分钟时效目标在多 Agent 降级后可能超时 |
| private-company-research | 无 tools，6 Agent + WebFetch 精读 | 全文 6 Agent 编排（1071 行，最长 skill） | 中-高：碎片信息交叉验证工作量巨大 |
| wechat-article | 无 | 作者-编辑-读者三 Agent 协作（顺序为主，并行审阅） | 低-中：串行降级完全可行 |

## 验证

- `python -X utf8 build_kimi_work_skills.py` 生成 21 个包；`--check` 校验幂等通过。
- 21 个 frontmatter 均通过 PyYAML 解析，`name` 与目录名一致，`description` 为中文且含触发场景。
- 正文残留扫描（去除 adapter note 后）：`python3 tools/`、`~/ai-berkshire`、`skills/financial-data.md`、`` `~/ ``、`/tmp/`、`` `reports/ `` 均为 0。
- 抽查：A 类 `dyp-ask`、B 类 `bottleneck-hunter`、C 类 `investment-team`（详见交付说明）。
