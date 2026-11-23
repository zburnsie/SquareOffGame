"""Wrap tools/square-off.html as a standalone index.html and copy data into the repo."""
import shutil, sys, os, glob
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(S)  # tools/ -> repo root
body = open(os.path.join(S, "square-off.html"), encoding="utf-8").read().replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
head = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Square Off: a party trivia game. Win duels, take your neighbors' squares, own the board.">
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#05050f">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Square Off">
<style>
:root{padding-top:env(safe-area-inset-top,0px); padding-bottom:env(safe-area-inset-bottom,0px); box-sizing:border-box}
body{margin:0; font:14px/1.4 system-ui,-apple-system,sans-serif}
img{max-width:100%}
[hidden]{display:none!important}
</style>
"""
i = body.index("</style>") + len("</style>")
open(os.path.join(R, "index.html"), "w", encoding="utf-8").write(head + body[:i] + "\n</head>\n<body>\n" + body[i:].lstrip() + "\n</body>\n</html>\n")
json_manifest = {"name": "Square Off", "short_name": "Square Off", "start_url": ".", "display": "fullscreen",
    "background_color": "#05050f", "theme_color": "#05050f"}
import json; json.dump(json_manifest, open(os.path.join(R, "manifest.json"), "w"), indent=2)
print("site built")
