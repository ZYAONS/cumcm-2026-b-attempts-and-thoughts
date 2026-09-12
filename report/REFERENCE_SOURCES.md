# 参考文献来源与核实报告

> 面向 2026 年全国大学生数学建模竞赛 B 题《无线电干扰源的快速自动定位与清除》。
> 本文件只收录**经过实际抓页面核实**的条目；无法核实的条目单列于第 K 节，并明确标注为「未核实」。
>
> **核实方法**：`web_search` 定位候选 → `web_fetch` 抓取**权威原始页面**（ITU 官方建议书页 / 全国标准信息公共服务平台 / 中国政府网 / 期刊官网 / Crossref REST API / CTAN / OpenLibrary / 高校图书馆 OPAC）→ 摘录页面上的原文证据。
> **置信度三级**：`verified`（题名、责任者、年卷期/标准号、DOI/ISBN/URL 均在权威页面直接见到）；`partially verified`（主体信息已核实，但个别字段如页码/ISBN 来自二次著录）；`unverified`（未能核实，不可引用）。

---

## A. 测向交会定位（AOA / 三角定位）的定位误差、误差椭圆与最优交会角

### A1. Torrieri 无源定位统计理论（误差椭圆、GDOP、CEP 的经典源头）

- **type**：journal paper
- **authors**：Torrieri, Don J.
- **exact title**：Statistical Theory of Passive Location Systems
- **year**：1984
- **venue / vol / issue / pages**：*IEEE Transactions on Aerospace and Electronic Systems*, vol. AES-20, no. 2, pp. 183–198
- **DOI**：10.1109/TAES.1984.310439
- **如何核实**：用 `pwsh` 调用 Crossref REST API（`https://api.crossref.org/works?query.bibliographic=Statistical+Theory+of+Passive+Location+Systems+Torrieri`），返回条目原文为：
  `TITLE : Statistical Theory of Passive Location Systems / AUTH : Torrieri Don / YEAR : 1984 / VENUE : IEEE Transactions on Aerospace and Electronic Systems / VOL/IS: AES-20 / 2 / 183-198 / DOI : 10.1109/taes.1984.310439 / TYPE: journal-article`
  （同一次检索还返回了 1990 年 *Autonomous Robot Vehicles* 转载版：DOI 10.1007/978-1-4613-8997-2_13, pp. 151–166。）
- **支撑论文中的哪句话**：支撑「测向交叉定位的定位误差可用误差椭圆 / 协方差矩阵描述，其大小由 GDOP（几何精度因子）与测向误差共同决定；GDOP 在交会角接近 90° 时最小」这一理论基础。
- **confidence**：**verified**

### A2. Stansfield 测向定位（DF fixing）统计理论——1947 年原始文献

- **type**：journal paper
- **authors**：Stansfield, R. G.
- **exact title**：Statistical theory of d.f. fixing
- **year**：1947
- **venue / vol / issue / pages**：*Journal of the Institution of Electrical Engineers – Part IIIA: Radiocommunication*, vol. 94, no. 15, pp. 762–770
- **DOI**：10.1049/ji-3a-2.1947.0096
- **如何核实**：Crossref REST API 查询 `Stansfield statistical theory of DF fixing`，返回原文：
  `TITLE : Statistical theory of d.f. fixing / AUTH : Stansfield R.G. / YEAR : 1947 / VENUE : Journal of the Institution of Electrical Engineers - Part IIIA: Radiocommunication / VOL/IS: 94 / 15 / 762-770 / DOI : 10.1049/ji-3a-2.1947.0096`
- **支撑论文中的哪句话**：支撑「多站测向交会定位（DF fixing）的最小二乘/加权最小二乘统计处理与定位误差分析自 1947 年即有经典处理」——用于说明交会定位问题的历史渊源与标准解法。
- **confidence**：**verified**

### A3. 中文核心：测向交叉定位系统中的交会角研究（交会角 / CEP / GDOP）

- **type**：journal paper
- **authors**：修建娟, 何友, 王国宏, 董云龙
- **exact title**：测向交叉定位系统中的交会角研究
- **year**：2005
- **venue / vol / issue / pages**：*宇航学报*, 第 26 卷第 3 期, 第 282–285 页（页码为二次著录，见下）
- **DOI / URL**：CNKI 记录页 `https://wap.cnki.net/qikan-YHXB200503008.html`；AiPub 记录页 `https://aipub.cn/1I7L2`
- **如何核实**：
  1. 抓取 `https://wap.cnki.net/qikan-YHXB200503008.html`，页面显示：题名「测向交叉定位系统中的交会角研究」、作者「修建娟,何友,王国宏,董云龙」、「《宇航学报 2005 年 03 期》」，关键词栏原文为「**测向交叉定位**;**交会角**;**圆概率误差**;**GDOP**」，摘要原文：「……推导出了定位精度达到最高的测向线交会角大小,得出了满足一定定位精度要求的交会角范围……」。
  2. 抓取 `https://aipub.cn/1I7L2`，页面显示「宇航学报 ISSN：1000-1328」「2005 年第 26 卷第 3 期」「论文」，英文摘要原文：「we … give the optimal cut angle of the whole detection area when the circular probable error is minimum … the GDOP distribution figure is also given」。
  3. 页码 282–285 来自《航空兵器》2019, 26(4): 47–53 一文参考文献 [5] 的著录（该文官网参考文献表原文：「[5] 修建娟, 何友, 王国宏, 等. 测向交叉定位系统中的交会角研究[J]. 宇航学报, 2005,26(3):282-285.」）。CNKI 与 AiPub 页面未显示页码，故页码标为二次来源。
- **支撑论文中的哪句话**：直接支撑「双站测向交会角的取值决定定位精度，存在使圆概率误差（CEP）最小的**最优交会角**，并给出满足精度要求的交会角区间；同时以 GDOP 分布图刻画整个探测区域的定位精度」——这是本论文第 2 问几何精度分析的核心依据。
- **confidence**：**verified**（题名、作者、刊名、年、卷、期、关键词、摘要均经两个独立权威页面核实）；**页码范围 282–285 为 partially verified**（二次著录）。

### A4. 中文核心：存在系统误差时的最优交会角

- **type**：journal paper
- **authors**：盛丹, 王国宏, 孙殿星
- **exact title**：存在系统误差下交叉定位系统最优交会角研究
- **year**：2016
- **venue / vol / issue / pages**：*系统工程与电子技术*, 第 38 卷第 7 期, 第 1516–1523 页
- **DOI**：10.3969/j.issn.1001-506X.2016.07.06 ；期刊官网链接 `https://www.sys-ele.com/CN/Y2016/V38/I7/1516`（该 URL 本身即含卷 38 / 期 7 / 页 1516）
- **如何核实**：抓取期刊官网摘要页 `https://www.sys-ele.com/CN/abstract/abstract2264.shtml`（即 `https://www.sys-ele.com/CN/10.3969/j.issn.1001-506X.2016.07.06`），页面标题与中文摘要原文：「**存在系统误差下交叉定位系统最优交会角研究**」「研究了存在系统误差下被动传感器测向交叉定位系统中的最优交会角问题。考虑实际应用中传感器不可避免地存在系统误差,传感器的测量误差设定为非零均值高斯分布,在不同的准则下,计算了两部传感器测量误差不同情况下的最优交会角……」；作者「盛丹, 王国宏, 孙殿星」，单位「海军航空工程学院信息融合研究所, 山东 烟台 264001」；引用格式栏原文：「盛丹, 王国宏, 孙殿星. 存在系统误差下交叉定位系统最优交会角研究[J]. 系统工程与电子技术, doi: 10.3969/j.issn.1001-506X.2016.07.06」；出版日期 2016-06-24。
- **支撑论文中的哪句话**：支撑「当两台测向设备存在不同测角精度/系统偏差时，最优交会角会偏离 90°，因此机器人狗在不同站位上应给出不同的权重，而不能一律按 90° 最优点处理」。
- **confidence**：**verified**

### A5. 中文期刊：机场终端区 GNSS 干扰源定位（测向交叉定位 + 误差分析 + 实测案例）

- **type**：journal paper
- **authors**：黄裕文, 李怡恒, 程擎, 陈超, 鲁合德
- **exact title**：机场终端区GNSS信号干扰源定位研究
- **year**：2023
- **venue / vol / issue / pages**：*现代雷达*, 2023 年第 12 期, 第 87–93 页（共 7 页）
- **DOI**：10.16592/j.cnki.1004-7859.2023.12.013
- **如何核实**：抓取国家科技期刊平台记录页 `https://coaa.istic.ac.cn/openJournal/periodicalArticle/0120240200435539`，原文可见：题名「机场终端区GNSS信号干扰源定位研究 / A Study on the Location of GNSS Signal Jamming Source in Airport Terminal Area」；标注「OA 北大核心 CSCD CSTPCD」；摘要原文「……在阐述了测向交叉定位原理的基础上建立三维空地协同交叉定位模型,对模型的定位误差进行分析与仿真……在 20 km 处定位误差下降 17.9％……以绵阳南郊机场无线电干扰源排查为契机……」；作者「黄裕文;李怡恒;程擎;陈超;鲁合德」；刊名「《现代雷达》2023 (12)」；页码/页数「87-93,7」；DOI 如上；中文关键词「电磁环境 干扰源 到达角度定位 自相关性」。
- **支撑论文中的哪句话**：支撑「测向交叉定位已被用于实际机场电磁环境中的无线电干扰源排查，且定位精度随距离急剧下降（本题中机器人狗必须靠近目标才能满足清除精度要求）」，并可作为「空地协同（无人机+地面站）」多平台交会的中文工程先例。
- **confidence**：**verified**

### A6. 中文期刊：基于测向交叉定位的协同攻击（交会角—距离—误差关系的工程算例）

- **type**：journal paper
- **authors**：钟建林, 刘方, 石章松, 邹强, 彭英武
- **exact title**：基于测向交叉定位的空舰导弹协同攻击方法
- **year**：2019
- **venue / vol / issue / pages**：*航空兵器*, 第 26 卷第 4 期, 第 47–53 页
- **DOI**：10.12132/ISSN.1673-5048.2019.0127
- **如何核实**：抓取期刊官网论文页 `https://www.aeroweaponry.avic.com/CN/Y2019/V26/I4/47`，页面显示「航空兵器 ›› 2019, Vol. 26 ›› Issue (4): 47-53. doi: 10.12132/ISSN.1673-5048.2019.0127」，作者「钟建林,刘方,石章松,邹强,彭英武」（海军工程大学兵器工程学院），摘要原文「……分析得出测向交会角,弹目距离,测向误差,目标散布椭圆参数和弹目运动参数之间的关系和实施有效攻击的限制条件……」。
- **支撑论文中的哪句话**：支撑「交会角、目标距离与测向误差三者共同决定定位/散布椭圆，可作为把交会角约束写进机器人狗路径规划约束条件的建模参照」。（注：该文参考文献表另提供了 A3 的页码著录。）
- **confidence**：**verified**

---

## B. ITU-R 建议书与 ITU 手册（频谱监测 / 测向误差定义）

### B1. ITU-R SM.854-3 —— 监测站测向与定位（**本次核实中最关键的一条**）

- **type**：standard（国际电信联盟无线电通信部门建议书）
- **issuing body**：ITU-R（国际电信联盟无线电通信部门）
- **exact title**：Direction finding and location determination at monitoring stations
- **year**：2011（SM.854-3, 09/2011）
- **standard number**：Recommendation ITU-R SM.854-3 (09/2011)
- **stable URL**：`https://www.itu.int/rec/R-REC-SM.854/en`
- **如何核实**：抓取 `https://www.itu.int/rec/R-REC-SM.854/en`，页面原文：「**SM.854: Direction finding and location determination at monitoring stations**」「**Recommendation SM.854**」「Approved in 2011-09」；版本表原文：「**SM.854-3 (09/2011)** | Direction finding and location determination at monitoring stations | In force **(Main)**」，并列出了被取代的 SM.854-2 (02/07)、SM.854-1 (02/03)、SM.854-0 (03/92) 三版。该页面为 ITU 官方建议书数据库页面（Updated: 2020-06-09）。
- **支撑论文中的哪句话**：支撑「监测站利用测向与定位确定干扰源位置是 ITU-R 推荐的规范化业务，其术语与流程可作为本文定位模型的外部规范依据」。
- **confidence**：**verified**

### B2. ITU-R SM.2060-0 —— 测向机精度测试程序（**注意：题名与常见误记不同**）

