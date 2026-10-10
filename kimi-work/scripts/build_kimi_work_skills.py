#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从仓库根 skills/*.md 生成 Kimi Work（桌面 GUI Agent）可用的标准 Agent Skills 包。

本脚本位于 fork 仓库（Flowergloden/ai-berkshire）kimi-work 分支的 kimi-work/scripts/ 下，
以仓库根为上游源（main 分支是纯上游镜像），输出两类产物，幂等可重跑（上游 sync 后重新执行即可）：
- kimi-work/dist/<name>/SKILL.md          —— 散装技能包（tools 用检出路径的绝对路径，install_skills.py 安装）
- kimi-work/plugin/personal/ai-berkshire/ —— Kimi 插件产物：skills/<name>/SKILL.md ×21 + tools/*.py
  （tools 引用用官方 <plugin-root> 占位约定；kimi.plugin.json 由官方脚手架一次性生成，本脚本不碰）
用法（在仓库根执行）：
    python kimi-work/scripts/build_kimi_work_skills.py           # 生成全部
    python kimi-work/scripts/build_kimi_work_skills.py --check   # 先跑规则命中断言，再校验产物是否最新，不写文件
"""

from __future__ import annotations

import re
import shutil
import sys
from collections.abc import Callable
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]  # 仓库根（本文件位于 kimi-work/scripts/ 下）
REPO = HERE  # fork 仓库根即上游源：kimi-work 分支含上游全部内容，skills/ 与 tools/ 在仓库根
CLAUDE_SKILLS = REPO / "skills"
DIST = HERE / "kimi-work" / "dist"
TOOLS_ABS = (REPO / "tools").as_posix()
# TODO(可移植性欠账)：REPORTS_DIR 为本机写死路径（个人专用 fork 定位下可接受，
# 与用户本机构建产物一致）；若将来需把 fork 分享给别人，应参数化（如环境变量）。
REPORTS_DIR = "C:/Users/xdhui/reports"  # 报告统一输出目录（Windows 用户目录下）

# 插件产物：kimi-work/plugin/personal/ai-berkshire/（kimi.plugin.json 由官方脚手架 create_plugin.py
# 一次性生成并入 git；本脚本只生成 skills/ 与 tools/，不碰 manifest/locales/icon）。
# 插件内 SKILL.md 的 tools 引用用官方 <plugin-root> 占位约定（参照 ifind），
# 运行时解析为插件实际安装根目录（SKILL.md 位于 <plugin-root>/skills/<name>/ 下，向上两级）。
PLUGIN_DIR = HERE / "kimi-work" / "plugin" / "personal" / "ai-berkshire"
PLUGIN_TOOLS_PREFIX = "<plugin-root>/tools"

# ---------------------------------------------------------------------------
# 分类映射表
#   A：纯方法论（仅搜索+写作）
#   B：依赖 tools/ 脚本
#   C：多 Agent 编排（含 B 类改动 + 编排段落说明）
# ---------------------------------------------------------------------------
CATEGORY: dict[str, str] = {
    "deep-company-series": "A",
    "dyp-ask": "A",
    "era-alpha": "A",
    "financial-data": "A",
    "income-investment": "A",
    "thesis-drift": "A",       # financial_rigor 仅为可选/非关键路径
    "wechat-article": "C",     # 作者/编辑/读者三 Agent 协作（顺序为主，含并行审阅）
    "earnings-team": "C",      # 四大师并行 + 编辑/读者评审六 Agent
    "bottleneck-hunter": "B",
    "earnings-review": "C",    # Task 工具并行取数 + tools 脚本
    "industry-funnel": "B",
    "news-pulse": "C",         # TeamCreate + 4 并行侦察 Agent + xueqiu_scraper
    "portfolio-review": "B",
    "quality-screen": "B",
    "thesis-tracker": "B",
    "industry-research": "C",
    "investment-checklist": "C",
    "investment-research": "C",
    "investment-team": "C",
    "management-deep-dive": "C",
    "private-company-research": "C",
}

# 涉及取数的技能：adapter note 注入「数据获取路由」段（优先官方数据插件）。
# dyp-ask / wechat-article 为纯问答/写作流程，不注入。
DATA_ROUTED_EXCLUDE = {"dyp-ask", "wechat-article"}

# 每个 skill 的中文 description（决定 Kimi Work 自动触发质量）
DESCRIPTIONS: dict[str, str] = {
    "bottleneck-hunter": "供应链瓶颈猎手：针对 AI、新能源等超级趋势，扫描全球产业链瓶颈环节并挖掘相关上市公司套利机会。当用户要求分析某产业趋势的瓶颈、卡点或受益标的时使用。",
    "deep-company-series": "深度公司系列长文：为一家公司撰写 3-8 篇《看懂XX》系列深度文章，强调事实核查与反复修改。当用户要求为公司写系列科普/深度内容（公众号、视频号）时使用。",
    "dyp-ask": "段永平问答：以段永平的投资哲学与思维方式回答用户关于商业、投资、企业文化的问题。当用户想以段永平视角思考或提问时使用。",
    "earnings-review": "财报精读：基于一手财报原文对单家公司财报做深度解读与数据抽检。当用户要求精读某公司最新财报、分析业绩公告时使用。",
    "earnings-team": "财报精读团队：从段永平、巴菲特、芒格、李录四个视角解读财报，再改写为可发布的公众号文章并经读者评审。当用户需要对重要公司的关键财报做深度解读并产出发布稿时使用。",
    "era-alpha": "时代α捕手：识别当下核心高增长行业中有定价权与壁垒的 α 企业，给出介入与退出纪律。当用户询问当前时代主线、高增长方向的投资机会时使用。",
    "financial-data": "财务数据获取与交叉验证规范：规定美股/港股/A股/台股的权威数据源与两源交叉验证规则。其他投研技能涉及取数时遵循本规范；当用户询问某市场财务数据去哪查时使用。",
    "income-investment": "分红收益投资分析：评估公司分红的可持续性与机会型分红价值。当用户关注股息、分红率、收益型投资标的时使用。",
    "industry-funnel": "行业漏斗筛选：从全市场逐层筛选，最终精选出 3 家价值投资标的。当用户要求在某行业内做系统化选股、筛出最值得投的公司时使用。",
    "industry-research": "行业产业链投资研究：产业链全景扫描加上中下游个股分析，产出行业投资研究报告。当用户要求系统研究某个行业的投资机会时使用。",
    "investment-checklist": "巴菲特买入前 Checklist：对一家或多家公司逐项执行价值投资买入前检查清单。当用户要求在买入前做系统性核查、或多公司对比时使用。",
    "investment-research": "系统化投资研究：以巴菲特、芒格、段永平、李录四大师框架对单家公司做全面投资研究并产出报告。当用户要求深入研究某家上市公司是否值得投资时使用。",
    "investment-team": "投研团队：商业模式、财务估值、行业竞争、风险管理四个角色并行分析一家公司并汇总成投资研究报告。当用户要求对一家公司做团队式、多角度的全面投研时使用。",
    "management-deep-dive": "管理层纵深研究：深度评估公司 CEO 与核心管理层的能力圈、诚信度与资本配置记录。当用户想研究某公司管理层、创始人是否靠谱时使用。",
    "news-pulse": "公司新闻脉搏：股价异动时快速侦察公司事件、监管政策、行业动态与市场情绪，归因异动主因并判断是否触发投资论文重审。当持仓或关注股票大涨大跌、想快速搞清原因时使用。",
    "portfolio-review": "投资组合审视：对整体持仓做健康度检查与优化建议。当用户要求复盘自己的股票组合、评估持仓结构时使用。",
    "private-company-research": "未上市公司深度研究：针对蚂蚁集团、小红书、SpaceX 等未上市公司，多维度并行收集碎片信息并交叉验证估值。当用户要求研究未上市/拟上市公司时使用。",
    "quality-screen": "去劣筛选：用 7 条一流公司指标快速排除不合格标的。当用户给出一批公司名单、想快速淘汰劣质标的时使用。",
    "thesis-drift": "投资论文漂移检测：对比新旧投资论述，区分事实变化与措辞变化，判断投资逻辑是否发生实质性漂移。当用户想检查自己对某公司的投资逻辑是否悄悄改变时使用。",
    "thesis-tracker": "投资论文追踪：买入后按纪律定期检查估值锚点、关键假设与催化剂兑现情况。当用户要求跟踪持仓的投资逻辑、做持有期复查时使用。",
    "wechat-article": "公众号深度文章：按作者-编辑-读者三视角流程，对主题深度研究后产出可直接发布的微信公众号文章。当用户要求写一篇可发布的公众号深度稿时使用。",
}


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 5:].lstrip("\n")


def yaml_quote(value: str) -> str:
    value = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{value}"'


def metadata_for(name: str) -> str:
    desc = DESCRIPTIONS[name]
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {yaml_quote(desc)}\n"
        "---\n\n"
    )


# ---------------------------------------------------------------------------
# 机械改写规则表（顺序即应用顺序，前序规则会消费后序规则的匹配文本，勿随意调整）。
# 每条规则登记期望命中语义：
#   "*"   —— 全部源文件聚合计数至少命中一次（上游多处出现）；
#   整数  —— 全部源文件聚合计数精确等于该值（0 = 当前上游不应再出现该形式，
#           作为"上游重新引入旧写法"的哨兵）。
# 命中断言见 check_rule_hits：上游改写原文导致命中数不符时构建大声失败，不静默跳过。
# ---------------------------------------------------------------------------
RuleApply = Callable[[str, str], tuple[str, int]]  # (body, tools_prefix) -> (new_body, 命中数)


def _rule_tilde_tools(body: str, tp: str) -> tuple[str, int]:
    return re.subn(r"~/ai-berkshire/tools/([a-z_0-9]+\.py)", tp + r"/\1", body)


def _rule_python3_tools(body: str, tp: str) -> tuple[str, int]:
    return re.subn(r"python3 tools/([a-z_0-9]+\.py)", "python " + tp + r"/\1", body)


def _rule_bare_tools(body: str, tp: str) -> tuple[str, int]:
    return re.subn(r"`tools/([a-z_0-9]+\.py)`", "`" + tp + r"/\1`", body)


def _rule_xref_backtick(body: str, tp: str) -> tuple[str, int]:
    # 交叉引用 skills/financial-data.md → 指向同包的 financial-data 技能
    # 先数后换：替换串内嵌 "`financial-data`" 技能名，直接 subn 会重复匹配。
    n = body.count("`skills/financial-data.md`")
    return body.replace(
        "`skills/financial-data.md`",
        "financial-data 技能（同一 ai-berkshire 技能包/插件内的 `financial-data` 技能）中的数据源规范",
    ), n


def _rule_xref_plain(body: str, tp: str) -> tuple[str, int]:
    n = body.count("skills/financial-data.md")
    return body.replace("skills/financial-data.md", "financial-data 技能中的数据源规范"), n


def _rule_reports_backtick(body: str, tp: str) -> tuple[str, int]:
    # 仓库相对路径 reports/... → Windows 用户报告目录（含中文/占位符，故按反引号整体匹配）
    return re.subn(r"`reports/", "`" + REPORTS_DIR + "/", body)


def _rule_report_flag(body: str, tp: str) -> tuple[str, int]:
    n = body.count("--report reports/")
    return body.replace("--report reports/", "--report " + REPORTS_DIR + "/"), n


def _rule_reports_zh(body: str, tp: str) -> tuple[str, int]:
    # 注意：该短语内含 "`reports/"，会被前序 _rule_reports_backtick 先行消费，
    # 在当前顺序下恒为 0；保留此规则作为顺序变动后的兜底子句。
    n = body.count("在 `reports/` 中")
    return body.replace("在 `reports/` 中", "在 `" + REPORTS_DIR + "/` 中"), n


def _rule_grep_reports(body: str, tp: str) -> tuple[str, int]:
    return re.subn(r"(?<!/)grep -r (.*?) reports/", r"grep -r \1 " + REPORTS_DIR + "/", body)


def _rule_tilde_md(body: str, tp: str) -> tuple[str, int]:
    # 报告输出路径 ~/xxx.md → Windows 用户目录
    return re.subn(r"`~/([^`\s]+\.md)`", r"`" + REPORTS_DIR + r"/\1`", body)


def _rule_tmp(body: str, tp: str) -> tuple[str, int]:
    n = body.count("/tmp/")
    return body.replace("/tmp/", "C:/Users/xdhui/AppData/Local/Temp/"), n


REWRITE_RULES: list[tuple[str, str | int, RuleApply]] = [
    ("~/ai-berkshire/tools/xxx.py 形式", 0, _rule_tilde_tools),
    ("python3 tools/xxx.py", "*", _rule_python3_tools),
    ("裸 `tools/xxx.py` 引用", "*", _rule_bare_tools),
    ("`skills/financial-data.md` 交叉引用", "*", _rule_xref_backtick),
    ("skills/financial-data.md 交叉引用（无反引号）", "*", _rule_xref_plain),
    ("`reports/ 仓库相对路径", "*", _rule_reports_backtick),
    ("--report reports/ 参数", 3, _rule_report_flag),
    ("在 `reports/` 中（中文表述，链式兜底子句）", 0, _rule_reports_zh),
    ("grep -r ... reports/ 用法", 1, _rule_grep_reports),
    ("`~/xxx.md` 报告输出路径", 4, _rule_tilde_md),
    ("/tmp/ 输出路径", 2, _rule_tmp),
]


def transform_body(body: str, tools_prefix: str = TOOLS_ABS) -> str:
    """机械改写：工具路径、输出路径、交叉引用。tools_prefix 为 tools/ 目录的引用前缀。

    逐条应用 REWRITE_RULES；命中断言不在此处做，由 check_rule_hits 对全部源文件聚合计数。
    """
    for _desc, _expected, apply in REWRITE_RULES:
        body, _n = apply(body, tools_prefix)
    return body


def check_rule_hits() -> None:
    """对全部源文件聚合计数每条改写规则的命中数，与期望语义比对，不符即非零退出。"""
    hits = {desc: 0 for desc, _expected, _apply in REWRITE_RULES}
    for source in sorted(CLAUDE_SKILLS.glob("*.md")):
        _fm, body = split_frontmatter(source.read_text(encoding="utf-8"))
        for desc, _expected, apply in REWRITE_RULES:
            body, n = apply(body, TOOLS_ABS)
            hits[desc] += n
    failures = []
    for desc, expected, _apply in REWRITE_RULES:
        actual = hits[desc]
        ok = actual > 0 if expected == "*" else actual == expected
        if not ok:
            want = "至少一次" if expected == "*" else f"精确 {expected} 次"
            failures.append(f"  - {desc}：期望 {want}，实际 {actual} 次")
    if failures:
        raise SystemExit(
            "转换规则命中断言失败（上游可能改写了原文，请人工核对并更新规则或期望）：\n"
            + "\n".join(failures)
        )


def adapter_note(name: str, source_name: str, category: str,
                 tools_prefix: str = TOOLS_ABS) -> str:
    lines = [
        "## Kimi Work 适配说明（adapter note）",
        "",
        f"本技能由 `ai-berkshire/skills/{source_name}` 自动生成，供 Kimi Work（桌面 GUI Agent）使用。",
        "执行前请先阅读以下平台差异说明，正文中的原始表述按此解释：",
        "",
        "- **参数**：正文中的 `$ARGUMENTS` 指当前会话中用户的请求内容。",
        "- **联网**：正文中的 WebSearch/WebFetch 对应 Kimi Work 内置联网搜索；"
        "需要阅读具体页面全文时，用 WebBridge 打开该页面抓取。联网不可用时禁止用训练知识冒充联网结果，"
        "须在报告中醒目标注「未能联网，基于训练知识，置信度降级」。",
        "- **日期基线**：开始研究前先确认当天日期，作为「最新」数据的基准，并在报告头部注明数据截止日期。",
        "- **报告输出**：正文中的 `~/xxx.md` 报告路径统一改写为 Windows 路径 "
        f"`{REPORTS_DIR}/xxx.md`（如目录不存在请先创建）。",
        "- **质量纪律**：关键财务数据须来自两个独立来源，误差 >1% 须标记；"
        "低置信度结论与数据缺口须明确标注。本项目仅供学习研究，不构成投资建议。",
    ]
    if name not in DATA_ROUTED_EXCLUDE:
        lines += [
            "",
            "### 数据获取路由（Kimi Work 数据层升级）",
            "",
            "正文的数据源规范（macrotrends、东方财富、FinMind 等通用网页来源）仍然有效，"
            "但在 Kimi Work 中取数时按以下优先级路由：",
            "",
            "1. **优先调用本机已装的官方数据插件**（比通用网页搜索更权威、结构化）：",
            "   - 行情/财务（A股、港股、美股）：`ifind`（同花顺）；美股可用 `yahoo_finance` 补充；",
            "   - 美股一手 filings（10-K/10-Q/8-K）：`sec_edgar`；",
            "   - 中国企业工商/股权信息：`tianyancha`；",
            "   - 宏观数据：`imf`、`world_bank_open_data`、`igo_open_data`（含 FRED）；",
            "   - 学术论文/研究：`scholar`。",
            "2. **通用联网搜索/WebBridge 作为第二来源**：用于双源交叉验证，以及插件覆盖不到的数据。",
            "3. **交叉验证纪律不变**：关键数据仍需两个独立来源，误差 >1% 须标记；"
            "官方插件与网页来源互为校验，不得因插件取数而省略第二来源。",
            "4. 插件不可用时按原有降级规则处理（醒目标注，禁止用训练知识冒充）。",
        ]
    if category in ("B", "C"):
        if tools_prefix == PLUGIN_TOOLS_PREFIX:
            lines += [
                "",
                "- **本地工具**：正文中 `python3 tools/xxx.py` 已全部改写为 "
                f"`python {PLUGIN_TOOLS_PREFIX}/xxx.py`（Windows 环境下 `python3` 命令不存在，统一用 `python`）。"
                "`<plugin-root>` 指本插件的实际安装根目录——本 SKILL.md 位于 "
                "`<plugin-root>/skills/<技能名>/` 下，运行时据此向上两级解析得到绝对路径。"
                "这些工具仅依赖 Python 标准库，直接在终端运行即可。",
            ]
        else:
            lines += [
                "",
                f"- **本地工具**：正文中 `python3 tools/xxx.py` 已全部改写为 "
                f"`python {TOOLS_ABS}/xxx.py`（Windows 环境下 `python3` 命令不存在，统一用 `python`）。"
                "这些工具仅依赖 Python 标准库，直接在终端运行即可。",
            ]
    if category == "C":
        lines += [
            "",
            "### 多 Agent 编排的 Kimi Work 执行方式（重要）",
            "",
            "正文描述了 Claude Code 的 Task/Team/SendMessage 多 Agent 编排。Kimi Work 中没有这些工具，"
            "请按以下保守方式执行，**忽略正文中 TeamCreate/TaskCreate/TaskUpdate/SendMessage/shutdown_request 等具体工具调用**：",
            "",
            "1. **角色拆解**：按正文定义的角色清单（如商业模式、财务估值、行业竞争、风险评估），"
            "为每个角色准备正文中规定的分析提纲与 prompt 模板。",
            "2. **并行子任务**：若当前环境支持 Agent 集群/并行子任务，将各角色作为相互独立的并行子任务同时启动；"
            "若不支持，则由主 Agent 依次串行完成各角色分析（结果等价，仅耗时更长）。"
            "各子任务相互独立执行，不得共享中间结论，以保证视角独立。",
            "3. **子任务要求**：每个子任务按正文要求联网搜索、调用本地工具验算，"
            "产出该角色的完整 Markdown 分析报告；联网失败必须如实标注，禁止伪装。",
            "4. **主 Agent 汇总**：全部角色报告完成后，由主 Agent（你）按正文的最终报告结构汇总、"
            "交叉核对数据、评估信息充分度，产出最终报告并写入输出路径。",
            "5. **进度同步**：执行过程中向用户实时说明各角色进展。",
        ]
    lines += ["", "---", ""]
    return "\n".join(lines) + "\n"


def build_one(source: Path, tools_prefix: str = TOOLS_ABS) -> str:
    name = source.stem
    category = CATEGORY[name]
    source_text = source.read_text(encoding="utf-8")
    existing_fm, body = split_frontmatter(source_text)
    # 若源文件自带 frontmatter（如 news-pulse），丢弃其英文 description，统一用中文映射
    _ = existing_fm
    content = (
        metadata_for(name)
        + adapter_note(name, source.name, category, tools_prefix)
        + "\n"
        + transform_body(body.rstrip(), tools_prefix)
        + "\n"
    )
    return content


def expected_outputs() -> dict[Path, bytes]:
    """全部生成产物的 {绝对路径: 期望内容} 映射：dist 散装技能 + 插件 skills/tools。"""
    outputs: dict[Path, bytes] = {}
    for source in sorted(CLAUDE_SKILLS.glob("*.md")):
        name = source.stem
        if name not in CATEGORY:
            raise SystemExit(f"缺少分类映射：{name}")
        outputs[DIST / name / "SKILL.md"] = build_one(source).encode("utf-8")
        outputs[PLUGIN_DIR / "skills" / name / "SKILL.md"] = build_one(
            source, PLUGIN_TOOLS_PREFIX
        ).encode("utf-8")
    for tool in sorted((REPO / "tools").glob("*.py")):
        outputs[PLUGIN_DIR / "tools" / tool.name] = tool.read_bytes()
    return outputs


def main() -> None:
    check = "--check" in sys.argv[1:]
    if not (PLUGIN_DIR / "kimi.plugin.json").is_file():
        raise SystemExit(
            f"{PLUGIN_DIR / 'kimi.plugin.json'} 不存在：插件 manifest 由官方脚手架生成，"
            "先按 docs 或 AGENTS.md 跑一次 plugin-builder 的 create_plugin.py"
        )
    check_rule_hits()  # 断言先行：规则失效（上游改写原文）时不产出任何产物更新
    outputs = expected_outputs()
    plugin_managed = [PLUGIN_DIR / "skills", PLUGIN_DIR / "tools"]

    if check:
        stale = [str(p) for p, want in outputs.items()
                 if not p.exists() or p.read_bytes() != want]
        # 插件 skills/tools 目录里的多余文件也算过期（删除后重跑即可收敛）
        for managed in plugin_managed:
            if managed.is_dir():
                for p in managed.rglob("*"):
                    if p.is_file() and p not in outputs:
                        stale.append(f"{p}（多余文件）")
        if stale:
            print("生成产物已过期，请重跑生成：")
            for p in stale:
                print(f"  {p}")
            raise SystemExit(1)
        print(f"校验通过：{len(outputs)} 个生成文件均为最新")
        return

    DIST.mkdir(exist_ok=True)
    # 插件 skills/tools 为全量托管目录：先清空再生成，保证无残留
    for managed in plugin_managed:
        if managed.exists():
            shutil.rmtree(managed)
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    n_dist = len(list(CLAUDE_SKILLS.glob("*.md")))
    n_tools = len(list((REPO / "tools").glob("*.py")))
    print(f"已生成 {n_dist} 个散装技能包到 {DIST}")
    print(f"已生成插件产物：{n_dist} 个技能 + {n_tools} 个工具脚本到 {PLUGIN_DIR}")


if __name__ == "__main__":
    main()
