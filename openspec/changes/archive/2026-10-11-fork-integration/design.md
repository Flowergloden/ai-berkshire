# Design

## Context

当前工作区是"外层非 git 目录 + `ai-berkshire/` 嵌套只读克隆"的结构，适配逻辑全部在 `scripts/build_kimi_work_skills.py` 的转换规则里（`REPO = HERE / "ai-berkshire"`，散装产物内嵌 `TOOLS_ABS` 本机绝对路径，`REPORTS_DIR = C:/Users/xdhui/reports` 写死并进入插件产物）。Kimi Work 个人市场的安装机制已确认：登记只接受本地目录（`kimi-daimon kimi-plugin register-personal <dir>`），无 zip 分发形态，因此 fork 仓库本身就是分发单位，生成产物须入库。

## Goals / Non-Goals

**Goals:**

- 移植层全部内容进 fork、受 git 版本管理；上游 sync 永远 fast-forward 零冲突。
- 构建脚本位置无关（任意检出路径、含 CI Linux runner 可跑）。
- 转换规则失效（上游改写原文）时构建大声失败，CI 成为适配完整性的自动哨兵。
- sync 后产物更新走 PR 人工把关；PR diff 即适配审计。

**Non-Goals:**

- 不做产物可移植化（`REPORTS_DIR` 参数化仅留 TODO，本 fork 个人专用）。
- 不做上游 sync 全自动化（不加定时 sync Action；sync 动作由人点 GitHub Sync fork 按钮触发）。
- 不改 21 个技能的适配分类与 adapter note 内容（纯结构迁移）。
- 散装 `dist/` 产物不入库、不在 CI 校验（本机路径产物，回滚手段定位不变）。

## Decisions

### D1: `main` 纯镜像 + `kimi-work` 集成分支，而非 main 上直接叠加

`main` 零自有 commit 保证 GitHub Sync fork 按钮永远可用（fast-forward），且"上游原貌 vs 适配产物"的对比就是两个分支的事。备选方案（移植层直接放 main）被否：Sync fork 按钮会退化成 merge，心智不干净。备选方案（单独的 generated 分支只放产物）被否：分发需要"源 + 产物"同在一个分支，拆两个分支让 clone 登记路径变复杂且无收益。

### D2: `kimi-work` 用 merge 更新，不用 rebase

`kimi-work` 是发布分支（本地 clone 固定停在它上面、登记 sourcePath 盯着它），rebase 改写历史会破坏本地 pull。merge commit 在此是特性：每个 merge 标记一次上游 sync 的落点。路径不相交（移植层全在 `kimi-work/` 与独立命名的 workflow 文件下）保证 merge 永远干净。

### D3: 目录布局——一切收进 `kimi-work/` 子目录

```
fork 仓库根（kimi-work 分支）
├── skills/  tools/  docs/(上游)  .github/(上游)   <- 上游内容，不动
├── kimi-work/
│   ├── scripts/         build / release / install / uninstall
│   ├── docs/            PLAN / adaptation-matrix / verification / porting-brief
│   ├── plugin/personal/ai-berkshire/   <- manifest 手工维护 + 生成物入库
│   ├── dist/            <- .gitignore（本机路径产物）
│   └── AGENTS.md
└── .github/workflows/kimi-work.yml    <- 文件名避开上游可能使用的名字
```

备选（铺仓库根）被否：与上游 `docs/`、未来可能的 `scripts/` 撞名，"哪部分是谁的"不直观，违背"只 add 不动"承诺的可维护性。workflow 文件无法收进子目录（GitHub 只认 `.github/workflows/`），用 `kimi-work.yml` 这种上游不可能取的名字规避。

### D4: 构建脚本路径解析改为"仓库根即源"

`HERE = Path(__file__).resolve().parents[2]`（`kimi-work/scripts/` 上溯两级到仓库根），`REPO = HERE`，输入 `REPO/skills`、`REPO/tools`，输出 `HERE/kimi-work/dist` 与 `HERE/kimi-work/plugin/personal/ai-berkshire`。`TOOLS_ABS` 继续动态推导（满足"任意检出位置可构建"）；`REPORTS_DIR` 保持写死并加 TODO 注释（个人专用定位，见 proposal）。

### D5: 转换断言实现为每条规则的命中计数

