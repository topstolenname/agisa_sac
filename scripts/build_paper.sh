#!/usr/bin/env bash
set -euo pipefail
mkdir -p build

INPUT="docs/Mindlink_Paper.md"
DATE="$(date +%Y-%m-%d)"
PDF_OUT="build/Mindlink_Paper_${DATE}.pdf"
HTML_OUT="build/Mindlink_Paper_${DATE}.html"

# HTML
pandoc "$INPUT"   --from markdown   --to html5   --metadata title="Mindlink Integrated Paper"   --standalone   --toc --toc-depth=3   -o "$HTML_OUT"

# PDF (uses wkhtmltopdf or LaTeX engine if available)
pandoc "$INPUT"   --from markdown   --pdf-engine=xelatex   --variable mainfont="DejaVu Serif"   --variable monofont="DejaVu Sans Mono"   --variable geometry:margin=1in   --toc --toc-depth=3   -o "$PDF_OUT"

echo "HTML: $HTML_OUT"
echo "PDF:  $PDF_OUT"