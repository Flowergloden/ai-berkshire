# Tasks

## 1. Fork 与分支准备

- [x] 1.1 在本地新 clone `git@github.com:Flowergloden/ai-berkshire.git`（作为迁移后的唯一工作副本），添加 `upstream` remote 指向 `git@github.com:xbtlin/ai-berkshire.git`；验证 `git fetch upstream && git diff main upstream/main` 为空
- [x] 1.2 确认 fork 的 `main` 为纯上游镜像（无自有 commit），从 `main` 创建 `kimi-work` 分支并推送；验证 GitHub 上 Sync fork 按钮对 `main` 可用（fast-forward）

## 2. 移植层迁移

- [x] 2.1 把当前外层项目的 `scripts/`、`docs/`（PLAN.md、EXECUTOR_PROMPT.md、adaptation-matrix.md、verification.md、porting-brief）、`plugin/`、`openspec/`、根 `AGENTS.md` 迁入新 clone 的 `kimi-work/` 子目录；验证 `kimi-work/` 下文件与源目录内容一致
- [x] 2.2 在仓库根写 `.gitignore` 排除 `kimi-work/dist/`；验证构建后 `git status` 不出现 dist 文件
- [x] 2.3 改 `kimi-work/scripts/build_kimi_work_skills.py` 路径解析：`REPO = 仓库根`（脚本位置 parents[2]），输入改 `REPO/skills`、`REPO/tools`，输出改 `kimi-work/dist` 与 `kimi-work/plugin/...`；`REPORTS_DIR` 处加 TODO 注释（可移植性欠账）；验证在新 clone 中 `python kimi-work/scripts/build_kimi_work_skills.py` 成功，产物与旧工作区产物 diff 仅含预期的路径差异
- [x] 2.4 同步修 `release_plugin.py` / `install_skills.py` / `uninstall_loose_skills.py` 中的路径引用；验证 `release_plugin.py --help`（或等价 dry-run）路径解析正确

## 3. 转换规则命中断言

- [x] 3.1 把 `transform_body` 的每条改写规则登记为带期望命中语义（至少一次 / 精确次数）的结构，对全部 21 个源文件聚合计数，不符即非零退出并列出失效规则与实际命中数；验证当前上游版本下全部断言通过（`python kimi-work/scripts/build_kimi_work_skills.py --check` 退出码 0）
- [x] 3.2 人为破坏一条规则的期望（临时改期望数）验证断言确实触发非零退出且信息可定位，随后还原

## 4. CI 工作流

- [x] 4.1 新增 `.github/workflows/kimi-work.yml`：`on: push: branches: [main]` + `workflow_dispatch`；步骤为 checkout `kimi-work` → merge `origin/main` → 跑构建（含断言）→ 产物有变化则推 `bot/kimi-work-sync-<run_id>` 并 `gh pr create` 开向 `kimi-work`（已有未合并同类 PR 时 force-push 更新）；构建失败则 workflow 红且不开 PR；验证 `workflow_dispatch` 手动触发冒烟成功
- [x] 4.2 验证无变化场景：对当前状态再触发一次 workflow，确认成功结束且不产生新 PR

## 5. 登记源切换与端到端验证

- [ ] 5.1 用 `kimi-work/scripts/release_plugin.py` 从新 clone 重登记插件；验证注册表条目 sourcePath 指向新 clone 的 `kimi-work/plugin/personal/ai-berkshire/`
- [ ] 5.2 在 Kimi Work 个人页签点「更新」，验证插件免重启生效、至少一个技能可被触发；按既有格式把结果记入 `kimi-work/docs/verification.md`
- [ ] 5.3 改写 `kimi-work/AGENTS.md` 的项目结构、环境事实与工作规则章节以匹配 fork 模型（clone 固定 `kimi-work` 分支的纪律、sync 流程、CI 把关）；验证文档中不再引用旧的"嵌套克隆"结构
- [ ] 5.4 （可选）单独 clone 一份固定作为登记源，与日常折腾的工作副本隔离；若做，验证登记条目指向登记源 clone

## 6. 收尾

- [ ] 6.1 全部验证通过后归档旧外层工作目录（保留至验证通过前不删）；验证新 clone 独立完整（移走旧目录后构建与登记仍正常）