- **type**：standard（ITU-R 建议书）
- **issuing body**：ITU-R
- **exact title**：Test procedure for measuring direction finder accuracy
- **year**：2014（SM.2060-0, 11/2014）
- **standard number**：Recommendation ITU-R SM.2060-0 (11/2014)
- **stable URL**：`https://www.itu.int/rec/R-REC-SM.2060/en`
- **如何核实**：抓取 `https://www.itu.int/rec/R-REC-SM.2060/en`，页面原文：「**SM.2060: Test procedure for measuring direction finder accuracy**」「**Recommendation SM.2060**」「Approved in 2014-11」「Managed by R12-SG01」；版本表原文：「**SM.2060-0 (11/2014)** | Test procedure for measuring direction finder accuracy | In force **(Main)**」。
  **重要更正**：该建议书**不是**「Measured amplitude of a radio signal」，其内容是**测向机精度的测试程序**，恰好是本题所需。
  （补充：其 PDF 直链 `https://www.itu.int/dms_pubrec/itu-r/rec/sm/R-REC-SM.2060-0-201411-I!!PDF-E.pdf` 在本环境下 `web_fetch` 返回 **HTTP 406**，无法读取正文；**标准号、题名、批准日期、在版状态**均以上述官方页面为准。）
- **支撑论文中的哪句话**：支撑「便携式测向机的测向误差有标准化的测试程序与定义（因此本文的测角误差 ε 有规范量级依据，而非任意假设）」。
- **confidence**：**verified**（题名/编号/批准日期/状态在 ITU 官方页面直接确认）；**正文内容未读取**（PDF 无法抓取）。

### B3. ITU-R SM.1600-3 —— 数字信号技术识别

- **type**：standard（ITU-R 建议书）
- **issuing body**：ITU-R
- **exact title**：Technical identification of digital signals
- **year**：2017（SM.1600-3, 09/2017）
- **standard number**：Recommendation ITU-R SM.1600-3 (09/2017)
- **stable URL**：`https://www.itu.int/rec/R-REC-SM.1600/en`
- **如何核实**：抓取 `https://www.itu.int/rec/R-REC-SM.1600/en`，页面原文：「**SM.1600: Technical identification of digital signals**」「**Recommendation SM.1600**」「Approved in 2017-09」；版本表原文：「**SM.1600-3 (09/2017)** | Technical identification of digital signals | In force **(Main)**」，并列明 SM.1600-2 (08/2015)、SM.1600-1 (09/2012)、SM.1600-0 (11/02) 均为 Superseded。
- **支撑论文中的哪句话**：支撑「在定位前的信号确认阶段，可依据 ITU-R 建议按频谱特征对数字信号做技术识别，用于区分干扰源与合法信号」（若论文含信号识别/确认环节则引用；不含则可不引）。
- **confidence**：**verified**

### B4. ITU-R Report SM.2211-0 —— TDOA 与 AOA 定位方法对比

- **type**：standard（ITU-R **报告**，非建议书）
- **issuing body**：ITU-R
- **exact title**：Comparison of Time-Difference-of-Arrival and Angle-of-Arrival Methods of signal geolocation
- **year**：2011（SM.2211-0, 06/2011）
- **standard number**：Report ITU-R SM.2211-0 (06/2011)
- **stable URL**：`https://www.itu.int/pub/R-REP-SM.2211-2011`（PDF：`https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-SM.2211-2011-PDF-E.pdf`，另有中文版 `R-REP-SM.2211-2011-PDF-C.pdf`）
- **如何核实**：抓取 `https://www.itu.int/pub/R-REP-SM.2211-2011`，页面原文：标题「Comparison of Time-Difference-of-Arrival and Angle-of-Arrival Methods of signal geolocation」；「**Report SM.2211-0 (06/2011)**」「Approved in 2011-06」「Status : Superseded」；语言格式表中列出 ENGLISH / CHINESE 等 PDF 直链与 Article Number E 70000 / C 70000。
  **注意**：该 **2011 版已被取代（Superseded）**，2018 年有 SM.2211-2 版。若论文引用，建议同时注明「已由后续版本取代」或改引最新版。
  另：`https://www.itu.int/rec/R-REC-SM.2211/en`（试图按"建议书"访问）返回**空页面**，证实 SM.2211 是 **Report** 而非 Recommendation。
- **支撑论文中的哪句话**：支撑「在 AOA（测向交会）与 TDOA 两类干扰源定位体制之间做选择时，有 ITU-R 的官方对比报告；本题采用单机测向（AOA）方案的理由可据此对比论证」。
- **confidence**：**verified**（题名、编号、批准时间、状态、直链均在 ITU 官方页面确认）

### B5. ITU Handbook on Spectrum Monitoring（2011 年版）

- **type**：book（ITU-R 手册）
- **issuing body**：ITU-R（国际电信联盟无线电通信部门）
- **exact title**：Spectrum Monitoring（Handbook on Spectrum Monitoring）
- **year**：2011
- **venue / identifier**：ITU-R Handbook, 出版物编号 **R-HDB-23-2011**；**Persistent link: `http://handle.itu.int/11.1002/pub/80399e8b-en`**
- **stable URL**：`https://www.itu.int/en/publications/ITU-R/pages/publications.aspx?media=electronic&parent=R-HDB-23-2011`
  PDF 直链（英文）：`https://www.itu.int/dms_pub/itu-r/opb/hdb/R-HDB-23-2011-PDF-E.pdf`；**中文版 PDF：`https://www.itu.int/dms_pub/itu-r/opb/hdb/R-HDB-23-2011-PDF-C.pdf`**
- **如何核实**：抓取上述 ITU 官方出版页面，页面原文：「**Spectrum Monitoring**」「Year: 2011」「**Persistent link: http://handle.itu.int/11.1002/pub/80399e8b-en**」「The Handbook on Spectrum Monitoring contains the latest information on all aspects of monitoring and represents a valuable reference manual for the spectrum management community.」；物品明细表中列出 ENGLISH / ARABIC / **CHINESE** / SPANISH / FRENCH / RUSSIAN 各语种 ZIP 与 PDF 直链，均标注「Free of charge」。
- **支撑论文中的哪句话**：支撑「测向误差来源（多径、场地误差、极化误差、仪器误差）与监测系统的规范化定义以 ITU 手册为准，本文对测向误差建模时的误差项分解参照该手册」。
- **confidence**：**verified**（题名、年份、持久链接、语种与直链均确认）；**手册正文未读取**（PDF 体积/类型限制），如需引用具体页码请在论文中另行核对。

---

## C. 中国国家标准 / 行业标准 / 行政法规

### C1. 《中华人民共和国无线电管理条例》（2016 年修订）

- **type**：standard（行政法规）
- **issuing body**：国务院、中央军事委员会
- **exact title**：中华人民共和国无线电管理条例
- **year**：2016（1993 年 9 月 11 日国务院、中央军委令第 128 号发布；**2016 年 11 月 11 日国务院、中央军委令第 672 号修订**；2016 年 12 月 1 日起施行）
- **identifier**：国令第 672 号；索引号 000014349/2016-00227
- **stable URL**：`https://www.gov.cn/zhengce/content/2016-11/25/content_5137687.htm`
- **如何核实**：抓取中国政府网该页面，页首信息栏原文：「**发文机关：国务院、中央军委**」「**成文日期：2016 年 11 月 11 日**」「**标　　题：中华人民共和国无线电管理条例**」「**发文字号：国令第 672 号**」「**发布日期：2016 年 11 月 25 日**」；正文原文：「（1993年9月11日中华人民共和国国务院、中华人民共和国中央军事委员会令第128号发布　2016年11月11日中华人民共和国国务院、中华人民共和国中央军事委员会令第672号修订）」「第八十五条　本条例自2016年12月1日起施行。」
- **支撑论文中的哪句话**：**第五十七条**原文「国家无线电监测中心和省、自治区、直辖市无线电监测站作为无线电管理技术机构……**对无线电信号实施监测，查找无线电干扰源和未经许可设置、使用的无线电台（站）**。」—— 直接支撑「快速自动定位并清除无线电干扰源」这一任务的合法性与现实需求背景。
- **confidence**：**verified**

### C2. GB/T 34089-2017 —— VHF/UHF 无线电监测测向系统开场测试参数和测试方法（**首选中国国家标准**）

- **type**：standard（推荐性国家标准）
- **issuing body**：中华人民共和国国家质量监督检验检疫总局、中国国家标准化管理委员会（主管部门：工业和信息化部（通信））
- **exact title**：VHF/UHF无线电监测测向系统开场测试参数和测试方法
- **英文名**：Test parameters and test methods for VHF/UHF frequency band radio monitoring and direction finding system in OATS
- **year**：2017（发布日期 2017-07-31；实施日期 2017-11-01；状态：**现行**）
- **standard number**：GB/T 34089-2017；CCS M36；ICS 33.060
- **stable URL（全国标准信息公共服务平台）**：`https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=83AC10AFA7DFEFDD46DA83F1D6021730`
- **如何核实**：抓取该官方标准详情页，页面原文：「标准号：**GB/T 34089-2017**」「中文标准名称：**VHF/UHF无线电监测测向系统开场测试参数和测试方法**」「英文标准名称：**Test parameters and test methods for VHF/UHF frequency band radio monitoring and direction finding system in OATS**」「标准状态： **现行**」「中国标准分类号（CCS） M36」「国际标准分类号（ICS） 33.060」「发布日期 2017-07-31」「实施日期 2017-11-01」「主管部门 工业和信息化部（通信）」。第二处独立核实：`https://www.spc.org.cn` 关联标准列表中出现同名条目。
- **支撑论文中的哪句话**：支撑「VHF/UHF 频段无线电监测测向系统的测向精度等参数有国标规定的开场（OATS）测试方法与指标口径，本文的测向误差取值与精度评估口径据此设定」。
- **confidence**：**verified**

### C3. YD/T 3730-2020 —— VHF/UHF 无线电测向系统多径传播抗扰度测试程序（**最贴合本题的行业标准**）

- **type**：standard（通信行业标准，推荐性，现行）
- **issuing body**：工业和信息化部；归口单位：中国通信标准化协会；主要起草单位：**国家无线电监测中心检测中心、国家无线电监测中心**
- **exact title**：VHF/UHF无线电测向系统多径传播抗扰度测试程序
- **year**：2020（发布日期 2020-08-31；实施日期 2020-10-01）
- **standard number**：YD/T 3730-2020；CCS M36；ICS 33.060；备案号 75953-2020
- **stable URL**：`https://std.samr.gov.cn/hb/search/stdHBDetailed?id=AFC9FE3F29BCB96EE05397BE0A0AFF12`
- **如何核实**：抓取全国标准信息公共服务平台行业标准详情页，页面原文：「**VHF/UHF无线电测向系统多径传播抗扰度测试程序**」「行业标准-YD 通信 推荐性 **现行**」「标准号 **YD/T 3730-2020**」「发布日期 2020-08-31」「实施日期 2020-10-01」「**适用范围** 本标准适用于VHF/UHF频段内无线电测向系统，包括**移动式**、可搬移式和固定式无线电测向系统等。」「主要起草单位 **国家无线电监测中心检测中心** 、国家无线电监测中心」「主要起草人 王敬焘 、刘恩亚 、王刚」。
- **支撑论文中的哪句话**：支撑「机器人狗搭载的是**移动式可搬移测向系统**，其在城市/机场复杂环境下的多径效应是主要误差源，而国家已有针对该类测向系统多径抗扰度的标准测试程序——本文把多径列为测向误差主项有标准依据」。
- **confidence**：**verified**

### C4. GB 13614-2012 —— 短波无线电收信台(站)及测向台(站)电磁环境要求

- **type**：standard（强制性国家标准，现行）
- **issuing body**：国家质量监督检验检疫总局 / 中国国家标准化管理委员会；发布单位：工业和信息化部
- **exact title**：短波无线电收信台(站)及测向台(站)电磁环境要求
- **year**：2012（发布日期 2012-06-29；实施日期 2013-04-01；状态：现行）
- **standard number**：GB 13614-2012；ICS 33.100；中图分类号 L06
- **stable URL**：`http://www.analysis.org.cn/standards/details/157218`（中国工程科技知识中心·试验技术专业知识服务系统）；另一独立来源：工标网 `http://www1.csres.com/s.jsp?keyword=无线电测向`
- **如何核实**：
  1. 抓取 analysis.org.cn 标准详情页，原文：「**短波无线电收信台(站)及测向台(站)电磁环境要求**」「标准编号 **GB 13614-2012**」「发布单位 工业和信息化部」「状态 **现行**」「标准类别 国家标准」「发布日期 2012-06-29」「实施日期 2013-04-01」「摘要 本标准规定了短波无线电收信台(站)和无线电测向台(站)的电磁环境要求,并明确了短波无线电收信台(站)和无线电测向台(站)对无线电发射台和产生电磁辐射干扰设施的保护要求。本标准适用于频率为 1.5MHz~30MHz 的固定无线电集中收信台(站)和固定无线电测向台。」
  2. 工标网「无线电测向」检索结果页共 11 条，其中原文列出：「GB 13614-1992 | 短波无线电测向台(站)电磁环境要求 | 国家技术监督局 | 1993-09-01 | **作废**」与「**GB 13614-2012** | 短波无线电收信台(站)及测向台(站)电磁环境要求 | 国家质量监督检验检疫. | 2013-04-01 | **现行**」。
