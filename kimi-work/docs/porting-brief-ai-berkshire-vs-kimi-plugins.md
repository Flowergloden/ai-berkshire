# 移植参考 Prompt：ai-berkshire 与 Kimi Work 官方金融插件的重合与互补

> 供负责移植/维护 ai-berkshire 的会话使用。本文件自包含，无需其他上下文。
> 当前处于测试阶段，以下结论均有调整空间，请以实测结果为准。

---

## 0. 你的任务背景

ai-berkshire（https://github.com/xbtlin/ai-berkshire ，MIT License）是一套价值投资投研 Skill 合集，原生于 Claude Code / Codex。此前一个会话已将它移植进 Kimi Work（见第 2 节现状）。你的职责是维护这次移植：**修正适配问题、评估与官方插件的取舍、必要时重新打包**。做任何改动前，先读完本文件第 1~4 节的事实与结论。

---

## 1. ai-berkshire 是什么

- **21 个 Markdown 技能 + 1 组 Python 工具脚本**（插件现交付 15 个，2026-10-11 裁剪 6 个，见第 2 节），核心是"巴菲特/芒格/段永平/李录"四大师价值投资方法论的结构化 prompt 工作流，不是代码项目。
- 技能清单（上游 21 个；★ = 已于 2026-10-11 从插件裁剪，源文件仍在上游 `skills/`）：

| 类别 | 技能 |
|---|---|
| 深度研究 | investment-research、investment-team、management-deep-dive、private-company-research、deep-company-series ★ |
| 财报分析 | earnings-review ★、earnings-team |
| 行业筛选 | industry-research ★、industry-funnel、quality-screen、bottleneck-hunter、era-alpha、investment-checklist |
| 持仓管理 | income-investment、portfolio-review ★、thesis-tracker、thesis-drift、news-pulse ★ |
| 思维工具 | dyp-ask（段永平问答）、financial-data ★、wechat-article |

- 工具脚本（`tools/` 下，仅依赖 Python 标准库）：financial_rigor.py（市值/估值验算、三情景估值，decimal 精确计算）、stock_screener.py、momentum_backtest.py、xueqiu_scraper.py、morningstar_fair_value.py、report_audit.py 等 12 个（xueqiu_scraper.py 依赖 playwright，其余仅标准库）。
- 上游仍在活跃更新（报告索引更新至 2026-10-09），移植后需考虑同步机制。

---

## 2. 当前移植现状（本机事实，已核实）

> 2026-10-11 起移植层迁入 fork 仓库（`Flowergloden/ai-berkshire`）`kimi-work` 分支的 `kimi-work/` 子目录；`main` 保持上游纯镜像。上游 sync = GitHub Sync fork（fast-forward `main`）→ CI 自动 merge + 构建 → 本地 `git pull`。

- **插件形态交付 15 个技能**（2026-10-11 从 21 裁剪 6 个：`news-pulse`、`financial-data`、`earnings-review`、`deep-company-series`、`industry-research`、`portfolio-review`，理由与恢复路径见 `../README.md` 裁剪记录）。散装技能已全部清理（`uninstall_loose_skills.py`，2026-10-11 验证通过，verification.md §8）；插件经「个人」页签热更安装，详情页技能列表与 `/` 触发列表实测恰为 15 个保留技能。
- **取数路由已升级（2026-10-10）**：除 dyp-ask / wechat-article 外的技能（现 13 个），adapter note 已注入「数据获取路由」段——取数优先路由到本机已装官方数据插件（ifind / yahoo_finance / sec_edgar / tianyancha / imf / world_bank / FRED / scholar），通用联网搜索作为第二来源；双源交叉验证纪律不变。
- **每个 SKILL.md 头部都有自动生成的「Kimi Work 适配说明」**，已处理：
  - `$ARGUMENTS` → 当前会话用户请求；
  - WebSearch/WebFetch → Kimi Work 内置联网 / WebBridge 抓全文；
  - 报告输出路径 `~/xxx.md` → `C:/Users/xdhui/reports/xxx.md`（目录需自建）；
  - `python3 tools/xxx.py` → `python <plugin-root>/tools/xxx.py`（插件产物用官方占位约定；散装产物为检出路径绝对路径）；
  - 日期基线、数据双源交叉验证、不编数纪律。
