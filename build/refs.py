"""Find and resolve the cross-references of one Part of the Ethics.

    python3 build/refs.py 1        # writes mapping/refs-part1.csv

Each row is one link: the exact words that will become the link, the
item they appear in, and the item they point to. Rows the rules could
not settle with confidence are flagged "check" or "unresolved"; they are
settled by entries in mapping/overrides.csv, which this script applies.
"""

import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from structure import ROOT, parse, roman  # noqa: E402

OVERRIDES_CSV = os.path.join(ROOT, "mapping", "overrides.csv")

ROMAN_OK = re.compile(r"^(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$")

TOKEN_RE = re.compile(r"""
  (?P<lastprop>\b(?:the\s+)?(?:last|foregoing|preceding|previous)\s+(?:Prop\b\.?|[Pp]roposition\b))
| (?P<lastcor>\b(?:the\s+)?(?:last|foregoing|preceding)\s+(?:Coroll\b\.?|Corollary\b))
| (?P<gendef>\b(?:the\s+)?general\s+(?:Definition|definition|Def\.)\s+of\s+(?:the\s+)?Emotions\b)
| (?P<emodef>\bDef(?:f|s)?\.\s+of\s+(?:the\s+)?Emotions\b|\bDefinitions?\s+of\s+(?:the\s+)?Emotions\b)
| (?P<lemax>\bAx(?:iom)?\.?\s*(?P<lemaxn>[ivx]+)\.?,?\s+after\s+(?:the\s+Coroll\.\s+of\s+)?Lemma\s+iii\.(?:\s+after\s+(?:II\.\s+xiii\.|Prop\.\s+xiii\.))?)
| (?P<lemdef>\bDef(?:inition)?\.?\s+(?:before\s+Lemma\s+iv\.|after\s+Lemma\s+iii\.)(?:\s+after\s+(?:II\.\s+xiii\.|Prop\.\s+xiii\.))?)
| (?P<ofpart>\bof\s+(?:Part|part)\s+(?P<ofpartn>[IVX]+|[ivx]+)\b\.?)
| (?P<part>\b(?:Part|Pt\.|part)\s+(?P<partn>[IVX]+|[ivx]+)\b\.?)
| (?P<thispart>\bof\s+this\s+(?:part|Part|book)\b)
| (?P<partpre>\b(?P<partpren>[IVX]+)\.(?=\s*(?:(?:[ivxl]+|\d+)\b|Deff?\.|Ax\.|Post\.|Lemma|Prop\.|Def\b)))
| (?P<noteto>\b[Nn]otes?\s+(?:to|on)\b)
| (?P<mod>\b(?:Corolls?\b\.?|Corollary\b|Corollaries\b|[Nn]otes?\b\.?|[Ee]xplanation\b|Proof\b)
    (?:\s+(?:to|of)\b)?)
| (?P<kind>\b(?:Props?\b\.?|Propositions?\b|Deff?\.|Def\b|Definitions?\b|Ax\.|Axioms?\b\.?
    |Post\.|Postulates?\b|Lemmas?\b))
| (?P<num>\b(?:[ivxl]+|\d+)\b\.?)
| (?P<conn>\band\b|\bor\b|&|,|;)
""", re.X)

KIND_OF = [
    (r"Prop", "prop"), (r"Def", "def"), (r"Ax", "ax"), (r"Post", "post"),
    (r"Lemma", "lem"),
]
MOD_OF = [(r"Coroll", "cor"), (r"[Nn]ote", "note"), (r"[Ee]xplanation", "expl"),
          (r"Proof", "proof")]


def kind_of(word, table):
    for prefix, k in table:
        if re.match(prefix, word):
            return k
    return None


def numval(s):
    s = s.rstrip(".")
    if s.isdigit():
        return int(s)
    if not ROMAN_OK.match(s):
        return None
    return roman(s)


class Link:
    def __init__(self, start, part, kind, num, explicit_part):
        self.start = start
        self.end = None
        self.part = part
        self.kind = kind
        self.num = num
        self.mods = []          # [(mod, number or 0)]
        self.explicit_part = explicit_part
        self.flag = "ok"
        self.rule = "pattern"


AHEAD_RE = re.compile(r"\s*(?:(?:[ivxl]+\b\.?|\d+)\s*)?,?\s*(?:of\s+|to\s+)?"
                      r"(?:Props?\b|[IVX]+\.\s+[ivxl]+\b)")


