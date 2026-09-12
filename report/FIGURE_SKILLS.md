# 论文配图与排版 Skills

> 来源：2026 国赛 B 题（无线电干扰源定位与清除）实战，22 张图 + 79 页论文的全部经验。
> 每一条都对应一次**真实的失败与修复**；代码见 `code/make_figures.py`、`code/audit_figures.py`。
> 适用：数学建模竞赛 / 学术论文的图表与 LaTeX 排版。

---

# 第一部分　心法（先读这 3 条）

### 1. 验收标准是"印在纸上能不能看清"，不是"代码跑通了"

一张图要过三关，缺一不可：

```
① 算字号预算（可计算，不靠感觉）
② 逐张 read_image 目视（不只看代码逻辑）
③ 在最终 PDF 页面上再看一遍（PNG 单看会漏掉与外部的碰撞）
```

本次有 3 类问题就是**只在前一关能发现、后一关才暴露**的：
- 图例压住 x 轴标签 → 只看 PNG 觉得"图例在下面啊"，看 PDF 才发现正好压在标签上；
- 缩画布后标签互相叠字 → 改代码时看不出来，重新出图才看见；
- 面板长标题伸进邻面板 y 标签 → 单面板看没问题，拼在一行才撞。

### 2. 90% 的"图不清晰"不是画得不好，而是**画布太大**

字号被缩放压扁是纯几何问题，可以算、可以预算、可以零成本解决（见 §1.3）。

### 3. 一切文字都要能"指认"到坐标区之外

坐标区是**数据的地盘**。图例、角度数值、理论界、临界值、说明文字——全部搬到区外，用引线或图例建立对应关系。
本次共修掉 **9 处**"文字压数据/压标签"，全部是这一条原则的违反。

---

# 第二部分　字号预算（第一优先级）

## 1.1 公式

```
等效字号 eff_pt = font_pt × display_in ÷ fig_in

display_in = width_frac × 6.30 in        # A4 + 2.5cm 页边距 → textwidth ≈ 6.30 in
fig_in     = 导出 PNG 的像素宽 ÷ savefig.dpi   # 必须用实际像素（bbox_inches='tight' 会裁切）
```

**门槛：eff_pt ≥ 9.0**。

## 1.2 反算：画布能画多大

```
fig_in ≤ font_pt × width_frac × 6.30 ÷ 9.0
```

常用配置查表（font_pt = 16）：

| 显示宽度 | 画布上限 | 典型用途 |
|---|---|---|
| 0.56\textwidth | 5.9 in | 单图（饼图、示意图） |
| 0.66\textwidth | 7.0 in | 单图（几何图） |
| 0.74\textwidth | 7.8 in | 单图（较多元素） |
| **0.84\textwidth** | **8.9 in** | **双面板 / 三面板（最常用）** |
| 0.95\textwidth | 10.0 in | 四面板 |

## 1.3 关键认知：**缩画布 ≠ 缩显示**（零成本提清晰度）

论文里图占的版面由 `width_frac` 决定，与 `fig_in` 无关。
缩小 `fig_in`（字号不动）→ 相同内容用**更大的相对字号**表达 → 等效字号上升，**一页都不多占**。

> 本次实测：22 张图首轮 **12 张 < 9 pt（最差 7.3 pt）**；把宽幅多面板图的画布从 10.5 in 压到 8.2~9.1 in 后，**全部 ≥ 9.1 pt，页数不变**。

**这是提清晰度的第一手段，永远优先于"把图放大"。**

## 1.4 审计脚本（每个项目必备）

```python
DPI, TEXTWIDTH_IN, BASE_PT, THRESHOLD = 220.0, 6.30, 16.0, 9.0
# 从 \includegraphics[width=X\textwidth]{.../fig.png} 抓 X，与 PNG 像素宽配对
eff = BASE_PT * (width_frac * TEXTWIDTH_IN) / (png_width_px / DPI)   # 逐图输出，<9 标红
```

输出示例：
```
figure                          fig_in width_fr   eff_pt  verdict
fig_q34_stats.png                7.88     0.76      9.7  OK
fig_q3_time_pie.png              6.23     0.56      9.1  OK
```

---