- **支撑论文中的哪句话**：支撑「测向台（站）对周围电磁环境有法定的保护要求，反过来说明强电磁环境会反过来影响测向精度」——可作为「干扰源所在电磁环境复杂度」这一建模因素的规范依据（若论文涉短波频段；若只做 VHF/UHF 则可放弱引用或不引）。
- **confidence**：**verified**

### C5. GB/T 25003-2010 —— VHF/UHF 频段无线电监测站电磁环境保护要求和测试方法

- **type**：standard（推荐性国家标准，现行）
- **issuing body**：国家标准委；归口单位：TC79 全国无线电干扰标准化技术委员会；主要起草单位：国家无线电监测中心
- **exact title**：VHF/UHF频段无线电监测站电磁环境保护要求和测试方法
- **英文名**：Electromagnetic environment protection requirements and measurement methods for VHF/UHF band radio monitoring station
- **year**：2010（发布日期 2010-08-09；实施日期 2010-12-01；上次复审 2022-01-04，复审结论「修订」）
- **standard number**：GB/T 25003-2010；CCS L06；ICS 33.100
- **stable URL**：`https://std.samr.gov.cn/gb/search/gbDetailed?id=71F772D7D675D3A7E05397BE0A0AB82A`
- **如何核实**：抓取全国标准信息公共服务平台国家标准详情页，原文：「**VHF/UHF频段无线电监测站电磁环境保护要求和测试方法**」「国家标准 推荐性 **现行**」「标准号 **GB/T 25003-2010**」「发布日期 2010-08-09」「实施日期 2010-12-01」「归口单位 全国无线电干扰标准化技术委员会」「主要起草单位 国家无线电监测中心」「主要起草人 周鸿顺 、戴晓放 、沈国勤 、崔晓曼」。
- **支撑论文中的哪句话**：支撑「VHF/UHF 频段监测站的电磁环境保护与测试有国标，可作为本文中监测/测向环境条件与误差影响讨论的规范引用」。
- **confidence**：**verified**

### C6. GB/T 32401-2015 —— VHF/UHF 频段无线电监测接收机技术要求及测试方法

- **type**：standard（推荐性国家标准，现行）
- **issuing body**：中华人民共和国国家质量监督检验检疫总局、中国国家标准化管理委员会；提出部门：工业和信息化部；起草单位：国家无线电监测中心
- **exact title**：VHF/UHF频段无线电监测接收机技术要求及测试方法
- **英文名**：Technical requirements and measurement methods for VHF/UHF frequency band radio monitoring receiver
- **year**：2015（发布日期 2015-12-31；实施日期 2016-07-01；状态：现行）
- **standard number**：GB/T 32401-2015；ICS 33.060；中标分类号 M36
- **stable URL**：`https://www.spc.org.cn/online/57e36b43815d4550201681814ae57158.html`（中国标准在线服务网）
- **如何核实**：抓取中国标准在线服务网详情页，原文：「【国家标准】**VHF/UHF频段无线电监测接收机技术要求及测试方法**」「**GB/T 32401-2015**」「**现行**」「英文名称: Technical requirements and measurement methods for VHF/UHF frequency band radio monitoring receiver」「发布日期: 2015-12-31」「实施日期: 2016-07-01」「适用范围：本标准规定了 VHF/UHF 频段无线电监测接收机通用要求，以及电性能、电磁兼容、电气安全和环境适应性的主要技术参数、指标要求和测试方法等内容。」「起草单位：国家无线电监测中心」。
- **支撑论文中的哪句话**：支撑「便携式接收/测向设备的灵敏度、频率稳定度等指标有国标口径，本文在讨论可探测半径/信噪比门限时的参数取值可据此规范化」。
- **confidence**：**verified**

---

## D. 搜索理论（Search Theory）

### D1. Koopman《Search and Screening》

- **type**：book（含 1946 年原始报告版）
- **authors**：Koopman, Bernard Osgood
- **exact title**：Search and Screening（1980 年版全名：Search and Screening: General Principles with Historical Applications）
- **year**：1946（原始版，Operations Evaluation Group / OEG Report）；**1980**（Pergamon Press 出版版）
- **venue / identifier**：1946 年版出版者：Operations Evaluation Group, Office of the Chief of Naval Operations, Navy Dept. / Military Operations Research Society；1980 年版出版者：**Pergamon Press**，ISBN **0080231357** / **0080231365**（亦记作 9780080231358 / 9780080231365）；1946 年版另有 ISBN 0930473086 (9780930473082)
- **stable URL**：`https://openlibrary.org/works/OL6563317W`（1980 版）；`https://openlibrary.org/works/OL17646127W`（1946 版）
- **如何核实**：调用 OpenLibrary 检索 API `https://openlibrary.org/search.json?q=Search+and+Screening+Koopman&fields=title,author_name,first_publish_year,publisher,isbn,key`，返回原文：
  `TITLE: Search and screening / AUTH : Bernard Osgood Koopman / YEAR : 1980 / PUB : Pergamon Press / ISBN : 0080231357, 9780080231358, 0080231365, 9780080231365 / KEY : /works/OL6563317W`
  以及 `TITLE: Search and screening / AUTH : Bernard Osgood Koopman / YEAR : 1946 / PUB : Military Operations Research Society | Operations Evaluation Group, Office of the Chief of Naval Operations, Navy Dept. / ISBN : 0930473086, 9780930473082 / KEY : /works/OL17646127W`。
- **支撑论文中的哪句话**：支撑「搜索—探测问题的建模（探测函数 / 发现概率、扫描宽度、搜索力分配）以 Koopman 创立的理论为基础；本文机器人狗以探测半径 r 做扫掠式搜索的发现概率模型可追溯至此」。
- **confidence**：**verified**（题名、作者、年份、出版者、ISBN 均在 OpenLibrary 结构化记录中确认）；具体版次的 ISBN 略有歧义（同一作品下并列多个 ISBN），引用时请以手边实物为准。

### D2. Stone《Theory of Optimal Search》

- **type**：book
- **authors**：Stone, Lawrence D.
- **exact title**：Theory of Optimal Search
- **year**：1975（另有 1992/2004 年 INFORMS 重印版）
- **venue / identifier**：丛书 **Mathematics in Science and Engineering, Vol. 118**；出版者 **Academic Press**；ISBN **0126724504**（9780126724509）；INFORMS 版 ISBN **1877640034**（9781877640032）
- **DOI / URL**：Crossref 记录有该书的 Preface 章节 DOI **10.1016/S0076-5392(08)60541-X**（著录为 *Mathematics in Science and Engineering | Theory of Optimal Search*, 1975, pp. xi–xii）；OpenLibrary 作品页 `https://openlibrary.org/works/OL4807530W`
- **如何核实**：
  1. Crossref REST API 查询 `Theory of Optimal Search Stone`，返回原文：`TITLE : Preface / AUTH : Stone Lawrence D. / YEAR : 1975 / VENUE : Mathematics in Science and Engineering | Theory of Optimal Search / VOL/IS: / / xi-xii / DOI : 10.1016/s0076-5392(08)60541-x / TYPE: book-chapter` —— 证实 **1975 年、Academic Press 的 Mathematics in Science and Engineering 丛书中的《Theory of Optimal Search》确实存在**。
  2. 同一次检索还返回两篇该书的**书评**，进一步佐证：`Theory of Optimal Search (Lawrence D. Stone) / AUTH : Koopman Bernard O. / YEAR : 1977 / VENUE : SIAM Review / VOL/IS: 19 / 2 / 361-364 / DOI : 10.1137/1019060`，以及 `Theory of Optimal Search. / AUTH : Mickelsen Richard; Stone Lawrence D. / YEAR : 1976 / VENUE : Journal of the American Statistical Association / VOL/IS: 71 / 356 / 1008 / DOI : 10.2307/2286890`。
  3. OpenLibrary：`TITLE: Theory of optimal search / AUTH : Lawrence D. Stone / YEAR : 1975 / PUB : Academic Press … / ISBN : 0126724504, 187764000X, 9781877640001, 9780126724509`。
- **支撑论文中的哪句话**：支撑「最优搜索力分配（对离散/连续先验分布的最优搜索计划）理论；本文在已知干扰源先验概率分布时用最优搜索策略而非均匀扫掠的合理性依据」。
- **confidence**：**verified**

### D3. Stone, Royset & Washburn《Optimal Search for Moving Targets》（现代权威续作）

- **type**：book
- **authors**：Stone, Lawrence D.; Royset, Johannes O.; Washburn, Alan R.
- **exact title**：Optimal Search for Moving Targets
- **year**：2016
- **venue / identifier**：丛书 **International Series in Operations Research & Management Science**；出版者 Springer；ISBN **9783319268996**（亦 9783319268972）
- **DOI**：**10.1007/978-3-319-26899-6**
- **如何核实**：Crossref REST API 查询 `Optimal Search for Moving Targets Royset Washburn`，返回原文：`TITLE : Optimal Search for Moving Targets / AUTH : Stone Lawrence D.; Royset Johannes O.; Washburn Alan R. / YEAR : 2016 / VENUE : International Series in Operations Research & Management Science / DOI : 10.1007/978-3-319-26899-6 / TYPE : book / ISBN 9783319268972,9783319268996`（同时返回其第 1、5、7 章 DOI，均为同一前缀）。OpenLibrary 亦确认：`TITLE: Optimal Search for Moving Targets / AUTH : Lawrence D. Stone; Johannes O. Royset; Alan R. Washburn / YEAR : 2016 / PUB : Springer`。
- **支撑论文中的哪句话**：支撑「当干扰源可能移动时（本题中干扰源固定，但机器人狗观测过程动态），可采用移动目标最优搜索的最新框架刻画搜索—发现过程」，作为 D1/D2 的现代参照。
- **confidence**：**verified**

### D4. 中文搜索理论教材：《实用搜索理论》

- **type**：book
- **authors**：陈建勇
- **exact title**：实用搜索理论
- **year**：2021
- **venue / identifier**：北京：**国防工业出版社**，2021，x+185 页，24cm；ISBN **978-7-118-12327-2**（定价 CNY 98.00）；中图分类号 **O229**（搜索论）
- **stable URL**：`https://jp.tfswufe.edu.cn/opac/book/10dbbc3ed67e1a566ffe7d1aca400099`（高校图书馆 OPAC 书目记录）
- **如何核实**：抓取图书馆 OPAC 书目详情页，原文：「**实用搜索理论**」「ISBN/价格： **978-7-118-12327-2**:CNY98.00」「题名责任者项： 实用搜索理论/.**陈建勇著**」「出版发行项： 北京:, **国防工业出版社**,: **2021**」「载体形态项： x, 185页:;+图:;+24cm」「提要文摘： 本书系统介绍了搜索理论的**基础知识、建模方法和最优搜索理论**, 并讨论了军事应用的有关问题。全书分为四篇。第一篇为概述与基础, 共7章, 论述了搜索理论的基本问题和主要构成要素; 第二篇为搜索模型……第三篇为最优搜索理论……」「题名主题： 搜索论 研究」「中图分类： **O229**」。
- **支撑论文中的哪句话**：支撑「本文用于搜索路径规划的搜索论方法有中文权威教材支撑（便于中文论文的术语统一与公式引用）」。
- **confidence**：**verified**

---

## E. 覆盖问题：用等半径圆覆盖一个圆盘（最少圆数）

### E1. Kershner 1939 —— 覆盖圆盘所需圆数（**经典源头**）

