# -*- coding: utf-8 -*-
"""交付前回归校验（断言式，Output Contract 的落地执行者）。

对交付目录中每件 docx 逐项断言（Output Contract 8 条中可机检的全部）：
  1 五段标题齐全  2 摘要≤300字  3 附图标记双向一致  4 含附图标记说明
  5 无黑名单词  6 权利要求编号连续  7 实施方式开头规范  8 文档可打开且段落达标

用法：python verify_docs.py <交付文本目录>
输出：逐件 PASS/FAIL + 汇总 ALL PASS / n FAIL（退出码非0）
"""
import os
import re
import sys

BLACKLIST = ["【待补】", "待补数据", "待实测", "以实测为准", "示意曲线",
             "数据待实测补实", "优先级", "风险提示", "（数据待实测",
             "示意，数值", "示意，特征"]

FIVE_SECTIONS = ["技术领域", "背景技术", "发明内容", "附图说明", "具体实施方式"]


def get_paras(path):
    from docx import Document
    return [p.text for p in Document(path).paragraphs]


def verify_one(path):
    errs = []
    paras = get_paras(path)
    full = "\n".join(paras)
    if len(paras) < 15:
        errs.append(f"段落数仅{len(paras)}，疑似生成截断")

    # 1 五段标题
    for s in FIVE_SECTIONS:
        if s not in paras:
            errs.append(f"缺五段标题：{s}")

    # 2 摘要 ≤300
    try:
        i = paras.index("说明书摘要")
        abstract = paras[i + 1] if i + 1 < len(paras) else ""
        if len(abstract) > 300:
            errs.append(f"摘要{len(abstract)}字 >300")
    except ValueError:
        errs.append("缺『说明书摘要』标题")

    # 3/4 附图标记
    try:
        from validate_marks import check_marks
        di = paras.index("附图说明")
        ej = paras.index("具体实施方式")
        drawings = "\n".join(paras[di:ej])
        ok, missing, extra = check_marks(drawings, full)
        if missing:
            errs.append(f"附图有但正文未带括号提及: {missing}")
        if extra:
            errs.append(f"正文有但附图说明未列: {extra}")
        if not any("图中" in p for p in paras[di:ej]):
            errs.append("缺『附图标记说明』行")
    except ValueError:
        pass

    # 5 黑名单
    for w in BLACKLIST:
        if w in full:
            errs.append(f"黑名单词出现：{w}")

    # 6 权利要求编号
    claim_nums = re.findall(r'^\s*(\d{1,2})\s*[\.、]', full, re.M)
    if claim_nums:
        nums = [int(x) for x in claim_nums]
        seq = [n for k, n in enumerate(nums) if k == 0 or n > nums[k - 1]]
        if seq and seq[0] == 1:
            expect = list(range(1, len(seq) + 1))
            if seq[:len(expect)] != expect and sorted(set(seq)) != list(range(1, max(seq) + 1)):
                errs.append(f"权利要求编号不连续: {seq}")
        else:
            errs.append(f"权利要求未从1开始: {nums[:5]}")

    # 7 实施方式开头
    if "具体实施方式" in paras:
        ei = paras.index("具体实施方式")
        tail = [p for p in paras[ei + 1:] if p.strip()][:2]
        if tail and not (tail[0].startswith("下面结合附图") or
                         tail[0].startswith("实施例") or
                         "实施例" in tail[0][:30]):
            errs.append(f"实施方式开头不规范: {tail[0][:40]}")

    return errs


def main(folder):
    files = sorted(f for f in os.listdir(folder) if f.endswith(".docx")
                   and not f.startswith("~$"))
    if not files:
        print("无 docx"); sys.exit(2)
    fail = 0
    for f in files:
        errs = verify_one(os.path.join(folder, f))
        if errs:
            fail += 1
            print(f"FAIL {f}")
            for e in errs:
                print(f"   - {e}")
        else:
            print(f"PASS {f}")
    print("=" * 40)
    if fail:
        print(f"{fail} FAIL / {len(files)}"); sys.exit(1)
    print("ALL PASS")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