# 第三部分　布局规则

## 2. 图例：外置四定律

### 2.1 两个模板函数

```python
def legend_below(ax, ncol=3, y=-0.20, fontsize=13, **kw):
    """单面板：图例置于坐标区下方"""
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, y), ncol=ncol,
              frameon=False, fontsize=fontsize, handlelength=1.8,
              columnspacing=1.4, **kw)

def figure_legend(fig, handles, labels=None, ncol=3, y=0.02, fontsize=13):
    """多面板：整图共用一个图外图例"""
    if labels is None:
        labels = [h.get_label() for h in handles]
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, y),
               ncol=ncol, frameon=False, fontsize=fontsize,
               handlelength=1.8, columnspacing=1.5)
```

### 2.2 定律

| # | 定律 | 违反后的症状 |
|---|---|---|
| **L1** | 禁止 `loc="best"`、禁止 `frameon=True` 放在区内 | 窄图上"最佳位置"必然落在数据上 |
| **L2** | 多面板**共用一条 figure 级图例**，不要每面板一条 | 各面板的下方图例在同一高度**串成一行**互相打架 |
| **L3** | 外置 ≠ 安全：必须给足底部留白 | 图例正好压住 x 轴标签（本次踩 2 次） |
| **L4** | 同一语义只给一个 `label=` | 图例出现两条重复条目 |

**L3 的参数配方**（`bbox_to_anchor` 的 y 与 `subplots_adjust(bottom)` 必须配对）：

| 图例规模 | `y` | `subplots_adjust(bottom=)` |
|---|---|---|
| 1 行 2~3 条 | −0.02 ~ −0.05 | 0.30 |
| 1 行 4~6 条 | −0.06 ~ −0.10 | 0.36 ~ 0.40 |
| 2 行 / 含长条目 | −0.10 ~ −0.15 | 0.40 ~ 0.45 |
| 单面板、矮坐标区 | ≤ −0.28 | 配合 `tight_layout` |

> 判定方法只有一个：**渲染最终 PDF 页面，肉眼确认**。

### 2.3 比图例更好的四种表达

| 场景 | 做法 | 收益 |
|---|---|---|
| 折线族 3~6 条 | 曲线**末端直接标注**（`annotate` 在 `xs[-1]`） | 省掉颜色图例，读图路径更短 |
| 阈值/参考线/理论界 | `axvline(..., label=)` + 图外图例 | **不要**把说明写在区内（会压柱/压点） |
| 小扇区饼图 | 只标大块百分比，全部占比进图外图例 | 避免小字挤成一团 |
| 多工况对比 | **颜色编码** + 各面板标题同色 | 窄图上塞文字标签必然叠字 |

## 3. 面板设计

### 3.1 禁止叠加小窗（inset），放大图做成独立面板

`ax.inset_axes()` 的"局部放大"**总会盖住主图的一部分**。改用真正的子图：

| 原布局 | 新布局 |
|---|---|
| 1 图 + 右上角 inset | `plt.subplots(1,2)`：(a) 整体 + (b) 放大（独立坐标轴、米级刻度） |
| 3 图各带"定位器" inset | `gridspec(1,4, width_ratios=[1.6,1,1,1])`：(a) 总览 + (b)(c)(d) 放大 |

联动技巧：总览里用**颜色**区分工况，与放大面板**标题同色**，就不必在总览里塞文字标签。

### 3.2 面板标题必须短

左侧面板的长标题会**伸进右侧面板的 y 轴标签区**。
**规则**：统一 `(a) 短标题` / `(b) 短标题`，数值与条件写进图注；标题字号 ≤ 正文字号。

### 3.3 面板数量与画布的关系

面板越多 → 每面板越窄 → 越容易撞车。经验上限：
- 2 面板：画布 ≤ 9.5 in 舒适；
- 3 面板：画布 ≤ 9.5 in，标题必须短、刻度标签可能要合并；
- 4 面板：只放"总览 + 3 个同构小图"，且总览面板 `width_ratio` 加大。

## 4. 几何标注：弧 + 空白角 + 引线

把 `φ*=36.8°` 直接放在两条线的交点旁边 → **文字盖住线**（本次用户截图指出）。

