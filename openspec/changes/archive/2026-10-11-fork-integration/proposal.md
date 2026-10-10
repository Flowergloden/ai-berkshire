# Proposal

## Why

当前移植层（`scripts/`、`docs/`、`plugin/` 等）不在任何 git 仓库下，版本管理缺失；`ai-berkshire/` 是上游的只读嵌套克隆，适配"补丁"只以构建脚本里的转换规则形式存在。用户已创建 fork（`git@github.com:Flowergloden/ai-berkshire.git`），需要把移植层迁入 fork 做版本管理，让上游 sync 变成零冲突的 fast-forward，并用 GitHub Action 在 sync 时自动重新生成 Kimi Work 产物、以 PR 形式人工把关。

## What Changes

- **仓库结构迁移**：fork 的 `main` 保持纯上游镜像（零自有 commit）；新建 `kimi-work` 分支承载全部移植内容，移植层收进 `kimi-work/` 子目录，与上游路径零交集。
- **构建脚本适配**：`build_kimi_work_skills.py` 的路径假设从"项目根 + 嵌套克隆"（`REPO = HERE / "ai-berkshire"`）改为"fork 仓库根即源"（`REPO = HERE`）；`transform_body` 的每条机械改写规则增加命中断言，上游改写导致规则失效时构建大声报错而非静默 no-op。
- **CI 工作流**：新增 `.github/workflows/kimi-work.yml`，`main` 收到 push（即 sync fork 发生）或手动 dispatch 时触发：merge `main` 到 `kimi-work`、运行构建、产物有变化则提交到临时分支并向 `kimi-work` 开 PR；构建失败则 workflow 标红、**不开 PR**。
- **生成产物入库**：插件产物（`kimi-work/plugin/personal/ai-berkshire/` 的 skills/ 与 tools/）提交进 `kimi-work` 分支，使 clone 该分支即可登记安装；散装 `dist/` 因内嵌本机绝对路径，入 `.gitignore` 不入库。
- **个人专用定位**：`REPORTS_DIR` 等本机路径保持写死，脚本中加 TODO 注释标记可移植性欠账（将来若需分享 fork 再参数化）。
- **BREAKING**：本地工作区结构改变——本地 clone 需固定在 `kimi-work` 分支，插件登记 sourcePath 指向新位置，需重新登记。

## Capabilities

### New Capabilities

- `fork-integration`: fork 仓库的分支模型、移植层目录布局、构建脚本的路径解析与断言行为、sync 触发的 CI 产物再生成与 PR 流程。

### Modified Capabilities

（无——本项目尚无任何已归档 spec。）

## Impact

- **代码**：`scripts/build_kimi_work_skills.py`（路径解析、命中断言）、`scripts/release_plugin.py` / `install_skills.py` / `uninstall_loose_skills.py`（路径引用跟随迁移）、新增 `.github/workflows/kimi-work.yml`。
- **仓库**：fork 新增 `kimi-work` 分支；本地工作区从"外层目录 + 嵌套克隆"变为"fork clone 单仓库"。
- **文档**：`AGENTS.md` 的项目结构与工作规则章节整体改写；`docs/verification.md` 追加迁移验证记录。
- **运行时**：插件登记 sourcePath 变更，需在 Kimi Work 重新登记并验证免重启更新链路。
