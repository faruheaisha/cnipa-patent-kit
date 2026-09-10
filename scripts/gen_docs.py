# -*- coding: utf-8 -*-
"""docx 生成器模板（内容与渲染分离架构）。

内容层：patent_content_*.py 提供纯数据字典，字段约定：
    title / stage / abstract / claims(list) / tech_field / background /
    problem / solution / effect / drawings(list) / embodiment
    可选覆盖：BODY_INTRO（实施方式引导段，使附图标记首次出现即带括号）、
    REWRITE_xx（某件的整体重构版权利要求/名称）

本模板把项目真实生成器的项目内路径抽成参数，开箱即用：
    from gen_docs import DocGen
    g = DocGen(out_final="交付文本", out_sub="在线提交", applicant="…", inventors={...})
    g.build_all(PATENTS)          # 4部分交付文本
    g.build_submission(PATENTS)   # 5标签页提交底稿

依赖：pip install python-docx
"""
import os
import sys
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

FIVE = ["技术领域", "背景技术", "发明内容", "附图说明", "具体实施方式"]


def set_cn(run, name="宋体", size=12, bold=False):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run._element.rPr.rFonts.set(qn('w:eastAsia'), name)


class DocGen:
    def __init__(self, out_final="交付文本", out_sub="在线提交",
                 applicant="", inventors=None, ipc=None, body_intro=None,
                 rewrite=None):
        self.out_final, self.out_sub = out_final, out_sub
        os.makedirs(out_final, exist_ok=True)
        os.makedirs(out_sub, exist_ok=True)
        self.applicant = applicant
        self.inventors = inventors or {}
        self.ipc = ipc or {}
        self.body_intro = body_intro or {}
        self.rewrite = rewrite or {}

    # ---------- 底层段落工具 ----------
    def _para(self, doc, text, size=12, bold=False, align=None,
              space_after=6, indent=24, name="宋体", line=1.5):
        p = doc.add_paragraph()
        if align is not None:
            p.alignment = align
        pf = p.paragraph_format
        pf.space_after = Pt(space_after)
        pf.line_spacing = line
        if indent:
            pf.first_line_indent = Pt(indent)
        if text:
            set_cn(p.add_run(text), name, size, bold)
        return p

    def _head(self, doc, text, size=15):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before, pf.space_after, pf.keep_with_next = Pt(16), Pt(10), True
        set_cn(p.add_run(text), "黑体", size, True)
        return p

    def _title(self, doc, text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf = p.paragraph_format
        pf.space_after, pf.line_spacing = Pt(18), 1.5
        set_cn(p.add_run(text), "黑体", 16, True)
        return p

    def _base_doc(self):
        doc = Document()
        sec = doc.sections[0]
        sec.top_margin = sec.bottom_margin = Cm(2.5)
        sec.left_margin, sec.right_margin = Cm(3.0), Cm(2.5)
        st = doc.styles['Normal']
        st.font.name = '宋体'
        st.font.size = Pt(12)
        st.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        return doc

    def _content_of(self, key, d, field):
        rw = self.rewrite.get(key)
        if rw and field in rw:
            return rw[field]
        return d[field]

    # ---------- 4 部分交付文本 ----------
    def build_final(self, key, d):
        doc = self._base_doc()
        title = self._content_of(key, d, "title")
        self._title(doc, title)
        self._head(doc, "说明书摘要")
        self._para(doc, d["abstract"])
        self._head(doc, "权利要求书")
        for c in self._content_of(key, d, "claims"):
            self._para(doc, c, indent=0)
        self._head(doc, "说明书")
        self._title(doc, title)
        self._para(doc, "技术领域", bold=True, indent=0)
        self._para(doc, d["tech_field"])
        self._para(doc, "背景技术", bold=True, indent=0)
        for seg in d["background"].split("\n"):
            if seg.strip():
                self._para(doc, seg)
        self._para(doc, "发明内容", bold=True, indent=0)
        self._para(doc, "（一）要解决的技术问题", bold=True)
        for seg in str(d["problem"]).split("\n"):
            if seg.strip():
                self._para(doc, seg)
        self._para(doc, "（二）技术方案", bold=True)
        for seg in str(d["solution"]).split("\n"):
            if seg.strip():
                self._para(doc, seg)
        self._para(doc, "（三）有益效果", bold=True)
        for seg in str(d["effect"]).split("\n"):
            if seg.strip():
                self._para(doc, seg)
        self._para(doc, "附图说明", bold=True, indent=0)
        for g in d["drawings"]:
            self._para(doc, g)
        self._para(doc, "具体实施方式", bold=True, indent=0)
        intro = self.body_intro.get(key, "")
        if intro:
            for seg in intro.split("\n"):
                if seg.strip():
                    self._para(doc, seg)
        for seg in str(d["embodiment"]).split("\n"):
            if seg.strip():
                self._para(doc, seg)
        fn = os.path.join(self.out_final, "%s_%s.docx" % (key, d.get("stage", key)))
        doc.save(fn)
        return fn

    def build_all(self, patents):
        return [self.build_final(k, d) for k, d in sorted(patents.items())]

    # ---------- 5 标签页提交底稿 ----------
    def build_submission(self, key, d):
        doc = self._base_doc()
        title = self._content_of(key, d, "title")
        inv = self.inventors.get(key, "")
        ipc = self.ipc.get(key, "")

        # 标签页1 请求书
        self._head(doc, "第一标签页　发明专利请求书（著录项）")
        rows = [("发明名称", title), ("发明人（按序）", inv),
                ("申请人", self.applicant), ("IPC主分类号", ipc),
                ("摘要附图", "指定 图1"),
                ("申请文件清单", "请求书；说明书摘要；权利要求书；说明书；说明书附图")]
        for k, v in rows:
            self._para(doc, "%s：%s" % (k, v), indent=0)
        # 标签页2 摘要
        self._head(doc, "第二标签页　说明书摘要")
        self._para(doc, d["abstract"])
        # 标签页3 权利要求书
        self._head(doc, "第三标签页　权利要求书")
        for c in self._content_of(key, d, "claims"):
            self._para(doc, c, indent=0)
        # 标签页4 说明书
        self._head(doc, "第四标签页　说明书")
        self._title(doc, title)
        self._para(doc, "技术领域", bold=True, indent=0)
        self._para(doc, d["tech_field"])
        self._para(doc, "背景技术", bold=True, indent=0)
        for seg in d["background"].split("\n"):
            if seg.strip():
                self._para(doc, seg)
        self._para(doc, "发明内容", bold=True, indent=0)
        self._para(doc, "（一）要解决的技术问题", bold=True)
        for seg in str(d["problem"]).split("\n"):
            if seg.strip():
                self._para(doc, seg)
        self._para(doc, "（二）技术方案", bold=True)
        for seg in str(d["solution"]).split("\n"):
            if seg.strip():
                self._para(doc, seg)
        self._para(doc, "（三）有益效果", bold=True)
        for seg in str(d["effect"]).split("\n"):
            if seg.strip():
                self._para(doc, seg)
        self._para(doc, "附图说明", bold=True, indent=0)
        for g in d["drawings"]:
            self._para(doc, g)
        self._para(doc, "具体实施方式", bold=True, indent=0)
        intro = self.body_intro.get(key, "")
        if intro:
            for seg in intro.split("\n"):
                if seg.strip():
                    self._para(doc, seg)
        for seg in str(d["embodiment"]).split("\n"):
            if seg.strip():
                self._para(doc, seg)
        # 标签页5 附图清单
        self._head(doc, "第五标签页　说明书附图（上传清单）")
        self._para(doc, "图号　文件名　说明", indent=0)
        n = len([x for x in os.listdir(".") if x.endswith(".jpg")]) if False else 6
        for i in range(1, n + 1):
            self._para(doc, "图%d　附图/%s/图%d.jpg　见附图说明" % (i, key, i), indent=0)
        fn = os.path.join(self.out_sub, "%s_%s_在线提交底稿.docx" % (key, d.get("stage", key)))
        doc.save(fn)
        return fn

    def build_submission_all(self, patents):
        return [self.build_submission(k, d) for k, d in sorted(patents.items())]
