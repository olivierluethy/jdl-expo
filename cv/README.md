# cv/

Tooling and sources for the repository owner's CV. This folder has nothing to do
with TuneVote or with news monitoring — it shares the repository only because it
shares a Python environment.

The workflow is: edit an HTML source in `templates/`, then render it to PDF with
the script in `scripts/`, and the result lands in `output/`.

## scripts/

| Script | Purpose |
|---|---|
| `convert_resume_html_to_pdf.py` | Render an HTML file to PDF through headless Chromium |

This is the most carefully written script in the repository and the only one
that was already documented before the reorganization. It uses Playwright to
drive Chromium, which means the PDF comes out of the same rendering and printing
code path as pressing Ctrl+P in Chrome. It waits for the network to settle and
for fonts to load, forces background colours into the PDF, freezes animations so
nothing is captured mid-frame, and honours the `@page` margins declared in the
document's own CSS instead of imposing its own.

It has a real command-line interface:

```bash
python cv/scripts/convert_resume_html_to_pdf.py cv/templates/olivier_luethy_cv_en.html \
    --output cv/output/olivier_luethy_cv_en.pdf
```

| Option | Effect |
|---|---|
| `--output`, `-o` | Output path (default: same name as input, `.pdf` extension) |
| `--scale` | CSS scale factor, 0.1–2.0 (default 1.0; only lower it if content overflows) |
| `--no-background` | Omit background colours and images |
| `--timeout` | Page-load timeout in ms (default 30000) |

**Setup gotcha:** installing the package is not enough. Playwright needs its
browser downloaded separately, and forgetting this produces an error only when
the script first launches Chromium:

```bash
pip install playwright
playwright install chromium
```

## templates/ — HTML sources

| File | Language | Note |
|---|---|---|
| `olivier_luethy_cv_en.html` | English | |
| `olivier_luethy_cv_de_2026-07-13.html` | German | Newest German source |
| `olivier_luethy_cv_de_2026-06-04.html` | German | Earlier German source |

The two German sources are near-identical in size and differ only slightly. They
are dated after the PDF renders they most plausibly produced, because nothing in
the files themselves distinguishes them — treat the date as a best-effort label
rather than a verified fact.

## output/ — rendered PDFs

| File | Created | Source language |
|---|---|---|
| `olivier_luethy_cv_de_2026-07-13.pdf` | 2026-07-13 | German — newest |
| `olivier_luethy_cv_2026-06-15.pdf` | 2026-06-15 | |
| `olivier_luethy_cv_2026-06-04.pdf` | 2026-06-04 | |
| `olivier_luethy_cv_de_2026-06-03.pdf` | 2026-06-03 | German |

All four are two-page A4 PDFs. The dates come from each file's own PDF metadata,
which was the only reliable way to tell four otherwise interchangeably-named
renders apart — the originals were called `resume.pdf`, `olivier_luethy_cv.pdf`,
`olivier_luethy_cv_de.pdf` and `Olivier Lüthy - CV - DE.pdf`.

Two of them are exactly the same size in bytes but are **not** identical files.

These are finished outputs and are kept deliberately; regenerating an old one
would need the exact source it was built from, which is not always recoverable.
