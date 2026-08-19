# Fix editable LaTeX report build

- Updated `hcmus-report-template.sty` to use Unicode-safe `fontspec` fonts under
  XeLaTeX/LuaLaTeX, while retaining a pdfLaTeX fallback.
- Added compile instructions to `docs/reports/main.tex`.
- Removed unsupported emoji glyphs from the report content.
- Verified two XeLaTeX passes produce `docs/reports/main.pdf` with 16 pages and
  no fatal errors or missing Vietnamese characters.

Known non-fatal layout warnings remain for a few long URLs/code/table lines.