```python
from matplotlib.patches import Arc
ang2 = math.degrees(math.atan2(S2[1]-S1[1], S2[0]-S1[0])) % 360.0
t1, t2 = min(th1, ang2), max(th1, ang2)
R = 560.0
ax.add_patch(Arc(S1, 2*R, 2*R, angle=0, theta1=t1, theta2=t2,
                 color="red", lw=2.2, zorder=5))              # ① 顶点处画角弧
aend = math.radians(t2)
ax.annotate(f"$\\varphi^*={phi:.1f}^\\circ$",
            xy=(S1[0]+R*math.cos(aend), S1[1]+R*math.sin(aend)),   # ② 指向弧端点
            xytext=(-1740, 940), fontsize=15, color="red", ha="left",
            arrowprops=dict(arrowstyle="-|>", color="red", lw=1.6))
```

三条要点：
1. 箭头指向**弧的端点**，不要指弧中点（中点引线常横穿另一条线 —— 本次第一版就是错的）；
2. 标签落在**用数据范围确认过的空白**区域；
3. 距离、尺寸等同类标注同理：数值外移，引线指对象。

## 5. 数据表达：让图自己说话

| 手段 | 适用 | 代码要点 |
|---|---|---|
| **分箱中位数趋势线** | 散点 >500 看不出趋势 | `np.linspace` 分箱 + `np.median`，黑粗线叠在浅色散点上 |
| **柱上标数值** | 所有柱状图 | `ax.bar_label(b, fmt="%.1f", fontsize=13, padding=3)` |
| **对数轴** | 跨 2 个数量级 | `set_yscale("log")` + `grid(which="both")`；**跨 ∞ 的数据不能画**，改竖排文字"存在无界情形" |
| **按类别着色** | 同一散点含多种结果 | 按结果分色，图例放图外（别让三种结果都是蓝色） |
| **公共轴标签** | 同量纲多面板 | 取消各面板 xlabel，改 `fig.text(0.5, 0.10, ...)` |
| **短刻度标签** | 窄面板两分类 | `问题3(全向)` 必然叠字 → 改 `问题 3`，细节进图注 |

---

# 第四部分　中文与公式

```python
for cand in ("Microsoft YaHei", "SimHei", "DengXian", "SimSun"):
    matplotlib.rcParams["font.sans-serif"] = [cand]; break
matplotlib.rcParams.update({
    "font.family": "sans-serif", "axes.unicode_minus": False,
    "font.size": 16, "axes.titlesize": 17, "axes.labelsize": 17,
    "xtick.labelsize": 14, "ytick.labelsize": 14, "legend.fontsize": 13,
    "lines.linewidth": 2.4, "lines.markersize": 8, "axes.linewidth": 1.3,
    "grid.alpha": 0.35, "figure.dpi": 200, "savefig.dpi": 220,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.08,
})
```

规则：
1. **中文标签放外部 UTF-8 数据文件**（`zh_labels.json`），源码保持纯 ASCII —— 既满足"代码中不出现中文"的可移植性要求，又能让图出现中文；
2. mathtext 混排：`"$\\pm1^\\circ$ 边界"`；下标用 `$S_1$`，**不要 Unicode 下标**（字体缺字 → 方块）；
3. **`%` 必须写 `%%`**：`"95%% 分位 %.1f m" % v`；
4. 线宽 ≥ 2.2 pt、点径 ≥ 8 pt、`grid.alpha` ≤ 0.4。

---

# 第五部分　流程图（TikZ）

**症状**：底部"汇总/内核"框比上方方框阵列窄 → 箭头**歪斜**；箭头标签长于间隙 → **压住方框**。

```latex
\usetikzlibrary{arrows.meta,positioning,calc}

% ① 方框等宽等距；间隙 > 标签宽度（4 个汉字 ≈ 1.5cm 间隙安全）
\node[box] (q1) {...};
\node[box, right=1.50cm of q1] (q2) {...};     % minimum width=2.58cm

% ② 汇总框宽度 = 阵列总宽 = n·w + (n−1)·gap，用 calc 居中
\node[core, minimum width=14.82cm] (core)
     at ($(q1.south)!0.5!(q4.south) + (0,-1.15cm)$) {...};

% ③ \foreach 画垂直箭头（自动对齐每个框的中心）
\foreach \q in {q1, q2, q3, q4}{%
  \draw[dar] (core.north -| \q.south) -- (\q.south);
}
```

