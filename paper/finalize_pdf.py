# -*- coding: utf-8 -*-
"""finalize_pdf.py -- move the freshly built electronic PDF into place.

Run this after closing any PDF viewer that has paper.pdf open.
"""
import os
import shutil
import time

HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(HERE, "paper_new.pdf")
dst = os.path.join(HERE, "paper.pdf")
if not os.path.exists(src):
    print("paper_new.pdf not found -- nothing to do")
    raise SystemExit(0)
for attempt in range(12):
    try:
        shutil.copyfile(src, dst)
        os.remove(src)
        print("paper.pdf updated from paper_new.pdf")
        break
    except PermissionError:
        print("paper.pdf is locked (close the PDF viewer), retry %d ..." % (attempt + 1))
        time.sleep(5)
else:
    print("still locked: the new build remains as paper_new.pdf")
