# Spec Delta

## ADDED Requirements

### Requirement: 技能裁剪排除集

构建脚本 SHALL 维护一个显式的技能裁剪排除集（如 `PRUNED_SKILLS`），列出不参与 Kimi Work 产物生成的上游技能名。生成散装 dist 与插件 skills/ 产物时 SHALL 跳过排除集中的技能；被裁技能的上游源文件 SHALL 保留在仓库根 `skills/` 中不动（上游镜像只读）。排除集变化后重跑构建，插件 skills/ 目录的全量重建 SHALL 使被裁技能的产物被移除、无残留。

#### Scenario: 被裁技能不进入产物

- **WHEN** 某技能名被列入裁剪排除集并重跑构建脚本
- **THEN** `kimi-work/dist/` 与 `kimi-work/plugin/personal/ai-berkshire/skills/` 中均不存在该技能的产物目录，且构建正常结束

#### Scenario: 裁剪不触碰上游源

- **WHEN** 技能被裁剪后执行任意次构建与上游 sync
- **THEN** 仓库根 `skills/<被裁技能>.md` 保持上游原文，不被修改或删除

### Requirement: 断言扫描范围与生成范围解耦

规则命中断言 SHALL 始终对仓库根全部 `skills/*.md` 源文件聚合计数，不因裁剪排除集而缩小扫描范围；裁剪技能 SHALL NOT 导致既有规则的期望命中次数需要重校准。裁剪排除集中技能的源文件若引用其他被裁技能（如交叉引用改写规则的目标），改写规则的替换文案 SHALL 不指向任何被裁技能在插件内的产物。

#### Scenario: 裁剪后断言零校准

- **WHEN** 裁剪排除集从空变为非空后运行 `build_kimi_work_skills.py --check`
- **THEN** 断言以原有期望命中次数通过，无「命中数不符」失败

#### Scenario: 被裁技能无悬空引用

- **WHEN** 被保留技能的产物正文中原本存在指向被裁技能的交叉引用
- **THEN** 改写后的产物文本不再引用被裁技能的插件内名称，而是指向仍存在的替代说明（如 adapter note 的数据路由段）

### Requirement: 裁剪后的插件元数据同步与散装清理

裁剪排除集变化后，插件 manifest 的技能清单条目（`skillOverrides`）与技能计数文案 SHALL 同步更新，`locales/` 翻译文件 SHALL 同步；重新登记后用户在个人市场更新即可生效。被裁技能若以散装形式安装在本机，SHALL 被卸载清理，避免与插件并存产生触发竞争。

#### Scenario: manifest 与产物一致

- **WHEN** 裁剪后重跑构建并检查 `kimi.plugin.json`
- **THEN** `skillOverrides` 不含任何被裁技能条目，描述文案中的技能数量与插件 skills/ 目录实际技能数一致

#### Scenario: 散装残留清理

- **WHEN** 在本机执行散装技能清理流程
- **THEN** Kimi Work 技能目录与本机技能登记中不再存在任何 ai-berkshire 散装技能，技能仅由插件提供