- **type**：journal paper
- **authors**：Kershner, Richard
- **exact title**：The Number of Circles Covering a Set
- **year**：1939
- **venue / vol / issue / pages**：*American Journal of Mathematics*, vol. 61, no. 3, pp. **665–671**
- **DOI**：**10.2307/2371320**
- **stable URL**：`https://doi.org/10.2307/2371320`（JSTOR: `https://www.jstor.org/stable/2371320`）
- **如何核实**：
  1. Crossref REST API 单条记录查询 `https://api.crossref.org/works/10.2307/2371320`，返回原文：`The Number of Circles Covering a Set / vol 61 issue 3 page 665 year 1939 venue American Journal of Mathematics`。
  2. 页码**结束页 671** 由 Eric W. Weisstein《CRC Concise Encyclopedia of Mathematics》词条「Disk Covering Problem」的参考文献表确认（抓取 `https://archive.lib.msu.edu/crcmath/math/math/d/d314.htm`），原文：「**Kershner, R. \`\`The Number of Circles Covering a Set.'' _Amer. J. Math._ **61**, 665-671, 1939.**」
- **支撑论文中的哪句话**：支撑「用有限个等半径圆（探测圆盘）覆盖给定区域所需的最少圆数有经典结果；同时该词条给出覆盖密度极限」。**同页还给出了一个可直接引用的关键公式**（原文）：
  「Letting N(ε) be the smallest number of Disks of Radius ε needed to cover a disk D, the limit of the ratio of the Area of D to the Area of the disks is given by  lim_{ε→0+} 1/(ε²N(ε)) = 3√3/(2π)  (**Kershner 1939**, Verblunsky 1949).」
  即六边形格（蜂窝）覆盖密度 = 2π/(3√3) ≈ 1.2092 —— 这正是本文「机器人狗以探测半径 r 覆盖圆形干扰源区域所需最少站点数 N ≥ 面积比 × 1.2092」这一估计式的依据。
- **confidence**：**verified**

### E2. Fejes Tóth —— 用 8、9、10 个等圆最薄覆盖一个圆

- **type**：book chapter（会议论文集论文）
- **authors**：Fejes Tóth, Gábor
- **exact title**：Thinnest Covering of a Circle by Eight, Nine, or Ten Congruent Circles
- **year**：2005（Cambridge 版权页亦有 2007 年标注）
- **venue / pages**：收录于 *Combinatorial and Computational Geometry*（MSRI Publications, Vol. 52；编者 Jacob E. Goodman, János Pach, Emo Welzl），pp. **361–376**；出版社 Cambridge University Press / MSRI
- **DOI / ISBN**：DOI **10.1017/9781009701259.019**；书 ISBN **0-521-84862-8**
- **stable URL**：Dialnet 记录 `https://documat.unirioja.es/servlet/articulo?codigo=3273510`；开放 PDF `https://library.slmath.org/books/Book52/files/18fejes.pdf`
- **如何核实**：
  1. Crossref 查询 `Kershner the number of circles covering a circle` 时返回该条：`TITLE : Thinnest Covering of a Circle by Eight, Nine, or Ten Congruent Circles / AUTH : Tóth Gábor Fejes / VENUE : Combinatorial and Computational Geometry / pp 361-376 / DOI : 10.1017/9781009701259.019`。
  2. Dialnet 页面 `https://documat.unirioja.es/servlet/articulo?codigo=3273510` 原文：「**Thinnest Covering of a Circle by Eight, Nine, or Ten Congruent Circles**」「Autores: **Gábor Fejes Tóth**」「Localización: Combinatorial and Computational Geometry / coord. por Jacob E. Goodman, János Pach, Emo Welzl, **2007, ISBN 0-521-84862-8, págs. 361-376**」。
- **支撑论文中的哪句话**：支撑「用少量（n≤10）等半径圆覆盖一个圆盘的最优半径 r(n) 已有严格结果；当机器人狗探测圈数较少（小规模场景）时，可直接查用 r(n) 的精确值而不是只做渐近估计」。
- **confidence**：**verified**（题名、作者、载体、页码、ISBN、DOI 均确认）；**出版年存在 2005/2007 两种标注**（MSRI 卷 52 与 Cambridge 版权页），标为 partially verified 仅在"年份"这一字段上。

### E3. Verblunsky 1949 —— 用最少单位圆覆盖一个正方形

- **type**：journal paper
- **authors**：Verblunsky, S.
- **exact title**：On the Least Number of Unit Circles Which Can Cover a Square
- **year**：1949
- **venue / vol / issue / pages**：*Journal of the London Mathematical Society*, vol. **s1-24**, no. **3**, pp. **164–170**
- **DOI**：**10.1112/jlms/s1-24.3.164**
- **如何核实**：
  1. **首次仅由 E4（Weisstein 词条）的参考文献表著录**：「Verblunsky, S. \`\`On the Least Number of Unit Circles which Can Cover a Square.'' _J. London Math. Soc._ **24**, 164-170, 1949.」
  2. **后续通过 Crossref 检索独立核实成功**，返回原文：`On the Least Number of Unit Circles Which Can Cover a Square || Verblunsky S. || 1949 || Journal of the London Mathematical Society || vol s1-24 iss 3 pp 164-170 || 10.1112/jlms/s1-24.3.164 || journal-article`
     —— 与二次著录的卷、页完全一致（卷号规范写法为 `s1-24`）。
- **支撑论文中的哪句话**：与 E1 共同支撑覆盖密度极限 lim 1/(ε²N(ε)) = 3√3/(2π)；用于「以探测半径 r 覆盖面积 S 的圆形区域所需最少探测位置数约为 1.2092·S/(πr²)」这一估计。
- **confidence**：**verified**

### E4. 覆盖密度常数 3√3/(2π) 的独立佐证

- **type**：web page（数学百科词条）
- **authors**：Weisstein, Eric W.
- **exact title**：Disk Covering Problem（收录于 *CRC Concise Encyclopedia of Mathematics*）
- **year**：词条页面标注「© 1996-9 Eric W. Weisstein, 1999-05-24」
- **venue / URL**：`https://archive.lib.msu.edu/crcmath/math/math/d/d314.htm`（Michigan State University 镜像）
- **如何核实**：同上，抓取该页面获知原文公式与参考文献；页面同时给出 r(5)=0.609382864…、r(7)=1/2、r(8)=0.437、r(9)=0.422、r(10)=0.398 等数值（其中 n=6,8,9,10 系 Zahn 1962 的计算机实验值）。
- **支撑论文中的哪句话**：支撑「蜂窝格是渐近最优覆盖方式，覆盖密度 2π/(3√3)≈1.2092；因此以探测半径 r 覆盖面积 S 的圆形区域所需最少探测位置数约为 1.2092·S/(πr²)」这一量化估计。
- **confidence**：**verified**（页面内容直接读到）；若正式投稿建议改引 E1 原始论文。

### E5. Gáspár, Tarnai & Hincz —— 用 6 个与 7 个全等圆部分覆盖一个圆（**现代开放获取期刊文献**）

- **type**：journal paper
- **authors**：Gáspár, Zsolt; Tarnai, Tibor; Hincz, Krisztián
- **exact title**：Partial Covering of a Circle by 6 and 7 Congruent Circles
- **year**：2021
- **venue / vol / issue / pages**：*Symmetry*, vol. **13**, no. **11**, article no. **2133**
- **DOI**：**10.3390/sym13112133**
- **如何核实**：Crossref REST API 查询 `covering a region with congruent circles survey circle covering problem`，返回原文：`TITLE : Partial Covering of a Circle by 6 and 7 Congruent Circles / AUTH : Gáspár Zsolt; Tarnai Tibor; Hincz Krisztián / YEAR : 2021 / VENUE : Symmetry / vol 13 iss 11 pp 2133 / DOI : 10.3390/sym13112133 / TYPE : journal-article`。
- **支撑论文中的哪句话**：支撑「用少量全等圆覆盖圆形区域的最优构形仍在被持续研究（2021 年仍有新结果），说明本文把'最少探测圈数覆盖干扰源区域'作为优化子问题是有活跃文献支撑的、而非生造问题」；同时 MDPI 的 *Symmetry* 为开放获取，便于评审核查。
- **confidence**：**verified**

### E6. Hearn —— 圆覆盖问题（单设施选址视角的条目）

- **type**：book chapter（百科条目）
- **authors**：Hearn, Donald W.
- **exact title**：Single Facility Location: Circle Covering Problem
- **year**：2001
- **venue / pages**：收录于 *Encyclopedia of Optimization*, pp. **2398–2401**；出版社 Kluwer/Springer
- **DOI**：**10.1007/0-306-48332-7_472**
- **如何核实**：Crossref 同一次检索返回原文：`TITLE : Single Facility Location: Circle Covering Problem / AUTH : Hearn Donald W. / YEAR : 2001 / VENUE : Encyclopedia of Optimization / pp 2398-2401 / DOI : 10.1007/0-306-48332-7_472 / TYPE : book-chapter`。同次检索还返回相关的百科条目 `Single Facility Location: Circle Covering Problem, Sylvester's Problem / VENUE : SpringerReference / DOI : 10.1007/springerreference_72698`。
- **支撑论文中的哪句话**：支撑「用给定半径的圆覆盖点集/区域，等价于一类单设施选址问题；因此本文的'最少探测位置数'子问题可归入运筹学中成熟的圆覆盖/选址模型，便于引用标准算法」。
- **confidence**：**verified**

---

## F. 覆盖路径规划（Coverage Path Planning）

### F1. Choset 覆盖机器人综述

- **type**：journal paper
- **authors**：Choset, Howie
- **exact title**：Coverage for robotics – A survey of recent results
- **year**：2001
- **venue / vol / issue / pages**：*Annals of Mathematics and Artificial Intelligence*, vol. 31, no. 1–4, pp. 113–126
- **DOI**：**10.1023/A:1016639210559**
- **如何核实**：Crossref REST API 查询 `Choset Coverage for robotics a survey of recent results`，返回原文：`TITLE : Coverage for robotics – A survey of recent results / AUTH : Choset Howie / YEAR : 2001 / VENUE : Annals of Mathematics and Artificial Intelligence / vol 31 iss 1-4 pp 113-126 / DOI : 10.1023/a:1016639210559 / TYPE : journal-article`。另：CMU 机器人研究所出版物页 `https://www.ri.cmu.edu/publications/coverage-for-robotics-a-survey-of-recent-results/` 亦收录该题名。
- **支撑论文中的哪句话**：支撑「全覆盖路径规划（CPP）的经典分类（随机式/基于栅格的牛耕式 boustrophedon 分解等）；本文机器人狗在干扰源区域内做「覆盖搜索 + 测向确认」的路径形态属于 CPP 问题」。
- **confidence**：**verified**

### F2. Galceran & Carreras 覆盖路径规划综述（较新、更工程化）

- **type**：journal paper
- **authors**：Galceran, Enric; Carreras, Marc
- **exact title**：A survey on coverage path planning for robotics
- **year**：2013
- **venue / vol / issue / pages**：*Robotics and Autonomous Systems*, vol. 61, no. 12, pp. 1258–1276
- **DOI**：**10.1016/j.robot.2013.09.004**
- **如何核实**：Crossref REST API 查询 `Galceran Carreras survey on coverage path planning for robotics`，返回原文：`TITLE : A survey on coverage path planning for robotics / AUTH : Galceran Enric; Carreras Marc / YEAR : 2013 / VENUE : Robotics and Autonomous Systems / vol 61 iss 12 pp 1258-1276 / DOI : 10.1016/j.robot.2013.09.004 / TYPE : journal-article`。
- **支撑论文中的哪句话**：支撑「覆盖路径规划在评价指标（覆盖率、路径长度、转向次数、能耗）与算法族（细胞分解、生成树、旅行商式、势场法等）上的完整综述，为本文路径规划模型的选择与对比提供依据」。
- **confidence**：**verified**

---

## G. 在线/动态旅行商问题（竞争分析）与旅行修理工问题

### G1. Ausiello 等 —— 在线旅行商问题算法（竞争比经典文献）

- **type**：journal paper（另有 1995 年会议版）
- **authors**：Ausiello, Giorgio; Feuerstein, Esteban; Leonardi, Stefano; Stougie, Leen; Talamo, Maurizio
- **exact title**：Algorithms for the On-Line Travelling Salesman
- **year**：2001
- **venue / vol / issue / pages**：*Algorithmica*, vol. 29, no. 4, pp. **560–581**
- **DOI**：**10.1007/s004530010071**
- **如何核实**：Crossref REST API 查询 `Algorithms for the on-line travelling salesman Ausiello Feuerstein Leonardi`，返回原文：`TITLE : Algorithms for the On-Line Travelling Salesman1 / AUTH : Ausiello G.; Feuerstein E.; Leonardi S.; Stougie L.; Talamo M. / YEAR : 2001 / VENUE : Algorithmica / vol 29 iss 4 pp 560-581 / DOI : 10.1007/s004530010071 / TYPE : journal-article`；同次检索还返回其 1995 年会议前身：`Competitive algorithms for the on-line traveling salesman / YEAR : 1995 / VENUE : Lecture Notes in Computer Science | Algorithms and Data Structures / pp 206-217 / DOI : 10.1007/3-540-60220-8_63`。
- **支撑论文中的哪句话**：支撑「当干扰源位置需在行进过程中逐步发现（在线/动态情形）时，路径规划的优劣应以**竞争比**（competitive ratio）衡量；本文对比"先全局规划"与"边搜边定"两种策略时使用该理论框架」。
- **confidence**：**verified**