- **多 Agent 技能（investment-team / earnings-team / 各技能的并行数据收集步骤）做了保守降级**：忽略 Claude 的 Task/Team/SendMessage 调用，支持并行子任务则并行，否则主 Agent 串行完成各角色分析（结果等价、仅耗时更长），并要求各角色视角独立、不共享中间结论。
- **安装形态为插件包**：15 个技能 + 12 个 tools 脚本聚合为单插件 `ai-berkshire`（源目录 `C:\Users\xdhui\CommonProjects\ai-berkshire\kimi-work\plugin\personal\ai-berkshire\`，manifest 由官方脚手架 create_plugin.py 生成、locales 手工维护），已登记进个人市场（`daimon-share/daimon/plugin-market/personal/ai-berkshire.json`，`kimi-work://plugin?id=ai-berkshire`），用户在插件页「个人」页签安装/更新，**daemon 热更免重启**；更新链路为 `build_kimi_work_skills.py` → `release_plugin.py`（升 `+local` 版本 + 重登记）。被裁技能在保留技能正文中的引用由 adapter note 兜底声明覆盖（忽略"调用该技能"含义，取数按「数据获取路由」段执行）。
- **上游工作副本**：`C:\Users\xdhui\CommonProjects\ai-berkshire\`（fork clone，固定 `kimi-work` 分支；`main` 为上游纯镜像）。

---

## 3. Kimi Work 官方金融插件全景（市场检索已核实）

### 3.1 本机已安装（默认自带）

ifind（同花顺，A/港/美）、yahoo_finance、sec_edgar、tianyancha、imf、world_bank_open_data、igo_open_data（含 FRED）、scholar；交付类：kimi-excel、kimi-word、kimi-pdf、kimi-slides、deep-research。

### 3.2 插件市场中未安装的金融类（按功能分四类）

| 类别 | 插件 | 覆盖 |
|---|---|---|
| 机构投研套件 | xtt-public-markets-investing | 11 顶层技能：公司/财报研究、估值（DCF/可比）、行业、宏观策略、量化回测、组合管理、报告生产 |
| 机构投研套件 | institutional-finance-kit | 10 交付技能：三表/DCF 建模（Excel）、IC PPT、公司深度/首覆（Word）、业绩点评（HTML）、一致预期地图、组合复盘、持仓早报、港股 IPO、授信报告、取数路由 |
| 数据/资讯源 | wind-allskill、sp_data、gildata-aifinmarket（均需用户自有凭证）；dongcai-mx-data（东财妙想，开箱即用）；alphapai-research、comein-agent、xhcj-news-agent（新华财经） | 行情、财务、研报、公告、快讯、智能选股、涨跌归因 |
| 交付/看板 | dynamic-finance-charts、financial-market-terminal | 研报级动态图表（K线/估值带/瀑布图）、基金经理日报看板与推送 |

---

## 4. 重合与互补结论（对照已核实）

### 4.1 逐个技能对照

| ai-berkshire 技能 | 官方侧对应 | 重合度 |
|---|---|---|
| financial-data ★（已裁剪） | ifind / Wind / 聚源 / S&P / 东财 + 取数路由 | 高（官方更强） |
| earnings-review ★（已裁剪） | institutional 业绩点评 + xtt 财报生命周期 + 东财业绩点评 | 高 |
| deep-company-series ★（已裁剪） | institutional 公司深度/首覆（Word） | 高 |
| industry-research ★（已裁剪） | xtt 行业研究 + 东财产业链报告 | 高 |
| portfolio-review ★（已裁剪） | institutional 组合复盘 + xtt 组合管理 | 高 |
| dyp-ask | 官方侧无内置同款（2026-10-10 复核：Kimi Work 未内置 dyp-ask，由本插件提供）；通用对话可部分替代 | 低 |
| investment-research | xtt 公司深研（流程重合，无四大师框架） | 中 |
| management-deep-dive | xtt business-model / competitive-landscape | 中 |
| private-company-research | xtt-ib-pe 尽调 + 天眼查 | 中 |
| industry-funnel / quality-screen | 东财智能选股 + 终端多因子选股 + xtt 筛选 | 中 |
| income-investment | xtt 固收 / ETF 产品研究 | 中 |
| thesis-tracker | xtt 组合 standing watch | 中 |
| news-pulse ★（已裁剪） | 东财涨跌归因/诊股 + 财联社/新华财经快讯 | 中 |
| earnings-team | 同 earnings-review + 公众号发布流程 | 中 |
| investment-team | 无四大师对抗式多 Agent 编排 | 低 |
| investment-checklist | 无（六关 + 镜子测试 + 8 条红线否决是独家） | 低 |
| thesis-drift | 无（论文漂移检测独家） | 低 |
| bottleneck-hunter | 无 | 低 |
| era-alpha | 无 | 低 |
| wechat-article | 无直接对应 | 低 |

### 4.2 总体判断

- **按功能/产出物算，重合率约 50%**（5 高 + 9 中 + 6 低，加权约一半）。重合集中在"交付形态"：业绩点评、深度报告、组合复盘、数据获取——官方插件做得更机构化（Excel 建模、PPT、看板）。
- **2026-10-11 已据此裁剪**：5 个高重合技能 + `news-pulse`（爬虫未验证）+ `financial-data`（规范已被取数路由吸收）共 6 个退出插件交付（见第 2 节）；插件聚焦下一条的差异化核心。
- **按核心价值算，重合率 < 20%**。ai-berkshire 的差异化全部在**决策纪律层**：四大师视角对抗、六关 Checklist、镜子测试、红线一票否决、芒格式逆向检验、投资论文追踪与漂移检测。这一层官方插件完全没有。
- **互补关系**：官方插件提供"数据 + 机构级交付物 + 可视化看板"，ai-berkshire 提供"方法论 + 决策纪律"。两者是上下叠层关系，不是替代关系——理想的组合是 ai-berkshire 做判断层、官方插件做数据与交付层。

---

## 5. 对移植会话的具体建议（调整空间所在）

按优先级排序：

1. ~~**数据层升级（收益最大）**~~ **已完成（2026-10-10）**：19 个涉及取数的技能（dyp-ask / wechat-article 除外）已在 adapter note 注入「数据获取路由」段：取数优先路由到本机已装的 **ifind 等官方数据插件**，通用搜索作第二来源；保留"关键数据双源交叉验证、误差 >1% 告警"纪律。由 `build_kimi_work_skills.py` 的 `DATA_ROUTED_EXCLUDE` 控制注入范围。
2. **多 Agent 编排复核**：~~确认目标环境是否支持并行子 Agent~~ 已确认支持——验证记录（`docs/verification.md` §3）实测 Kimi Work Agent 集群并行启动 2 个子任务成功。adapter note 现行为"支持并行则并行、否则串行降级"，与实测一致，无需改动。
3. **触发冲突预案**：高重合技能已于 2026-10-11 裁剪退出插件（见第 2 节），触发竞争面已收敛；若用户后续安装 institutional-finance-kit 或 xtt 套件，剩余中重合技能（investment-research / management-deep-dive / industry-funnel / quality-screen / income-investment / thesis-tracker / earnings-team）仍可能与官方技能产生触发竞争，必要时调整 description 的触发边界。
4. ~~**打包形态（中期）**~~ **已完成（2026-10-10，2026-10-11 裁剪后收敛为 15 技能）**：21 个 SKILL.md + tools/ 已打成单插件 `ai-berkshire` 并登记进个人市场（保留现有适配说明与中文 description），链路为 `build_kimi_work_skills.py`（同时产出散装 dist 与插件产物）→ `release_plugin.py`（校验 + 升版本 + 官方 CLI 登记）→ 用户「个人」页签安装/更新；同步上游仍是上游 Sync fork 后 `git pull` 重跑该链路。注意：登记必须显式传 `--share-dir` 指向 `daimon-share`（官方脚本在非 macOS 下回退 `~/.kimi` 是错的），`release_plugin.py` 已内置。
5. ~~**不要重复移植 dyp-ask**~~（已更正）：dyp-ask 并非 Kimi Work 内置，而是由移植脚本与其余 20 个一并安装（见第 2 节复核结论）；安装脚本幂等覆盖同名目录，无冲突风险，可随其他技能一并更新。
6. **保持质量纪律**：任何重写都必须保留原文的"不编数、低置信度标注、日期基线、留白原则"条款，这些是项目灵魂，且与 Kimi Work 的证据规范一致。
7. **输出路径**：报告统一写 `C:/Users/xdhui/reports/`（已建则复用），不要散落到 home 根目录或会话工作区。

## 6. 验证清单（测试阶段建议）

- [ ] 用 1 家熟悉的公司实跑 investment-checklist，核对六关评分、镜子测试、financial_rigor.py 验算是否端到端可用。
- [ ] 用 1 次财报实跑 earnings-review，检查数据时效与来源标注。（注：earnings-review 已于 2026-10-11 裁剪出插件；如需财报精读交付可改用 earnings-team 或官方机构套件。）
- [ ] 断网/联网降级场景：确认适配说明中"未能联网须醒目标注"的条款被遵守。
- [ ] 安装 dynamic-finance-charts 后，验证已装技能调用图表能力无冲突。
- [ ] 上游 git pull 后重新生成技能，确认适配说明不被覆盖丢失。
