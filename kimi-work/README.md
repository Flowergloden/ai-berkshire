# ai-berkshire → Kimi Work 插件（本机备忘录）

把开源项目 [ai-berkshire](https://github.com/xbtlin/ai-berkshire)（MIT，巴菲特/芒格/段永平/李录四大师价值投资方法论）的 21 个 Claude Code / Codex 投研 Skill 移植为 **Kimi Work（桌面 GUI Agent）** 的个人市场插件，并持续跟随上游更新。

- 上游源：仓库根 `skills/*.md` + `tools/*.py`（`main` 分支为上游纯镜像，只通过 Sync fork 更新，勿直接改）。
- 插件产物：`kimi-work/plugin/personal/ai-berkshire/`（skills ×15 + tools ×12 + manifest/locales，生成脚本全量托管，勿手工编辑）。
- 当前技能数：**15 个**（2026-10-11 起从 21 个裁剪 6 个，见下文「裁剪记录」）。

## 技能清单（15 个）

| 类别 | 技能 |
|---|---|
| 深度研究 | investment-research、investment-team、management-deep-dive、private-company-research |
| 财报分析 | earnings-team（四大师视角 + 公众号发布稿） |
| 行业筛选 | industry-funnel、quality-screen、bottleneck-hunter、era-alpha、investment-checklist |
| 持仓管理 | income-investment、thesis-tracker、thesis-drift |
| 思维工具 | dyp-ask（段永平问答）、wechat-article（公众号深度文章） |

每个 SKILL.md 头部带自动生成的「Kimi Work 适配说明」（adapter note）：`$ARGUMENTS`/联网/日期基线/报告路径/数据获取路由（优先官方数据插件）/多 Agent 编排降级等。正文中提及的被裁技能（见下）按 adapter note 的兜底声明处理。

### 裁剪记录（2026-10-11）

被裁 6 个（仍保留在上游 `skills/`，不参与产物生成，恢复 = 从构建脚本的 `PRUNED_SKILLS` 集合删名 + 重跑构建 + 重发布）：

- `news-pulse` — playwright 雪球爬虫从未验证通过；
- `financial-data` — 取数规范已被各技能 adapter note 的「数据获取路由」段实质吸收；
- `earnings-review`、`deep-company-series`、`industry-research`、`portfolio-review` — 与官方机构投研套件交付形态高重合。

## 安装 / 更新链路

插件已登记进 Kimi Work 个人市场（`kimi-work://plugin?id=ai-berkshire`）。

- **用户侧更新**：Kimi Work → 插件页 →「个人」页签 → 点「更新」（**免重启**，daemon 热更）。
- **发布侧**（本机维护者，仓库根执行）：
  1. 上游 Sync fork 后 `git pull`（停在 `kimi-work` 分支）；
  2. `python kimi-work/scripts/build_kimi_work_skills.py` 重新生成产物（幂等；`--check` 校验断言与产物新鲜度）；
  3. `python kimi-work/scripts/release_plugin.py` 校验 + 升 `+local` 版本 + 重登记；
  4. 用户回 Kimi Work「个人」页签点「更新」。

散装形态（`install_skills.py` / `uninstall_loose_skills.py`）已于 2026-10-11 全部清理，仅作回滚手段保留脚本。

## 前置依赖

- Windows；Python 命令名为 `python`（无 `python3`）；tools 脚本仅依赖标准库。
- 推荐同时安装官方数据插件以发挥「数据获取路由」：ifind（同花顺）、yahoo_finance、sec_edgar、tianyancha、imf、world_bank_open_data、igo_open_data、scholar。
- 登记/发布依赖官方 CLI：`%APPDATA%\kimi-desktop\daimon-bundle\bin\kimi-daimon.cmd`（`release_plugin.py` 已内置正确路径）。

## 报告输出目录

报告统一输出到 `C:/Users/xdhui/reports/`（skills 内已改写为绝对路径，目录不存在时先创建）。

## 免责声明

本项目仅供学习研究，不构成投资建议。