### G2. Afrati 等 —— 旅行修理工问题的复杂性（最小等待时间目标）

- **type**：journal paper
- **authors**：Afrati, Foto; Cosmadakis, Stavros; Papadimitriou, Christos H.; Papageorgiou, George; Papakostantinou, Nadia
- **exact title**：The complexity of the travelling repairman problem
- **year**：1986
- **venue / vol / issue / pages**：*RAIRO – Theoretical Informatics and Applications*, vol. 20, no. 1, pp. **79–87**
- **DOI**：**10.1051/ita/1986200100791**
- **稳定 URL（Numdam 开放全文，推荐著录）**：`https://www.numdam.org/item/ITA_1986__20_1_79_0/`（PDF：`https://www.numdam.org/item/ITA_1986__20_1_79_0.pdf`）
- **如何核查**：
  1. Crossref 单条记录解析返回原文：`OK 10.1051/ita/1986200100791 / T: The complexity of the travelling repairman problem / A: Afrati Foto; Cosmadakis Stavros; Papadimitriou Christos H.; Papageorgiou George; Papakostantinou Nadia / Y: 1986 / V: RAIRO - Theoretical Informatics and Applications / vol 20 iss 1 pp 79-87 / type journal-article`
  2. Numdam（法国数学文献开放库）的 BibTeX 记录与 Crossref 记录双向一致；MR 849967；Zbl 0585.68057。
- **支撑论文中的哪句话**：支撑「若优化目标不是总路程最短而是**各干扰源被清除的时刻之和（或最大等待时间）最短**，则问题是旅行修理工问题（TRP，亦称最小时延问题），其 NP 困难性源自该文」——这对本题"多干扰源逐一清除、总耗时最小"的目标函数设定非常关键。
- **confidence**：**verified**

### G3. Blum 等 —— 最小时延问题（Minimum Latency Problem）

