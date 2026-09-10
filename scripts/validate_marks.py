# -*- coding: utf-8 -*-
"""附图标记 ↔ 说明书正文 一致性校验（细则21条）。

规则：
1. 附图说明中列出的每个标记，必须在正文（含"下面结合附图"引导段）中以
   带括号编号形式出现，如"处理器（8）"
2. 正文括号标记不得出现在附图说明之外却从未定义（双向差集为空）
3. 同一标记在同件内只能指同一部件（人工抽查项，脚本输出标记清单辅助）

用法：
    python validate_marks.py <docx_path>
或
    from validate_marks import check_marks
    ok, missing, extra = check_marks(drawings_text, body_text)
"""
import re
import sys


def extract_marks(text):
    """提取正文中的括号标记：处理器（8）→ '8'；兼容半角 (8)"""
    nums = re.findall(r'[（(]\s*(\d{1,3})\s*[)）]', text)
    return set(nums)


def extract_drawing_marks(drawings_text):
    """附图标记说明行格式：'图中：1-基体；2-感知单元；…' 或列表逐项"""
    nums = set()
    m = re.search(r'图中[：:](.*)', drawings_text, re.S)
    seg = m.group(1) if m else drawings_text
    for part in re.split(r'[；;，,]', seg):
        m2 = re.match(r'\s*(\d{1,3})\s*[-—－~至]', part.strip())
        if m2:
            nums.add(m2.group(1))
    return nums


def check_marks(drawings_text, body_text):
    """返回 (ok, missing_in_body, undefined_in_body)"""
    d_marks = extract_drawing_marks(drawings_text)
    b_marks = extract_marks(body_text)
    missing = sorted(d_marks - b_marks, key=int)     # 附图有、正文没提 → 违反细则21条
    extra = sorted(b_marks - d_marks, key=int)       # 正文有、附图说明未列 → 疑似漏标
    return (not missing and not extra), missing, extra


def check_docx(path):
    from docx import Document
    doc = Document(path)
    paras = [p.text for p in doc.paragraphs]
    full = "\n".join(paras)
    # 定位附图说明段
    try:
        i = paras.index("附图说明")
        j = paras.index("具体实施方式")
    except ValueError:
        return False, ["未找到附图说明/具体实施方式标题"], []
    drawings = "\n".join(paras[i:j])
    body = full
    return check_marks(drawings, body)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ok, missing, extra = check_docx(sys.argv[1])
        print("PASS" if ok else "FAIL")
        if missing:
            print("  附图有但正文未带括号提及:", missing)
        if extra:
            print("  正文有但附图说明未列:", extra)
    else:
        print(__doc__)
