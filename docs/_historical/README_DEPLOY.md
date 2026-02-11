# Deployment & Versioning Guide (v1.0)

## One-Time Setup
1. Push this folder structure to your repo root (`agisa_sac/`).
2. In GitHub > Settings > Pages, set source to **GitHub Actions**.

## Build the Docs Site
- Auto on every push to `main` (see `.github/workflows/pages.yml`)
- Manual local build:
  ```bash
  pip install mkdocs-material mkdocstrings[python] mkdocs-mermaid2-plugin
  mkdocs serve  # http://127.0.0.1:8000
  ```

## Build Paper (PDF + HTML)
- On tag push (e.g., `v1.0`), CI runs Pandoc and uploads artifacts.
- Local build (requires Pandoc + TeX):
  ```bash
  bash scripts/build_paper.sh
  ```

## Versioning
- Tag the integrated research-ready edition:
  ```bash
  git tag -a v1.0 -m "Research-ready integrated edition"
  git push origin v1.0
  ```

## Repository Alignment
- Ensure project root is named `agisa_sac/`.
- Place this `docs/` folder at the repository root.
- Keep figures at `docs/figs/{src,svg,png,alt}`.

## Visualization Gallery
- Add/modify figures in `docs/figs/src/`, CI renders to `docs/figs/svg/`.
- Update gallery pages in `docs/gallery/` if you add new figures.

## API Docs
- `mkdocstrings` pulls Python docstrings from the `agisa_sac` package.
- Ensure package is importable for local preview (`pip install -e .`) or adjust `mkdocs.yml` plugin config to load from source.