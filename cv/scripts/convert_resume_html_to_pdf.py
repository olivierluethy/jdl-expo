#!/usr/bin/env python3
"""
convert_resume_html_to_pdf.py — render an HTML resume to a pixel-perfect PDF with Playwright and Chromium.

Description:
    Converts an HTML CV to PDF through headless Chromium, which is the closest
    automated equivalent to opening the file in Chrome and printing it. The page
    is loaded from disk as a file:// URL so local fonts, stylesheets, images and
    SVGs resolve normally. The script waits for the network to go idle and for
    document.fonts to report ready, then injects a small stylesheet that forces
    background colours to be printed, freezes animations and transitions so
    nothing is captured mid-frame, and neutralizes collapsing margins at the page
    edges. It reads the @page margins out of the document's own stylesheets and
    honours them instead of imposing its own, then prints A4 at a 2x device scale
    for sharp text. GPU compositing is disabled so the output is identical on
    Windows, macOS and Linux.

Requirements:
    - Python 3.x
    - Packages: playwright — after installing it, run: playwright install chromium
    - External services: none; everything is rendered locally
    - Environment variables / credentials needed: none

Inputs:
    The path to an .html or .htm file, given as the first argument.
    Options: --output/-o, --scale, --no-background, --timeout.

Outputs:
    A PDF file. By default it is written next to the input with the same stem and
    a .pdf extension; --output overrides that. Missing parent directories are
    created. Progress and the final file size are printed to stdout.

Usage:
    # from the repository root, with the virtual environment activated
    python cv/scripts/convert_resume_html_to_pdf.py cv/templates/olivier_luethy_cv_en.html \
        --output cv/output/olivier_luethy_cv_en.pdf

Notes:
    The rendered PDFs already in cv/output were produced this way. Use --scale
    below 1.0 only if the content overflows the page width; the default of 1.0
    preserves the design exactly. --no-background omits background colours and
    images, which is useful for a print-friendly version. The default page-load
    timeout is 30 seconds. If Playwright is missing the script exits with an
    explanatory message rather than a traceback, but the separate
    "playwright install chromium" step is easy to forget and produces an error
    only when the browser is first launched.

    Why Playwright and Chromium, from the original author's notes:
      - Uses the same rendering engine as Google Chrome, the gold standard for
        HTML/CSS fidelity.
      - Loads local fonts, CSS, images and SVGs from disk without sandboxing
        issues.
      - Supports the CSS @page rule, so the HTML's own margin and page-size
        declarations are honoured.
      - Waits for full network idle and layout completion before printing, which
        eliminates flash-of-unstyled-content artefacts.
      - Chromium's PDF print path is the same code used by "Print to PDF" in
        Chrome, so the result matches opening the CV in Chrome and pressing
        Ctrl+P.
"""

import argparse
import asyncio
import sys
from pathlib import Path


# ── helpers ────────────────────────────────────────────────────────────────────

def _ensure_playwright() -> None:
    """Friendly error if Playwright is not installed."""
    try:
        import playwright  # noqa: F401
    except ImportError:
        sys.exit(
            "\n[ERROR] Playwright is not installed.\n"
            "Run:  pip install playwright && playwright install chromium\n"
        )


def _resolve_paths(html_path: str, output_path: str | None) -> tuple[Path, Path]:
    src = Path(html_path).resolve()
    if not src.exists():
        sys.exit(f"[ERROR] Input file not found: {src}")
    if not src.suffix.lower() in {".html", ".htm"}:
        sys.exit(f"[ERROR] Input file must be an HTML file, got: {src.suffix}")

    dst = Path(output_path).resolve() if output_path else src.with_suffix(".pdf")
    dst.parent.mkdir(parents=True, exist_ok=True)
    return src, dst


# ── CSS injection for print fidelity ──────────────────────────────────────────

FIDELITY_CSS = """
/* ── Playwright print-fidelity overrides ────────────────────────────────── *
 * These rules are injected AFTER your stylesheet so they only patch the     *
 * known gaps between screen rendering and Chromium's PDF print path.        *
 * They deliberately avoid touching layout, spacing, or color values so your *
 * original design is preserved exactly.                                     *
 * ─────────────────────────────────────────────────────────────────────── */

/* Force Chromium to emit background colours and images into the PDF.        */
* {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    color-adjust: exact !important;
}

/* Prevent phantom extra pages caused by collapsing margins at page edges.   */
html, body {
    /* Do NOT set height/overflow here — let your layout control that.        */
    margin: 0;
}

/* Disable CSS animations/transitions during the PDF snapshot so nothing is  *
 * caught mid-frame.                                                         */
*, *::before, *::after {
    animation-duration: 0s !important;
    transition-duration: 0s !important;
}
"""


