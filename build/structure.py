"""Parse the original PG HTML of the Ethics (3800-h.htm) into numbered items.

Every paragraph of the five Parts is assigned to a structural item
(definition, axiom, postulate, lemma, proposition, proof, corollary,
note, explanation, preface, appendix ...). The first paragraph of each
item receives an id; later paragraphs of the same item are continuations.

Run directly to (re)write mapping/items.csv:

    python3 build/structure.py
"""

import csv
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "3800-h.htm")
ITEMS_CSV = os.path.join(ROOT, "mapping", "items.csv")

ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}


def roman(s):
    s = s.upper()
    total = 0
    for i, ch in enumerate(s):
        v = ROMAN[ch]
        if i + 1 < len(s) and ROMAN[s[i + 1]] > v:
            total -= v
        else:
            total += v
    return total


def to_roman(n):
    out = ""
    for v, r in ((100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"),
                 (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out += r
            n -= v
    return out


def load_source():
    raw = open(SRC, "rb").read().decode("latin-1")
    return raw.replace("\r\n", "\n")


def plain(fragment):
    """Visible text of an HTML fragment, whitespace collapsed."""
    text = re.sub(r"<[^>]+>", " ", fragment)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------- blocks

BLOCK_RE = re.compile(
    r'<A NAME="(chap0\d)"></A>'
    r'|<(H[1-6])[^>]*>(.*?)</H[1-6]>'
    r'|<P([^>]*)>(.*?)</P>',
    re.S)


def blocks(src):
    """Yield (kind, attrs, inner, start, end) for the body of the Ethics."""
    start = src.index('<A NAME="chap01">')
    end = src.index("End of the Ethics by")
    for m in BLOCK_RE.finditer(src, start, end):
        if m.group(1):
            yield ("anchor", m.group(1), "", m.start(), m.end())
        elif m.group(2):
            yield ("h", m.group(2), m.group(3), m.start(), m.end())
        else:
            yield ("p", m.group(4), m.group(5), m.start(), m.end())


# ---------------------------------------------------------------- items

KIND_LABEL = {
    "def": "Def.", "ax": "Ax.", "post": "Post.", "lem": "Lemma",
    "prop": "Prop.", "proof": "Proof", "cor": "Coroll.", "note": "Note",
    "expl": "Explanation", "emodef": "Def. of the Emotions",
}


class Item:
    def __init__(self, id, part, kind, number, label, parent=""):
        self.id = id
        self.part = part
        self.kind = kind
        self.number = number
        self.label = label
        self.parent = parent
        self.paras = []        # indices into the paragraph list

    def row(self, paras):
        first = paras[self.paras[0]]
        return {
            "id": self.id, "part": self.part, "kind": self.kind,
            "number": self.number, "label": self.label,
            "parent": self.parent, "paragraphs": len(self.paras),
            "words": sum(len(paras[i]["text"].split()) for i in self.paras),
            "start": first["text"][:90],
        }


def parse():
    """Return (paras, items). paras: list of dicts with keys
    text, inner, attrs, start, end, item (id), first (bool)."""
    src = load_source()
    paras, items = [], []
    byid = {}
    part = 0
    section = ""
    prop = None          # current Proposition item
    lemma = None         # current Lemma item (Part II)
    last_numbered = None  # last top-level numbered item (def/ax/post/...)
    current = None       # item that continuation paragraphs belong to
    counters = {}

    def new(id, kind, number, label, parent=""):
        nonlocal current
        if id in byid:
            raise ValueError("duplicate id " + id)
        it = Item(id, part, kind, number, label, parent)
        items.append(it)
        byid[id] = it
        current = it
        return it

    def sub(base, kind, explicit_num):
        """Child item of `base` (corollary, note, explanation, proof)."""
        key = (base.id, kind)
        n = explicit_num or counters.get(key, 0) + 1
        counters[key] = n
        suffix = {"proof": "proof", "cor": "cor", "note": "note",
                  "expl": "expl"}[kind]
        id = "%s-%s%s" % (base.id, suffix, n if (explicit_num or n > 1) else "")
        return id, n

    for kind, attrs, inner, s, e in blocks(src):
        if kind == "anchor":
            part = int(attrs[-1])
            section, prop, lemma, current, last_numbered = "", None, None, None, None
            continue
        if kind == "h":
            title = plain(inner).upper().rstrip(".:")
            if title.startswith("PART"):
                continue
            section = title
            prop = lemma = last_numbered = None
            if section in ("PREFACE", "APPENDIX"):
                tag = {"PREFACE": "pref", "APPENDIX": "app"}[section]
                new("p%d-%s" % (part, tag), tag, "", section.title())
            elif section == "GENERAL DEFINITION OF THE EMOTIONS":
                new("p3-emodef-gen", "emodef", "",
                    "General Definition of the Emotions")
            else:
                current = None
            continue

        text = plain(inner)
        cls = re.search(r'CLASS="([^"]*)"', attrs or "")
        cls = cls.group(1) if cls else ""
        p = {"text": text, "inner": inner, "attrs": attrs, "cls": cls,
             "start": s, "end": e, "part": part, "item": None, "first": False}
        idx = len(paras)
        paras.append(p)
        if cls == "footnote":
            p["item"] = "footnote"
            continue

        it = None
        m = re.match(r"PROP\. ([IVXLC]+)\.", text)
        if m:
            n = roman(m.group(1))
            it = prop = new("p%d-prop%d" % (part, n), "prop", n,
                            "Prop. " + m.group(1))
            lemma = None
        elif re.match(r"(Proof|Another [Pp]roof|Second [Pp]roof)", text) and (lemma or prop):
            # a proof straight after a corollary proves that corollary
            base = current if current is not None and current.kind == "cor" else (lemma or prop)
            id, n = sub(base, "proof", 0)
            it = new(id, "proof", n, base.label + (", Another proof" if n > 1 else ", Proof"), base.id)
        elif re.match(r"(Corollary|Coroll\.)", text) and (lemma or prop):
            base = lemma or prop
            m = re.match(r"(?:Corollary|Coroll\.) ([IVX]+)\b", text)
            id, n = sub(base, "cor", roman(m.group(1)) if m else 0)
            it = new(id, "cor", n, base.label + ", Coroll." +
                     (" " + to_roman(n) if m else ""), base.id)
        elif re.match(r"Note\b", text) and (lemma or prop):
            m = re.match(r"Note ([IVX]+)\b", text)
            base = lemma or prop
            # An unnumbered note following a corollary belongs to the
            # proposition (Latin "Scholium"), unless the proposition already
            # has its note; then it is the corollary's note (e.g. III. xl.,
            # xli., lv.: "Corollarii Scholium").
            cor = None
            if current is not None and current.kind == "cor":
                cor = current
            elif current is not None and current.kind == "proof" and byid[current.parent].kind == "cor":
                cor = byid[current.parent]
            if not m and cor is not None and (base.id + "-note") in byid:
                base = cor
            id, n = sub(base, "note", roman(m.group(1)) if m else 0)
            it = new(id, "note", n, base.label + ", Note" +
                     (" " + to_roman(n) if m else ""), base.id)
        elif re.match(r"Explanation", text) and (current or last_numbered):
            base = last_numbered if last_numbered and current is last_numbered else (current or last_numbered)
            if base.kind in ("expl",):
                base = byid[base.parent]
            id, n = sub(base, "expl", 0)
            it = new(id, "expl", n, base.label + ", Explanation", base.id)
        elif re.match(r"N\.B\.", text):
            base = prop or last_numbered
            owner = base.id if base else "p%d-%s" % (part, section.lower()[:4])
            id = owner + "-nb"
            it = new(id, "nb", "", (base.label if base else section.title()) + ", N.B.", owner if base else "")
        else:
            # Part II physical digression after Prop. XIII
            m = re.match(r"(AXIOM|LEMMA|Axiom) ([IVX]+)\.", text)
            if m and part == 2:
                n = roman(m.group(2))
                if m.group(1) == "LEMMA":
                    it = lemma = new("p2-lem%d" % n, "lem", n, "Lemma " + m.group(2))
                    last_numbered = lemma
                elif m.group(1) == "AXIOM":      # before Lemma I
                    it = last_numbered = new("p2-ax%d-bodies" % n, "ax", n,
                                             "Axiom %s (after Prop. XIII)" % m.group(2))
                else:                              # after Lemma III
                    it = last_numbered = new("p2-lem3-ax%d" % n, "ax", n,
                                             "Axiom %s (after Lemma III)" % m.group(2))
                    lemma = None
            elif part == 2 and re.match(r"Definition\.", text):
                it = last_numbered = new("p2-lem3-def", "def", "",
                                         "Definition (after Lemma III)")
                lemma = None
            else:
                m = (re.match(r"DEFINITION ([IVXL]+)\.", text)
                     or re.match(r"([IVXL]+)\.(?=\s)", text))
                kinds = {"DEFINITIONS": "def", "AXIOMS": "ax", "AXIOM": "ax",
                         "POSTULATES": "post",
                         "DEFINITIONS OF THE EMOTIONS": "emodef"}
                k = kinds.get(section)
                if m and k:
                    n = roman(m.group(1))
                    label = ("%s %s" % (KIND_LABEL[k], m.group(1)) if k != "emodef"
                             else "Def. of the Emotions %s" % m.group(1))
                    it = last_numbered = new("p%d-%s%d" % (part, k, n), k, n, label)
                elif section == "APPENDIX" and part == 4 and re.match(r"([IVXL]+)\.\s", text):
                    n = roman(re.match(r"([IVXL]+)\.", text).group(1))
                    it = new("p4-app%d" % n, "app", n, "Appendix, " + to_roman(n), "p4-app")
                elif section == "AXIOM" and part == 4 and not m and last_numbered is None:
                    it = last_numbered = new("p4-ax1", "ax", 1, "Axiom")

        if it is None:
            if current is None and part == 3 and section == "ON THE ORIGIN AND NATURE OF THE EMOTIONS":
                current = new("p3-pref", "pref", "", "Preface")
            if current is None:
                current = new("p%d-%s-intro" % (part, re.sub(r"\W+", "", section.lower())[:12] or "x"),
                              "text", "", section.title() or "Text")
            it = current
        else:
            p["first"] = True
        p["item"] = it.id
        it.paras.append(idx)

    return paras, items


def write_items(paras, items):
    os.makedirs(os.path.dirname(ITEMS_CSV), exist_ok=True)
    cols = ["id", "part", "kind", "number", "label", "parent",
            "paragraphs", "words", "start"]
    with open(ITEMS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for it in items:
            w.writerow(it.row(paras))


if __name__ == "__main__":
    paras, items = parse()
    write_items(paras, items)
    from collections import Counter
    c = Counter((it.part, it.kind) for it in items)
    for part in range(1, 6):
        print("Part", part, {k: v for (p, k), v in sorted(c.items()) if p == part})
    print(len(items), "items,", len(paras), "paragraphs ->", ITEMS_CSV)
