# Tasks

## 1. 构建脚本：裁剪机制

- [x] 1.1 在 `kimi-work/scripts/build_kimi_work_skills.py` 新增 `PRUNED_SKILLS = {"news-pulse", "financial-data", "earnings-review", "deep-company-series", "industry-research", "portfolio-review"}`；`expected_outputs` 与产物统计跳过该集合（`check_rule_hits` 保持扫描全部 `skills/*.md` 不变）；验证：`python kimi-work/scripts/build_kimi_work_skills.py` 输出技能数为 15，dist 与插件 skills/ 中无 6 个被裁目录
- [x] 1.2 修改 `_rule_xref_backtick` / `_rule_xref_plain` 的替换文案，指向 adapter note 的「数据获取路由」段（匹配模式与期望计数不变）；验证：生成的保留技能产物（如 investment-research）中不再出现"同一 ai-berkshire 技能包/插件内的 `financial-data` 技能"字样，改为指向数据获取路由
- [x] 1.3 在 `adapter_note` 中为保留技能追加兜底声明：正文提及的 6 个被裁技能未包含在本插件中，遇此类引用忽略其"调用技能"含义、取数按「数据获取路由」段执行；验证：抽查 industry-funnel、earnings-team、income-investment 产物含该声明
- [x] 1.4 跑 `python kimi-work/scripts/build_kimi_work_skills.py --check`；验证：断言全部通过（期望计数零调整），退出码 0

## 2. 插件元数据同步

- [ ] 2.1 用 plugin-builder `update_plugin.py` 更新 `kimi-work/plugin/personal/ai-berkshire/kimi.plugin.json`：删除 6 条被裁技能的 `skillOverrides`，description/longDescription 中"21 个"改"15 个"并调整分类描述；验证：manifest 的 `skillOverrides` 键集合与插件 `skills/` 目录名集合逐一相等
- [ ] 2.2 同步 `locales/en-US.json` 中被裁技能条目与计数文案；验证：locales 中不出现 6 个被裁技能名
- [ ] 2.3 重跑构建后 `git add` 插件产物并提交；验证：`git status` 干净，插件产物（15 技能 + 12 tools + manifest/locales）已入库

## 3. 本机散装清理与发布

- [ ] 3.1 执行 `python kimi-work/scripts/uninstall_loose_skills.py` 清理全部 21 个散装技能；验证：`%APPDATA%\kimi-desktop\daimon-share\daimon\skills\` 下无 21 个 ai-berkshire 技能目录，`kimi-agent\official-skill-origins.json` 无对应登记
- [ ] 3.2 执行 `python kimi-work/scripts/release_plugin.py` 升版重登记；验证：`plugin-market/personal/ai-berkshire.json` 回读的 `skillNames` 恰为 15 个保留技能、版本号已升
- [ ] 3.3 在 Kimi Work「个人」页签点更新（免重启），新开会话抽查：investment-checklist 可触发、earnings-review 等被裁技能不出现在 `/` 触发列表；验证结果追加到 `kimi-work/docs/verification.md`

## 4. 文档收尾

- [ ] 4.1 新建 `kimi-work/README.md`（本机备忘录）：插件简介、15 技能清单、安装/更新链路（个人市场 + release_plugin.py）、前置依赖（Windows、`python`、推荐官方数据插件）、报告输出目录、免责声明；验证：README 所述命令与本机实际路径一致
- [ ] 4.2 修正 `kimi-work/docs/porting-brief-ai-berkshire-vs-kimi-plugins.md`：§2 过时路径改为 fork 仓库现状、§4.1 dyp-ask 行与 §2/§5 更正对齐、技能总数与裁剪事实更新；验证：简报中不再出现 `ai-berkshire-kimi-work-integration` 路径与"dyp-ask 已内置"表述
- [ ] 4.3 在 `kimi-work/docs/adaptation-matrix.md` 标注 6 个被裁技能及理由；验证：矩阵技能计数与本 change 一致
- [ ] 4.4 更新 `AGENTS.md`（如技能数量、裁剪纪律等描述受影响处）；验证：AGENTS.md 与构建脚本行为一致
