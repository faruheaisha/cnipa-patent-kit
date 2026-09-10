# -*- coding: utf-8 -*-
"""技能包自检脚本（正式文件，可重复运行）。
运行：python self_test.py  （需 python-docx）
"""
import os
import sys
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "scripts")
sys.path.insert(0, SCRIPTS)


def main():
    import py_compile
    for f in os.listdir(SCRIPTS):
        if f.endswith(".py"):
            py_compile.compile(os.path.join(SCRIPTS, f), doraise=True)
    print("1. 全部脚本编译 OK")

    from validate_marks import check_marks
    drawings = "图1 为…结构示意图；\n图中：1-基体；2-感知单元；8-处理器"
    body = "本实施例的装置包括基体（1）、感知单元（2）和处理器（8）。"
    ok, missing, extra = check_marks(drawings, body)
    assert ok and not missing and not extra
    ok2, m2, _ = check_marks(drawings, "本实施例包括基体（1）。")
    assert not ok2 and set(m2) == {"2", "8"}
    print("2. validate_marks 正反用例 OK")

    from extract_claims_data import extract_all
    fake = {"01": {"embodiment": "采样率不低于1kHz，检测限0.1Pa。这是不含数字的句子。",
                   "effect": ["灵敏度达到0.8kPa-1。"]}}
    assert len(extract_all(fake)) == 2
    assert extract_all({"02": {"embodiment": "检测结果显示样本阈值45分贝。"}}
                       )[0]["strong_assert"] is True
    print("3. extract_claims_data 正反用例 OK")

    from gen_docs import DocGen
    d = {"title": "测试装置", "stage": "测试", "abstract": "短摘要" * 3,
         "claims": ["1. 一种测试装置，其特征在于包括基体（1）。",
                    "2. 根据权利要求1所述的测试装置，其特征在于还包括处理器（8）。"],
         "tech_field": "测试领域", "background": "背景。", "problem": "问题。",
         "solution": "方案。", "effect": "效果。",
         "drawings": ["图1 为测试装置结构示意图；", "图中：1-基体；8-处理器"],
         "embodiment": "下面结合附图对本发明作进一步说明。如图1所示，包括基体（1）与处理器（8）。"}
    g = DocGen(out_final=os.path.join(HERE, "_t_final"),
               out_sub=os.path.join(HERE, "_t_sub"),
               applicant="测试单位", inventors={"01": "甲、乙"}, ipc={"01": "G01"})
    from verify_docs import verify_one
    errs = verify_one(g.build_final("01", d))
    assert not errs, errs
    print("4. verify_docs 合规样例 ALL PASS")

    d_bad = dict(d)
    d_bad["abstract"] = "长" * 301
    errs2 = verify_one(g.build_final("01b", d_bad))
    assert any("300" in e for e in errs2)
    print("5. verify_docs 抓超字数 OK:", errs2[0])

    fn3 = g.build_submission("01", d)
    assert os.path.exists(fn3)
    print("6. submission 5标签页生成 OK")

    shutil.rmtree(os.path.join(HERE, "_t_final"))
    shutil.rmtree(os.path.join(HERE, "_t_sub"))
    print("自检全部通过 ✓")


if __name__ == "__main__":
    main()
