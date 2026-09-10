# -*- coding: utf-8 -*-
"""专利附图绘制公共模块 v2：黑白线条图，300 DPI JPEG，符合 CNIPA 上传要求

v2 改进（针对移位/重叠/不精准）：
1. chain(): 垂直流程链自动布局，等间距、自动箭头，杜绝手工坐标错位
2. elbow(): 90° 折线路由（曼哈顿走线），连线不再斜穿图形
3. ref2(): 标号引出线改为水平/垂直折线，数字不压图形
4. fbox(): 文字超宽自动缩号，杜绝文字溢框
5. 统一是/否标签位置约定（右出口=右上方，下出口=右下方）
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyBboxPatch, Arc
import numpy as np
import os

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

OUT = os.environ.get("CNIPA_FIG_OUT", os.path.join(os.getcwd(), "附图"))
LW = 1.2


def set_out(path):
    """运行时切换输出根目录（也可用环境变量 CNIPA_FIG_OUT 预设）"""
    global OUT
    OUT = path


def canvas(w=160, h=105):
    fig = plt.figure(figsize=(w / 25.4, h / 25.4), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis('off')
    return fig, ax


def text_w(s, fs):
    """估算单行文本渲染宽度(mm)：中文/全角按1字宽，ASCII按0.55字宽"""
    w = 0.0
    for ch in s:
        w += fs * 0.3528 * (0.55 if ord(ch) < 256 else 1.0)
    return w


def fit_fs(text, box_w, fs, min_fs=6.2):
    """框内多行文本：若最宽行超出框宽的92%，按比例缩字号"""
    lines = text.split('\n')
    need = max(text_w(l, fs) for l in lines)
    if need <= box_w * 0.92 or fs <= min_fs:
        return fs
    return max(min_fs, fs * box_w * 0.92 / need)


def fbox(ax, cx, cy, w, h, text, fs=9.5, rnd=False, lw=LW, ls='-'):
    if text:
        fs2 = fit_fs(text, w, fs)
    else:
        fs2 = fs
    if rnd:
        ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                     boxstyle="round,pad=0,rounding_size=3.5",
                     fill=False, lw=lw, ec='k', linestyle=ls))
    else:
        ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h,
                     fill=False, lw=lw, ec='k', linestyle=ls))
    if text:
        ax.text(cx, cy, text, ha='center', va='center', fontsize=fs2,
                linespacing=1.25)
    return fs2


def diamond(ax, cx, cy, w, h, text, fs=8.8):
    fs2 = fit_fs(text, w * 0.62, fs)
    ax.add_patch(Polygon([(cx, cy + h / 2), (cx + w / 2, cy),
                          (cx, cy - h / 2), (cx - w / 2, cy)],
                         fill=False, lw=LW, ec='k'))
    ax.text(cx, cy, text, ha='center', va='center', fontsize=fs2,
            linespacing=1.2)


def farr(ax, x1, y1, x2, y2, lw=LW, ls='-', ms=11):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', color='k', lw=lw,
                                linestyle=ls, mutation_scale=ms))


def elbow(ax, pts, lw=1.0, ls='-', arrow=True, ms=10):
    """折线路由：pts=[(x,y),...]，仅最后一段带箭头"""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color='k', lw=lw, linestyle=ls,
                solid_capstyle='round', solid_joinstyle='miter')
    if arrow:
        farr(ax, xs[-2], ys[-2], xs[-1], ys[-1], lw=lw, ls=ls, ms=ms)
    else:
        ax.plot([xs[-2], xs[-1]], [ys[-2], ys[-1]], color='k', lw=lw,
                linestyle=ls, solid_capstyle='round')


def chain(ax, x, y_top, items, w=70, bh=11, gap=7.5, fs=9,
          dias=(), dw=62, dh=17, dfs=8.4):
    """垂直流程链自动布局。
    items: 文本列表（按顺序自上而下）；dias: 菱形节点的下标集合。
    自动画相邻节点箭头，返回 [(cx, cy, 'box'|'dia'), ...]。
    """
    nodes = []
    y = y_top
    for i, s in enumerate(items):
        if i in dias:
            cy = y - dh / 2
            diamond(ax, x, cy, dw, dh, s, fs=dfs)
            nodes.append((x, cy, 'dia'))
            step = dh + gap
        else:
            cy = y - bh / 2
            fbox(ax, x, cy, w, bh, s, fs=fs)
            nodes.append((x, cy, 'box'))
            step = bh + gap
        y -= step
    for a, b in zip(nodes[:-1], nodes[1:]):
        y1 = a[1] - (dh / 2 if a[2] == 'dia' else bh / 2)
        y2 = b[1] + (dh / 2 if b[2] == 'dia' else bh / 2)
        farr(ax, x, y1, x, y2)
    return nodes


def side_box(ax, src, x2, w, h, text, fs=8.2, y2=None, label='', lab_dx=9,
             lab_dy=2.8):
    """菱形右分支：从菱形右尖水平箭头到侧框左缘，标签放线上方"""
    x1, y1 = src[0], src[1]
    if y2 is None:
        y2 = y1
    x1 = src[0] + (src[3] if len(src) > 3 else 0)
    farr(ax, x1, y1, x2 - w / 2, y2)
    if label:
        txt(ax, x1 + lab_dx, y1 + lab_dy, label, fs=8.5)
    fbox(ax, x2, y2, w, h, text, fs=fs)
    return (x2, y2, w, h)


def yes_no(ax, x, y, s='是', side='r'):
    """统一的是/否标签放置：
    side='r'：水平出口线上方（x 为菱形右尖横坐标，y 为其纵坐标）
    side='d'：竖直出口右侧（x,y 为菱形底尖坐标，标签在底尖下方偏右）"""
    if side == 'r':
        txt(ax, x + 7, y + 2.6, s, fs=8.5)
    else:
        txt(ax, x + 2.5, y - 3.8, s, fs=8.5)


def ref2(ax, num, px, py, tx, ty, fs=10):
    """标号引出：先从部件点走垂直段再水平段到编号，避免斜穿图形"""
    elbow(ax, [(px, py), (px, ty), (tx, ty)], lw=0.7, arrow=False, ms=0)
    ax.text(tx, ty, str(num), fontsize=fs, ha='center', va='center',
            bbox=dict(fc='white', ec='none', pad=0.6))


def lead(ax, px, py, tx, ty, lw=0.7):
    """纯引线（编号融入名称文字，由调用者用 txt 标注）"""
    elbow(ax, [(px, py), (px, ty), (tx, ty)], lw=lw, arrow=False, ms=0)


def ref(ax, num, px, py, tx, ty, fs=10):
    ax.annotate(str(num), xy=(px, py), xytext=(tx, ty), fontsize=fs,
                ha='center', va='center',
                arrowprops=dict(arrowstyle='-', lw=0.7, color='k',
                                shrinkA=2, shrinkB=1))


def line(ax, xs, ys, lw=LW, ls='-'):
    ax.plot(xs, ys, color='k', lw=lw, linestyle=ls, solid_capstyle='round')


def txt(ax, x, y, s, fs=9, ha='left', va='center', weight='normal'):
    ax.text(x, y, s, fontsize=fs, ha=ha, va=va, fontweight=weight)


def figlabel(fig, text, y=0.025):
    fig.text(0.5, y, text, ha='center', va='bottom', fontsize=11)


def legend2(ax, x, y, s, fs=8.5):
    ax.text(x, y, s, fontsize=fs, ha='left', va='center')


def save(fig, pat, num):
    d = os.path.join(OUT, pat)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, '图%d.jpg' % num)
    fig.savefig(p, dpi=300, facecolor='white')
    plt.close(fig)
    return p
