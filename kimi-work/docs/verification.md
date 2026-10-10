# 端到端验证记录 — ai-berkshire 接入 Kimi Work

验证日期：2026-10-10
验证环境：Windows，Kimi Work（Kimi.exe，K2.8 Preview），Python 3.13.15（命令名 `python`）

## 0. 计划与实际路径的差异（按本项目约束调整）

| 原计划 | 实际 | 原因 |
|---|---|---|
| 仓库克隆到 `C:\Users\xdhui\ai-berkshire\` | 已存在于 `C:\Users\xdhui\CommonProjects\ai-berkshire-kimi-work-integration\ai-berkshire\` | 本项目已克隆，不重复克隆、不污染用户根目录 |
| 工作文件放 `C:\Users\xdhui\CommonProjects\ai-berkshire-kimi-work-integration\` | 放 `C:\Users\xdhui\CommonProjects\ai-berkshire-kimi-work-integration\` | 计划文件本身即在本项目内 |
| tools 引用 `C:/Users/xdhui/ai-berkshire/tools/...` | `C:/Users/xdhui/CommonProjects/ai-berkshire-kimi-work-integration/ai-berkshire/tools/...` | 跟随实际克隆路径 |
| `python3` | `python`（`python3` 在本机不可用） | 阶段 0 实测 |

## 1. 触发面检查 — 通过

- 技能面板（插件 → 技能 → 已添加）：21/21 全部可见，name/description 正确。
- 输入框 `/` 触发列表：21/21 全部出现，可按名称过滤选中。
- 注意：批量安装需**完全退出并重启 Kimi Work**（杀掉全部 Kimi.exe 进程）后生效；仅关闭窗口不重扫技能目录。

## 2. 安装机制（探路结论）

- GUI「技能 → 自定义技能 → 上传技能 → 选择技能文件夹」上传 1 个技能后实测：
  - 技能文件夹落盘到 `%APPDATA%\kimi-desktop\daimon-share\daimon\skills\<name>\`（与内置技能同目录，文件原样拷贝）
  - 在 `%APPDATA%\kimi-desktop\kimi-agent\official-skill-origins.json` 登记 `{"<name>": {"kind": "custom"}}`
- 据此实现脚本化批量安装（`install_skills.py`，幂等），21 个全部生效。

## 3. 分类抽样真实执行

| 类别 | 测试 | 结果 |
|---|---|---|
| A 类·纯方法论 | `/dyp-ask 拼多多的护城河在哪里？` | ✅ 通过。技能被触发，以段永平视角口吻作答（用户信任与心智 / 规模与网络效应 / 团队与文化三点），方法论文本生效 |
| B 类·tools 脚本 | `/investment-checklist` + 指示执行 `python C:/Users/xdhui/CommonProjects/ai-berkshire-kimi-work-integration/ai-berkshire/tools/financial_rigor.py verify-market-cap --price 1700 --shares 1.256e9 --reported 2.135e12 --currency CNY` | ✅ 通过。Kimi Work 终端真实执行该命令，输出「市值验算…偏差 0.01%，验证通过」，绝对路径改写生效 |
| C 类·多 Agent 编排 | `/investment-team` + 最小规模编排演示（2 个并行子任务概述美团护城河/风险，主 Agent 汇总写报告） | ✅ 通过。Agent 集群并行启动 2 个助手（护城河、风险），各自独立完成，主 Agent 汇总，报告落盘到 `C:\Users\xdhui\reports\美团投资研究报告_验证.md`（3416 字节，内容与编排记录完整） |

## 4. 已知限制（如实标注）

- 未做 21 个技能的全量逐一执行（仅触发面全检 + A/B/C 各抽 1 个真实执行）。
- `news-pulse` 引用的 `tools/xueqiu_scraper.py` 依赖 playwright（第三方库，未安装），且依赖雪球网页抓取，未验证；其余 3 个主 tools（financial_rigor / terminal_value / report_audit）仅用标准库，已冒烟。
- 正文保留的 `$ARGUMENTS`、`Task` 等 Claude Code 字样由 adapter note 统一覆盖说明，未做正文级删除（保持与上游可 diff）；实测 Kimi Work 能正确理解执行。
- Kimi Work Beta 高频迭代，技能机制若变化，重跑 `build_kimi_work_skills.py` + `install_skills.py` 即可。

## 5. 数据层升级与文档复核（2026-10-10 追加）

- **brief 复核**：`docs/porting-brief-...md` 中「20 个技能」「dyp-ask 为 Kimi Work 内置」两条与事实不符，已更正——实际 21 个技能，`official-skill-origins.json` 恰好 21 条登记且 dyp-ask 为 `custom`（脚本安装，非内置）。
- **数据层升级已实施**：build 脚本新增 `DATA_ROUTED_EXCLUDE`，为 19 个涉及取数的技能（dyp-ask / wechat-article 除外）的 adapter note 注入「数据获取路由」段——优先 ifind / yahoo_finance / sec_edgar / tianyancha 等本机官方数据插件，通用搜索作第二来源，双源交叉验证纪律不变。
- **验证状态**：`build_kimi_work_skills.py` + `--check` + `install_skills.py` 全部通过（21/21）；抽查 dist/investment-research、dist/financial-data 含路由段，dyp-ask、wechat-article 不含。**Kimi Work 端实际触发取数路由的效果未实测**——需完全重启 Kimi Work 后用人熟悉的标的跑 investment-research / earnings-review 验证。

## 6. 插件化打包验证（2026-10-10 追加）

- **插件构建**：`plugin/personal/ai-berkshire/` = 官方脚手架 `create_plugin.py` 生成的 manifest/locales + 生成脚本产出的 skills ×21（`<plugin-root>/tools/` 占位路径）+ tools ×12 拷贝；`validate_plugin.py` 0 error 0 warning。
- **登记**：`release_plugin.py --no-bump` 走官方 CLI 登记成功，条目 `daimon-share/daimon/plugin-market/personal/ai-berkshire.json` 回读核对 id/version/sourcePath 正确，21 个 skillNames 全在；链接 `kimi-work://plugin?id=ai-berkshire`。
- **踩坑记录**：官方 register 脚本在非 macOS 下 share 目录回退 `~/.kimi`（错误位置，Kimi Work 看不到），必须显式传 `--share-dir` 指向 `%APPDATA%\kimi-desktop\daimon-share`；首次误登记的 `~/.kimi/daimon/plugin-market/` 已清理。`release_plugin.py` 已内置正确路径。
- **已知限制（如实标注）**：
  - **Kimi Work 端安装与触发未实测**——需用户在插件页「个人」页签点 ＋ 安装后，新开会话验证技能触发与 `<plugin-root>` 路径下 tools 脚本真实可跑（建议用 investment-checklist / quality-screen 抽验）。
  - 散装技能暂未清理，待插件验证通过后跑 `uninstall_loose_skills.py`；清理前散装与插件同名技能并存，可能存在触发竞争。
  - 插件未设图标（客户端默认兜底）；xueqiu_scraper.py 的 playwright 依赖限制同第 4 节。

