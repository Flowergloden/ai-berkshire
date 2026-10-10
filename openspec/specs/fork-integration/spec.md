# fork-integration Specification

## Purpose

定义 ai-berkshire fork 仓库承载 Kimi Work 移植层的行为契约：分支模型、目录布局、构建脚本的路径解析与转换断言、以及上游 sync 触发的 CI 产物再生成与人工把关流程。

## Requirements

### Requirement: 分支模型与上游同步

fork 仓库 SHALL 维持两个长期分支：`main` 为上游（xbtlin/ai-berkshire）的纯镜像，不携带任何自有 commit；`kimi-work` 分支承载全部移植内容，由 `main` merge 而来。上游同步 SHALL 通过 fast-forward 更新 `main` 完成，不向 `main` 引入合并或改写。

#### Scenario: 上游 sync 无冲突

- **WHEN** 上游发布新 commit，维护者在 GitHub 上执行 Sync fork（或手动 `git fetch upstream && git merge --ff-only`）
- **THEN** `main` 以 fast-forward 方式前进，不产生合并冲突

#### Scenario: 移植层路径与上游不相交

- **WHEN** `kimi-work` 分支 merge 最新 `main`
- **THEN** 合并不产生冲突（移植层全部位于上游不使用的路径下，包括 `kimi-work/` 目录与命名避开上游的 workflow 文件）

### Requirement: 移植层目录布局

移植层的全部自有内容 SHALL 收进仓库根的 `kimi-work/` 子目录，包括构建与发布脚本、移植文档、插件源目录与 AGENTS.md。散装技能产物目录（`dist/`）SHALL 被 `.gitignore` 排除，不进入版本库。插件产物（`kimi-work/plugin/` 下的 skills/ 与 tools/）SHALL 提交入库，使 clone `kimi-work` 分支即可登记安装，无需先运行构建。

#### Scenario: clone 即可登记

- **WHEN** 用户在新机器上 clone fork 并切到 `kimi-work` 分支
- **THEN** `kimi-work/plugin/personal/ai-berkshire/` 下的插件产物完整存在，可直接用官方 CLI 登记进个人市场，无需运行任何构建步骤

#### Scenario: 散装产物不入库

- **WHEN** 在任意机器上运行构建脚本
- **THEN** 生成的 `kimi-work/dist/` 不出现在 `git status` 的未跟踪列表中

### Requirement: 构建脚本路径解析

构建脚本 SHALL 以脚本文件位置推导仓库根，并将仓库根的 `skills/` 与 `tools/` 作为输入源，输出写入仓库根的 `kimi-work/dist/` 与 `kimi-work/plugin/personal/ai-berkshire/`。脚本 MUST NOT 依赖仓库的检出位置（绝对路径须动态推导，仅报告输出目录等用户级路径允许固定值）。

#### Scenario: 任意检出位置可构建

- **WHEN** fork 被 clone 到任意目录（含非 `C:\Users\xdhui` 的路径，以及 CI 的 Linux runner），运行构建脚本
- **THEN** 构建成功，产物中 tools 引用路径与实际检出位置一致（散装）或使用 `<plugin-root>` 占位（插件）

### Requirement: 转换规则命中断言

构建脚本中的每条机械改写规则 SHALL 声明其期望命中次数（至少一次或精确次数）。规则实际命中次数与期望不符时，构建 MUST 以非零退出码失败并指明失效规则，MUST NOT 静默跳过该规则。

#### Scenario: 上游改写触发告警

- **WHEN** 上游修改了某条改写规则所匹配的原文，导致该规则命中次数为零
- **THEN** 构建失败并在输出中列出失效规则，不产生产物更新

#### Scenario: `--check` 与断言联动

- **WHEN** 在断言失败的情形下运行 `build_kimi_work_skills.py --check`
- **THEN** `--check` 同样以非零退出码失败，而不是仅报告产物过期

### Requirement: sync 触发的 CI 产物再生成

仓库 SHALL 包含一个 GitHub Actions 工作流，在 `main` 收到 push 或手动 dispatch 时触发。工作流 SHALL：merge `main` 到 `kimi-work`、运行构建；产物有变化时提交到临时分支并向 `kimi-work` 发起 PR；构建失败（含断言失败）时 MUST 使工作流运行标红且 MUST NOT 创建 PR。

#### Scenario: 上游变更产生产物 PR

- **WHEN** 上游变更影响了生成产物，`main` 被 sync 后工作流运行成功
- **THEN** 存在一个指向 `kimi-work` 的 PR，其 diff 精确反映上游变更导致的产物变化

#### Scenario: 构建失败不开 PR

- **WHEN** 工作流中构建步骤失败（例如转换断言命中）
- **THEN** 工作流运行标记为失败，不创建任何 PR，失败原因可在日志中定位到具体规则

#### Scenario: 无变化不开 PR

- **WHEN** `main` 的 push 不影响任何生成产物
- **THEN** 工作流成功结束且不创建 PR

### Requirement: 本地登记源纪律

本地用于 Kimi Work 插件登记的 clone SHALL 固定在 `kimi-work` 分支，登记 sourcePath 指向该 clone 内的插件源目录。迁移完成后 SHALL 重新登记并在 Kimi Work 验证免重启更新链路，验证结果按既有格式记录到验证文档。

#### Scenario: 登记路径与新结构一致

- **WHEN** 迁移完成后执行发布脚本登记插件
- **THEN** 注册表中的 sourcePath 指向本地 clone 的 `kimi-work/plugin/personal/ai-berkshire/`，且 Kimi Work 个人页签可见并可热更新