def scan(text, cur_part):
    """Return a list of Link objects found in one paragraph's text."""
    links = []
    toks = list(TOKEN_RE.finditer(text))

    chain = False          # inside a reference chain
    part, explicit = cur_part, False
    kind = None
    link_start = None
    pending = []           # modifiers seen before their proposition
    last = None            # last Link created in this chain
    after_conn = False
    expect_modnum = False
    prev_end = 0
    chain_start = 0

    def reset():
        nonlocal chain, part, explicit, kind, link_start, pending, last, after_conn, expect_modnum
        chain, part, explicit, kind = False, cur_part, False, None
        link_start, pending, last, after_conn, expect_modnum = None, [], None, False, False

    for m in toks:
        g = None
        # which top-level group matched?
        for name in ("lastprop", "lastcor", "gendef", "emodef", "lemax", "lemdef",
                     "ofpart", "part", "thispart", "partpre", "noteto", "mod", "kind", "num", "conn"):
            if m.group(name) is not None:
                g = name
                break
        gap = text[prev_end:m.start()]
        if chain and (gap.strip(" \n.") != ""):
            reset()
        prev_end = m.end()
        tok = m.group(0)

        if g == "conn":
            if chain:
                after_conn = after_conn or tok.strip() in ("and", "or", "&")
                expect_modnum = False
            continue

        if g == "lastprop":
            l = Link(m.start(), cur_part, "prop", None, False)
            l.end, l.rule = m.end(), "last-prop"
            links.append(l)
            reset()
            chain, last, chain_start = True, l, m.start()
            continue
        if g == "lastcor":
            l = Link(m.start(), cur_part, "lastcor", None, False)
            l.end, l.rule, l.flag = m.end(), "last-coroll", "check"
            links.append(l)
            reset()
            continue
        if g == "gendef":
            l = Link(m.start(), 3, "emodef", "gen", True)
            l.end = m.end()
            links.append(l)
            reset()
            continue
        if g == "lemax":
            l = Link(m.start(), 2, "lemax", numval(m.group("lemaxn")), True)
            l.end = m.end()
            links.append(l)
            reset()
            continue
        if g == "lemdef":
            l = Link(m.start(), 2, "lemdef", 0, True)
            l.end = m.end()
            links.append(l)
            reset()
            continue
        if g == "emodef":
            reset()
            chain, kind, part, explicit = True, "emodef", 3, True
            link_start = chain_start = m.start()
            continue
        if g == "ofpart":
            # trailing qualifier only: "Prop. xxviii. of Part i."
            if chain and last is not None and not explicit:
                n = numval(m.group("ofpartn").lower())
                for l in links:
                    if l.start >= chain_start and not l.explicit_part:
                        l.part, l.explicit_part = n, True
            reset()
            continue
        if g == "thispart":
            if chain and last is not None:
                for l in links:
                    if l.start >= chain_start and not l.explicit_part:
                        l.part, l.explicit_part = cur_part, True
            reset()
            continue
        if g == "part":
            n = numval(m.group("partn").lower())
            if chain and last is not None and not explicit:
                # trailing qualifier: "Prop. vii. of Part i." / "Prop. xi., Part i."
                for l in links:
                    if l.start >= chain_start and not l.explicit_part:
                        l.part, l.explicit_part = n, True
                reset()
                continue
            if not chain:
                reset()
                chain, chain_start = True, m.start()
            part, explicit = n, True
            link_start = m.start() if link_start is None else link_start
            kind = kind or "prop"
            continue
        if g == "partpre":
            if not chain:
                reset()
                chain, chain_start = True, m.start()
            part, explicit, kind = roman(m.group("partpren")), True, "prop"
            link_start = m.start()
            after_conn = False
            continue
        if g == "noteto":
            if not chain:
                reset()
                chain, chain_start = True, m.start()
            pending.append(("note", 0))
            link_start = m.start() if link_start is None else link_start
            continue
        if g == "mod":
            mod = kind_of(tok, MOD_OF)
            # "and Coroll. Prop. xiii." / "and note 2, Prop. viii.": the
            # modifier belongs to the proposition that follows it
            ahead = AHEAD_RE.match(text, m.end())
            if chain and after_conn and ahead:
                last, after_conn = None, False
                link_start = m.start()
            if chain and last is not None and not after_conn and not pending:
                last.mods.append((mod, 0))
                last.end = m.end() if not tok.endswith((" to", " of")) else m.start() + len(tok.split()[0])
                expect_modnum = True
            elif chain and last is not None and after_conn:
                # "II. vii. and Coroll." -> new link on the same base
                base_kind = last.kind if last.kind == "prop" or not last.mods else last.kind
                l = Link(m.start(), last.part, base_kind, last.num, last.explicit_part)
                l.mods = [(mod, 0)]
                l.end = m.start() + len(tok.split()[0])
                links.append(l)
                last, after_conn, expect_modnum = l, False, True
            else:
                if not chain:
                    reset()
                    chain, chain_start = True, m.start()
                pending.append((mod, 0))
                link_start = m.start() if link_start is None else link_start
                expect_modnum = True
            continue
        if g == "kind":
            k = kind_of(tok, KIND_OF)
            if tok in ("Definition", "Definitions", "Axiom", "Axioms", "Proposition",
                       "Propositions", "Postulate", "Postulates") and not chain:
                # prose words; only references when a number follows
                pass
            if not chain:
                reset()
                chain, chain_start = True, m.start()
            kind = k
            if link_start is None:
                link_start = m.start()
            after_conn = False
            expect_modnum = False
            continue
        if g == "num":
            v = numval(tok)
            if v is None or not chain or kind is None and not pending:
                if chain and v is None:
                    reset()
                continue
            if expect_modnum and last is not None and last.mods and last.mods[-1][1] == 0 and not pending:
                mod = last.mods[-1][0]
                last.mods[-1] = (mod, v)
                last.end = m.end()
                expect_modnum = False
                continue
            if expect_modnum and pending and pending[-1][1] == 0:
                pending[-1] = (pending[-1][0], v)
                expect_modnum = False
                continue
            k = kind or "prop"
            l = Link(link_start if link_start is not None else m.start(), part, k, v, explicit)
            l.end = m.end()
            if pending:
                l.mods = pending
                pending = []
            links.append(l)
            last = l
            link_start = None
            after_conn = False
            expect_modnum = False
            continue
    # links whose span ends with a trailing comma/space: trim
    for l in links:
        while l.end > l.start and text[l.end - 1] in " ,":
            l.end -= 1
    return [l for l in links if l.num is not None or l.kind in ("prop", "lastcor")]


