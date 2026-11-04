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
if os.path.exists(S('pmcoach-logo.png')): s = s.replace('src="pmcoach-logo.png"', 'src="' + b64('pmcoach-logo.png', 'image/png') + '"')
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
# ---- Instalar como app (PWA): íconos, manifest, service worker y botón "Instalar app" ----
import json
icon(192, 16).save(os.path.join(R, 'icon-192.png'), optimize=True)
icon(512, 96).save(os.path.join(R, 'icon-maskable.png'), optimize=True)  # margen extra para íconos recortados en círculo (Android)
manifest = {
    "name": "Cracks Dorados 2026", "short_name": "Cracks Dorados",
    "description": "Estadísticas del equipo · Liga Independiente de Fútbol",
    "lang": "es", "id": "./", "start_url": "./", "scope": "./", "display": "standalone",
    "orientation": "portrait", "background_color": "#141845", "theme_color": "#141845",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icon-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}
open(os.path.join(R, 'manifest.webmanifest'), 'w', encoding='utf-8').write(json.dumps(manifest, ensure_ascii=False, indent=1) + '\n')
# Service worker: siempre intenta traer la versión nueva (datos al día) y solo usa la copia guardada si no hay internet.
SW = """const C = "cracks-dorados-v1";
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", e => {
  const r = e.request;
  if (r.method !== "GET" || new URL(r.url).origin !== location.origin) return;
  e.respondWith(
    fetch(r, r.mode === "navigate" ? { cache: "no-cache" } : {})
      .then(res => { if (res.ok) { const cp = res.clone(); caches.open(C).then(c => c.put(r, cp)); } return res; })
      .catch(() => caches.match(r).then(m => m || caches.match("./")))
  );
});
"""
open(os.path.join(R, 'sw.js'), 'w', encoding='utf-8').write(SW)
PWA_HEAD = ('<link rel="manifest" href="manifest.webmanifest">'
            '<meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-capable" content="yes">'
            '<meta name="apple-mobile-web-app-title" content="Cracks Dorados">'
            '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">'
            '<script>window.cdInstall=null;addEventListener("beforeinstallprompt",function(e){e.preventDefault();window.cdInstall=e;});'
            'if("serviceWorker" in navigator)addEventListener("load",function(){navigator.serviceWorker.register("sw.js").catch(function(){});});</script>')
SHARE_SVG = ('<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round" stroke-linejoin="round"><path d="M12 15V3M8 7l4-4 4 4"/><path d="M6 11H5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-8a1 1 0 0 0-1-1h-1"/></svg>')
DOTS_SVG = ('<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="currentColor">'
            '<circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/></svg>')
PWA_BTN = ('<button type="button" class="cdi-btn" id="cdiBtn" hidden>'
           '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
           '<rect x="6" y="2" width="12" height="20" rx="2.5"/><path d="M12 7v7M9 11l3 3 3-3"/></svg>Instalar app</button>')
