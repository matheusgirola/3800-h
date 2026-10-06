"""Write mapping/ethics-dependencies.xlsx from items.csv and refs-partN.csv.

    python3 build/report.py

Sheets:
  Items         every numbered item, with how many references it makes and receives
  References    every link, one row each (the refs-partN.csv files together)
  Dependencies  one row per item that cites something: what it cites and what cites it
The CSV files remain the source of truth; this workbook is a generated view.
"""

import csv
import os
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from structure import ROOT  # noqa: E402

MAP = os.path.join(ROOT, "mapping")
OUT = os.path.join(MAP, "ethics-dependencies.xlsx")
PART_ROMAN = ["", "I", "II", "III", "IV", "V"]


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sheet(wb, title, header, rows, widths):
    ws = wb.create_sheet(title)
    ws.append(header)
    for r in rows:
        ws.append(r)
    for c in ws[1]:
        c.font = Font(bold=True)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
        if w >= 40:
            for cell in ws[get_column_letter(i)][1:]:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
    return ws


def main():
    items = read(os.path.join(MAP, "items.csv"))
    byid = {it["id"]: it for it in items}
    refs, parts_done = [], []
    for p in range(1, 6):
        path = os.path.join(MAP, "refs-part%d.csv" % p)
        if os.path.exists(path):
            parts_done.append(p)
            refs += [dict(r, part=p) for r in read(path)]
    live = [r for r in refs if r["flag"] in ("ok", "check") and r["target"]]

    cites, cited_by = {}, {}
    for r in live:
        cites.setdefault(r["source"], []).append(r["target"])
        cited_by.setdefault(r["target"], []).append(r["source"])

    def lab(i):
        it = byid[i]
        return "%s %s" % (PART_ROMAN[int(it["part"])], it["label"])

    def uniq(seq):
        seen, out = set(), []
        for x in seq:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    wb = Workbook()
    wb.remove(wb.active)
    sheet(wb, "Items",
          ["id", "part", "kind", "label", "parent", "words", "cites", "cited by", "opening words"],
          [[it["id"], int(it["part"]), it["kind"], it["label"], it["parent"], int(it["words"]),
            len(cites.get(it["id"], [])), len(cited_by.get(it["id"], [])), it["start"]]
           for it in items],
          [20, 6, 8, 30, 16, 8, 8, 9, 70])
    sheet(wb, "References",
          ["part", "source", "source label", "words linked", "target", "target label",
           "flag", "rule", "note", "context"],
          [[r["part"], r["source"], r["source_label"], r["text"], r["target"], r["target_label"],
            r["flag"], r["rule"], r["note"], r["context"]] for r in refs],
          [6, 20, 24, 22, 20, 26, 9, 10, 40, 70])
    dep_rows = []
    for it in items:
        if int(it["part"]) not in parts_done:
            continue
        out = uniq(cites.get(it["id"], []))
        inn = uniq(cited_by.get(it["id"], []))
        if not out and not inn:
            continue
        dep_rows.append([it["id"], lab(it["id"]), len(out), "; ".join(lab(t) for t in out),
                         len(inn), "; ".join(lab(s) for s in inn)])
    sheet(wb, "Dependencies",
          ["id", "item", "n cites", "cites", "n cited by", "cited by"],
          dep_rows, [20, 28, 8, 60, 10, 60])
    wb.save(OUT)
    print("%d references (%d live), parts %s -> %s" % (len(refs), len(live), parts_done, OUT))


if __name__ == "__main__":
    main()
