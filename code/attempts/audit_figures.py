# -*- coding: utf-8 -*-
"""audit_figures.py -- measure the effective font size of every figure inside the
compiled paper and flag anything below the readability threshold.

    effective_pt = font_pt * display_width_in / figure_width_in
    display_width_in = \\includegraphics width fraction * 6.30 in  (A4, 2.5 cm margins)
    figure_width_in  = png width in px / savefig dpi
"""
import glob
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
FIGDIR = os.path.join(ROOT, "figures")
PAPER = os.path.join(ROOT, "paper")
DPI = 220.0
TEXTWIDTH_IN = 6.30
BASE_PT = 16.0
THRESHOLD = 9.0

# figure -> display width fraction in the paper
disp = {}
for f in glob.glob(os.path.join(PAPER, "paper_p*.tex")):
    s = io.open(f, encoding="utf-8").read()
    for m in re.finditer(r"includegraphics\[width=([0-9.]+)\\textwidth\]\{\.\./figures/([a-z0-9_]+\.png)\}", s):
        disp[m.group(2)] = float(m.group(1))

rows = []
try:
    from PIL import Image
    have_pil = True
except Exception:
    have_pil = False

for name in sorted(os.listdir(FIGDIR)):
    if not name.endswith(".png"):
        continue
    wpx = None
    if have_pil:
        with Image.open(os.path.join(FIGDIR, name)) as im:
            wpx = im.size[0]
    if wpx is None:
        continue
    fig_in = wpx / DPI
    frac = disp.get(name)
    if frac is None:
        rows.append((name, fig_in, None, None, "not used"))
        continue
    disp_in = frac * TEXTWIDTH_IN
    eff = BASE_PT * disp_in / fig_in
    rows.append((name, fig_in, frac, eff, "OK" if eff >= THRESHOLD else "TOO SMALL"))

rows.sort(key=lambda r: (r[3] if r[3] is not None else 99))
print("%-32s %8s %8s %8s  %s" % ("figure", "fig_in", "width_fr", "eff_pt", "verdict"))
for r in rows:
    print("%-32s %8.2f %8s %8s  %s"
          % (r[0], r[1], "-" if r[2] is None else "%.2f" % r[2],
             "-" if r[3] is None else "%.1f" % r[3], r[4]))
ok = [r for r in rows if r[3] is not None and r[3] >= THRESHOLD]
bad = [r for r in rows if r[3] is not None and r[3] < THRESHOLD]
print("\n%d figures in the paper, %d at/above %.1f pt, %d below"
      % (len([r for r in rows if r[3] is not None]), len(ok), THRESHOLD, len(bad)))
if bad:
    print("below threshold:", ", ".join("%s(%.1fpt)" % (r[0], r[3]) for r in bad))
