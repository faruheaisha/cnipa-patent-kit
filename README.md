# cnipa-patent-kit

**CNIPA 中国发明专利申请全流程 Agent Skill** —— 从技术交底、五书撰写、附图绘制，
到提交底稿与提交后期限管理。

*An Agent Skill for drafting and filing invention patents with CNIPA (China National
Intellectual Property Administration) — from disclosure triage and claim drafting
through figure generation, submission-ready deliverables, and post-filing deadline
management.*

[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-black.svg)](https://www.python.org/)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-black.svg)](https://agentskills.io)

遵循 [Agent Skills 开放标准](https://agentskills.io)（`SKILL.md` + 渐进式披露），
已在真实的多件发明专利组合申报（6 件专利、36 张附图、约 6.5 万字申请文本）中全流程验证，
并持续用真实办理现场遇到的问题反哺。案例已匿名化，见
[assets/case-study.md](assets/case-study.md)。

> **关于保密**：本仓库只包含方法论、脚本与匿名化案例，
> **不含任何真实专利文本、附图、数据、申请人或发明人信息**。

## 它解决什么

| 痛点 | 本 skill 的做法 |
|---|---|
| 多件专利自我抵触 | 在先专利权利要求逐条划界表 + 术语黑名单 + 高风险件重构策略 |
| 文本不合细则 | 《专利法实施细则》20-23 条落地模板 + 断言式校验（摘要 ≤300 字、附图标记双向一致等 8 条 Output Contract） |
| 附图手工布局反复重叠 | matplotlib 自动布局库（链式流程图 / 曼哈顿走线 / 文字自动缩号），300DPI 黑白 JPEG 直达 cponline 上传规范 |
| 数据来源说不清 | 数值声明自动提取 → [A] 自产材料 / [B] 文献 / [C] 实施例示例 三级溯源标注 → 溯源核对表 |
| 交付即战力 | 内容 / 生成 / 校验三层分离架构：改内容 → 重跑生成 → 回归校验，一轮 3 分钟 |
| 提交后就不知该干什么 | 提交通知书接收确认路径 + 三个法定期限表 + 漏勾选补办路径 + 12 组误区 FAQ |

## 覆盖范围（八阶段）

| 阶段 | 产出 | 对应 reference |
|---|---|---|
| 1–3 交底整理 / 体系设计 / 在先划界 | 可申报主题清单、多件组合方案、权利要求逐条划界表 | [prior-art-mapping.md](references/prior-art-mapping.md) |
| 4 正文撰写 | 权利要求书、说明书、摘要、请求书著录项 | [drafting-spec.md](references/drafting-spec.md) |
| 5 附图绘制 | 300DPI 黑白线条 JPEG 附图组 | [figure-drawing.md](references/figure-drawing.md) |
| 6 数据溯源审核 | 数值声明清单 + A/B/C 三级溯源表 | [data-provenance.md](references/data-provenance.md) |
| 7 提交底稿与回归校验 | 4 部分交付文本 + 5 标签页在线提交底稿 | [submission-checklist.md](references/submission-checklist.md) |
| 8 提交后程序与期限管理 | 通知书接收与归档、缴费与实审期限台账 | [post-filing.md](references/post-filing.md) |

## 目录

```
cnipa-patent-kit/
├── SKILL.md                      # 入口（八阶段流程 + Output Contract + 硬性红线 + 经验教训）
├── references/
│   ├── prior-art-mapping.md      # 在先专利划界方法论 + 术语黑名单机制
│   ├── drafting-spec.md          # 撰写规范全文（细则 20-23 条落地模板）
│   ├── figure-drawing.md         # 附图规范 + draw_helpers API
│   ├── data-provenance.md        # 数据溯源三级标注
│   ├── submission-checklist.md   # cponline 提交规范 + 回归校验断言
│   └── post-filing.md            # 提交后程序：受理发文时间 / 通知书接收 / 法定期限 / FAQ
├── scripts/
│   ├── draw_helpers.py           # 附图绘制公共库（自动布局 / 防重叠）
│   ├── extract_claims_data.py    # 数值声明句提取
│   ├── gen_docs.py               # docx 生成器（4 标签页 + 5 标签页）
│   ├── validate_marks.py         # 附图标记 ↔ 正文一致性校验
│   └── verify_docs.py            # 交付前回归校验（断言式）
├── evals/
│   └── evals.json                # 触发 / 验收 / 边界评测集（10 组）
├── assets/
│   └── case-study.md             # 匿名化实战案例（方法论决策链）
├── CHANGELOG.md                  # 版本变更记录
├── CONTRIBUTING.md               # 贡献指南（含保密要求）
├── self_test.py                  # 自检（python self_test.py 应全部通过）
├── LICENSE                       # MIT
└── .gitignore                    # 含保密拦截目录
```

## 安装

任选其一（目录名保持 `cnipa-patent-kit`）：

```bash
# Claude Code / 通用 agent（用户级）
git clone https://github.com/faruheaisha/cnipa-patent-kit ~/.claude/skills/cnipa-patent-kit

# WorkBuddy
git clone https://github.com/faruheaisha/cnipa-patent-kit ~/.workbuddy/skills/cnipa-patent-kit

# npx skills CLI
npx skills add faruheaisha/cnipa-patent-kit
```

依赖：`python>=3.10`，`pip install python-docx matplotlib numpy`

## 快速开始

安装后对 agent 说：

> 我有三项技术点（…），想申报发明专利，已发表 N 篇论文，比赛材料公开过部分参数。

agent 会按 SKILL.md 八阶段走：
交底整理 → 体系设计 → 在先划界 → 撰写 → 附图 → 溯源审核 → 提交底稿与回归校验 → 提交后期限管理。

单独画图 / 校验也可直接用脚本：

```bash
python scripts/validate_marks.py 交付文本/01_装置类.docx     # 标记一致性
python scripts/verify_docs.py 交付文本/                      # 全量回归
```

## 提交后必知的三条期限

提交不是终点。本 skill 会把下面三条一并交代给办理人：

1. **申请费 + 公布印刷费**自申请日起 **2 个月内**缴纳，逾期申请视为撤回（唯一紧急项）
2. **实质审查请求**自申请日起 **3 年内**提出，国知局只在此期限届满前 3 个月提醒一次
3. 通知书以电子形式送达，**自发出之日起满 15 日即推定为收到日**，
   须开通发文提醒并定期登录领取，不能等通知

细则见 [references/post-filing.md](references/post-filing.md)。

## 自检

```bash
python self_test.py
# 1. 全部脚本编译 OK
# 2. validate_marks 正反用例 OK
# 3. extract_claims_data 正反用例 OK
# 4. verify_docs 合规样例 ALL PASS
# 5. verify_docs 抓超字数 OK
# 6. submission 5标签页生成 OK
```

## 隐私与保密声明

本仓库为公开发布，但只包含方法论、脚本与**匿名化案例**——
不含任何真实专利文本、附图、数据、申请人或发明人信息。

使用本 skill 产出专利材料时，申请公开前的文本与附图属未公开专利内容，
**请勿提交到任何公开仓库或渠道**（先申请后公开）。
仓库 `.gitignore` 已默认拦截 `专利申请/`、`交付文本/`、`在线提交/`、`附图/` 与 `*.docx`。

## 免责声明

本 skill 输出为申请底稿，正式提交前建议由专利代理师复核；
法律条款、期限与费用标准引用以国家知识产权局现行规定及
cponline 实际界面为准。本仓库不构成法律意见。

## Contributing

见 [CONTRIBUTING.md](CONTRIBUTING.md)。改 `description` 前请先过一遍
[evals/evals.json](evals/evals.json)；提 Issue 时请遮蔽申请号与发明人信息。

版本变更见 [CHANGELOG.md](CHANGELOG.md)。

## License

[MIT](LICENSE) © 2026 faruheaisha
