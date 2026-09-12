# -*- coding: utf-8 -*-
"""fix_tech_docs.py -- apply the very rules of FIGURE_SKILLS to the two technical
reports: kill every overfull box.

  * global emergencystretch for CJK paragraphs with long inline maths
  * the two-metric formula split over two lines
  * formal-test tables: breakable code column
  * longtable column widths trimmed
  * one long cell shortened, one wrong cross-reference fixed
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def edit(fname, pairs):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s:
            print("  !! missing in %s: %s" % (fname, a[:46].replace("\n", " ")))
            continue
        s = s.replace(a, b, 1)
        print("  ok %s: %s" % (fname, a[:46].replace("\n", " ")))
    io.open(p, "w", encoding="utf-8").write(s)


# ---------------------------------------------------------- common --------
edit("tech_common.tex", [
    ("\\setlength{\\parskip}{0.35em}",
     "\\setlength{\\emergencystretch}{2.5em}\n\\setlength{\\parskip}{0.35em}"),
])

# ------------------------------------------------------------- Q3 ---------
edit("tech_q3.tex", [
    ("""\\begin{equation}
\\text{被清除干扰源个数的比例}=\\frac{\\text{被清除干扰源的个数}}{\\text{干扰源总数}},\\qquad
\\text{平均定位清除时间}=\\frac{\\text{定位清除总时间}}{\\text{被清除干扰源的个数}}
\\end{equation}""",
     """\\begin{equation}
\\begin{aligned}
\\text{被清除干扰源个数的比例}&=\\frac{\\text{被清除干扰源的个数}}{\\text{干扰源总数}},\\\\[2pt]
\\text{平均定位清除时间}&=\\frac{\\text{定位清除总时间}}{\\text{被清除干扰源的个数}} .
\\end{aligned}
\\end{equation}"""),
    ("""\\begin{tabular}{cccc}
\\toprule
测试案例编码 & 清除干扰源个数 & 平均定位清除时间/s & 程序运行时间/s \\\\ \\midrule
Q3-810001-020304050708101112131415171819 & 15（15） & 268.4 & 1.7 \\\\
Q3-810002-010203070809101215171819 & 12（12） & 375.2 & 1.3 \\\\
Q3-810003-01020405061013141516 & 10（10） & 399.6 & 1.5 \\\\
\\bottomrule
\\end{tabular}""",
     """\\small
\\begin{tabular}{p{5.4cm}ccc}
\\toprule
测试案例编码 & 清除干扰源\\newline 个数 & 平均定位清除\\newline 时间/s & 程序运行\\newline 时间/s \\\\ \\midrule
\\ttfamily Q3-810001-\\hspace{0pt}0203040507\\hspace{0pt}0810111213\\hspace{0pt}1415171819 & 15（15） & 268.4 & 1.7 \\\\
\\ttfamily Q3-810002-\\hspace{0pt}0102030708\\hspace{0pt}0910121517\\hspace{0pt}1819 & 12（12） & 375.2 & 1.3 \\\\
\\ttfamily Q3-810003-\\hspace{0pt}0102040506\\hspace{0pt}1013141516 & 10（10） & 399.6 & 1.5 \\\\
\\bottomrule
\\end{tabular}"""),
    ("\\begin{longtable}{p{0.6cm}p{4.6cm}p{4.4cm}p{5.0cm}}",
     "\\begin{longtable}{p{0.55cm}p{4.5cm}p{4.3cm}p{4.7cm}}"),
    ("""6 & 论文首轮编译报错 \\texttt{Environment proposition undefined} & cumcmthesis 自带 theorem/lemma/corollary/proof，与 amsthm 冲突 & 去掉 amsthm，只定义 proposition 与轻量 pf 环境 \\\\""",
     """6 & 论文首轮编译报错 \\texttt{Environment proposition undefined} & cumcmthesis 已自带 theorem/lemma/proof，与 amsthm 冲突 & 去掉 amsthm，只定义 proposition 与轻量 pf 环境 \\\\"""),
])

# ------------------------------------------------------------- Q4 ---------
edit("tech_q4.tex", [
    ("""\\begin{tabular}{cccc}
\\toprule
测试案例编码 & 清除干扰源个数 & 平均定位清除时间/s & 程序运行时间/s \\\\ \\midrule
Q4-910001-0104050607081013171820 & 11（11） & 602.6 & 2.0 \\\\
Q4-910002-030405060809111215161920 & 11（12） & 654.5 & 2.3 \\\\
Q4-910003-0102030711131415171819 & 11（11） & 718.8 & 2.3 \\\\
\\bottomrule
\\end{tabular}""",
     """\\small
\\begin{tabular}{p{5.4cm}ccc}
\\toprule
测试案例编码 & 清除干扰源\\newline 个数 & 平均定位清除\\newline 时间/s & 程序运行\\newline 时间/s \\\\ \\midrule
\\ttfamily Q4-910001-\\hspace{0pt}0104050607\\hspace{0pt}0810131718\\hspace{0pt}20 & 11（11） & 602.6 & 2.0 \\\\
\\ttfamily Q4-910002-\\hspace{0pt}0304050608\\hspace{0pt}0911121516\\hspace{0pt}1920 & 11（12） & 654.5 & 2.3 \\\\
\\ttfamily Q4-910003-\\hspace{0pt}0102030711\\hspace{0pt}1314151718\\hspace{0pt}19 & 11（11） & 718.8 & 2.3 \\\\
\\bottomrule
\\end{tabular}"""),
    ("\\begin{longtable}{p{0.6cm}p{4.4cm}p{4.6cm}p{5.0cm}}",
     "\\begin{longtable}{p{0.55cm}p{4.3cm}p{4.5cm}p{4.7cm}}"),
    ("""第 2 局未清除的干扰源是一个位于目标域边缘、定向方向朝外的源，属于 3.5 节讨论的
"半平面黑洞"极端情形。""",
     """第 2 局未清除的干扰源是一个位于目标域边缘、定向方向朝外的源，
属于 4.5 节讨论的"半平面黑洞"极端情形。"""),
])
print("done")
