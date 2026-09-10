# cnipa-patent-kit

**CNIPA 中国发明专利申请全流程 Agent Skill** —— 从技术交底到一键可提交的五书材料。
遵循 [Agent Skills 开放标准](https://agentskills.io)（anthropics/skills 格式），
已在真实项目（6 件发明专利、36 张附图、约 6.5 万字申请文本）中全流程验证。

## 它解决什么

| 痛点 | 本 skill 的做法 |
|---|---|
| 多件专利自我抵触 | 在先专利权利要求逐条划界表 + 术语黑名单 + 高风险件重构策略 |
| 文本不合细则 | 《专利法实施细则》20-23 条落地模板 + 断言式校验（摘要≤300字、附图标记双向一致等 8 条 Output Contract） |
| 附图手工布局反复重叠 | matplotlib 自动布局库（链式流程图/曼哈顿走线/文字自动缩号），300DPI 黑白 JPEG 直达 cponline 上传规范 |
| 数据来源说不清 | 数值声明自动提取 → [A]自产材料/[B]文献/[C]实施例示例 三级溯源标注 → 溯源核对表 |
| 交付即战力 | 内容/生成/校验三层分离架构：改内容→重跑生成→回归校验，一轮 3 分钟 |

## 目录

```
cnipa-patent-kit/
├── SKILL.md                      # 入口（八阶段流程 + Output Contract + 硬性红线）
├── references/
│   ├── prior-art-mapping.md      # 在先专利划界方法论
│   ├── drafting-spec.md          # 撰写规范全文（细则 20-23 条）
│   ├── figure-drawing.md         # 附图规范 + draw_helpers API
│   ├── data-provenance.md        # 数据溯源三级标注
│   └── submission-checklist.md   # cponline 提交规范 + 回归校验
├── scripts/
│   ├── draw_helpers.py           # 附图绘制公共库
│   ├── extract_claims_data.py    # 数值声明句提取
│   ├── gen_docs.py               # docx 生成器（4 标签页 + 5 标签页）
│   ├── validate_marks.py         # 附图标记↔正文一致性校验
│   └── verify_docs.py            # 交付前回归校验
├── evals/
│   └── evals.json                # 触发/验收/边界评测集（6 组）
├── assets/case-study.md          # 匿名化实战案例（方法论决策链，已脱敏）
└── self_test.py                  # 自检（python self_test.py 应全部通过）
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

agent 会按 SKILL.md 八阶段走：交底整理 → 体系设计 → 在先划界 → 撰写 → 附图 → 溯源审核 → 提交底稿 + 回归校验 → 提交后期限管理。

单独画图 / 校验也可直接用脚本：

```bash
python scripts/validate_marks.py 交付文本/01_装置类.docx     # 标记一致性
python scripts/verify_docs.py 交付文本/                      # 全量回归
```

> **隐私声明**：本仓库为公开发布，但只包含方法论、脚本与**匿名化案例**——
> 不含任何真实专利文本、附图、数据、申请人或发明人信息。
> 使用本 skill 产出专利材料时，申请公开前的文本与附图属未公开专利内容，
> **请勿提交到任何公开仓库或渠道**（先申请后公开）。

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

## 免责声明

本 skill 输出为申请底稿，正式提交前建议由专利代理师复核；
法律条款引用以国家知识产权局现行规定为准。

## License

MIT