**兜底**：整图套 `\resizebox{\textwidth}{!}{...}`，从结构上保证永不超框（缩放 <3% 肉眼不可见）。
**去噪**：语义重复的长箭头要删 —— 本次拥挤的主因就是一条与内核框重复的"位置估计"长箭头。

---

# 第六部分　LaTeX 排版

## 6.1 overfull 检索工作流

```
xelatex paper.tex  →  grep "Overfull \hbox" paper.log  →  按行号定位
```

⚠️ 若正文由 `paper_p1..p4.tex` 合并为 `paper.tex`，日志行号是**合并后**的行号，需减去各分节起始偏移。写个 `show_region.py <file> <a> <b>` 打印带行号片段最省事。

## 6.2 五类成因与修法

| 成因 | 症状 | 修法 |
|---|---|---|
| **行内长公式** | 公式冲出版心，单位被拆行（`1000` 换行成 `m`） | 改**独立编号公式**；并 `\setlength{\emergencystretch}{2.5em}` 让中文段落中的长公式可断 |
| **宽表格** | 超 60~100 pt | ①长文本列改 `p{宽}`；②长编码串用 `\hspace{0pt}` 制造断行点（**不加连字符**）；③表头 `\newline` 折行 + `\small` |
| **长条目** | 超 5~40 pt | 拆句、把括号内长公式移到句外、缩短修饰语 |
| **流程图** | 超 10~35 pt | §5 三条修法 + `\resizebox` 兜底 |
| **定理陈述** | 夹长公式 | 拆两句，公式单独成行 |

**验收标准：`Overfull \hbox = 0`**。剩余 `Underfull` 若只在窄表格列与附录代码清单中，属正常。

## 6.3 版面总检：30 页联系表

```python
imgs = [pdf[i].render(scale=0.42).to_pil().convert('RGB') for i in range(1, 31)]
sheet = Image.new('RGB', (6*w, 5*h), 'white')
for k, im in enumerate(imgs): sheet.paste(im, ((k%6)*w, (k//6)*h))
```

一眼扫出：大片空白（浮动体错位）、图例压轴标签、表格越界、孤行。

## 6.4 与页数的联动（清晰度优先）

压缩顺序，**前面做完再考虑后面**：

1. **缩画布、不动显示宽度**（提清晰度、零页数成本）—— 永远第一步；
2. 浮动体间距 `\textfloatsep/\floatsep/\intextsep → 7pt`；行距 `\baselinestretch` 1.38 → 1.18~1.30（格式规范不限行距）；
3. 多面板改整图共用图例（省一行）；
4. 摘要压到 1 页、精简冗余叙述；
5. **最后才减图** —— 绝不为页数牺牲清晰度。

---

# 第七部分　自检清单（逐项打勾）

**图的清晰度**
- [ ] 等效字号 ≥ 9 pt（跑审计脚本）
- [ ] 线宽 ≥ 2.2 pt、点径 ≥ 8 pt、柱上有数值

**遮挡**
- [ ] 图例全部在坐标区外，且**没有压住任何面板的 x 轴标签**（**必须看最终 PDF**）
- [ ] 面板长标题没有伸进相邻面板的 y 标签区
- [ ] 角度/尺寸/理论界标注**全部在图外**（弧+引线 或 图例），区内无任何说明文字
- [ ] 无 inset 叠加小窗（本项目硬要求）
- [ ] 无任何两段文字重叠；边缘标签未被裁切

**内容**
- [ ] 散点有趋势线、折线有末端标注、类别有颜色区分
- [ ] 极值/临界/理论界的标注在空白侧
- [ ] **图改了，图注跟上了吗**（本次踩坑：图改双面板后图注仍写"右下角为局部放大"）

**排版**
- [ ] `Overfull \hbox = 0`
- [ ] 流程图箭头垂直对齐、标签在间隙内
- [ ] 30 页联系表整体扫过一遍

---

# 第八部分　故障速查表