# ------------------------------------------------------------- resolution

def resolve(l, byid, ctx):
    """Map a Link to an item id. Returns (id or '', note)."""
    part = l.part
    if l.rule == "last-prop":
        if ctx["prop"] is None:
            return "", "no current proposition"
        if ctx["kind"] == "proof" and not ctx["in_cor"]:
            # in the proof of Prop. n, "the last Prop." is Prop. n-1
            return "p%d-prop%d" % (part, ctx["prop"] - 1), ""
        # in a corollary or note it usually means the Prop. just proved
        return ("p%d-prop%d" % (part, ctx["prop"]),
                "in a %s: taken as the Prop. it belongs to" % ctx["kind"])
    if l.kind == "lastcor":
        return ctx.get("last_cor", "") or "", "most recent corollary before the source"
    if l.kind == "lemax":
        return "p2-lem3-ax%d" % l.num, ""
    if l.kind == "lemdef":
        return "p2-lem3-def", ""
    if l.kind == "emodef":
        return ("p3-emodef-gen" if l.num == "gen" else "p3-emodef%d" % l.num), ""
    if l.kind == "lem":
        base = "p2-lem%d" % l.num
    else:
        base = "p%d-%s%d" % (part, l.kind, l.num)
    for mod, n in l.mods:
        cand = ["%s-%s%s" % (base, mod, n)] if n else ["%s-%s" % (base, mod), "%s-%s1" % (base, mod)]
        hit = [c for c in cand if c in byid]
        if not hit:
            return "", "no item %s" % cand[0]
        if not n and hit[0].endswith("1") and "%s-%s2" % (base, mod) in byid:
            return hit[0], "unnumbered %s but %s has several" % (mod, base)
        base = hit[0]
    if base not in byid:
        return "", "no item %s" % base
    return base, ""


def load_overrides():
    rows = []
    if os.path.exists(OVERRIDES_CSV):
        with open(OVERRIDES_CSV, newline="", encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["source"].strip()]
    return rows


def find_occurrence(text, needle, n):
    pos = -1
    for _ in range(n):
        pos = text.find(needle, pos + 1)
        if pos < 0:
            return -1
    return pos


