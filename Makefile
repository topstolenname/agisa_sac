.PHONY: paper html pdf site

paper: html pdf

html:
	bash scripts/build_paper.sh >/dev/null || true

pdf:
	bash scripts/build_paper.sh >/dev/null || true

site:
	mkdocs build