| # | 症状 | 根因 | 修法 |
|---|---|---|---|
| 1 | 图印出来字太小 | 画布过大 → 缩放压扁 | 算 eff_pt，**缩画布**（§1.3） |
| 2 | 图例压住数据点 | `loc="best"` / 区内图例 | 改 `legend_below` / `figure_legend` |
| 3 | 两个面板图例底部串行重叠 | 各面板各画一条下方图例 | 改 `figure_legend` |
| 4 | **图例压住 x 轴标签** | `y` 与 `bottom` 留白不配对 | 按 §2.2 配方表调参 |
| 5 | **面板长标题撞邻面板 y 标签** | 标题过长 | 统一 `(a) 短标题`，条件进图注 |
| 6 | 角度标注盖住视线 | 标签放在交点附近 | `Arc` + 空白角 + 引线指**弧端点** |
| 7 | 理论界/临界值文字压住柱或散点 | 写在坐标区内 | 给参考线加 `label=`，进图外图例 |
| 8 | 局部放大窗盖住主图 | 用了 `inset_axes` | 改独立面板 |
| 9 | 缩画布后标签互相叠字 | 字号相对变大 | 短标签 + 加大 `w_pad`/`bottom` + 细节进图注 |
| 10 | 散点图看不出趋势 | 点太密 | 叠分箱中位数黑粗线 |
| 11 | 流程图箭头歪斜 | 汇总框宽度 ≠ 阵列总宽 | `minimum width=n·w+(n−1)·gap` + `calc` 居中 + `\foreach` |
| 12 | 流程图箭头标签压框 | 标签比间隙宽 | 缩短到 ≤4 字或加大间隙 |
| 13 | LaTeX 行内长公式冲出版心 | 无法断行 | 改独立编号公式 + `\emergencystretch` |
| 14 | 表格超出边界 | 列过宽 | `p{}` 定宽 / `\hspace{0pt}` 断行点 / 表头 `\newline` / `\small` |
| 15 | 正文超页数 | 图多 | 按 §6.4 顺序压缩，**最后才减图** |
| 16 | 编码：`truncated \uXXXX escape` | docstring 里有 `\u` | docstring 前缀 `r"""` |
| 17 | 编码：`Circle() takes 2-3 args` | 坐标要传元组 | `Circle((x, y), r, ...)` |
| 18 | 编码：`unsupported format character` | 中文标签里裸 `%` | 写 `%%` |
| 19 | `UserWarning: Axes not compatible with tight_layout` | gridspec + `fig.legend` | 只用 `subplots_adjust` |
| 20 | **编译后 PDF 没更新（静默失败）** | PDF 被阅读器占用 | 关阅读器；或 `-jobname=paper_new` 后复制替换，**并检查时间戳** |

---

# 第九部分　标准工作流

```
① 定字号 + 显示宽度 → 反算画布上限（§1.2）
② 画图：全局 rcParams + 图例一律外置 + 所有文字标注外移
③ 生成 → read_image 逐张目视
④ 跑 audit_figures.py，<9 pt 的回炉缩画布
⑤ 缩画布后**必须重新目视**（相对字号变大，标签会新碰撞）
⑥ 同步更新图注（描述图内布局的话必须改）
⑦ 编译 → grep Overfull → 逐条修 → 渲染 PDF 页面复核
⑧ 30 页联系表整体扫一遍
```

---

# 附　本次项目终检数据

| 指标 | 结果 |
|---|---|
| 插图数量 | 22 张（论文正文全部引用） |
| 等效字号 | **22/22 ≥ 9.1 pt**（9.1 ~ 12.8 pt）；修复前 12 张 <9 pt（最差 7.3） |
| 图例压数据 / 压轴标签 | 0 处 |
| inset 叠加小窗 | 0 处（全部改独立面板） |
| 面板标题越界 | 0 处 |
| 区内说明文字 | 0 处（全部移入图外图例或引线标注） |
| `Overfull \hbox` | **0**（修复前 8 处，最大 100.6 pt） |
| 正文页数 | 30 页（限制 30 页） |
| 双版本 | 电子版 79 页 / 纸质版 81 页 |

审计命令：`python code/audit_figures.py`