def collect(part_no):
    paras, items = parse()
    byid = {it.id: it for it in items}
    order = {it.id: i for i, it in enumerate(items)}
    rows = []
    last_cor = ""
    for pi, p in enumerate(paras):
        if p["part"] != part_no or p["item"] in (None, "footnote"):
            continue
        src = byid[p["item"]]
        top = src
        while top.parent and top.parent in byid and byid[top.parent].kind != "app":
            top = byid[top.parent]
        ctx = {"prop": top.number if top.kind == "prop" else None,
               "kind": src.kind, "last_cor": last_cor,
               "in_cor": src.parent in byid and byid[src.parent].kind == "cor"}
        for l in scan(p["text"], part_no):
            target, note = resolve(l, byid, ctx)
            flag = l.flag
            if not target:
                flag = "unresolved"
            elif note and flag == "ok":
                flag = "check"
            elif target and order.get(target, 0) >= order[src.id] and flag == "ok":
                flag, note = "check", "forward or self reference"
            rows.append({"para": pi, "source": src.id, "start": l.start, "end": l.end,
                         "text": p["text"][l.start:l.end], "target": target,
                         "rule": l.rule, "flag": flag, "note": note})
        if src.kind == "cor" and p["first"]:
            last_cor = src.id

    # number occurrences of the same text inside the same source item
    seen = {}
    for r in rows:
        key = (r["source"], r["text"])
        seen[key] = seen.get(key, 0) + 1
        r["occ"] = seen[key]

    # overrides
    for o in load_overrides():
        if byid.get(o["source"]) is None or byid[o["source"]].part != part_no:
            continue
        hits = [r for r in rows if r["source"] == o["source"] and r["text"] == o["text"]
                and (not o["occ"] or r["occ"] == int(o["occ"]))]
        if o["action"] == "add":
            if hits:
                continue
            it = byid[o["source"]]
            occ = int(o["occ"] or 1)
            for pi in it.paras:
                pos = find_occurrence(paras[pi]["text"], o["text"], occ)
                if pos >= 0:
                    break
                occ -= paras[pi]["text"].count(o["text"])
            else:
                print("override not found:", o, file=sys.stderr)
                continue
            rows.append({"para": pi, "source": o["source"], "start": pos,
                         "end": pos + len(o["text"]), "text": o["text"],
                         "target": o["target"], "rule": "manual", "flag": "ok",
                         "note": o["note"], "occ": int(o["occ"] or 1)})
            continue
        if not hits:
            print("override matches nothing:", dict(o), file=sys.stderr)
            continue
        for r in hits:
            if o["action"] == "skip":
                r["flag"], r["target"], r["rule"] = "skip", "", "manual"
            else:
                r["target"], r["flag"], r["rule"] = o["target"], "ok", "manual"
            r["note"] = o["note"]
    for r in rows:
        if r["flag"] != "skip" and r["target"] and r["target"] not in byid:
            r["flag"], r["note"] = "unresolved", "unknown id " + r["target"]
    rows.sort(key=lambda r: (r["para"], r["start"]))

    for r in rows:
        s = byid[r["source"]]
        t = byid.get(r["target"])
        txt = paras[r["para"]]["text"]
        r["source_label"] = s.label
        r["target_label"] = (("" if t.part == part_no else "Part %s, " % PART_ROMAN[t.part])
                             + t.label) if t else ""
        r["context"] = txt[max(0, r["start"] - 50):r["end"] + 30]
    return rows


PART_ROMAN = ["", "I", "II", "III", "IV", "V"]

COLS = ["para", "source", "source_label", "text", "occ", "target", "target_label",
        "rule", "flag", "note", "start", "end", "context"]


def write(part_no, rows):
    out = os.path.join(ROOT, "mapping", "refs-part%d.csv" % part_no)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return out


RESIDUE_RE = re.compile(r"\b(Props?\b|Deff?\b|Def\.|Ax\b|Axiom|Post\b|Postulate|Lemma|Coroll|"
                        r"Corollary|[Nn]otes? (?:to|on)\b|[IVX]+\. [ivxl]+\b|"
                        r"(?:last|foregoing|preceding|same) (?:Prop|Def|Ax|Post|Coroll|note))")


def m0(p):
    return False


def residue(part_no, rows):
    """Reference-like words not covered by any link: possible misses."""
    paras, items = parse()
    spans = {}
    for r in rows:
        spans.setdefault(r["para"], []).append((int(r["start"]), int(r["end"])))
    out = []
    for pi, p in enumerate(paras):
        if p["part"] != part_no or p["item"] in (None, "footnote") or (p["first"] and m0(p)):
            continue
        for m in RESIDUE_RE.finditer(p["text"]):
            if p["first"] and m.start() < 12:
                continue      # the item's own heading ("Corollary I.", "PROP. ...")
            if any(a <= m.start() < b for a, b in spans.get(pi, [])):
                continue
            out.append((pi, p["item"], p["text"][max(0, m.start() - 60):m.end() + 40]))
    return out


if __name__ == "__main__":
    part_no = int(sys.argv[1])
    rows = collect(part_no)
    out = write(part_no, rows)
    if "--residue" in sys.argv:
        for pi, item, ctx in residue(part_no, rows):
            print("%5d %-22s %s" % (pi, item, ctx.replace("\n", " ")))
    from collections import Counter
    print(Counter(r["flag"] for r in rows), len(rows), "links ->", out)