# ── core conversion ────────────────────────────────────────────────────────────

async def convert(
    src: Path,
    dst: Path,
    *,
    scale: float = 1.0,
    print_background: bool = True,
    timeout_ms: int = 30_000,
) -> None:
    from playwright.async_api import async_playwright

    file_url = src.as_uri()  # file:///absolute/path/to/cv.html — loads local assets

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            # Disable GPU compositing so the PDF rasteriser is deterministic
            # across machines (same output on Windows, macOS, Linux).
            args=["--disable-gpu", "--no-sandbox"],
        )

        context = await browser.new_context(
            # A4 viewport gives Chromium the correct reference width for any
            # responsive CSS rules you may have.  96 dpi × 210 mm ≈ 794 px.
            viewport={"width": 794, "height": 1123},
            device_scale_factor=2,          # render at 2× for sharper text in PDF
        )

        page = await context.new_page()

        # ── 1. Load the HTML from disk ─────────────────────────────────────
        await page.goto(file_url, wait_until="networkidle", timeout=timeout_ms)

        # ── 2. Wait for fonts to finish loading ────────────────────────────
        await page.evaluate("() => document.fonts.ready")

        # ── 3. Inject fidelity CSS (after all stylesheets) ────────────────
        await page.add_style_tag(content=FIDELITY_CSS)

        # ── 4. Wait one more frame so the injected styles are painted ──────
        await page.wait_for_timeout(200)

        # ── 5. Read @page margins from the document if declared ────────────
        #       Playwright's pdf() accepts margin as a dict; we want to honour
        #       whatever the HTML author set in CSS @page {margin: …} rather
        #       than imposing our own.  If no @page rule exists we fall back to
        #       zero margins (i.e. the HTML itself controls whitespace via
        #       padding/margin on the body).
        page_margin = await page.evaluate("""() => {
            for (const sheet of document.styleSheets) {
                try {
                    for (const rule of sheet.cssRules) {
                        if (rule instanceof CSSPageRule) {
                            const s = rule.style;
                            return {
                                top:    s.marginTop    || '0',
                                right:  s.marginRight  || '0',
                                bottom: s.marginBottom || '0',
                                left:   s.marginLeft   || '0',
                            };
                        }
                    }
                } catch (_) { /* cross-origin sheet — skip */ }
            }
            return null;  // no @page rule found
        }""")

        margin = page_margin or {"top": "0", "right": "0", "bottom": "0", "left": "0"}

        # ── 6. Generate the PDF ────────────────────────────────────────────
        pdf_bytes = await page.pdf(
            format="A4",
            scale=scale,
            print_background=print_background,
            margin=margin,
            # prefer_css_page_size=True makes Chromium use the width/height from
            # the CSS @page rule (if present) instead of the `format` argument.
            prefer_css_page_size=True,
        )

        await browser.close()

    dst.write_bytes(pdf_bytes)


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    _ensure_playwright()

    parser = argparse.ArgumentParser(
        description="Convert an HTML CV to a pixel-perfect PDF using Chromium/Playwright.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("html", help="Path to the source HTML file")
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output PDF path (default: same directory/name as input, .pdf extension)",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="CSS scale factor for the PDF (0.1–2.0, default: 1.0). "
             "Use values < 1 only if content overflows the page width.",
    )
    parser.add_argument(
        "--no-background",
        dest="print_background",
        action="store_false",
        default=True,
        help="Omit CSS background colours and images from the PDF.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30_000,
        help="Page-load timeout in milliseconds (default: 30000).",
    )
    args = parser.parse_args()

    src, dst = _resolve_paths(args.html, args.output)

    print(f"[html_to_pdf] Source : {src}")
    print(f"[html_to_pdf] Output : {dst}")
    print(f"[html_to_pdf] Scale  : {args.scale}")
    print(f"[html_to_pdf] Rendering …")

    asyncio.run(
        convert(
            src,
            dst,
            scale=args.scale,
            print_background=args.print_background,
            timeout_ms=args.timeout,
        )
    )

    size_kb = dst.stat().st_size / 1024
    print(f"[html_to_pdf] Done    : {dst} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()