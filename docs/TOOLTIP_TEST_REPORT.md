# Cross-reference tooltips for PG eBook #3800: test log and design decisions

*Spinoza, The Ethics (trans. R. H. M. Elwes). Sample covers Part I: Definitions, Axioms, Propositions I–VIII; §3.10 covers the change made for the full book. Last updated 2026-10-06.*

## 1. Summary

The goal is to let a reader hover over a reference in a proof, such as "This is clear from Deff. iii. and v.", and see the cited definition, axiom or proposition without leaving the page. The design has to stay within Project Gutenberg's rules and work for assistive technology.

After six iterations, the approach that passes every test so far is **variant D**:

```html
<a class="ref" href="#p1-def3" aria-describedby="p1-def3">Deff. iii.</a><span class="tip" data-tip="Def. III. By substance, I mean …" aria-hidden="true"></span>
```

- The reference is an ordinary internal link to the cited paragraph.
- `aria-describedby` points at the **cited paragraph itself**, so screen readers announce the original definition as the link's description.
- The visible pop-up is drawn by CSS (`::after { content: attr(data-tip) }`) from an attribute on an **empty** span. The cited text is never part of the document's content, so reading apps that ignore CSS neither show nor speak it.

**Why it took six iterations:** Dolphin EasyReader reads aloud any text inside the document content, whether it is hidden with CSS (`display: none`), HTML (`hidden`) or ARIA (`aria-hidden="true"`). Only text held in an attribute is safe. Variant D is the only design found that keeps a styled, keyboard-accessible tooltip, uses `aria-describedby` as PG requested, and is silent in EasyReader.

**Layout change for the full book (§3.10):** in the full book, the pop-up no longer floats over the text. It opens below the line containing the reference, as a full-width float, and pushes the following lines down. A first attempt with a plain block box flickered on hover; §3.10 explains why and how it was fixed.

**How it relates to PG's suggestions:** variant D uses `aria-describedby` and `aria-hidden`. It does **not** use `role="tooltip"`, because every way of keeping the tooltip text in an element failed in EasyReader. Section 7 lists every departure and addition.

## 2. Goal and Project Gutenberg constraints

Constraints found in PG's documentation and correspondence:

