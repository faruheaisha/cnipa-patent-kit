# -*- coding: utf-8 -*-
"""从专利内容字典中提取全部数值声明句（数据溯源审核第一步）。

用法：
    from extract_claims_data import extract_all
    items = extract_all(patents_dict)   # {patent_id: content_dict}

content_dict 支持 embodiment/effect/solution/problem 四个字段（str 或 list[str]）。
输出按专利分组的声明句列表，供人工对照语料做 [A]/[B]/[C] 三级标注。
"""
import re

UNIT_PAT = re.compile(
    r'(\d+(?:\.\d+)?\s*(?:千赫兹|kHz|Hz|赫兹|分贝|dB|帕|千帕|Pa|kPa|'
    r'毫米|mm|微米|μm|um|%|倍|人|名|例|次|个|层|秒|小时|年|岁|天|帧))'
)

# 实验报告风强断言词：[C]类数据命中即提示软化措辞
STRONG = ["实测", "依托的项目", "项目中", "验证", "试验", "测得",
          "检测显示", "结果显示", "统计", "完成部署", "应用效果", "效果达到"]


def sent_split(text):
    return re.split(r'(?<=[。；])', re.sub(r'\s+', '', text))


def extract(patent_id, content):
    fields = []
    for f in ("embodiment", "effect", "solution", "problem"):
        v = content.get(f)
        if isinstance(v, str):
            fields.append((f, v))
        elif isinstance(v, list):
            fields.extend((f, s) for s in v if isinstance(s, str))
        elif v is None:
            continue
        else:
            fields.append((f, str(v)))
    items = []
    seen = set()
    for f, t in fields:
        for s in sent_split(t):
            if UNIT_PAT.search(s) and len(s) > 5 and s not in seen:
                seen.add(s)
                items.append({
                    "patent": patent_id,
                    "field": f,
                    "sentence": s,
                    "strong_assert": any(w in s for w in STRONG),
                })
    return items


def extract_all(patents_dict):
    out = []
    for pid, content in patents_dict.items():
        out.extend(extract(pid, content))
    return out


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    # 演示：配合项目内容字典使用
    print("import extract_all; extract_all(PATENTS) -> list of dict")
