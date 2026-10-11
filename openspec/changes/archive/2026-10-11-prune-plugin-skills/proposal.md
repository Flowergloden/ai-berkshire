# Proposal

## Why

移植进 Kimi Work 的 21 个 ai-berkshire 技能中，6 个与官方插件生态高度重合或维护负担过重：`news-pulse` 依赖从未验证通过的 playwright 雪球爬虫；`financial-data` 的取数规范角色已被注入各技能的「数据获取路由」adapter note 实质吸收；`earnings-review`、`deep-company-series`、`industry-research`、`portfolio-review` 与官方机构投研套件在交付形态上高重合。裁剪后插件聚焦 ai-berkshire 的差异化核心——决策纪律层（四大师对抗、六关 Checklist、镜子测试、论文追踪/漂移检测），减少触发面噪声与跟随上游的维护面。同时补齐两份欠账：面向本机用户的安装/维护 README，以及简报中已过时的路径与相互矛盾的结论。

## What Changes

- 构建脚本 `kimi-work/scripts/build_kimi_work_skills.py` 新增 `PRUNED_SKILLS` 排除集（6 个技能）：产物生成（散装 dist + 插件 skills/）跳过被裁技能；规则命中断言**仍扫描全部上游 `skills/*.md`**（断言是上游健康哨兵，与生成范围解耦），精确计数期望不变。
- 交叉引用改写规则（`_rule_xref_backtick` / `_rule_xref_plain`）替换文案改为指向各技能 adapter note 的「数据获取路由」段，消除对被裁技能 `financial-data` 的悬空引用。
- 插件 manifest `kimi.plugin.json`（经 plugin-builder `update_plugin.py`）删除 6 条 `skillOverrides`、技能计数文案 21→15；`locales/en-US.json` 同步。
- 重跑构建并提交插件产物；执行 `uninstall_loose_skills.py` 清理 21 个散装残留技能（插件已验证可热更触发，回滚窗口关闭）；`release_plugin.py` 升版重登记。
- 新增 `kimi-work/README.md`：本机备忘录性质的安装/更新/触发说明（受众为本机用户，保留硬编码路径事实）。
- 修正 `kimi-work/docs/porting-brief-ai-berkshire-vs-kimi-plugins.md`：fork 迁移后的过时路径、§4.1 dyp-ask 行与 §2/§5 更正的矛盾；`kimi-work/docs/verification.md` 追加本次裁剪与散装清理记录。
- **BREAKING**（对插件用户）：更新插件后 6 个被裁技能从 Kimi Work 消失，相关触发词不再命中。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `fork-integration`：构建脚本行为契约变化——新增技能裁剪机制（`PRUNED_SKILLS` 排除集约束生成范围），明确规则命中断言的扫描范围与生成范围解耦（断言始终覆盖全部上游源文件），并要求裁剪后 manifest/locales 与生成产物同步收敛。

## Impact

- **代码**：`kimi-work/scripts/build_kimi_work_skills.py`（PRUNED_SKILLS、xref 规则文案、统计输出）。
- **插件产物**：`kimi-work/plugin/personal/ai-berkshire/`（skills 21→15、`kimi.plugin.json`、`locales/en-US.json`），重新登记后用户在「个人」页签点更新生效。
- **本机环境**：`%APPDATA%\kimi-desktop\daimon-share\daimon\skills\` 下 21 个散装技能与 `kimi-agent\official-skill-origins.json` 登记被清理。
- **文档**：新增 `kimi-work/README.md`；修正 `porting-brief`、`adaptation-matrix.md`（分类表标注被裁技能）、`verification.md`。
- **CI**：`.github/workflows/kimi-work.yml` 无需改动——裁剪集在构建脚本内，断言扫描范围不变，CI 行为一致。
- **上游兼容**：不触碰仓库根 `skills/`（上游镜像只读）；被裁技能仍随上游 sync 进入仓库，只是不参与产物生成。
