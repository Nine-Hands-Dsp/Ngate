"""Apercu NGATE : compose le fond et tout ce que le plugin dessine par-dessus (meme geometrie que Layout.h).
Usage : python3 tools/preview.py <seuil dB> <niveau entree dB> <hard 0/1> <bass 0/1> <bypass 0/1> <sortie.png> [texte barre]"""
import os, sys, json, math, pathlib
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
G = json.load(open(os.path.join(HERE, 'layout.json')))
AS = 2
thr = float(sys.argv[1]) if len(sys.argv) > 1 else -53.5
lvl = float(sys.argv[2]) if len(sys.argv) > 2 else -30.0
hard = int(sys.argv[3]) if len(sys.argv) > 3 else 1
bass = int(sys.argv[4]) if len(sys.argv) > 4 else 0
bypass = int(sys.argv[5]) if len(sys.argv) > 5 else 0
outp = sys.argv[6] if len(sys.argv) > 6 else os.path.join(ROOT, 'design', 'preview.png')
bar = sys.argv[7] if len(sys.argv) > 7 else '1  Clean Single Coils'
power = 0.0 if bypass else 1.0
is_open = (lvl > thr) and not bypass

bg = Image.open(os.path.join(ROOT, 'background.png')).convert('RGBA')
W, H = bg.size
SS = 3                                                    # sur-echantillonnage du dessin vectoriel
canvas = bg.resize((W * SS, H * SS), Image.LANCZOS)

def paste(im, x, y):
    canvas.alpha_composite(im, (int(round(x)), int(round(y))))

def U(v): return v * AS * SS

# --- halos et LED allumees
def led(name, glow, pos, on):
    if on <= 0: return
    gl = Image.open(os.path.join(ROOT, glow)).convert('RGBA')
    r = G['glowG'] if 'green' in glow else G['glowO']
    gl = gl.resize((int(U(r[2])), int(U(r[3]))), Image.LANCZOS)
    paste(gl, U(r[0]), U(r[1]))
    sp = Image.open(os.path.join(ROOT, name)).convert('RGBA')
    s = int(U(G['ledS'])); sp = sp.resize((s, s), Image.LANCZOS)
    paste(sp, U(pos[0]) - s / 2, U(pos[1]) - s / 2)
led('led_green_on.png', 'glow_green.png', G['openLed'], is_open)
led('led_orange_on.png', 'glow_orange.png', G['gateLed'], (not is_open) and not bypass)

# --- potard : usure + index qui tournent
t = (thr + 95.0) / 95.0
ang = -G['dotA'] + t * 2 * G['dotA']
top = Image.open(os.path.join(ROOT, 'knob_top.png')).convert('RGBA')
s = int(U(G['knobSpr'])); top = top.resize((s, s), Image.LANCZOS).rotate(-ang, resample=Image.BICUBIC)
paste(top, U(G['knob'][0]) - s / 2, U(G['knob'][1]) - s / 2)

# --- inverseur (kit) : haut = HARD
strip = Image.open(os.path.join(ROOT, 'toggle_strip.png')).convert('RGBA')
fh = strip.height // 3
fr = strip.crop((0, (0 if hard else 2) * fh, strip.width, (1 if hard else 3) * fh))   # 0 HARD (droite), 2 SOFT (gauche)
s = int(U(G['togS'])); fr = fr.resize((s, s), Image.LANCZOS)
paste(fr, U(G['toggle'][0]) - s / 2, U(G['toggle'][1]) - s / 2)

# --- dessin vectoriel
over = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); d = ImageDraw.Draw(over)
FONT = {0: 'Poppins-Medium.ttf', 1: 'Poppins-Bold.ttf', 2: 'Poppins-Light.ttf', 3: 'Poppins-Regular.ttf'}
def font(k, em): return ImageFont.truetype(os.path.join(ROOT, FONT[k]), max(4, int(round(U(em)))))

