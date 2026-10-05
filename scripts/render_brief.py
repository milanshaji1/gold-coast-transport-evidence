"""Render the canonical decision brief as a readable, dependency-free web page."""

import re
from html import escape
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = (root / "docs/decision-brief.md").read_text()


def inline(text):
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", escape(text))


parts = []
for block in source.strip().split("\n\n"):
    if block.startswith("# "):
        parts.append("<h1>" + inline(block[2:]) + "</h1>")
    elif block.startswith("|"):
        rows = [
            [cell.strip() for cell in line.strip().strip("|").split("|")]
            for line in block.splitlines()
        ]
        head = "".join('<th scope="col">' + inline(cell) + "</th>" for cell in rows[0])
        body = "".join(
            "<tr>" + "".join("<td>" + inline(cell) + "</td>" for cell in row) + "</tr>"
            for row in rows[2:]
        )
        parts.append(
            '<div class="table-wrap"><table><thead><tr>'
            + head
            + "</tr></thead><tbody>"
            + body
            + "</tbody></table></div>"
        )
    else:
        parts.append("<p>" + inline(block.replace("\n", " ")) + "</p>")

page = (
    """<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Decision brief | Gold Coast serious crash hotspots</title>
<meta name="author" content="Milan Shaji">
<link rel="stylesheet" href="style.css?v=1.1.0">
<style>.brief{max-width:900px;margin:auto;padding:42px 0}.brief h1{max-width:none;font-size:clamp(32px,4vw,52px)}.brief p{max-width:none}.brief table{min-width:620px}.brief .table-wrap{margin:28px 0}</style>
</head><body><header><a class="brand" href="index.html">Gold Coast crash hotspots</a>
<a href="index.html#shortlist">Back to the dashboard</a><a class="byline" href="https://milanshaji.com">By Milan Shaji</a></header>
<main><article class="brief"><p class="context">Decision brief · Milan Shaji · Gold Coast crash data, 2020–2024</p>
"""
    + "\n".join(parts)
    + "\n</article></main></body></html>\n"
)
(root / "site/decision-brief.html").write_text(page)