PWA_BODY = ('''
<style>
.cdi-btn{position:absolute;top:14px;right:max(16px,env(safe-area-inset-right,0px));z-index:2;display:inline-flex;align-items:center;gap:7px;
  border:0;border-radius:999px;padding:8px 14px;background:var(--gold-fill,#e3bd36);color:#141845;font:inherit;font-size:14px;font-weight:700;
  cursor:pointer;box-shadow:0 4px 14px rgba(0,0,0,.35);white-space:nowrap}
.cdi-btn:focus-visible,.cdi-dlg button:focus-visible{outline:3px solid var(--focus,#e3bd36);outline-offset:2px}
.cdi-btn.cdi-fixed{position:fixed;top:calc(10px + env(safe-area-inset-top,0px))}
.cdi-dlg{border:0;padding:0;border-radius:16px;width:min(420px,calc(100vw - 32px));background:var(--surface,#fff);color:var(--ink,#12153a);
  box-shadow:0 20px 60px rgba(0,0,0,.4)}
.cdi-dlg::backdrop{background:rgba(8,10,34,.6)}
.cdi-in{padding:20px;display:grid;gap:14px}
.cdi-top{display:flex;gap:12px;align-items:center}
.cdi-top img{width:48px;height:48px;border-radius:12px;flex:none}
.cdi-top h2{margin:0;font-family:var(--display,system-ui);font-size:24px;line-height:1;text-transform:uppercase}
.cdi-top p{margin:3px 0 0;color:var(--muted,#5a5e7c);font-size:14px}
.cdi-dlg h3{margin:0 0 6px;font-size:15px}
.cdi-dlg ol{margin:0;padding-left:22px;display:grid;gap:7px}
.cdi-dlg li svg{vertical-align:-4px;margin:0 2px;color:var(--gold,#b8890c)}
.cdi-dlg .cdi-note{margin:0;font-size:13px;color:var(--muted,#5a5e7c)}
.cdi-close{justify-self:stretch;border:0;border-radius:10px;padding:11px;background:var(--gold-fill,#e3bd36);color:#141845;font:inherit;font-weight:700;cursor:pointer}
@media (display-mode:standalone){html{background:#141845}}
</style>
<dialog class="cdi-dlg" id="cdiDlg" aria-labelledby="cdiTitle">
  <div class="cdi-in">
    <div class="cdi-top"><img src="apple-touch-icon.png" alt=""><div><h2 id="cdiTitle">Instalar app</h2>
      <p>Deja Cracks Dorados en tu pantalla de inicio, como una app más.</p></div></div>
    <section data-os="ios"><h3>En iPhone</h3><ol>
      <li>Abre esta página en <b>Safari</b>.</li>
      <li>Toca el botón Compartir ''' + SHARE_SVG + ''' (abajo o arriba de la pantalla).</li>
      <li>Baja y elige <b>Agregar a pantalla de inicio</b>.</li>
      <li>Toca <b>Agregar</b>.</li></ol></section>
    <section data-os="android"><h3>En Android</h3><ol>
      <li>Abre esta página en <b>Chrome</b>.</li>
      <li>Toca el menú ''' + DOTS_SVG + ''' arriba a la derecha.</li>
      <li>Elige <b>Instalar app</b> o <b>Agregar a la pantalla principal</b>.</li>
      <li>Confirma con <b>Instalar</b>.</li></ol></section>
    <p class="cdi-note">La app se actualiza sola: cada vez que la abras verás las estadísticas al día.</p>
    <button type="button" class="cdi-close" id="cdiClose">Entendido</button>
  </div>
</dialog>
<script>
(function(){
  var btn=document.getElementById("cdiBtn"), dlg=document.getElementById("cdiDlg");
  if(!btn||!dlg) return;
  function installed(){ return navigator.standalone===true || (window.matchMedia && matchMedia("(display-mode: standalone)").matches); }
  if(installed()) return;
  btn.hidden=false;
  var ua=navigator.userAgent, ios=/iPhone|iPad|iPod/.test(ua)||(/Macintosh/.test(ua)&&navigator.maxTouchPoints>1), android=/Android/.test(ua);
  dlg.querySelectorAll("section[data-os]").forEach(function(s){
    s.hidden=(ios&&s.dataset.os!=="ios")||(android&&s.dataset.os!=="android");
  });
  btn.addEventListener("click",function(){
    var p=window.cdInstall;
    if(p){ window.cdInstall=null; p.prompt(); p.userChoice.then(function(c){ if(c.outcome==="accepted") btn.hidden=true; }).catch(function(){}); return; }
    if(dlg.showModal) dlg.showModal(); else dlg.setAttribute("open","");
  });
  document.getElementById("cdiClose").addEventListener("click",function(){ dlg.close?dlg.close():dlg.removeAttribute("open"); });
  dlg.addEventListener("click",function(e){ if(e.target===dlg) dlg.close(); });
  addEventListener("appinstalled",function(){ btn.hidden=true; window.cdInstall=null; });
})();
</script>
''')
anchor = '<header class="band">\n  <div class="wrap">'
if anchor in s:
    s = s.replace(anchor, anchor + '\n    ' + PWA_BTN, 1)
else:  # si cambia el encabezado de la app, el botón queda fijo arriba a la derecha
    s = PWA_BTN.replace('class="cdi-btn"', 'class="cdi-btn cdi-fixed"') + '\n' + s
s = s + PWA_BODY
head = ('<!doctype html><html lang="es"><head><meta charset="utf-8"><link rel="icon" type="image/png" href="favicon.png"><link rel="apple-touch-icon" href="apple-touch-icon.png">'
        '<meta name="theme-color" content="#141845">' + PWA_HEAD + '<meta property="og:title" content="Cracks Dorados 2026">'
        '<meta property="og:description" content="Estadísticas del equipo · Liga Independiente de Fútbol">'
        '<meta property="og:type" content="website"><meta property="og:url" content="' + URL + '">'
        '<meta property="og:image" content="' + URL + 'og-image.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
        '<meta property="og:image:alt" content="Escudo de Cracks Dorados"><meta name="twitter:card" content="summary_large_image">'
        '<meta name="twitter:image" content="' + URL + 'og-image.png">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>\n')
open(os.path.join(R, 'index.html'), 'w', encoding='utf-8').write(head + s + '\n</body></html>')
print("index.html generado,", len(head + s), "bytes")