# couronne de points : perles eteintes, puis allumees jusqu'au niveau d'entree
glowl = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glowl)
for i in range(G['nDots']):
    db = -95 + 95 * i / (G['nDots'] - 1)
    a = math.radians(-G['dotA'] + 2 * G['dotA'] * i / (G['nDots'] - 1))
    x = G['knob'][0] + G['dotsR'] * math.sin(a); y = G['knob'][1] - G['dotsR'] * math.cos(a)
    d.ellipse([U(x - 2.0), U(y - 1.5), U(x + 2.6), U(y + 3.1)], fill=(0, 0, 0, 110))
    d.ellipse([U(x - 2.2), U(y - 2.2), U(x + 2.2), U(y + 2.2)], fill=(150, 150, 148, 255))
    d.ellipse([U(x - 1.2), U(y - 1.4), U(x + 0.4), U(y + 0.2)], fill=(215, 215, 212, 255))
    if power and db <= lvl:
        col = (255, 138, 30) if db < thr else (54, 224, 92)
        gd.ellipse([U(x - 9), U(y - 9), U(x + 9), U(y + 9)], fill=col + (90,))
        d.ellipse([U(x - 3.9), U(y - 3.9), U(x + 3.9), U(y + 3.9)], fill=col + (255,))
        d.ellipse([U(x - 1.6), U(y - 1.8), U(x + 0.8), U(y + 0.6)], fill=(255, 250, 230, 230))
glowl = glowl.filter(__import__('PIL.ImageFilter', fromlist=['x']).GaussianBlur(U(4)))
canvas.alpha_composite(glowl)

def text(s_, k, em, track, x, y, col, rot=0.0, anchor='c', alpha=240, target=None):
    f = font(k, em)
    widths = [f.getlength(ch) for ch in s_]
    tw = sum(widths) + U(track) * (len(s_) - 1)
    asc, desc = f.getmetrics()
    bb = f.getbbox('H'); cap_mid = (bb[1] + bb[3]) / 2
    pad = int(U(em) * 2)
    tile = Image.new('RGBA', (int(tw) + 2 * pad, int(asc + desc) + 2 * pad), (0, 0, 0, 0)); td = ImageDraw.Draw(tile)
    xx = pad
    for ch, w in zip(s_, widths):
        td.text((xx, pad), ch, font=f, fill=tuple(col) + (alpha,)); xx += w + U(track)
    cx_t = pad + (tw / 2 if anchor == 'c' else 0); cy_t = pad + cap_mid
    if rot:
        tile = tile.rotate(rot, resample=Image.BICUBIC, expand=False, center=(cx_t, cy_t))
    (target or over).alpha_composite(tile, (int(round(U(x) - cx_t)), int(round(U(y) - cy_t))))

for t_ in G['texts']:
    text(t_[0], t_[1], t_[2], t_[3], t_[4], t_[5], t_[7], t_[6], t_[8])
for (x0, x1, y, w) in G['rules']:
    d.rectangle([U(x0), U(y - w / 2), U(x1), U(y + w / 2)], fill=(214, 214, 211, 225))
canvas.alpha_composite(over)

# --- NGATE en relief (lettres metal, ombre douce vers le bas a droite)
tx, ty, tem, ttr = G['title']
m = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
text('NGATE', 1, tem, ttr, tx, ty, (255, 255, 255), alpha=255, target=m)
M = np.asarray(m)[..., 3].astype(np.float32) / 255
cv = np.asarray(canvas).astype(np.float32)
shm = np.roll(np.roll(M, int(U(1.4)), 0), int(U(1.0)), 1)
sh = cv2.GaussianBlur(shm, (0, 0), U(1.6)) * 0.75
cv[..., :3] *= (1 - sh * (1 - M))[..., None]
yy = np.arange(cv.shape[0])[:, None].astype(np.float32)
ys = np.where(M.any(1))[0]; y0, y1 = ys.min(), ys.max()
grad = np.clip(1.0 - (yy - y0) / max(1, y1 - y0) * 0.30, 0.68, 1.0)
rng = np.random.default_rng(2)
brush = cv2.GaussianBlur(rng.standard_normal(M.shape).astype(np.float32), (0, 0), sigmaX=U(6), sigmaY=0.6) * 9
face = (np.broadcast_to(grad, M.shape) * 222 + brush)[..., None] * np.array([1.0, 1.0, 0.99])
e = int(max(1, U(0.7)))
hi = np.clip(M - np.roll(np.roll(M, e, 0), e, 1), 0, 1)
lo = np.clip(M - np.roll(np.roll(M, -e, 0), -e, 1), 0, 1)
face = face + hi[..., None] * 38 - lo[..., None] * 95
cv[..., :3] = cv[..., :3] * (1 - M[..., None]) + np.clip(face, 0, 255) * M[..., None]

