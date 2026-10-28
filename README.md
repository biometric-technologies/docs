# docs.iriscan.net

Source of the Iriscan developer documentation.

- `src/pages/*.md` — page content (Markdown with a small YAML header)
- `src/tenant-api.yaml` — OpenAPI spec of the Cloud Iris API, rendered into `cloud-api.html`
- `src/build.py` — generator (`pip install markdown pyyaml`, then `python3 src/build.py docs`)
- `docs/` — built site, served by GitHub Pages