| Constraint | Source |
|---|---|
| No scripting of any kind; ebookmaker strips `<script>` elements | PG HTML FAQ; ebookmaker changelog |
| HTML must be valid; HTML5 + UTF-8 recommended for new uploads | PG submission how-to |
| CSS must use W3C Recommendation (REC) features | PG HTML5 guidance |
| Only HTML (and plain text) is submitted; PG generates EPUB/Kindle with ebookmaker. Hand-crafted EPUB/MOBI files are not accepted | PG submission how-to |
| PG prefers improving existing books to adding duplicates | *Forty-Five Years of Digitizing Ebooks* (PG #60600) |
| Accessibility checks are now required for novel markup; use `aria-describedby` and `role="tooltip"`; check with WAVE | PG reply #1 |
| Consider low-vision users on text-to-speech: NVDA, JAWS, Dolphin EasyReader, VoiceOver, Narrator | PG reply #2 |
| "There's an ARIA attribute that prevents text from being spoken" | PG reply #3 |
| EPUB 2 will be abandoned; only EPUB 3 matters | PG reply #4 |

## 3. Chronology

### 3.1 First CSS-only sample

The source file (`3800-h.htm`) is HTML 4.01 Transitional in ISO-8859-1. The sample was rebuilt as HTML5 in UTF-8 with:

- an `id` on every definition, axiom and proposition of Part I (`p1-def3`, `p1-ax4`, `p1-prop6`, `p1-prop6-cor`, …);
- 28 references in the proofs turned into internal links, with the cited text in a `data-tip` attribute shown by `a.ref:hover::after { content: attr(data-tip) }`;
- a transcriber's note explaining the addition.

Two layout bugs were found and fixed:

1. **Pop-up off the screen.** It was anchored to the link (`position: relative` on `<a>`, `width: 22em`). In a 265 px viewport, 16 of the 28 pop-ups overflowed the right edge, and the same would happen on desktop for references at the end of a line. **Fix:** anchor the pop-up to the paragraph (`p { position: relative }`, pop-up `left: 0; right: 0`) and leave its vertical position at the static position of the reference.
2. **Pop-up hiding the reference.** The static position is the top of the line containing the reference, so the pop-up covered that line. **Fix:** a top margin of about one line.

Text fidelity was checked by stripping tags from both files and comparing: the translation's text is identical to the original. The sample passed the W3C Nu HTML validator and the W3C CSS validator (CSS level 3) with no errors. This version was sent to PG.

### 3.2 ARIA tooltip markup (PG reply #1)

PG asked for `aria-describedby` with `role="tooltip"` and suggested WAVE. Each reference became:

```html
<a class="ref" href="#p1-def3" aria-describedby="tip-1">Deff. iii.</a><span class="tip" role="tooltip" id="tip-1">Def. III. …</span>
```

- The `.tip` span is `display: none` and becomes visible on `a.ref:hover`, `a.ref:focus` and `.tip:hover`, so the pointer can move onto the pop-up without it closing.
- A visible focus outline was added for keyboard users.
- **axe-core 4.10.2** (WCAG 2.0/2.1/2.2 A and AA, plus best practices) reported two best-practice violations: `landmark-one-main` and `region`. **Fix:** wrap the content in `<main>`. After that: 0 violations. Nine `color-contrast` items were reported as "incomplete", because axe cannot determine the background of overlapping positioned elements. The actual colours are black on white and black on `#fffbe8`.
- **WAVE was not run.** The online WAVE tool only accepts public URLs. The WAVE browser extension would work on the local file.
- **Escape dismissal (WCAG 1.4.13).** A CSS-only tooltip cannot be closed with Esc, because CSS cannot react to key presses. The tooltip closes when hover or focus moves away. This limitation was reported to PG.

### 3.3 Investigating Escape dismissal without JavaScript

HTML's new *interest invokers* (`interestfor` plus `popover="hint"`) give hover/focus tooltips with native Esc dismissal and no script. A prototype showed this cannot be used yet:

- The W3C Nu validator rejects it: *"Attribute interestfor not allowed on element a at this point."* (`popover="hint"` alone validates.)
- The W3C CSS validator rejects `position-area` and `interest-delay`. Both are needed to place and time the tooltip, and neither is a W3C Recommendation.
- Browser support: Chrome/Edge 142+, Firefox 149+, no Safari.

Not adopted. This was reported to PG with an offer to build a comparison sample.

### 3.4 Text-to-speech, first pass (PG reply #2)

- In Chromium, `innerText` and the text of a selection both exclude `display: none` content. The accessibility tree exposes only the link.
- **VoiceOver on macOS with Safari:** tabbing to a reference reads the link, then the cited definition as its description. Confirmed by the tester.
- **macOS Speak Selection in Safari:** did not read the tooltip text. Confirmed by the tester.

### 3.5 EPUB output

- A hand-built EPUB 3 of the same HTML (`sample_ebook3800.epub`) passed **EPUBCheck 5.4.0** with 0 messages (fatal, error, warning, info and usage).
- The HTML was then run through PG's online **ebookmaker 0.14.6** (log in `prototypes/ebookmaker/ebookmaker-log.txt`). HTML validation passed and all formats were generated. The only warnings were `dropping by-heading … by benedict de spinoza`, for the `<h3>by Benedict de Spinoza</h3>` title line, which ebookmaker leaves out of the table of contents.

What ebookmaker did to the markup:

| | EPUB 2 (`3800-epub.epub`) | EPUB 3 (`3800-images-epub3.epub`) |
|---|---|---|
| `aria-describedby` / `role="tooltip"` | **removed** (0 of 28) | kept (28 of 28) |
| `<main>` | n/a | kept |
| CSS `position`, `left`, `right` | removed | removed |
| CSS `box-shadow` | removed | kept |
| Extra CSS | none | `a[href] { text-decoration: underline }` appended after the author CSS, which overrides `text-decoration: none` on the references |
| EPUBCheck 5.4.0 | 0 errors | **1 error**, in ebookmaker's generated `toc.xhtml`: `attribute "aria-label" not allowed here` on `<nav epub:type="toc" role="doc-toc" aria-label="Table of Contents">`. Not caused by the sample's markup. |

Because `position` is removed, a pop-up shown on hover in a reading app appears in the flow of the text and pushes the following lines down, instead of floating.

### 3.6 Reading-app results with the ARIA version

- **Apple Books (macOS), EPUB 2 from ebookmaker:** speaking a text selection **read the tooltip text**. Books appears to take selection text without applying CSS.
- **Dolphin EasyReader:** the full text of every cited definition is **shown and read aloud inside the proof**. EasyReader ignores the CSS `display: none`.

### 3.7 Variants A and B

| Variant | Change | EasyReader result |
|---|---|---|
| **A**: `hidden` attribute | `<span class="tip" role="tooltip" hidden="hidden" id="tip-1">`; author CSS still shows it on hover/focus | Text hidden visually, **but still spoken** |
| **B**: `title` attribute | Cited text moved into the link: `<a class="ref" href="#p1-def3" title="Def. III. …">`; no span, no ARIA | **Passed**: nothing shown or spoken inline |

Notes:

- Building variant A as an EPUB failed at first. XHTML does not allow the minimized attribute `hidden`; it must be written `hidden="hidden"`. A `sed` replacement also changed only the first occurrence on each line (21 of 28) until the global flag was added.
- In variant A, author CSS (`a.ref:hover + .tip { display: block }`) overrides the browser's built-in rule for `[hidden]`. Hover was confirmed in Chromium.
- Variant B's tooltip is the browser's native one: mouse hover only (not keyboard focus), no styling, shown after a delay, and possibly truncated for long text in some browsers. Because its presentation is controlled by the browser, WCAG 1.4.13 does not apply to it. Screen readers expose `title` as the link's description.

### 3.8 Variant C: `aria-hidden` (PG reply #3)

`<span class="tip" role="tooltip" hidden="hidden" aria-hidden="true" id="tip-1">`

- **W3C Nu validator:** no errors, but 28 warnings: *"Attribute aria-hidden is unnecessary for elements that have attribute hidden."*
- **EPUBCheck 5.4.0:** 0 messages.
- **Accessible description:** computed with `dom-accessibility-api` 0.7.0, the description is still the definition text. The accessible-name spec includes hidden content when it is directly referenced by `aria-describedby`.
- **EasyReader: failed.** The definitions were still spoken, both in the hand-built EPUB and in the EPUB generated by ebookmaker.

**Conclusion from A and C:** EasyReader speaks any text in the document content, regardless of CSS, `hidden` or `aria-hidden`.

### 3.9 Variant D: final

The idea was to combine what made B pass (text only in an attribute) with what PG asked for (`aria-describedby`):

- The cited text moves to `data-tip` on an **empty** span. CSS draws the pop-up from it with `::after { content: attr(data-tip) }`, on hover, on keyboard focus, and while the pointer is over the pop-up.
- `aria-describedby` points to the **original paragraph** (`#p1-def3`), not to a copy.
- The empty span is `aria-hidden="true"`, so the generated pop-up is not announced a second time.
- The pop-up is generated on the span *after* the link, not on the link. If it were generated on the link itself, the pop-up text would become part of the link's accessible name while it is visible.

Verification:

- **W3C Nu validator:** 0 messages (the 28 warnings from C are gone).
- **W3C CSS validator:** no errors.
- **EPUBCheck 5.4.0:** 0 messages.
- **Text content:** with tags stripped, the paragraph text is identical to the original, including the raw `textContent`. No cited text is inside the proofs.
- **Accessible name and description** (`dom-accessibility-api` 0.7.0): name "Deff. iii.", description "III. By substance, I mean that which is in itself…". The name is unchanged while the pop-up is visible.
- **Chromium:** the pop-up appears on hover below the reference line.
- **EasyReader: passed.** Reported by the tester.

### 3.10 In-flow pop-up (full book)

After the full book was converted (all five Parts, 1394 references, generated by `build/build_html.py` into `3800-h-tooltips.html`), the pop-up was changed so that it **pushes the text down instead of covering it**. The markup and ARIA are unchanged from variant D; only the CSS is different. This took two attempts.

**First attempt: block box.** `position: absolute`, `z-index`, `left`, `right` and the one-line `margin-top` were removed, the pop-up became an ordinary `display: block` box, and `p { position: relative }` was removed. The `::after` box was then a block inside an inline element, so the line containing the reference ended just after the reference, and the rest of the sentence continued below the pop-up. **The pop-up flickered on hover.** A script compared each reference's position with the pop-up closed and open (applying the pop-up rule through a test class, because the pop-up cannot be opened from a script by hover or focus):

- In 219 of the first 300 references, the link moved sideways when its pop-up opened, by up to 68 px. Cutting the line short after the reference turned it from a justified line into the last line of a block, which is not justified. The link slid out from under the pointer, the pop-up closed, the line was justified again, the link was back under the pointer, and the cycle repeated.
- For every reference, there was a strip between the link and the pop-up (its 0.3em top margin plus the line's leading) that belonged to neither. Moving the pointer down onto the pop-up crossed it and closed the pop-up.

**Second attempt: full-width float (current).** The pop-up is `float: left; width: 100%` (`box-sizing: border-box`). A float that does not fit beside the content of the current line is placed below that line, so:

- the line containing the reference is laid out exactly as before, justified and complete, and the pop-up opens under it;
- the following lines are pushed down below the pop-up;
- the pop-up has a 0.3em **transparent** top border and a −0.3em top margin, so its box overlaps the bottom of the reference's line and there is no gap to cross; `background-clip: padding-box` keeps the background off that border, and an inset `box-shadow` draws the visible top edge;
- `p::after { content: ""; display: block; clear: both }` keeps a pop-up opened on the last line of a paragraph inside that paragraph, so the next paragraph moves down too.

With the same script on all 1394 references, at desktop width and at 375 px: **0 links move** when the pop-up opens, and for every reference the pointer passes from the link directly onto the pop-up.

Effects:

- **Nothing is hidden.** The pop-up no longer covers the lines below the reference, so they stay readable while it is open.
- **The reference and its line do not move,** so the pop-up does not flicker, and the pointer can move down onto the pop-up and keep it open (`.tip:hover`).
- **Cost:** while the pop-up is open, the paragraph is taller.
- **ebookmaker:** it removed `position`, `left` and `right` from the sample (§3.5). Whether it keeps `float`, `box-sizing`, `background-clip` and the `p::after` rule has not been checked. If it removes `float`, the pop-up falls back to the block-box layout of the first attempt, which still pushes the text down but cuts the line short.
- **WCAG 1.4.13:** the "Dismissible" requirement does not apply to additional content that does "not obscure or replace other content". The in-flow pop-up arguably falls under that exception, which would close the Esc-dismissal gap (§3.2, §3.3). W3C's Understanding document does not discuss content that pushes the page down, so this is an interpretation that PG should confirm.
- The axe-core "incomplete" `color-contrast` items in §3.2 were caused by overlapping positioned elements. They should disappear, but axe has not been re-run.

Verification of the full book after the change:

- **W3C Nu validator:** 0 messages.
- **W3C CSS validator (CSS level 3):** no errors.
- **Text content:** identical to the original (517,424 characters, tags stripped).
- **Chromium:** the position script above, plus screenshots of an open pop-up mid-paragraph, on the last line of a paragraph, and at 375 px. Real mouse hover could not be simulated in the test browser, so hovering is to be confirmed by hand.
- **Not yet re-tested** with this layout: EasyReader, VoiceOver, Apple Books, the ebookmaker EPUB 3, EPUBCheck and axe. Screen-reader behaviour should not change, because the markup and ARIA are the same as in variant D.

The variant D sample (`prototypes/teste_D_describedby.html` / `.epub`), which is the one tested in §3.9, keeps the earlier overlaid layout.

## 4. Test matrix

✅ = behaves as intended · ❌ = problem · — = not tested

| | ARIA span (§3.2) | A: `hidden` | B: `title` | C: `hidden` + `aria-hidden` | **D: `data-tip` + describedby → source** |
|---|---|---|---|---|---|
| W3C Nu HTML | ✅ 0 | ✅ 0 | ✅ 0 | ⚠️ 28 warnings | ✅ 0 |
| W3C CSS (level 3) | ✅ | — | ✅ | — | ✅ |
| EPUBCheck 5.4.0 (hand-built EPUB 3) | ✅ 0 | ✅ 0 | ✅ 0 | ✅ 0 | ✅ 0 |
| axe-core 4.10.2 | ✅ 0 violations (after `<main>`) | — | — | — | — |
| Styled pop-up on hover | ✅ | ✅ | ❌ native only | ✅ | ✅ |
| Pop-up on keyboard focus | ✅ | ✅ | ❌ | ✅ | ✅ |
| VoiceOver + Safari, description on Tab | ✅ | — | — | — (spec computation ✅) | — (spec computation ✅) |
| Speak Selection, Safari (HTML) | ✅ not read | — | — | — | — |
| Apple Books, Speak Selection | ❌ read (EPUB 2) | — | — | — | — |
| **Dolphin EasyReader** | ❌ shown and read | ❌ read | ✅ | ❌ read | ✅ |
| `role="tooltip"` present | ✅ | ✅ | ❌ | ✅ | ❌ |

The full book (§3.10) uses variant D markup with an in-flow pop-up. So far it has been checked with the Nu and CSS validators, text fidelity and Chromium layout.

## 5. Problems found and resolutions

| # | Problem | Resolution |
|---|---|---|
| 1 | Pop-up overflowed the right edge of the screen | Anchored to the paragraph, full paragraph width |
| 2 | Pop-up covered the line containing the reference | Pushed down one line with a top margin. In the full book, the pop-up is in the flow and covers nothing (§3.10) |
| 3 | axe: no `main` landmark; content outside landmarks | Wrapped content in `<main>` |
| 4 | Tooltip cannot be dismissed with Esc (WCAG 1.4.13) without JavaScript | Investigated `interestfor` + `popover`; rejected (invalid HTML/CSS, no Safari). The in-flow pop-up of the full book obscures nothing, so the requirement arguably no longer applies (§3.10). **To be confirmed with PG** |
| 5 | ebookmaker EPUB 2 strips all ARIA | Out of scope: PG is abandoning EPUB 2 |
| 6 | ebookmaker removes CSS positioning | Accepted at first: pop-ups flowed inline in reading apps. The full book now uses the in-flow layout everywhere (§3.10) |
| 7 | ebookmaker appends `a[href] { text-decoration: underline }` | Cosmetic, open (references get both an underline and the dotted border) |
| 8 | EPUBCheck error in ebookmaker's own `toc.xhtml` (`aria-label` on `nav`) | Not ours; to be reported to PG |
| 9 | Apple Books Speak Selection reads hidden tooltip text | Solved by D, where no tooltip text is in the content (D not yet re-tested in Books) |
| 10 | EasyReader shows and speaks `display: none` text | Solved by D |
| 11 | EasyReader speaks `hidden` and `aria-hidden` text | Solved by D |
| 12 | Minimized `hidden` attribute broke the XHTML (EPUB) build | Written as `hidden="hidden"` |
| 13 | Nu warnings for `aria-hidden` together with `hidden` | Gone in D |
| 14 | Full book, first in-flow attempt: pop-up flickered on hover (the link moved when its line lost justification; gap between link and pop-up) | Full-width float below the line, overlapping it by a transparent top border (§3.10) |

## 6. Final implementation (variant D)

Markup, one reference:

```html
<p>
Proof.&mdash;This is clear from <a class="ref" href="#p1-def3" aria-describedby="p1-def3">Deff. iii.</a><span class="tip" data-tip="Def. III. By substance, I mean that which is in itself, and is conceived through itself: in other words, that of which a conception can be formed independently of any other conception." aria-hidden="true"></span> and <a class="ref" href="#p1-def5" aria-describedby="p1-def5">v.</a><span class="tip" data-tip="Def. V. By mode, I mean the modifications of substance, or that which exists in, and is conceived through, something other than itself." aria-hidden="true"></span>
</p>
```

CSS, as used in the full book (§3.10). The variant D sample differed only in the pop-up's layout: instead of the float, it used `display: block; position: absolute; z-index: 10; left: 0; right: 0; margin-top: 1.2em`, a plain border with `box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2)`, and `p { position: relative }` instead of the `p::after` rule.

```css
p { text-indent: 4%; }

p::after {  /* keeps an open pop-up on the last line inside its paragraph */
  content: "";
  display: block;
  clear: both;
}

a.ref {
  color: inherit;
  text-decoration: none;
  border-bottom: 1px dotted #555;
}

a.ref:focus {
  outline: 2px solid #1a5fb4;
  outline-offset: 1px;
}

a.ref:hover + .tip::after,
a.ref:focus + .tip::after,
.tip:hover::after {
  content: attr(data-tip);
  float: left;
  box-sizing: border-box;
  width: 100%;
  margin: -0.3em 0 0.4em;
  padding: 0.5em 0.7em;
  background: #fffbe8;
  background-clip: padding-box;
  color: black;
  border: 1px solid #b8a878;
  border-top: 0.3em solid transparent;
  box-shadow: inset 0 1px #b8a878;  /* the visible top edge */
  font-size: 0.9em;
  font-style: normal;
  line-height: 1.35;
  text-align: left;
  text-indent: 0;
  white-space: normal;
}

/* Briefly highlight the paragraph reached by following a reference. */
:target {
  background: #fff4c2;
}
```

What each audience gets:

| User | Behaviour |
|---|---|
| Mouse | Styled pop-up below the reference line, pushing the rest of the paragraph down; stays open while the pointer is over it |
| Keyboard | Visible focus outline and the same pop-up; Enter follows the link |
| Screen reader | Link name "Deff. iii."; description = the full text of the cited paragraph |
| Text-to-speech / apps ignoring CSS | Hears only "Deff. iii."; can follow the link |
| Touch | Tapping follows the link (no hover on touch screens) |
| No CSS at all | Plain internal links; nothing added to the text |

Conventions:

- **Pop-up text** is the cited item's number and full statement, e.g. `Def. III. …` or `Prop. VI, Corollary. …`. Footnote markers (the `[1]` in Def. V) are omitted.
- **Each item in a list** such as "Deff. iii. and v." gets its own link.
- **"The last Prop."** links to the preceding proposition.
- **The screen-reader description** is the paragraph's own text, so it starts with the original numbering ("III.", "PROP. IV."), and Def. V includes its footnote marker "[1]".

## 7. What goes beyond or departs from PG's suggestions

### PG's suggestions and what was done

| PG suggestion | In variant D | Notes |
|---|---|---|
| `aria-describedby` | ✅ Used | **Extended:** it points at the original cited paragraph rather than at a tooltip element, so no duplicated hidden text is needed |
| `role="tooltip"` | ❌ **Not used** | Every variant that kept the text in a tooltip element (§3.2, A, C) was read aloud by EasyReader. The pop-up is now generated content, which has no element to carry the role |
| WAVE | ❌ **Not run** | The online WAVE only accepts public URLs. axe-core 4.10.2 was used instead, on the §3.2 version only; it has **not** been re-run on D |
| An ARIA attribute that prevents speech (`aria-hidden`) | ✅ Used, differently | In C it hid the tooltip text (EasyReader ignored it). In D it hides the empty span, so the CSS-generated pop-up is not announced twice |

### Implemented on our own initiative

- HTML 4.01 / ISO-8859-1 → HTML5 / UTF-8, as PG recommends for uploads.
- Internal links on every reference, plus `id`s on every definition, axiom, proposition and corollary of Part I.
- The pop-up text is stored in a `data-tip` attribute and drawn with CSS `content: attr()`.
- The pop-up appears on keyboard focus as well as hover, with a visible focus outline.
- The pop-up stays open while hovered (`.tip:hover`), so it can be read.
- The pop-up spans the paragraph width and sits below the reference line, so it is never off-screen. In the full book it is in the flow and pushes the text down instead of covering it (§3.10).
- `:target` highlight on the paragraph reached through a link.
- `<main>` landmark.
- Transcriber's note explaining the cross-references.
- Text-fidelity check against the original file after every change.
- Accessibility metadata (`schema:accessibilityFeature`, etc.) in the hand-built test EPUBs only. These EPUBs are test files and are not meant for submission.
- Investigation of `interestfor` + `popover` for Esc dismissal (not adopted).

## 8. Tools, versions and files

### Tools

| Tool | Version | Use |
|---|---|---|
| W3C Nu HTML Checker | 26.9.30 (validator.w3.org/nu) | HTML validity |
| W3C CSS Validator | CSS level 3 profile (jigsaw.w3.org) | CSS validity |
| EPUBCheck | 5.4.0 (OpenJDK 11) | EPUB validity |
| PG ebookmaker | 0.14.6 (ebookmaker.pglaf.org) | Generate PG's EPUB 2/3 and Kindle files |
| axe-core | 4.10.2 | Automated accessibility audit |
| dom-accessibility-api | 0.7.0 | Accessible name/description per the W3C spec |
| Chromium (Claude browser pane) | n/a | Hover, `innerText`, selection and layout checks |
| VoiceOver + Safari, macOS | n/a | Screen-reader test (tester) |
| Apple Books, macOS | n/a | Speak Selection test (tester) |
| Dolphin EasyReader | n/a | Text-to-speech test (tester) |

### Files in the project folder

| File | Contents |
|---|---|
| `3800-h.htm` | Original PG HTML (unchanged) |
| `3800-h-tooltips.html` | Full book, all five Parts, variant D with in-flow pop-ups (§3.10); generated by `build/build_html.py` |
| `prototypes/sample_ebook3800.html` / `.epub` | ARIA `role="tooltip"` version (§3.2) and its hand-built EPUB 3 |
| `prototypes/ebookmaker/3800-epub.epub`, `3800-images-epub3.epub`, `ebookmaker-log.txt` | ebookmaker output for the §3.2 version, and its log |
| `prototypes/teste_A_hidden.epub` | Variant A |
| `prototypes/sample_ebook3800_title.html`, `teste_B_title.epub` | Variant B |
| `prototypes/teste_C_aria_hidden.html` / `.epub` | Variant C |
| `prototypes/teste_D_describedby.html` / `.epub` | **Variant D** sample, with the overlaid pop-up tested in §3.9 |

## 9. Open items and next steps

1. **Run WAVE** (browser extension) and **axe-core** on variant D. Neither has been run on D yet.
2. **Confirm variant D in:** VoiceOver + Safari (description on Tab), the ebookmaker EPUB 3 (check that `data-tip`, `aria-hidden` and the `::after` rule survive), and Apple Books Speak Selection.
3. **Untested screen readers:** NVDA, JAWS and Narrator (Windows).
4. **WCAG 1.4.13 Esc dismissal:** the in-flow pop-up of the full book obscures nothing and arguably falls under the requirement's exception (§3.10). Ask PG whether they agree, or whether the lack of Esc dismissal is acceptable in any case.
5. **Re-test the in-flow layout** of the full book: EasyReader, VoiceOver, Apple Books, the ebookmaker EPUB 3, EPUBCheck and axe.
6. **Report to PG:** the EPUBCheck error in ebookmaker's `toc.xhtml`, and the appended `a[href]` underline rule.
7. **Ask PG to confirm** that dropping `role="tooltip"` in favour of variant D is acceptable.
8. ~~**Full-book conversion**~~: done 2026-10-06. All five Parts have `id`s and 1394 references are linked (generated by the scripts in `build/`), and the text-fidelity comparison and the validators pass. The pop-up was then made in-flow (§3.10).