# --- logo NINE HANDS | DSP (SVG officiel, rendu par Chromium)
logo_png = os.path.join(HERE, '_logo.png')
if not os.path.exists(logo_png):
    from playwright.sync_api import sync_playwright
    svg = open(os.path.join(ROOT, 'NineHandsLogo.svg')).read()
    html = f"<html><body style='margin:0;background:transparent'><div id=l style='width:2400px'>{svg.replace('<svg ', '<svg width=2400 ')}</div></body></html>"
    with sync_playwright() as p_:
        b_ = p_.chromium.launch(); pg = b_.new_page(); pg.set_content(html)
        pg.locator('svg').screenshot(path=logo_png, omit_background=True); b_.close()
lg = Image.open(logo_png).convert('RGBA')
lw = int(U(G['logo'][2])); lh = int(lg.height * lw / lg.width)
lg = lg.resize((lw, lh), Image.LANCZOS)
la = np.asarray(lg).astype(np.float32); la[..., 3] *= 0.92
cvi = Image.fromarray(np.clip(cv, 0, 255).astype(np.uint8), 'RGBA')
cvi.alpha_composite(Image.fromarray(la.astype(np.uint8), 'RGBA'), (int(U(G['logo'][0]) - lw / 2), int(U(G['logo'][1]) - lh / 2)))

# --- afficheur du seuil
d2 = ImageDraw.Draw(cvi)
wr = G['win']
val = '%.1f' % thr
fv = font(0, 30.0)
bbv = fv.getbbox(val)
cream = (239, 217, 176) if power else (110, 100, 82)
d2.text((U(wr[0] + wr[2] - 10) - bbv[2], U(wr[1] + wr[3] / 2) - (bbv[1] + bbv[3]) / 2), val, font=fv, fill=cream + (255,))

# --- barre de presets (pastille 400 x 38, Poppins Medium 23)
px, py, pw, ph = G['preset']
d2.rounded_rectangle([U(px) - U(1.5), U(py) - U(1.5), U(px + pw) + U(1.5), U(py + ph) + U(1.5)], radius=U(ph / 2 + 1.5), fill=(10, 10, 11, 255))
d2.rounded_rectangle([U(px), U(py), U(px + pw), U(py + ph)], radius=U(ph / 2), fill=(6, 7, 8, 255), outline=(78, 80, 84, 255), width=int(U(0.6)))
fp = font(0, 23.0 if not ('dB' in bar) else 19.0)
bbp = fp.getbbox(bar)
d2.text((U(px + pw / 2) - (bbp[0] + bbp[2]) / 2, U(py + ph / 2) - (bbp[1] + bbp[3]) / 2), bar, font=fp, fill=(232, 232, 230, 255))
for sgn, xc in (((-1, px + 17), (1, px + pw - 17)) if not ('dB' in bar or 'BYPASS' in bar) else ()):
    tri = [(U(xc + sgn * 5.5 * 0.6), U(py + ph / 2)), (U(xc - sgn * 5.5 * 0.6), U(py + ph / 2 - 5.5)), (U(xc - sgn * 5.5 * 0.6), U(py + ph / 2 + 5.5))]
    d2.polygon(tri, fill=(150, 150, 150, 255))

# --- BASS actif : couronne orange autour du bouton
if bass and power:
    bx, by = G['bass']; r = G['btnR']
    ring = Image.new('RGBA', cvi.size, (0, 0, 0, 0)); rd = ImageDraw.Draw(ring)
    rd.ellipse([U(bx - r - 1), U(by - r - 1), U(bx + r + 1), U(by + r + 1)], outline=(255, 122, 47, 230), width=int(U(1.4)))
    ring2 = ring.filter(__import__('PIL.ImageFilter', fromlist=['x']).GaussianBlur(U(3)))
    cvi.alpha_composite(ring2); cvi.alpha_composite(ring)

out = cvi.resize((W, H), Image.LANCZOS)
fin = Image.new('RGBA', (W, H), (22, 22, 24, 255)); fin.alpha_composite(out)
fin.convert('RGB').save(outp)
print('ok', outp)