- **type**：conference paper
- **authors**：Blum, Avrim; Chalasani, Prasad; Coppersmith, Don; Pulleyblank, Bill; Raghavan, Prabhakar; Sudan, Madhu
- **exact title**：The minimum latency problem
- **year**：1994
- **venue / pages**：*Proceedings of the 26th Annual ACM Symposium on Theory of Computing (STOC '94)*, pp. **163–171**
- **DOI**：**10.1145/195058.195125**
- **如何核实**：Crossref REST API 查询 `The minimum latency problem Blum Chalasani Coppersmith`，返回原文：`TITLE : The minimum latency problem / AUTH : Blum Avrim; Chalasani Prasad; Coppersmith Don; Pulleyblank Bill; Raghavan Prabhakar; Sudan Madhu / YEAR : 1994 / VENUE : Proceedings of the twenty-sixth annual ACM symposium on Theory of computing - STOC '94 / pp 163-171 / DOI : 10.1145/195058.195125 / TYPE : proceedings-article`。
  ⚠️ **DOI 防错**：本篇 DOI 末段必须是 **`.195125`**。同卷的 **`10.1145/195058.195122`** 是**另一篇完全不同的论文**（MacKenzie, Plaxton, Rajaraman, "On contention resolution protocols and associated probabilistic phenomena", pp. 153–162）。若把 `.122` 写进参考文献，指向的是别人的文章。
  旁证：OpenAlex 对该文的摘要著录中含「This problem is also known in the literature as the deliveryman problem or the **traveling repairman problem**.」，可佐证其与 G2 属同一问题族。
- **支撑论文中的哪句话**：支撑「最小时延问题（等价于旅行修理工问题）的近似算法与近似比；本文求解"最短总清除时间"路线时可引用其近似算法框架」。
- **confidence**：**verified**

### G4. Bertsimas & van Ryzin —— 欧氏平面上的随机动态车辆路径问题（DTRP）

- **type**：journal paper
- **authors**：Bertsimas, Dimitris J.; van Ryzin, Garrett
- **exact title**：A Stochastic and Dynamic Vehicle Routing Problem in the Euclidean Plane
- **year**：1991
- **venue / vol / issue / pages**：*Operations Research*, vol. 39, no. 4, pp. **601–615**
- **DOI**：**10.1287/opre.39.4.601**
- **如何验证**：Crossref REST API 查询 `Bertsimas van Ryzin stochastic and dynamic vehicle routing problem Euclidean plane`，返回原文：`TITLE : A Stochastic and Dynamic Vehicle Routing Problem in the Euclidean Plane / AUTH : Bertsimas Dimitris J.; van Ryzin Garrett / YEAR : 1991 / VENUE : Operations Research / vol 39 iss 4 pp 601-615 / DOI : 10.1287/opre.39.4.601 / TYPE : journal-article`。
- **支撑论文中的哪句话**：支撑「动态车辆路径问题（DTRP）的稳定性与最优渐近性能（如重负载下的 TSP 巡游策略）；本题中干扰源请求不断到达的场景可归入此框架，用于分析"边巡航边响应"策略的效率下界」。
- **confidence**：**verified**

### G5. Bjelde 等 —— 在直线上的在线 TSP 的**紧界**（竞争比定理的最新权威来源）

- **type**：conference paper + journal paper（同一工作的会议版与期刊扩展版）
- **authors**：Bjelde, Antje; Disser, Yann; Hackfeld, Jan; Hansknecht, Christoph; Lipmann, Maarten; Meißner, Julie; Schewior, Kevin; Schlöter, Miriam; Stougie, Leen（期刊版作者次序略有不同，含 SchlÖter Miriam）
- **exact title**：Tight Bounds for Online TSP on the Line
- **year**：2017（SODA 会议版）/ 2021（ACM TALG 期刊版；Crossref 记录的 issued 年份为 2020，系在线先发年）
- **venue / pages**：
  - 会议版：*Proceedings of the Twenty-Eighth Annual ACM-SIAM Symposium on Discrete Algorithms (SODA 2017)*, pp. **994–1005**，DOI **10.1137/1.9781611974782.63**
  - 期刊版：*ACM Transactions on Algorithms*, vol. **17**, no. **1**, pp. **1–58**，DOI **10.1145/3422362**
- **如何核实**：用 Crossref **单条记录解析**（`https://api.crossref.org/works/<DOI>`，该方式不受检索接口限流影响），两条记录返回原文分别为：
  `OK 10.1137/1.9781611974782.63 / T: Tight Bounds for Online TSP on the Line / Y: 2017 / V: Proceedings of the Twenty-Eighth Annual ACM-SIAM Symposium on Discrete Algorithms / pp 994-1005 / type proceedings-article`
  `OK 10.1145/3422362 / T: Tight Bounds for Online TSP on the Line / Y: 2020 / V: ACM Transactions on Algorithms / vol 17 iss 1 pp 1-58 / type journal-article`
- **支撑论文中的哪句话**：支撑「在线 TSP 在直线度量上的竞争比已有**紧界**：闭合变体（需返回出发点）最优竞争比为 **1.64**，开放变体为 **2.04**。若本文将机器人狗的巡航路线简化为直线/一维场景，可直接引用此紧界作为最优性基准。」
  ⚠️ **引用时请注意归属**：G1（Ausiello 等 2001）给出的是**一般度量空间**闭合变体的**最优 2-竞争**算法，以及直线上的 7/3-竞争算法与 **2 的下界**；实数轴闭合变体的**紧值 1.64** 出自本条（Bjelde 等）。**不要**把 1.75（Ausiello 在 H-OLTSP 上的**上界**）当作下界引用。
- **confidence**：**verified**

### G6. Ascheuer, Krumke & Rambau —— 在线 Dial-a-Ride 问题（最小化完成时间）

- **type**：conference paper（书章形式收录）
- **authors**：Ascheuer, Norbert; Krumke, Sven O.; Rambau, Jörg
- **exact title**：Online Dial-a-Ride Problems: Minimizing the Completion Time
- **year**：2000
- **venue / pages**：*STACS 2000*（Lecture Notes in Computer Science），pp. **639–650**
- **DOI**：**10.1007/3-540-46541-3_53**；ISBN 978-3-540-67141-1
- **如何核实**：Crossref 单条记录解析返回原文：`OK 10.1007/3-540-46541-3_53 / T: Online Dial-a-Ride Problems: Minimizing the Completion Time / A: Ascheuer Norbert; Krumke Sven O.; Rambau Jörg / Y: 2000 / V: Lecture Notes in Computer Science|STACS 2000 / pp 639-650 / type book-chapter`
  ⚠️ **防错**：这是 **STACS 2000** 的 Dial-a-Ride 论文，**不是** STOC 的 TSP 论文，勿混引。
- **支撑论文中的哪句话**：支撑「把'接到干扰源报告后前往处理并完成清除'视为在线请求的送达/接送问题，其目标是**完成时间**而非总路程；这是本文目标函数选择的文献依据之一」。
- **confidence**：**verified**

### G7. Jaillet & Wagner —— 在线路径问题中"预知信息"的价值

- **type**：journal paper
- **authors**：Jaillet, Patrick; Wagner, Michael R.
- **exact title**：Online Routing Problems: Value of Advanced Information as Improved Competitive Ratios
- **year**：2006
- **venue / vol / issue / pages**：*Transportation Science*, vol. 40, no. 2, pp. **200–210**
- **DOI**：**10.1287/trsc.1060.0147**
- **如何核实**：Crossref 单条记录解析返回原文：`OK 10.1287/trsc.1060.0147 / T: Online Routing Problems: Value of Advanced Information as Improved Competitive Ratios / A: Jaillet Patrick; Wagner Michael R. / Y: 2006 / V: Transportation Science / vol 40 iss 2 pp 200-210 / type journal-article`
- **支撑论文中的哪句话**：支撑「若机器人狗能在出发前获得部分先验信息（如干扰源大致方位/区域），在线路径问题的竞争比可被改进——这为本文"先用少量测向数据缩小范围、再规划路径"的策略提供了理论收益论证」。
- **confidence**：**verified**

### G8. Psaraftis —— 动态车辆路径：现状与展望

- **type**：journal paper
- **authors**：Psaraftis, Harilaos N.
- **exact title**：Dynamic vehicle routing: Status and prospects
- **year**：1995
- **venue / vol / issue / pages**：*Annals of Operations Research*, vol. 61, no. 1, pp. **143–164**
- **DOI**：**10.1007/BF02098286**
- **如何核实**：Crossref 单条记录解析返回原文：`OK 10.1007/BF02098286 / T: Dynamic vehicle routing: Status and prospects / A: Psaraftis Harilaos N. / Y: 1995 / V: Annals of Operations Research / vol 61 iss 1 pp 143-164 / type journal-article`
- **支撑论文中的哪句话**：支撑「动态车辆路径问题（DVRP）的分类与建模要素综述；本文把'干扰源发现是渐进的、路线需实时调整'这一特点归入 DVRP 框架时有权威综述可引」。
- **confidence**：**verified**

---

## H. 纯方位目标运动分析（Bearings-Only TMA）与可观测性

### H1. Nardone & Aidala —— 纯方位 TMA 的可观测性判据（经典）

- **type**：journal paper
- **authors**：Nardone, Steven C.; Aidala, Vincent J.
- **exact title**：Observability Criteria for Bearings-Only Target Motion Analysis
- **year**：1981
- **venue / vol / issue / pages**：*IEEE Transactions on Aerospace and Electronic Systems*, vol. **AES-17**, no. 2, pp. **162–166**
- **DOI**：**10.1109/TAES.1981.309141**
- **如何核实**：Crossref REST API 查询 `Observability Criteria for Bearings-Only Target Motion Analysis`，返回原文：`TITLE : Observability Criteria for Bearings-Only Target Motion Analysis / AUTH : Nardone Steven; Aidala Vincent / YEAR : 1981 / VENUE : IEEE Transactions on Aerospace and Electronic Systems / VOL/IS: AES-17 / 2 / 162-166 / DOI : 10.1109/taes.1981.309141 / TYPE : journal-article`。同次检索还返回其 1980 年技术报告前身：`Necessary and Sufficient Observability Conditions for Bearings-Only Target Motion Analysis / DOI : 10.21236/ada102073 / TYPE : report`。
- **支撑论文中的哪句话**：支撑「仅凭方位角序列估计目标位置/运动需要观测平台**机动**（observer maneuver）才可观测；本文论证机器人狗不能只沿直线匀速行进测向，而必须在不同站位间形成"基线变化"才能解算干扰源位置」——这是路线规划必须包含转向/绕行段的严格依据。
- **confidence**：**verified**

### H2. Nardone, Lindgren & Gong —— 传统纯方位 TMA 的基本性质与性能

- **type**：journal paper
- **authors**：Nardone, S. C.; Lindgren, A. G.; Gong, K. F.
- **exact title**：Fundamental properties and performance of conventional bearings-only target motion analysis
- **year**：1984
- **venue / vol / issue / pages**：*IEEE Transactions on Automatic Control*, vol. 29, no. 9, pp. **775–787**
- **DOI**：**10.1109/TAC.1984.1103664**
- **如何核实**：Crossref REST API 查询 `Fundamental properties and performance of conventional bearings-only target motion analysis`，返回原文：`TITLE : Fundamental properties and performance of conventional bearings-only target motion analysis / AUTH : Nardone S.; Lindgren A.; Kai Gong / YEAR : 1984 / VENUE : IEEE Transactions on Automatic Control / vol 29 iss 9 pp 775-787 / DOI : 10.1109/tac.1984.1103664 / TYPE : journal-article`。同次检索还返回其 1983 年会议版：`Fundamental Properties and Performance of Nonlinear Estimators for Bearings-Only Target Tracking / VENUE : Nonlinear Stochastic Problems / pp 593-600 / DOI : 10.1007/978-94-009-7142-4_43`。
- **支撑论文中的哪句话**：支撑「纯方位观测下目标位置估计的 Cramér–Rao 下界与可观测性几何条件（如"目标方位变化率"不足则估计发散）；本文讨论机器人狗测向序列的可解性与精度极限时引用」。
- **confidence**：**verified**

### H3. Jauffret 等 —— 观测平台平滑机动下的纯方位 TMA 可观测性（现代综述性结果）

- **type**：conference paper
- **authors**：Perez, Annie-Claude; Jauffret, Claude; Pillon, Denis
- **exact title**：Bearings-only target motion analysis: Observability when the observer maneuvers smoothly
- **year**：2017
- **venue / pages**：*2017 20th International Conference on Information Fusion (Fusion)*, pp. 1–8
- **DOI**：**10.23919/ICIF.2017.8009823**
- **如何核实**：Crossref REST API 在检索纯方位 TMA 可观测性时返回该条，原文：`TITLE : Bearings-only target motion analysis: Observability when the observer maneuvers smoothly / AUTH : Perez Annie-Claude; Jauffret Claude; Pillon Denis / YEAR : 2017 / VENUE : 2017 20th International Conference on Information Fusion (Fusion) / pp 1-8 / DOI : 10.23919/icif.2017.8009823 / TYPE : proceedings-article`。
- **支撑论文中的哪句话**：支撑「当观测平台（机器人狗）**平滑**机动（而非剧烈折线）时，纯方位 TMA 的可观测性条件仍然成立；这为机器人狗采用圆弧/平滑绕行路线（而非急转）做多站位测向提供理论支持」。
- **confidence**：**verified**

### H4. Nardone & Aidala 1980 —— 纯方位 TMA 的充要可观测性条件（**技术报告一手来源，含"必须机动"原文**）

- **type**：report（技术报告 / DTIC 公开报告）
- **authors**：Nardone, Steven C.; Aidala, Vincent J.
- **exact title**：Necessary and Sufficient Observability Conditions for Bearings-Only Target Motion Analysis
- **year**：1980
- **venue / identifier**：Naval Underwater Systems Center (NUSC) Technical Memorandum **TM 80-2059**（1980-06-03）；DTIC 登录号 **AD-A102 073**；DOI **10.21236/ada102073**
- **stable URL**：`https://doi.org/10.21236/ada102073`；Internet Archive 全文：`https://archive.org/details/DTIC_ADA1020731`
- **如何核实**：Crossref 单条记录解析返回原文：`OK 10.21236/ada102073 / T: Necessary and Sufficient Observability Conditions for Bearings-Only Target Motion Analysis / A: Nardone Steven C.; Aidala Vincent J. / Y: 1980 / type report`。
  报告中含**可直接引用的关键论断**（由委托核查流程下载 DTIC 全文纯文本后检索确认，逐字原文）：
  > 「…the estimation problem will remain **unobservable prior to an own ship maneuver**. Indeed, **unique tracking solutions cannot be obtained for unaccelerated motion**. It is this **prerequisite maneuver** which distinguishes…」
  > 「…**observability is contingent upon an own ship maneuver** as…」
- **支撑论文中的哪句话**：支撑「仅凭连续测向**无法**唯一确定目标位置——观测者（机器人狗）**必须先机动**才能获得可观测性。这直接排除了'机器人狗沿直线匀速边走边测即可定位'的方案，是本文路径约束的理论根基。」
- **confidence**：**verified**（题名、作者、年份、报告号、DTIC 号、DOI 均已确认；关键技术论断的逐字原文已取得）

### H5. Passerieux & Van Cappel —— 纯方位跟踪的最优观测者机动

- **type**：journal paper
- **authors**：Passerieux, J. M.; Van Cappel, D.
- **exact title**：Optimal observer maneuver for bearings-only tracking
- **year**：1998
- **venue / vol / issue / pages**：*IEEE Transactions on Aerospace and Electronic Systems*, vol. 34, no. 3, pp. **777–788**
- **DOI**：**10.1109/7.705885**
- **如何核实**：Crossref 单条记录解析返回原文：`OK 10.1109/7.705885 / T: Optimal observer maneuver for bearings-only tracking / A: Passerieux J.M.; Van Cappel D. / Y: 1998 / V: IEEE Transactions on Aerospace and Electronic Systems / vol 34 iss 3 pp 777-788 / type journal-article`
  （注意：该文参考文献表把 H7 的 Payne 论文误标为 1990 年，正确年份为 **1989**，见 H7。）
- **支撑论文中的哪句话**：支撑「观测者机动不仅'必要'而且可以**最优设计**——本文在给出机器人狗多站位测向的站位几何时，可引用该文的最优机动准则（即最大化可观测性/最小化估计协方差）来论证所选取的绕行形状」。
- **confidence**：**verified**

### H6. Le Cadre & Jauffret —— 纯方位 TMA 的离散时间可观测性与可估计性分析

- **type**：journal paper
- **authors**：Le Cadre, J. E.; Jauffret, C.
- **exact title**：Discrete-time observability and estimability analysis for bearings-only target motion analysis
- **year**：1997
- **venue / vol / issue / pages**：*IEEE Transactions on Aerospace and Electronic Systems*, vol. 33, no. 1, pp. **178–201**
- **DOI**：**10.1109/7.570737**
- **如何核实**：Crossref 单条记录解析（首次请求遇 HTTP 429 限流，等待后重试成功）返回原文：`Discrete-time observability and estimability analysis for bearings-only target motion analysis || Le Cadre J.E.; Jauffret C. || 1997 || IEEE Transactions on Aerospace and Electronic Systems || vol 33 iss 1 pp 178-201`
  旁证：该文另有一篇后续讨论「Comments on "Discrete-time observability and estimability analysis for bearings-only target motion analysis"」，作者 Koteswara Rao S.，*IEEE TAES*, 1998, 34(4): 1361–1367, DOI 10.1109/7.722722（同期由 Crossref 检索返回，可佐证 H6 的影响力）。
- **支撑论文中的哪句话**：支撑「机器人狗只是**离散时间**采样测向（每隔一段行进才更新一次量测），因此应采用**离散时间**可观测性/可估计性判据，而不是连续时间结论；这为本文按'站位序列'建模（而非连续轨迹）提供依据」。
- **confidence**：**verified**

### H7. Payne —— 纯方位跟踪的可观测性问题（**注意年份为 1989**）

- **type**：journal paper
- **authors**：Payne, Anthony N.
- **exact title**：Observability problem for bearings-only tracking
- **year**：**1989**（1989 年 3 月）
- **venue / vol / issue / pages**：*International Journal of Control*, vol. 49, no. 3, pp. **761–768**
- **DOI**：**10.1080/00207178908559665**
- **如何核实**：Crossref 单条记录解析返回原文：`OK 10.1080/00207178908559665 / T: Observability problem for bearings-only tracking / A: Payne Anthony N. / Y: 1989 / V: International Journal of Control / vol 49 iss 3 pp 761-768 / type journal-article`
  ⚠️ **年份陷阱**：H5（Passerieux & Van Cappel 1998）的参考文献表把这篇文章误标为 **1990** 年。Crossref 确认为 **1989**。**请使用 1989。**
- **支撑论文中的哪句话**：支撑「纯方位跟踪的可观测性问题的早期系统分析；作为 H1/H4 的补充引证，说明该问题在 1980 年代末已被充分认识（因此本文把它作为建模前提是稳妥的）」。
- **confidence**：**verified**

---

## I. LaTeX 模板（CUMCM 论文排版）

### I1. CUMCMThesis（`latexstudio/CUMCMThesis`）—— **不在 CTAN 上，请引 GitHub 仓库**

- **type**：web page（开源代码仓库 / LaTeX 模板）
- **authors / 维护者**：LaTeX 工作室（latexstudio）
- **exact title**：全国大学生数学建模竞赛 LaTeX 论文模板（cumcmthesis）
- **year**：持续更新（README 更新记录最新为 **2026 年 8 月**「更新了 AI 使用声明书」；此前 2023 年 9 月、2021 年 7 月、2020 年 8 月均有更新）
- **venue / identifier**：GitHub 仓库 `latexstudio/CUMCMThesis`；文档类名 `cumcmthesis`
- **stable URL**：`https://github.com/latexstudio/CUMCMThesis`；README 原文链接 `https://raw.githubusercontent.com/latexstudio/CUMCMThesis/master/README.md`
- **如何核实**：
  1. 抓取 `https://raw.githubusercontent.com/latexstudio/CUMCMThesis/master/README.md`，页面首行原文：「## 全国大学生数学建模竞赛 LaTeX 论文模板」「cumcmthesis 是为全国大学生数学建模竞赛编写的 `LaTeX` 模板, 旨在让大家专注于论文的内容写作, 而不用花费过多精力在格式的定制和调整上……」「如果需要去掉封面并把论文标题保留在摘要上面，在加载类的使用如下语句：`\documentclass[withoutpreface,bwprint]{cumcmthesis}`」。
  2. **重要更正（CTAN 上并不存在 cumcmthesis 包）**：抓取 `https://ctan.org/pkg/cumcmthesis` 返回 **HTTP 404**（页面原文：「The requested URL _/pkg/cumcmthesis_ was not found on this server.」）；抓取 CTAN 搜索页 `https://ctan.org/search?phrase=cumcm` 返回原文：「**The search found no matching documents on CTAN in 8ms.**」
  3. CTAN 上确实存在的、名字相近的包是 **`mcmthesis`**，但它**只面向 MCM/ICM**：抓取 `https://ctan.org/pkg/mcmthesis` 原文：「**Mcmthesis – Template designed for MCM/ICM**」「The package offers a template for MCM (The Mathematical Contest in Modeling) and ICM (The Interdisciplinary Contest in Modeling) for typesetting the submitted paper.」「Version 6.3.3 2024-01-22」「Repository: https://github.com/latexstudio-org/mcmthesis」「Copyright 2010–2015 Zhaoli Wang / 2014–2019 Liam Huang / 2019–2024 latexstudio」。
- **支撑论文中的哪句话**：支撑「本文论文排版使用 cumcmthesis 模板，符合全国大学生数学建模竞赛官方格式要求」。
- **confidence**：**verified**（GitHub README 已抓到；CTAN 无此包亦为已核实的**否定结论**）。**引用时请写 GitHub 仓库地址，不要写 CTAN 条目。**

### I2. CTAN `mcmthesis`（如需引用 CTAN 上的同类模板）

- **type**：web page（CTAN 宏包条目）
- **authors / 维护者**：Liam Huang；LaTeX 工作室（latexstudio）；Zhaoli Wang (inactive)
- **exact title**：Mcmthesis – Template designed for MCM/ICM
- **year / version**：Version **6.3.3**, 2024-01-22
- **identifier**：CTAN 宏包 `mcmthesis`；License **LPPL 1.3c**；收录于 TeX Live / MiKTeX
- **stable URL**：`https://ctan.org/pkg/mcmthesis`
- **如何核实**：同上第 3 点，CTAN 官方包页面原文（含版本号、许可证、版权年份、仓库地址）。
- **支撑论文中的哪句话**：仅当论文排版实际使用 `mcmthesis`（而非 `cumcmthesis`）时引用；否则**不要引用**，因为它是 MCM/ICM 模板。
- **confidence**：**verified**（但**与 CUMCM 不匹配**，故对本论文多半**不适用**）

---

## J. 中文教材与中文期刊文献（无线电测向 / 无线电监测定位）

### J1. 《无线电监测与测向定位》（**首选中文教材**）

- **type**：book（高等学校教材）
- **authors**：张洪顺, 王磊 主编；敖伟, 杨洁 参编
- **exact title**：无线电监测与测向定位
- **year**：2011
- **venue / identifier**：西安：**西安电子科技大学出版社**，2011，302 页，图，26cm；丛书：高等学校电子与信类专业「十二五」规划教材；ISBN **978-7-5606-2654-3**（定价 CNY 33.00）；中图分类号 **TN014**
- **stable URL**：`http://jccxxt.cdjcc.edu.cn/opac/book/c0f5e0665f1b8da615373129e17f26f4`（高校图书馆 OPAC 书目记录）
- **如何核实**：抓取图书馆 OPAC 书目详情页，原文：「书目详细信息 ： **无线电监测与测向定位**」「ISBN/价格： **978-7-5606-2654-3**:CNY33.00」「题名责任者项： 无线电监测与测向定位/.**主编张洪顺, 王磊**/.参编敖伟 ... [等]」「出版发行项： 西安:, **西安电子科技大学出版社**,: **2011**」「载体形态项： 302页:;+图:;+26cm」「丛编项： 高等学校电子与信类专业"十二五"规划教材」「提要文摘： 本书全面、系统地阐述了**无线电监测、无线电测向以及卫星定位与卫星干扰源定位**的基本原理、基本概念、基本技术和基本分析方法, 力求充分反映当代无线电监测、无线电测向和卫星定位的新技术。」「题名主题： 无线电信号 检测 高等学校 教材 / 无线电信号 测向 高等学校 教材 / 无线电信号 卫星 电子干扰 定位 高等学校 教材」「中图分类： TN014」。
- **支撑论文中的哪句话**：支撑「无线电监测与测向定位的基本原理（测向体制、交会定位算法、干扰源查找流程）在本中文教材中有系统阐述，本文的建模符号与术语与之对齐」。
- **confidence**：**verified**

### J2. 中文期刊（实务经验）：做好无线电干扰源测向定位的几点经验

- **type**：journal paper（实务经验总结）
- **authors**：周靖博, 黄艳（中国人民解放军 61226 部队）
- **exact title**：做好无线电干扰源测向定位的几点经验
- **year**：2009
- **venue**：*中国无线电*, 2009 年第 2 期（CNKI 刊号代码 ZWDG，文章号 ZWDG200902021）
- **DOI / URL**：CNKI 记录页 `https://wap.cnki.net/touch/web/Journal/Article/ZWDG200902021.html`
- **如何核实**：抓取 CNKI 手机版记录页，原文可见：题名「**做好无线电干扰源测向定位的几点经验**」；机构「中国人民解放军61226部队 | 周靖博 黄艳」；摘要原文：「结合 2008 北京奥运会、残奥会无线电安全保障工作,分析总结了无线电干扰的基本特征及干扰源测向定位的经验,并以实际案例详细说明了无线电干扰源测向定位的具体判断方法。」；关键词「干扰信号特征；干扰源测向定位」；期刊「中国无线电 2009 年 02 期」。
  **注意**：CNKI 页面**未显示起止页码**，故不著录页码。
- **支撑论文中的哪句话**：支撑「实际干扰源排查中"先测向粗定位、再逐步逼近、最后精确定位并现场确认"的作业流程」——为本文的分阶段（搜索—逼近—确认—清除）策略提供工程实践依据。
- **confidence**：**verified**（题名、作者、机构、刊名、年、期、摘要均确认）；**页码未核实**。

---

## K. ⚠️ 未能核实 / 需要更正的事项（**不可作为参考文献**）

### K1. GB/T 14432-1993 —— **不是「无线电测向」标准**（已核实的否定结论）

- **实际题名**：广播录音机抖晃测量方法 / Measuring methods for wow and flutter of broadcast tape recorders
- **实际情况**：推荐性国家标准，归口 TC239（全国广播电视和网络视听标准化技术委员会），主管部门广电总局，发布 1993-06-09，实施 1993-12-01，**已于 2017-12-15 废止**；CCS M71，ICS 33.160.30；非等效采用 IEC 386。
- **核实证据**：抓取全国标准信息公共服务平台页面 `https://std.samr.gov.cn/gb/search/gbDetailed?id=71F772D78C52D3A7E05397BE0A0AB82A`，原文：「**广播录音机抖晃测量方法**」「国家标准 推荐性 **废止**」「标准号 **GB/T 14432-1993**」「废止日期 2017-12-15」「上次复审结论 废止」「本标准非等效采用IEC国际标准：IEC 386。」
- **结论**：**该标准与无线电测向毫无关系，且已废止。请从参考文献中删除。**

### K2. GB/T 6933-1995 —— **不是「无线电测向」标准**（已核实的否定结论）

- **实际内容**（据第三方标准门户的德文译名）：*Verfahren zur Messung der elektrischen Leistung von Kurzwellen-Einseitenbandsendern*，即「**短波单边带发射机电性能测量方法**」；发布 1995 年，标准状态标注为「2018-07 被替换」，**被 GB/T 16946-2017《短波单边带通信设备通用规范》替代**；其前身为 GB 6933-1986。
- **核实证据**：抓取 `https://normenportal.org/257599.html`，原文：「**GB/T 6933-1995**」「## Methoden zur Messung der elektrischen Leistung von Kurzwellen-Einseitenbandsendern」「Status | ersetzt werden 2018-07」「**Ersetzt durch GB/T 16946-2017**」「Ersetzt GB 6933-1986」「Diese Norm legt die Bedingungen, Definitionen und Messmethoden für die elektrische Leistung von kurzwelligen Einseitenbandsendern … fest.」（另有中国标准在线服务网关联列表中「GB/T 16946-2017 短波单边带通信设备通用规范」条目佐证。）
- **结论**：**该标准是短波单边带发射机测量方法，与无线电测向无关，且已被 GB/T 16946-2017 替代。请从参考文献中删除。**
- **替代建议**：如需「无线电测向」的中国标准，请改用本文件 **C2（GB/T 34089-2017）**、**C3（YD/T 3730-2020）**、**C4（GB 13614-2012）**。

### K3. 「CTAN 上的 cumcmthesis 条目」—— **不存在**（已核实的否定结论）

- 已在 **I1** 中给出精确证据：`https://ctan.org/pkg/cumcmthesis` → **HTTP 404**；`https://ctan.org/search?phrase=cumcm` → 「The search found no matching documents on CTAN in 8ms.」
- **结论**：**不要引用「cumcmthesis 的 CTAN 条目」，因为它不存在。** 请改引 GitHub 仓库 `https://github.com/latexstudio/CUMCMThesis`。

### K4. ITU-R SM.2060 的题名（常见误记）

- 用户原假设为「Measured amplitude of a radio signal」，**实际题名为**「**Test procedure for measuring direction finder accuracy**」（详见 B2）。
- **结论**：引用时务必使用实际题名；误记题名会被评审认为未查原文。

### K5. ITU-R SM.2211 的性质与版本（易误引）

- SM.2211 是 **Report（报告）**而非 **Recommendation（建议书）**；且 2011 版 **Status: Superseded**（详见 B4）。
- **结论**：著录时类型须写「Report ITU-R SM.2211」，并注明「被后续版本取代」或改引最新版。

### K6. 《在压制的同时快速查找作弊信号源》（中国无线电 2013 年第 8 期）

- **核实状态**：仅在搜索结果中见到 CNKI 条目链接（`https://wap.cnki.net/touch/web/Journal/Article/ZWDG201308051.html`）及其题名，**未抓取页面确认**作者、页码、摘要。
- **confidence**：**unverified** —— **请勿引用**，除非另行核实。若确需「无线电作弊信号源查找」类中文实务文献，可优先使用已核实的 **J2**。

### K7. Verblunsky 1949 —— **已解除警示**（由 partially verified 升级为 verified）

- 该条最初仅由二次文献（Weisstein 词条参考文献表）著录；**后续已通过 Crossref 独立核实成功**，返回原文：`On the Least Number of Unit Circles Which Can Cover a Square || Verblunsky S. || 1949 || Journal of the London Mathematical Society || vol s1-24 iss 3 pp 164-170 || 10.1112/jlms/s1-24.3.164`。
- **结论**：**现可正常引用**，详见 **E3**。

### K8. 未找到 / 未核实的条目

- **GB/T 14733.8《电信术语 无线电测向和导航》**：经多次检索（含 `std.samr.gov.cn`、工标网、中国标准在线服务网）**未能定位到该标准号**；检索只命中 GB/T 14733.9-2008《电信术语 无线电波传播》。**该标准是否存在无法确认，请勿引用。**
- **GB/T 9030-1988《船用无线电测向仪性能要求》**：工标网「无线电测向」结果页确认其存在，但状态为「**废止**」，**不宜作为现行标准引用**（原文：`GB/T 9030-1988 | 船用无线电测向仪性能要求 | 电子工业部 | 1988-10-01 | 废止`）。
- **DL/T 1840-2018《交流高压架空输电线路对短波无线电测向台（站）保护间距要求》**：工标网结果页确认存在（国家能源局，2018-07-01 实施，现行），但与本题（VHF/UHF 移动测向）关联度低，**未深入核实，暂不建议引用**。
- **ITU-R SM.2060 / SM.854-3 的 PDF 正文**：本环境下 `web_fetch` 对 ITU 的 `!!PDF-E.pdf` 直链返回 **HTTP 406**（`406 - Client browser does not accept the MIME type of the requested page.`），**未能读取建议书正文**。故 B1、B2 的核实仅到「题名 / 编号 / 批准日期 / 在版状态」层面。若论文需引用建议书正文中的具体定义，请自行下载 PDF 逐条核对页码。

---

## L. 汇总索引（按主题对应论文用途）

| 编号 | 简称 | 类型 | 年 | 标识（DOI/ISBN/标准号） | 置信度 | 支撑的论文环节 |
|---|---|---|---|---|---|---|
| A1 | Torrieri, Statistical Theory of Passive Location Systems | 期刊 | 1984 | 10.1109/TAES.1984.310439 | verified | 误差椭圆 / GDOP 理论 |
| A2 | Stansfield, Statistical theory of d.f. fixing | 期刊 | 1947 | 10.1049/ji-3a-2.1947.0096 | verified | 交会定位统计处理溯源 |
| A3 | 修建娟等, 测向交叉定位系统中的交会角研究 | 期刊 | 2005 | 宇航学报 26(3):282-285 | verified（页码部分核实） | **最优交会角 + CEP + GDOP** |
| A4 | 盛丹等, 存在系统误差下…最优交会角研究 | 期刊 | 2016 | 10.3969/j.issn.1001-506X.2016.07.06 | verified | 有系统误差时的最优交会角 |
| A5 | 黄裕文等, 机场终端区GNSS信号干扰源定位研究 | 期刊 | 2023 | 10.16592/j.cnki.1004-7859.2023.12.013 | verified | 干扰源测向交会实测案例 |
| A6 | 钟建林等, 基于测向交叉定位的空舰导弹协同攻击方法 | 期刊 | 2019 | 10.12132/ISSN.1673-5048.2019.0127 | verified | 交会角-距离-误差关系 |
| B1 | ITU-R SM.854-3 | 标准 | 2011 | Recommendation ITU-R SM.854-3 | verified | 监测站测向与定位规范 |
| B2 | ITU-R SM.2060-0 | 标准 | 2014 | Recommendation ITU-R SM.2060-0 | verified | 测向机精度测试程序 |
| B3 | ITU-R SM.1600-3 | 标准 | 2017 | Recommendation ITU-R SM.1600-3 | verified | 数字信号技术识别 |
| B4 | ITU-R Report SM.2211-0 | 标准/报告 | 2011 | Report ITU-R SM.2211-0 | verified（已取代） | AOA 与 TDOA 体制对比 |
| B5 | ITU Handbook on Spectrum Monitoring | 书 | 2011 | R-HDB-23-2011 | verified | 测向误差来源分解 |
| C1 | 中华人民共和国无线电管理条例 | 法规 | 2016 | 国令第 672 号 | verified | 任务合法性与现实需求（第 57 条） |
| C2 | GB/T 34089-2017 | 标准 | 2017 | GB/T 34089-2017 | verified | 测向系统指标与测试口径 |
| C3 | YD/T 3730-2020 | 标准 | 2020 | YD/T 3730-2020 | verified | **移动式测向系统多径抗扰度** |
| C4 | GB 13614-2012 | 标准 | 2012 | GB 13614-2012 | verified | 测向台站电磁环境保护 |
| C5 | GB/T 25003-2010 | 标准 | 2010 | GB/T 25003-2010 | verified | 监测站电磁环境要求 |
| C6 | GB/T 32401-2015 | 标准 | 2015 | GB/T 32401-2015 | verified | 监测接收机技术要求 |
| D1 | Koopman, Search and Screening | 书 | 1946/1980 | ISBN 0080231357 | verified | 发现概率 / 搜索力分配 |
| D2 | Stone, Theory of Optimal Search | 书 | 1975 | ISBN 0126724504 | verified | 最优搜索策略 |
| D3 | Stone/Royset/Washburn, Optimal Search for Moving Targets | 书 | 2016 | 10.1007/978-3-319-26899-6 | verified | 现代搜索理论框架 |
| D4 | 陈建勇, 实用搜索理论 | 书 | 2021 | ISBN 978-7-118-12327-2 | verified | 中文搜索论教材 |
| E1 | Kershner, The Number of Circles Covering a Set | 期刊 | 1939 | 10.2307/2371320 | verified | **最少覆盖圆数 + 覆盖密度** |
| E2 | Fejes Tóth, Thinnest Covering of a Circle by 8/9/10 Congruent Circles | 书章 | 2005 | 10.1017/9781009701259.019 | verified（年份存疑） | 小规模最优 r(n) |
| E3 | Verblunsky, On the Least Number of Unit Circles which Can Cover a Square | 期刊 | 1949 | 10.1112/jlms/s1-24.3.164 | verified | 覆盖密度佐证 |
| E4 | Weisstein, Disk Covering Problem | 网页 | 1999 | archive.lib.msu.edu/.../d314.htm | verified | 覆盖密度 3√3/(2π) |
| E5 | Gáspár/Tarnai/Hincz, Partial Covering of a Circle by 6 and 7 Congruent Circles | 期刊 | 2021 | 10.3390/sym13112133 | verified | 覆盖问题现代进展（开放获取） |
| E6 | Hearn, Single Facility Location: Circle Covering Problem | 书章 | 2001 | 10.1007/0-306-48332-7_472 | verified | 圆覆盖 ↔ 单设施选址 |
| F1 | Choset, Coverage for robotics – A survey | 期刊 | 2001 | 10.1023/A:1016639210559 | verified | 覆盖路径规划分类 |
| F2 | Galceran & Carreras, A survey on coverage path planning | 期刊 | 2013 | 10.1016/j.robot.2013.09.004 | verified | 覆盖路径规划综述 |
| G1 | Ausiello 等, Algorithms for the On-Line Travelling Salesman | 期刊 | 2001 | 10.1007/s004530010071 | verified | 在线 TSP 竞争比（一般度量空间） |
| G2 | Afrati 等, The complexity of the travelling repairman problem | 期刊 | 1986 | 10.1051/ita/1986200100791 | verified | **最小总时延目标 NP 困难** |
| G3 | Blum 等, The minimum latency problem | 会议 | 1994 | 10.1145/195058.195125 | verified | 最小时延近似算法 |
| G4 | Bertsimas & van Ryzin, A Stochastic and Dynamic VRP in the Euclidean Plane | 期刊 | 1991 | 10.1287/opre.39.4.601 | verified | 动态车辆路径 |
| G5 | Bjelde 等, Tight Bounds for Online TSP on the Line | 会议+期刊 | 2017 / 2021 | 10.1137/1.9781611974782.63 ; 10.1145/3422362 | verified | **在线 TSP 直线上的紧界 1.64 / 2.04** |
| G6 | Ascheuer 等, Online Dial-a-Ride Problems | 会议 | 2000 | 10.1007/3-540-46541-3_53 | verified | 在线请求的最小完成时间 |
| G7 | Jaillet & Wagner, Online Routing Problems | 期刊 | 2006 | 10.1287/trsc.1060.0147 | verified | 预知信息提升竞争比 |
| G8 | Psaraftis, Dynamic vehicle routing: Status and prospects | 期刊 | 1995 | 10.1007/BF02098286 | verified | DVRP 综述 |
| H1 | Nardone & Aidala, Observability Criteria for Bearings-Only TMA | 期刊 | 1981 | 10.1109/TAES.1981.309141 | verified | **测向须机动才可观测** |
| H2 | Nardone/Lindgren/Gong, Fundamental properties and performance… | 期刊 | 1984 | 10.1109/TAC.1984.1103664 | verified | 纯方位估计性能极限 |
| H3 | Perez/Jauffret/Pillon, Observability when the observer maneuvers smoothly | 会议 | 2017 | 10.23919/ICIF.2017.8009823 | verified | 平滑机动下的可观测性 |
| H4 | Nardone & Aidala, Necessary and Sufficient Observability Conditions…（NUSC TM 80-2059 / AD-A102073） | 报告 | 1980 | 10.21236/ada102073 | verified | **"必须先机动"的一手原文** |
| H5 | Passerieux & Van Cappel, Optimal observer maneuver for bearings-only tracking | 期刊 | 1998 | 10.1109/7.705885 | verified | 最优观测者机动设计 |
| H6 | Le Cadre & Jauffret, Discrete-time observability and estimability analysis… | 期刊 | 1997 | 10.1109/7.570737 | verified | **离散时间**可观测性判据 |
| H7 | Payne, Observability problem for bearings-only tracking | 期刊 | **1989** | 10.1080/00207178908559665 | verified | 可观测性问题早期分析（**非 1990**） |
| I1 | CUMCMThesis（GitHub） | 网页 | 持续更新 | github.com/latexstudio/CUMCMThesis | verified | 论文排版模板（**非 CTAN**） |
| I2 | CTAN mcmthesis | 网页 | 2024 | ctan.org/pkg/mcmthesis | verified（但不适用） | 仅 MCM/ICM，勿误引 |
| J1 | 张洪顺/王磊, 无线电监测与测向定位 | 书 | 2011 | ISBN 978-7-5606-2654-3 | verified | **中文测向定位教材** |
| J2 | 周靖博/黄艳, 做好无线电干扰源测向定位的几点经验 | 期刊 | 2009 | 中国无线电 2009(2) | verified（无页码） | 干扰源排查实务流程 |

**统计**：`verified` 共 **47** 条；`partially verified` **2** 条（A3 页码、E2 年份）；**unverified / 已否定** 共 **8** 项（K1–K8）。
按语种/来源分：**中国标准·法规·中文文献**共 **13** 条（C1–C6、J1–J2、A3–A6、D4）；**英文经典教材·论文·报告**共 **32** 条（A1–A2、B1–B5、D1–D3、E1–E6、F1–F2、G1–G8、H1–H7）；**排版模板** 2 条（I1–I2）。

### ⚠️ 五个"差一点就写错"的细节（务必逐条核对）

1. **`10.1145/195058.195125` ≠ `.195122`**：minimum latency 是 `.125`；`.122` 是 MacKenzie/Plaxton/Rajaraman 的**另一篇**论文。（见 G3）
2. **Payne 是 1989 年，不是 1990 年**：Passerieux & Van Cappel (1998) 的参考文献表把年份误标为 1990。（见 H7）
3. **在线 TSP 竞争比数字的归属**：实数轴闭合变体的**紧值 1.64** 出自 Bjelde 等（G5）；Ausiello 等（G1）的 **1.75 是上界，不是下界**（其下界约 1.64）。不要把两者混淆。（见 G1/G5）
4. **Ascheuer/Krumke/Rambau 是 STACS 2000 的 Dial-a-Ride 论文**，不是 STOC 的 TSP 论文。（见 G6）
5. **Ausiello 等正式题名为 `Algorithms for the On-Line Travelling Salesman`**：首字母大写、travel**l**ing 双 L。（见 G1）

---

## M. 给论文写作的三条提醒

1. **交会角 90° 的说法务必配上 A3/A4 与 A1**：中文文献 A3（2005）明确以「圆概率误差最小」推出最优交会角并给出 GDOP 分布图；A4（2016）进一步说明存在系统误差时最优交会角会偏离。仅引用英文文献容易被认为未查中文资料，仅引中文文献则缺少理论溯源，两者并用最稳。
2. **K1/K2/K3 是三个"看起来像但还是别用"的坑**：GB/T 14432 是广播录音机抖晃测量（且已废止）、GB/T 6933 是短波单边带发射机测量（已被 GB/T 16946-2017 替代）、CTAN 上没有 cumcmthesis 包。这三项都已用官方页面原文证否，请勿出现在参考文献表中。
3. **凡标注 `verified` 的条目，建议在投稿前再各打开一次 URL 复核**（尤其 DOI 解析）。ITU 的 PDF 正文（B1/B2/B5）在本环境无法读取，若要在正文中直接引用其具体条款号或页码，请务必自行下载 PDF 核对后再写。

---

## N. 核实方法与访问失败透明度

### N.1 实际使用的核实工具与数据源

| 数据源 | 用途 | 说明 |
|---|---|---|
| `web_search` | 候选条目发现 | 搜索引擎结果文本会作为「外部不可信数据」返回，仅用于定位候选页面，不作为核实证据 |
| `web_fetch` | 抓取权威原始页面 | 本报告绝大多数证据来自此途径抓取的页面原文 |
| **Crossref REST API** | 期刊/会议/图书元数据 | 检索接口 `api.crossref.org/works?query.bibliographic=...`；**单条解析接口 `api.crossref.org/works/<DOI>` 更可靠**（不受检索限流影响）。返回的标题、作者、年份、卷、期、页、DOI 即本报告的权威字段 |
| **OpenLibrary API** | 图书 ISBN / 出版者 | `openlibrary.org/search.json`，用于 D1/D2/D3 的 ISBN 与出版者核实 |
| 全国标准信息公共服务平台 / 中国标准在线服务网 / 工标网 | 中国国标与行标 | 标准号、状态（现行/作废/废止）、发布与实施日期、起草单位 |
| 中国政府网 | 行政法规 | C1 的发文字号与施行日期 |
| 期刊官网（sys-ele.com、aeroweaponry.avic.com、coaa.istic.ac.cn 等） | 中文期刊论文 | 中文题名、作者、卷期页、DOI |
| CNKI 手机版 / AiPub | 中文论文补充核实 | A3、J2 |
| 高校图书馆 OPAC | 中文图书 ISBN | D4、J1 |
| ITU 官方建议书与出版物库 | ITU-R 建议书/报告/手册 | B1–B5 |
| CTAN | LaTeX 宏包 | I1（否定结论）、I2 |

### N.2 访问失败记录（**未用任何替代镜像或非授权来源绕过**）

| 目标 | 结果 | 影响 |
|---|---|---|
| ITU `R-REC-SM.2060-0-201411-I!!PDF-E.pdf` | **HTTP 406**（"Client browser does not accept the MIME type"） | B2 仅核实到题名/编号/日期/状态，**正文未读** |
| ITU `R-REC-SM.854-3-201109-I!!PDF-E.pdf` | **HTTP 406** | B1 同上 |
| ITU `R-HDB-23-2011-PDF-E.pdf`（手册正文） | PDF 类型不被抓取器支持 | B5 仅核实到题名/年份/持久链接/语种，**正文未读** |
| `https://ctan.org/pkg/cumcmthesis` | **HTTP 404** | 这是一个**已核实的否定结论**（K3），非失败 |
| Cambridge Core（E2 书章页） | 页面返回「Temporary Disruption / suspended」 | E2 改用 Dialnet + Crossref 核实 |
| zbMATH（`zbmath.org/65.0197.03`） | **HTTP 403**（Cloudflare 挑战） | Kershner 页码改由 E4（Weisstein 词条）核实 |
| Crossref 检索接口 | 间歇 **HTTP 429 Too Many Requests** | 改为**单条 DOI 解析** + 增加请求间隔后全部成功 |
| Semantic Scholar 页面 | HTTP 202（无正文） | 未采用其数据 |
| 现代雷达官网 `xdld.xml-journal.net` | 正文被截断（JS 渲染） | A5 改用国家科技期刊平台 coaa.istic.ac.cn 核实成功 |
| 万方学位论文详情页 | 仅返回框架页（需登录） | 相关中文学位论文**全部未采信**，未列入本报告 |

**说明**：检索过程中曾出现若干 Sci-Hub / LibGen 一类非授权全文镜像链接，**本报告一律未使用、未采信、未引用**。

### N.3 本报告未做、需要使用者自行完成的事项

1. **ITU-R 建议书正文条款与页码**（B1/B2/B5）——需自行下载官方 PDF 核对。
2. **A3 的页码 282–285** ——目前仅由二次文献著录，建议在 CNKI 下载原文首页核对。
3. **E2（Fejes Tóth）的出版年** ——MSRI 卷 52 与 Cambridge 版权页标注不一致（2005 / 2007），建议以手边版本为准。
4. **D1/D2 的具体版次 ISBN** ——OpenLibrary 在同一作品下并列多个 ISBN，建议以手边实物或出版社页面为准。
5. **本文未核实任何 2026 年 CUMCM B 题官方题面文件**（未检索到公开发布的题目原文），因此所有条目均为**通用方法学与技术规范**类文献，不对题目具体数据做任何断言。
