#!/usr/bin/env python3
"""Generate the static Ishtaria portal (English at /, Czech at /cs/).

Usage: build.py [OUTPUT_DIR]   (default: build/html)
Only the Python standard library is used.
"""
import html
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGES = ("index", "download")
LANGS = ("en", "cs")


def e(text):
    return html.escape(text, quote=True)


def layout(t, site, lang, page, body):
    prefix = "../" if lang == "cs" else ""
    other = "en" if lang == "cs" else "cs"
    switch = f"{prefix}{page}.html" if lang == "cs" else f"cs/{page}.html"
    nav = "".join(
        f'<a href="{p}.html"{" aria-current=\"page\"" if p == page else ""}>{e(t[k])}</a>'
        for p, k in (("index", "nav_home"), ("download", "nav_download"))
    )
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(t["name"])} – {e(t["nav_" + ("home" if page == "index" else page)])}</title>
<meta name="description" content="{e(t["tagline"])}">
<link rel="stylesheet" href="{prefix}style.css">
<link rel="alternate" hreflang="{other}" href="{switch}">
</head>
<body>
<header class="top">
  <a class="brand" href="index.html">{e(t["name"])}</a>
  <nav>{nav}<a href="{e(site["docs_url"])}">{e(t["nav_docs"])}</a>
  <a class="lang" lang="{other}" hreflang="{other}" href="{switch}">{e(t["footer_lang"])}</a></nav>
</header>
<main>
{body}
</main>
<footer><p>{e(t["footer_license"])}</p>
<p><a href="{e(site["github"])}">GitHub</a></p></footer>
</body>
</html>
"""


def index(t, site):
    feats = "".join(
        f'<article><h3>{e(t[f"feat_{i}_h"])}</h3><p>{e(t[f"feat_{i}_p"])}</p></article>'
        for i in range(1, 5)
    )
    return f"""<section class="hero"><h1>{e(t["home_title"])}</h1>
<p class="lead">{e(t["home_lead"])}</p>
<p><a class="button" href="download.html">{e(t["home_cta"])}</a></p></section>
<section><h2>{e(t["feat_title"])}</h2><div class="grid">{feats}</div></section>
<section class="note"><h2>{e(t["status_title"])}</h2><p>{e(t["status_p"])}</p></section>"""


def download(t, site):
    repo = site["repo_url"]
    setup = (
        f"sudo wget -O /usr/share/keyrings/vitexsoftware.gpg {repo}/KEY.gpg\n"
        f'echo "deb [signed-by=/usr/share/keyrings/vitexsoftware.gpg] {repo} $(lsb_release -sc) main games" '
        "| sudo tee /etc/apt/sources.list.d/vitexsoftware.list\n"
        "sudo apt update"
    )
    play = "sudo apt install " + " ".join(site["play"])
    host = "sudo apt install " + " ".join(site["host"])
    rows = "".join(
        f'<tr><td><code>{e(p)}</code></td><td>{e(t["pkg_" + p])}</td>'
        f'<td><a href="{e(site["github"])}/{e(site["sources"].get(p, p))}">'
        f'{e(site["sources"].get(p, p))}</a></td></tr>'
        for p in site["packages"]
    )
    rel = site["release"]
    base = f'{rel["repo"]}/download/{rel["tag"]}'
    files = "".join(
        f'<tr><td><a href="{e(base)}/{e(f["file"])}"><code>{e(f["file"])}</code></a></td>'
        f'<td>{e(t[f["label"]])}</td></tr>'
        for f in rel["files"]
    )
    direct = (
        f'<h2>{e(t["dl_direct_h"])}</h2><p>{e(t["dl_direct_p"])}</p>'
        f'<div class="scroll"><table><thead><tr><th>{e(t["dl_col_file"])}</th><th>{e(t["dl_col_for"])}</th></tr></thead>'
        f'<tbody>{files}</tbody></table></div>'
        f'<p><a href="{e(rel["repo"])}/tag/{e(rel["tag"])}">{e(t["dl_all_releases"])}</a></p>'
    )
    return f"""<h1>{e(t["dl_title"])}</h1><p class="lead">{e(t["dl_lead"])}</p>
<h2>{e(t["dl_step1_h"])}</h2><pre><code>{e(setup)}</code></pre>
<h2>{e(t["dl_step2_h"])}</h2>
<div class="grid"><article><h3>{e(t["dl_play"])}</h3><p>{e(t["dl_play_p"])}</p><pre><code>{e(play)}</code></pre></article>
<article><h3>{e(t["dl_host"])}</h3><p>{e(t["dl_host_p"])}</p><pre><code>{e(host)}</code></pre></article></div>
{direct}
<h2>{e(t["dl_table_h"])}</h2>
<div class="scroll"><table><thead><tr><th>{e(t["dl_col_package"])}</th><th>{e(t["dl_col_what"])}</th><th>{e(t["dl_col_source"])}</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<h2>{e(t["dl_req_h"])}</h2><p>{e(t["dl_req_p"])}</p>"""


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "build" / "html"
    site = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
    if out.exists():
        shutil.rmtree(out)
    (out / "cs").mkdir(parents=True)
    shutil.copy(ROOT / "static" / "style.css", out / "style.css")
    builders = {"index": index, "download": download}
    for lang in LANGS:
        t = json.loads((ROOT / "i18n" / f"{lang}.json").read_text(encoding="utf-8"))
        for page in PAGES:
            target = out / ("cs" if lang == "cs" else "") / f"{page}.html"
            target.write_text(layout(t, site, lang, page, builders[page](t, site)), encoding="utf-8")
    print(f"built {len(LANGS) * len(PAGES)} pages into {out}")


if __name__ == "__main__":
    main()
