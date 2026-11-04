#!/usr/bin/env python3
"""Genera index.html (web pública, solo lectura) desde src/app.html + src/data.json + imágenes.
Uso: python3 tools/build.py   (desde la raíz del repo)"""
import base64, os, sys
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = lambda f: os.path.join(R, 'src', f)
s = open(S('app.html'), encoding='utf-8').read()
d = open(S('data.json'), encoding='utf-8').read()
b64 = lambda f, t: f"data:{t};base64," + base64.b64encode(open(S(f), 'rb').read()).decode()
s = s.replace('src="crest.png"', 'src="' + b64('crest.png', 'image/png') + '"')
s = s.replace('url("equipo.jpg")', 'url("' + b64('equipo.jpg', 'image/jpeg') + '")')
a = '  try{ const r=await fetch("data.json",{cache:"no-store"}); D=await r.json(); }'
if a not in s: sys.exit("ERROR: no se encontró la carga de data.json en app.html")
s = s.replace(a, '  try{ D=JSON.parse(document.getElementById("cd-data").textContent); }')
s = s.replace('<script>\n(function(){', '<script type="application/json" id="cd-data">' + d.replace('</', '<\\/') + '</script>\n<script>\n(function(){', 1)
s = s.replace('  for(let i=0;i<30 && !(window.claude && window.claude.use);i++)', '  return;\n  for(let i=0;i<30 && !(window.claude && window.claude.use);i++)', 1)
im = Image.open(S('crest.png')); im.thumbnail((128, 128))
import io; buf = io.BytesIO(); im.save(buf, 'PNG')
fav = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
head = ('<!doctype html><html lang="es"><head><meta charset="utf-8"><link rel="icon" href="' + fav + '"><link rel="apple-touch-icon" href="' + fav + '">'
        '<meta name="theme-color" content="#141845"><meta property="og:title" content="Cracks Dorados 2026">'
        '<meta property="og:description" content="Estadísticas del equipo · Liga Independiente de Fútbol">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>\n')
open(os.path.join(R, 'index.html'), 'w', encoding='utf-8').write(head + s + '\n</body></html>')
print("index.html generado,", len(head + s), "bytes")
