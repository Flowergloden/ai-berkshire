# Design

## Context

动机见 proposal.md。本设计所依据的现状约束：

- 构建脚本 `kimi-work/scripts/build_kimi_work_skills.py` 按 `skills/*.md` glob 全量生成 21 个技能产物；插件 skills/ 与 tools/ 目录为全量托管（先 `rmtree` 再生成，天然收敛无残留）；manifest/locales 为手工维护（脚本明确不碰）。
- 规则命中断言（`check_rule_hits`）对全部 21 个上游源文件聚合计数，含 4 条精确计数期望（3、1、4、2 次）。
- 被裁 6 技能（`news-pulse`、`financial-data`、`earnings-review`、`deep-company-series`、`industry-research`、`portfolio-review`）在**保留技能**正文中被引用两类形式：
  1. `skills/financial-data.md` 形式（bottleneck-hunter、investment-team、investment-research、income-investment）——现有 `_rule_xref_backtick` / `_rule_xref_plain` 两条规则已改写，但替换文案指向"同一插件内的 financial-data 技能"，裁剪后悬空。
  2. 裸技能名提及（industry-funnel→industry-research、era-alpha→industry-research/financial-data、earnings-team→/earnings-review、income-investment→portfolio-review/earnings-review/news-pulse/financial-data）——现有规则不覆盖。
- 插件形态已于 2026-10-11 实测通过（免重启热更 + 技能触发，verification.md §7）；21 个散装技能仍残留在 `daimon-share/daimon/skills/` 且 `official-skill-origins.json` 登记为 custom，与插件并存。

## Goals / Non-Goals

**Goals:**

- 插件产物从 21 技能收敛到 15 技能，散装与插件形态一致收敛。
- 断言期望零重校准；保留技能产物无指向被裁技能的误导性引用。
- manifest/locales/文档与产物同步；散装残留清理干净。

**Non-goals:**

- 不裁 tools/ 脚本（12 个全量保留——`xueqiu_scraper.py` 虽仅被裁技能引用，但保留无害且避免 tools 引用核对成本）。
- 不改 CI 工作流、不改发布脚本逻辑、不参数化 `REPORTS_DIR`（既有可移植性欠账，不在本 change 范围）。
- 不删除上游 `skills/` 下任何文件。

## Decisions

### D1：断言扫描范围与生成范围解耦

`check_rule_hits` 继续扫描**全部** `skills/*.md`（含被裁技能源文件），只有产物生成循环（`expected_outputs` / dist 输出）按 `PRUNED_SKILLS` 跳过。

理由：断言是"上游是否改写了原文"的哨兵，被裁技能的上游原文同样需要监护（上游改动被裁技能时维护者仍要知道）；且 4 条精确计数期望一字不动，裁剪操作本身不会触发断言失败。备选方案"断言也只扫保留集"需要重校准全部精确计数，且丧失对被裁技能原文的哨兵——拒绝。

### D2：悬空引用双层处理

- **改写规则层**：`_rule_xref_backtick` / `_rule_xref_plain` 的替换文案从"financial-data 技能（同一插件内）"改为指向各技能 adapter note 已有的「数据获取路由」段（匹配模式与期望计数不变，仅替换串变化）。
- **adapter note 层**：为保留技能的 adapter note 增加一条统一兜底声明——正文提及的 6 个被裁技能名未包含在本插件中，遇此类引用时忽略其"调用该技能"的含义，取数需求按「数据获取路由」段执行。

理由：为每个裸提及形式新增改写规则需登记并维护大量精确计数，上游任何措辞变化都会引爆断言，脆且贵；统一声明一次覆盖全部形式。备选"保留 financial-data 作为规范桩技能"会保留一个用户可触发但功能已被 adapter note 吸收的空壳，触发面噪声正是裁剪要消除的——拒绝。

### D3：裁剪实现于构建脚本的 `PRUNED_SKILLS` 集合

上游 `skills/` 只读（main 纯镜像纪律），不能删源文件；Kimi 插件机制无 per-skill 禁用开关，manifest 层隐藏不可行。构建期排除是唯一干净挂点，且恢复任一技能 = 从集合删名 + 重跑构建 + 重发布，完全可逆。

### D4：manifest 维持手工维护，用任务与验证兜底

`kimi.plugin.json` 与 locales 历来由 plugin-builder 官方脚手架维护（`update_plugin.py`），构建脚本不碰。裁剪后手工删 6 条 `skillOverrides`、改技能计数文案（21→15）与 locales 同步，由 tasks 中的验证步骤（比对 manifest 条目与插件 skills/ 目录实际集合）兜底防漏。把 manifest 纳入脚本托管会扩大本 change 范围，留作未来改进。

### D5：散装清理范围 = 全部 21 个，不只被裁 6 个

插件形态已实测通过，散装作为回滚手段的窗口已关闭；只清 6 个会留下 15 个与插件同名并存的散装技能，触发竞争依旧。一次性跑 `uninstall_loose_skills.py` 全清。

## Risks / Trade-offs

- [被裁的高重合技能在本机无官方替代（xtt/institutional 套件未安装），裁后相关交付能力（业绩点评、深度报告、行业研究、组合复盘）暂时失去专属技能] → 用户已知情接受（聚焦差异化决策）；通用对话 + 数据插件仍可完成同类工作；恢复路径见 D3。
- [`income-investment` 等技能正文的关系表大量提及被裁技能，阅读体验略损] → D2 adapter note 兜底声明覆盖；不重写上游正文。
- [上游未来删除某被裁技能源文件 → glob 计数变化 → 断言失败] → 这正是期望的哨兵行为，届时人工核对并调整排除集与期望。
- [manifest 手工同步可能漏改某条目] → tasks 含 manifest 条目与产物目录的集合比对验证步骤；`release_plugin.py` 的 validate 也会拦截结构错误。

## Migration Plan

1. 改构建脚本（PRUNED_SKILLS + 规则文案 + adapter note 兜底）→ 本地构建 + `--check` 通过。
2. 手工同步 manifest 与 locales → 重跑构建提交插件产物。
3. 本机跑 `uninstall_loose_skills.py` 清理 21 个散装 → 确认 `daimon-share/daimon/skills/` 与 origins 登记无 ai-berkshire 残留。
4. `release_plugin.py` 升版重登记 → 用户在 Kimi Work「个人」页签点更新（免重启）→ 抽查：保留技能（如 investment-checklist）正常触发；被裁技能（如 earnings-review）不再出现在触发列表。
5. 文档收尾：`kimi-work/README.md` 新建；简报路径与 dyp-ask 行修正；adaptation-matrix 标注被裁；verification.md 追加记录。

回滚：从 `PRUNED_SKILLS` 移除技能名 → 重跑构建 → 重发布，插件更新即恢复；散装清理如需回滚，重跑 `install_skills.py`。