## 7. fork 迁移端到端验证（2026-10-11 追加）

迁移背景：移植层从「外层非 git 目录 + 嵌套只读克隆」迁入 fork（`Flowergloden/ai-berkshire`）`kimi-work` 分支的 `kimi-work/` 子目录，`main` 保持上游纯镜像。详见 `../../openspec/changes/fork-integration/`（openspec 目录已于 2026-10-11 上移至仓库根）。

| 验证项 | 方法 | 结果 |
|---|---|---|
| main 纯镜像 | `git diff main upstream/main` 为空；GitHub compare `xbtlin:main...Flowergloden:main` = identical（ahead 0 / behind 0） | ✅ 通过（Sync fork 可走 fast-forward） |
| 移植层迁移完整性 | `diff -r` 比对 8 类文件（scripts/docs×5/plugin/openspec/AGENTS.md），文件清单与内容逐字节一致 | ✅ 通过 |
| 散装产物排除 | 仓库根 `.gitignore` 加 `kimi-work/dist/`；构建后 `git status` 0 条 dist | ✅ 通过 |
| 新结构构建 | `python kimi-work/scripts/build_kimi_work_skills.py` 成功；插件 skills/tools 与旧工作区逐字节一致，散装 21 包中 18 包 diff 仅含 tools 绝对路径差异（检出路径变化所致，预期内）、3 包（无 tools 引用的 A 类）逐字节一致 | ✅ 通过 |
| 规则命中断言 | 当前上游版本下 `--check` 退出码 0（11 条规则全部命中期望）；人为把「python3 tools/xxx.py」期望改为 999 → 非零退出且输出列出「期望 精确 999 次，实际 50 次」，还原后恢复 0 | ✅ 通过 |
| CI 工作流 | `workflow_dispatch` 两次手动触发（runs 38066183148 / 38066217698）：checkout kimi-work → merge origin/main → 构建（含断言）→ 无产物变化 → 成功结束且**零 PR** | ✅ 通过（「产物有变化开 PR」「构建失败不开 PR」两场景待首次真实上游 sync 时验证） |
| 插件重登记 | `release_plugin.py` 从新 clone 登记成功；注册表 `plugin-market/personal/ai-berkshire.json` 回读 sourcePath = `C:\Users\xdhui\CommonProjects\ai-berkshire\kimi-work\plugin\personal\ai-berkshire` | ✅ 通过 |
| 免重启热更 + 技能触发 | Kimi Work 运行中在插件页「个人」页签安装（未重启任何进程），按钮变「使用」；新任务发送「用段永平的视角回答…」，transcript（`agents/main/memory/transcripts/days/2026-10-11/conv-aefee1a5….jsonl`）记录 `Skill "dyp-ask" loaded inline.`，回答符合技能口吻 | ✅ 通过 |

### 实施期设计变更（已补记 design.md D8）

GitHub 只从**默认分支**发现 workflows，与「main 纯镜像」冲突。解法：fork 默认分支改为 `kimi-work`（main 纯镜像性不受影响；PR 默认 base 与 clone 默认检出顺带一致化）。

### 已知限制（如实标注）

- CI「产物有变化 → 开 PR」与「构建失败 → 红且不开 PR」两条路径未实测（当前无变化场景无法触发；待首次上游 sync 观察）。
- 本次未重跑 B 类 tools 脚本抽验（`<plugin-root>` 占位解析在 2026-10-10 第 6 节前已验证过机制，本次迁移插件产物逐字节未变，仅安装来源路径变化）；如需可再跑 investment-checklist 抽验。
- 旧外层目录 `ai-berkshire-kimi-work-integration\` 尚未归档删除（待确认无遗漏后执行，见 fork-integration 任务 6.1）。