`transform_body` 的每条改写规则登记为 `(规则, 期望命中)`，期望分两种语义：`*`（至少一次，上游可能多处出现，如 `reports/` 路径）或精确整数（只应出现一次，如 `skills/financial-data.md` 交叉引用）。构建时对每个源文件或全部源文件聚合计数，不符即 `SystemExit` 并列出规则描述与实际命中数。`--check` 路径同样先跑断言再比对产物。断言失败 = CI 红 = 不开 PR，语义闭环。

### D6: CI 工作流 `kimi-work.yml` 的行为

触发：`on: push: branches: [main]` + `workflow_dispatch`。步骤：checkout `kimi-work` → merge `origin/main`（应永远干净，冲突即失败并告警）→ 跑构建（含断言）→ `git status --porcelain` 判断产物是否变化 → 有变化则推送 `bot/kimi-work-sync-<run_id>` 分支并用 `gh pr create` 开向 `kimi-work` 的 PR（已存在未合并的同类 PR 时 force-push 更新之而非堆叠）。构建失败：workflow 红，不开 PR。权限：GITHUB_TOKEN 默认 `contents: write` + `pull-requests: write`。

备选（CI 直接推到 `kimi-work` 不开 PR）被否：违背人工把关定位；产物入库的 diff 审查是适配审计的核心价值。

### D7: 迁移与登记源切换

本地新 clone fork 固定 checkout `kimi-work` 分支作为唯一工作副本；当前外层目录的文件迁移进新 clone 的 `kimi-work/` 后，用 `release_plugin.py` 重登记（sourcePath 指向新位置），Kimi Work 个人页签验证热更新。旧外层目录在验证通过后归档删除。OpenSpec 的 `openspec/` 目录随移植层一并迁入 `kimi-work/`。

### D8: fork 默认分支设为 `kimi-work`（实施期发现，对 D1/D6 的必要补强）

GitHub 只从**默认分支**发现 workflows（`push`/`workflow_dispatch` 触发均要求 workflow 文件存在于默认分支），而 D1 要求 `main` 纯镜像零自有 commit——workflow 放 `main` 会立刻破坏 fast-forward sync。因此把 fork 的默认分支改为 `kimi-work`：`main` 的纯镜像性与 Sync fork 行为不受影响（sync 的是分支内容而非默认分支设置），同时获得两个顺带的收益：PR 默认 base 即 `kimi-work`；clone 默认检出 `kimi-work`，与"本地固定 kimi-work 分支"的纪律一致。代价：仓库首页默认展示 `kimi-work` 而非上游 README——可接受。

## Risks / Trade-offs

- [本地 clone 切分支导致登记源被偷偷换掉] → AGENTS.md 写明纪律；或单独一个 clone 专做登记源（tasks 中作为可选步骤）。
- [merge `main` 理论上冲突（上游新增 `kimi-work/` 同名路径或同名 workflow）] → 概率极低；CI merge 步骤冲突即红并告警，人工处理。
- [断言的期望命中数需人工校准，上游合理改动会增加维护次数] → 这正是设计意图（显式 > 静默）；断言失败信息给出规则描述便于快速定位更新。
- [CI 生成的产物含 `REPORTS_DIR` 本机路径，与用户本地构建一致只是因为两者用同一写死值] → 个人专用定位下可接受；TODO 标记可移植化欠账。
- [fork 的 `kimi-work` 分支公开可见，含个人路径信息] → 仅路径（`C:/Users/xdhui/reports`），无敏感信息；可接受。

## Migration Plan

1. fork 配置 remote（origin=Flowergloden fork，upstream=xbtlin），推 `main` 纯镜像。
2. 从 `main` 切 `kimi-work` 分支，迁移当前项目文件进 `kimi-work/` 子目录，改脚本路径解析（D4）与断言（D5）。
3. 本地跑构建 + `--check`，确认产物与现网一致（除路径变化外 diff 应为空或仅路径差异）。
4. 提交推送，写 workflow（D6），手动 dispatch 冒烟验证。
5. 本地重登记插件，Kimi Work 验证热更新；更新 AGENTS.md 与 docs/verification.md。
6. 验证通过后归档旧外层工作目录。

回滚：fork 分支可随时删除重建；旧外层目录在验证通过前保持原样，旧登记条目不动。
