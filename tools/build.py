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
# Logos para compartir el link (WhatsApp, Facebook, etc.) y para el ícono del navegador/celular
from PIL import ImageDraw, ImageFont
URL = 'https://patriciomaldonado0904.github.io/cracks-dorados/'
NAVY, GOLD, WHITE = (20, 24, 69), (232, 197, 71), (244, 245, 255)
crest = Image.open(S('crest.png')).convert('RGBA')
def fit(img, h):
    return img.resize((round(img.width * h / img.height), h), Image.LANCZOS)
def font(sz):
    for f in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/Library/Fonts/Arial Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf'):
        if os.path.exists(f): return ImageFont.truetype(f, sz)
    return ImageFont.load_default()
og = Image.new('RGB', (1200, 630), NAVY); dr = ImageDraw.Draw(og)
c = fit(crest, 440); og.paste(c, (110, 95), c)
x = 110 + c.width + 70
dr.text((x, 200), 'CRACKS', font=font(96), fill=WHITE)
dr.text((x, 310), 'DORADOS', font=font(96), fill=GOLD)
dr.rectangle((x, 430, x + 120, 438), fill=GOLD)
dr.text((x, 460), 'Estadísticas 2026', font=font(40), fill=WHITE)
og.save(os.path.join(R, 'og-image.png'), optimize=True)
def icon(size, pad):
    bg = Image.new('RGBA', (size, size), NAVY + (255,)); c = fit(crest, size - 2 * pad)
    bg.paste(c, ((size - c.width) // 2, (size - c.height) // 2), c); return bg.convert('RGB')
icon(180, 14).save(os.path.join(R, 'apple-touch-icon.png'), optimize=True)
icon(512, 40).save(os.path.join(R, 'icon-512.png'), optimize=True)
fv = fit(crest, 64); fb = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); fb.paste(fv, ((64 - fv.width) // 2, 0), fv)
fb.save(os.path.join(R, 'favicon.png'), optimize=True)
head = ('<!doctype html><html lang="es"><head><meta charset="utf-8"><link rel="icon" type="image/png" href="favicon.png"><link rel="apple-touch-icon" href="apple-touch-icon.png">'
        '<meta name="theme-color" content="#141845"><meta property="og:title" content="Cracks Dorados 2026">'
        '<meta property="og:description" content="Estadísticas del equipo · Liga Independiente de Fútbol">'
        '<meta property="og:type" content="website"><meta property="og:url" content="' + URL + '">'
        '<meta property="og:image" content="' + URL + 'og-image.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
        '<meta property="og:image:alt" content="Escudo de Cracks Dorados"><meta name="twitter:card" content="summary_large_image">'
        '<meta name="twitter:image" content="' + URL + 'og-image.png">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>\n')
open(os.path.join(R, 'index.html'), 'w', encoding='utf-8').write(head + s + '\n</body></html>')
print("index.html generado,", len(head + s), "bytes")
