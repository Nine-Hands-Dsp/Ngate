"""
NGATE (NINE HANDS | DSP) - visuel du plugin v2 (nov. 2026) : pedale simple, 1800 px de haut, plein cadre.

Pieces (toutes photographiques) :
  src_art/facade.png   facade noire usee vide (fournie par l'utilisateur, nov. 2026)
  src_art/knob.png     gros potard alu brosse, rainure vers le haut (fourni par l'utilisateur)
  src_art/button.png   bouton poussoir noir dans sa bague (LEARN / BASS, fourni par l'utilisateur)
  src_art/design_v1.png  ancien visuel : seulement les 4 vis d'angle (gardees a la demande de l'utilisateur)
  assets/kit/*         kit NINE HANDS | DSP : jacks, inverseur, footswitch, LED
Textes, graduations, lettres NGATE en relief et logo : vectoriels, dessines par le plugin (Layout.h).
Une seule lumiere : en haut a gauche (ombres vers le bas a droite).

Repere du plugin = image / 2 (unites). Sorties a la racine du depot :
  background.png      fond RGBA (facade, vis, plaque, fenetre, potard eclaire fixe, boutons, LED eteintes,
                      footswitch, jacks) ; transparent seulement autour des jacks et dans les coins arrondis
  knob_top.png        usure + index du potard (calques fournis), qui tournent avec le potard
  led_green_on.png / led_orange_on.png, glow_green.png / glow_orange.png (calques alpha : lumiere ajoutee)
  toggle_strip.png    inverseur haut / milieu / bas (kit)
  Layout.h, tools/layout.json, design/preview_art.png
"""
import os, sys, math, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import photo_controls as PC
import toggle_photo as TP
import toggle_h as TH

AS = 2                                    # pixels par unite
OUT_H = 1800
BW_PX = 1130                              # largeur du boitier (proportions de la facade fournie)
JACK_LEN = 105.0
_j = PC.jack_sprite(JACK_LEN, AS, 1)
JP_PX = _j[0].shape[1]                    # saillie d'une embase (px)
# la facade photo a une tranche sombre (flanc du boitier) plus large a droite qu'a gauche : les embases s'appuient
# sur le flanc, sans recouvrir l'arete claire usee
OUT_OV, IN_OV = 3, 9
BXP = JP_PX - OUT_OV                      # x du boitier dans l'image (px)
W = BXP + BW_PX - IN_OV + JP_PX
H = OUT_H
BX0, BW, BH = BXP / AS, BW_PX / AS, H / AS
CX = BX0 + BW / 2
print('image', W, 'x', H, 'saillie jack', JP_PX)

# ancien visuel (design_v1, boitier x 134.5 + 846.5, y 19 + 1347) -> nouveau repere
DX = lambda x: BX0 + (x - 134.5) * (BW / 846.5)
DY = lambda y: (y - 19.0) * (BH / 1347.0)

# ------------------------------------------------------------------ disposition (unites)
SCREWS = [((DX(184.5), DY(56.25)), (184.5, 56.25)), ((DX(933.25), DY(53.75)), (933.25, 53.75)),
          ((DX(179.5), DY(1323.75)), (184.5, 56.25)), ((DX(939.25), DY(1326.25)), (933.25, 53.75))]
SCREW_R_SRC = 21.5                         # rayon de la vis dans design_v1 (px)
PLATE = (DX(195), DY(68), DX(493) - DX(195), DY(161) - DY(68))
PLATE_R, PLATE_T = 6.0, 3.0
WIN = (DX(692), DY(73), DX(921) - DX(692), DY(152) - DY(73))
KNOB = (CX, 330.0)
CAP_R = 143.6                              # rayon du chapeau alu
DOTS_R, N_DOTS, DOT_A = 174.0, 31, 133.85
LEARN = (DX(865), DY(272)); BASS = None
BTN_R = 26.0                               # rayon exterieur de la bague des boutons
TOG = (CX, DY(825)); TOG_R = 21.0; TOG_S = TOG_R * 3.6
ROW_Y = 640.0
OPEN_LED, GATE_LED = (DX(357), ROW_Y), (DX(756.5), ROW_Y)
BASS = (CX, ROW_Y)
LED_LENS = 9.0
PRESET = (CX - 200.0, 694.0, 400.0, 38.0)
FS = (CX, 792.0); FS_FLATS = 88.0
LOGO_C, LOGO_W = (CX, 870.0), 160.0
JACK_Y = DY(605)

# ------------------------------------------------------------------ outils
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
UX, UY = (XX + 0.5) / AS, (YY + 0.5) / AS
L = np.array([-0.46, -0.62, 0.64]); L /= np.linalg.norm(L)
V = np.array([0.0, 0.0, 1.0]); HV = (L + V) / np.linalg.norm(L + V)

def rrect_sd(x, y, x0, y0, w, h, r):
    cx, cy = x0 + w / 2, y0 + h / 2
    qx = np.abs(x - cx) - (w / 2 - r); qy = np.abs(y - cy) - (h / 2 - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r

def over(dst, rgba, x0, y0):
    h, w = rgba.shape[:2]
    X0, Y0 = int(round(x0)), int(round(y0))
    sx0, sy0 = max(0, -X0), max(0, -Y0)
    ex, ey = min(w, dst.shape[1] - X0), min(h, dst.shape[0] - Y0)
    a = rgba[sy0:ey, sx0:ex, 3:4] / 255.0
    reg = dst[Y0 + sy0:Y0 + ey, X0 + sx0:X0 + ex]
    dst[Y0 + sy0:Y0 + ey, X0 + sx0:X0 + ex] = reg * (1 - a) + rgba[sy0:ey, sx0:ex, :3] * a

def place(src, c, k, n):
    """alpha premultiplie : point c de src au centre d'un carre de n px, echelle k"""
    pm = src.astype(np.float32).copy(); pm[..., :3] *= pm[..., 3:4] / 255.0
    k1 = min(1.0, k * 2.0); n1 = int(round(n * k1 / k))
    M1 = np.float32([[k1, 0, n1 / 2 - c[0] * k1], [0, k1, n1 / 2 - c[1] * k1]])
    big = cv2.warpAffine(pm, M1, (n1, n1), flags=cv2.INTER_AREA if k1 < 1 else cv2.INTER_CUBIC, borderValue=0)
    small = cv2.resize(big, (n, n), interpolation=cv2.INTER_AREA) if n1 != n else big
    a = np.clip(small[..., 3] / 255.0, 0, 1)
    rgb = np.where(a[..., None] > 1e-4, small[..., :3] / np.maximum(a, 1e-4)[..., None], 0)
    return rgb, a

def shadowed(rgb, a, s, cast_amt=0.6):
    sh = lambda m, dx, dy: cv2.warpAffine(m, np.float32([[1, 0, dx], [0, 1, dy]]), (m.shape[1], m.shape[0]))
    cast = cv2.GaussianBlur(sh(a, 0.06 * s, 0.09 * s), (0, 0), 0.06 * s) * cast_amt
    contact = cv2.GaussianBlur(sh(a, 0.010 * s, 0.016 * s), (0, 0), 0.016 * s) * 0.55
    shd = np.clip(cast + contact, 0, 0.86) * (1 - a)
    alpha = np.clip(a + shd, 0, 1)
    col = np.where(alpha[..., None] > 1e-4, rgb * (a / np.maximum(alpha, 1e-4))[..., None], 0)
    return np.dstack([np.clip(col, 0, 255), alpha * 255]).astype(np.float32)

def disc(c, r):
    return np.clip((r - np.hypot(UX - c[0], UY - c[1])) * AS, 0, 1)

def load(p):
    return np.asarray(Image.open(os.path.join(ROOT, p)).convert('RGBA')).astype(np.float32)

# ------------------------------------------------------------------ 1. facade (photo) + vis d'angle
fac = load('design/source/src_art/facade.png')
ab = fac[..., 3] > 8
ys, xs = np.where(ab)
fx0, fx1, fy0, fy1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
crop = fac[fy0:fy1, fx0:fx1].copy(); crop[..., :3] *= crop[..., 3:4] / 255.0
crop = cv2.resize(crop, (BW_PX, H), interpolation=cv2.INTER_AREA)
img = np.zeros((H, W, 3), np.float32); body = np.zeros((H, W), np.float32)
a_ = np.clip(crop[..., 3] / 255.0, 0, 1)
img[:, BXP:BXP + BW_PX] = np.where(a_[..., None] > 1e-4, crop[..., :3] / np.maximum(a_, 1e-4)[..., None], 0)
body[:, BXP:BXP + BW_PX] = a_
print('facade', fx1 - fx0, 'x', fy1 - fy0, '->', BW_PX, 'x', H)

def occlusion(mask, contact=3.0, soft=14.0, strength=1.0, cap=0.5):
    c = cv2.GaussianBlur(mask, (0, 0), contact * AS); s = cv2.GaussianBlur(mask, (0, 0), soft * AS)
    o = np.clip(c * 0.55 + s * 0.9, 0, cap) * strength * (1.0 - mask)
    img[...] = img * (1.0 - o * body)[..., None]

# vis d'angle (photo de l'ancien visuel, recopiees en bas comme sur la v1)
old = load('design/source/src_art/design_v1.png')
for (pos, src) in SCREWS:
    n = int(round(2 * 15 * AS)); k = (13.2 * AS) / SCREW_R_SRC
    rgb, a = place(old, src, k, n)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    m = np.clip((13.4 * AS - np.hypot(xx - n / 2, yy - n / 2)) / 1.2, 0, 1)
    # usm leger : la photo d'origine est agrandie
    blur = cv2.GaussianBlur(rgb, (0, 0), 1.2)
    rgb = np.clip(rgb + (rgb - blur) * 0.6, 0, 255)
    over(img, np.dstack([rgb, m * 255]), pos[0] * AS - n / 2, pos[1] * AS - n / 2)

# ------------------------------------------------------------------ 2. plaque NGATE (cadre chrome) et fenetre d'affichage
def tube(sd_abs, half_w, base, spec_col=(1.0, 1.0, 1.0), metal=170.0):
    """profil de tube arrondi d'apres une distance signee ; renvoie (rgb, alpha)"""
    d = sd_abs
    hgt = np.sqrt(np.clip(half_w ** 2 - d ** 2, 0, None))
    gy, gx = np.gradient(cv2.GaussianBlur(hgt.astype(np.float32), (0, 0), 0.6), 1.0 / AS)
    nrm = np.dstack([-gx, -gy, np.ones_like(hgt)]); nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
    ndl = np.clip(nrm @ L, 0, 1); ndh = np.clip(nrm @ HV, 0, 1)
    col = (base + metal * ndl ** 1.5)[..., None] * np.array([1.0, 1.0, 1.0]) + (110 * ndh ** 30 + 40 * ndh ** 6)[..., None] * np.array(spec_col)
    a = np.clip((half_w - d) * AS, 0, 1)
    return col, a

sdp = rrect_sd(UX, UY, *PLATE, PLATE_R)
pd = np.abs(sdp + PLATE_T / 2)                                   # milieu du tube a T/2 a l'interieur du bord
pa_mask = np.clip((PLATE_T / 2 - pd) * AS, 0, 1)
occlusion(pa_mask, 1.2, 4.0, 1.0, 0.45)
col, a = tube(pd, PLATE_T / 2, 70.0)
rng = np.random.default_rng(3)
wear = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 1.0) * 10
col = np.clip(col + wear[..., None], 0, 255) * np.array([1.0, 0.99, 0.97])
img[...] = img * (1 - a[..., None]) + col * a[..., None]

# fenetre d'affichage : verre noir dans un cadre biseaute (comme le visuel)
sdw = rrect_sd(UX, UY, *WIN, 5.0)
win_m = np.clip(-sdw * AS, 0, 1)
occlusion(win_m, 1.5, 6.0, 1.0, 0.5)
bev = np.clip((-sdw) / 2.0, 0, 1)                                 # 2 unites de biseau
t_ = np.clip((UY - WIN[1]) / WIN[3], 0, 1)
glass = (6.0 + 14.0 * t_)[..., None] * np.array([1.0, 1.04, 1.1])
# reflet diagonal tres doux en haut a gauche
refl = np.exp(-(((UX - WIN[0]) / (WIN[2] * 0.35)) ** 2 + ((UY - WIN[1]) / (WIN[3] * 0.5)) ** 2)) * 10
glass = glass + refl[..., None]
# biseau : clair en bas a droite (paroi tournee vers la lumiere), sombre en haut a gauche
nx = np.clip((UX - (WIN[0] + WIN[2] / 2)) / (WIN[2] / 2), -1, 1); ny = np.clip((UY - (WIN[1] + WIN[3] / 2)) / (WIN[3] / 2), -1, 1)
edge_l = 0.5 + 0.5 * np.clip(nx * 0.4 + ny * 0.9, -1, 1)
edge_col = (20 + 105 * edge_l)[..., None] * np.array([1.0, 1.02, 1.05])
ring = (1 - bev) * win_m
img[...] = img * (1 - win_m[..., None]) + (glass * (1 - ring[..., None]) + edge_col * ring[..., None]) * win_m[..., None]

# ------------------------------------------------------------------ 3. gros potard : eclairage fixe dans le fond, matiere qui tourne a part
# Calques fournis par l'utilisateur (ChatGPT, 1024 px, nov. 2026) : ombre, jupe, chapeau, usure, index.
# Corrections : chapeau / jupe legerement ovales (~2 %) -> ramenes a un cercle exact (sinon le potard voilerait
# en tournant) ; index recentre sur le chapeau (decale de 4,5 px). Fixes dans le fond : ombre, jupe (lisse : sa
# rotation serait invisible), fond sombre de la gorge, chapeau et ses reflets. Tournent : usure + index (knob_top.png).
KL = {n: load('design/source/src_art/knob_layers/%s.png' % n) for n in ('shadow', 'skirt', 'cap', 'wear', 'index')}
KC0 = (507.96, 508.97)                 # centre du chapeau (ellipse ajustee sur son contour)
SY = 845.31 / 861.98                   # remise au cercle : echelle verticale
KR_PX = 845.31 / 2                     # rayon du chapeau (px du calque)
def unoval(a, dx=0.0):
    M = np.float32([[1, 0, dx], [0, SY, KC0[1] * (1 - SY)]])
    pm = a.copy(); pm[..., :3] *= pm[..., 3:4] / 255.0
    o = cv2.warpAffine(pm, M, (a.shape[1], a.shape[0]), flags=cv2.INTER_CUBIC, borderValue=0)
    al = np.clip(o[..., 3:4], 0, 255)
    o[..., :3] = np.where(al > 0.5, o[..., :3] * 255.0 / np.maximum(al, 1e-3), 0); o[..., 3:4] = al
    return o
for n in KL: KL[n] = unoval(KL[n], dx=(KC0[0] - 512.5) if n == 'index' else 0.0)
# gorge sombre entre le chapeau et la jupe (le calque de jupe a un trou un peu plus grand que le chapeau)
hh_, ww_ = KL['cap'].shape[:2]
yk, xk = np.mgrid[0:hh_, 0:ww_].astype(np.float32)
rk_ = np.hypot(xk - KC0[0], yk - KC0[1])
floor = np.dstack([np.full((hh_, ww_, 3), 14.0), np.clip((KR_PX + 12 - rk_) * 1.0, 0, 1)[..., None] * 255])
def stack(layers):
    out = np.zeros((hh_, ww_, 4), np.float32)
    for l in layers:
        a2 = l[..., 3:4] / 255.0
        out[..., :3] = out[..., :3] * (1 - a2) + l[..., :3] * a2
        out[..., 3:4] = out[..., 3:4] + (255 - out[..., 3:4]) * a2
    al = out[..., 3:4] / 255.0
    return out, al
# fond : ombre + gorge + jupe + chapeau (ombre composee a part pour garder sa transparence)
k_px = CAP_R * AS / KR_PX
n = int(round(2 * 1.12 * (KR_PX + 45) * k_px))
occlusion(disc(KNOB, CAP_R * 1.05), 3.0, 12.0, 1.0, 0.35)
def placed(l):
    rgb, a = place(l, KC0, k_px, n); return np.dstack([rgb, a * 255])
for l in (KL['shadow'], floor, KL['skirt'], KL['cap']):
    over(img, placed(l), KNOB[0] * AS - n / 2, KNOB[1] * AS - n / 2)
# sprite qui tourne : usure + index (2 px par unite), centre du chapeau au centre du sprite
nd = int(round(2 * (KR_PX + 2) * k_px)) | 1
topl = np.zeros((hh_, ww_, 4), np.float32)
# crasse du chapeau (demande « salis un peu le gros potard ») : physique, donc elle tourne avec le potard.
# poussiere grise prise dans les stries + voile gras irregulier + crasse plus dense au bord (contre la jupe),
# plus marquee en bas (la ou le pied passe) ; l'usure fournie est renforcee un peu.
rngk = np.random.default_rng(21)
def nfield(scale, seed):
    r_ = np.random.default_rng(seed)
    n_ = r_.standard_normal((hh_ // scale + 3, ww_ // scale + 3)).astype(np.float32)
    return cv2.resize(n_, (ww_ + 3 * scale, hh_ + 3 * scale), interpolation=cv2.INTER_CUBIC)[:hh_, :ww_]
thk_ = np.arctan2(xk - KC0[0], -(yk - KC0[1]))
capin = np.clip((KR_PX - 3 - rk_) / 3.0, 0, 1)
blot = np.clip(0.55 * nfield(110, 3) + 0.35 * nfield(45, 4) + 0.10 * nfield(16, 5) - 0.25, 0, None) ** 1.3
edge = np.clip((rk_ - 0.80 * KR_PX) / (0.18 * KR_PX), 0, 1) ** 1.6 * (0.55 + 0.45 * np.clip(nfield(30, 6), -1, 1))
lowb = 0.65 + 0.35 * np.clip((yk - KC0[1]) / KR_PX, 0, 1)
# poussiere : petits points clairs etires le long des stries (direction tangentielle)
dust = (rngk.random((hh_, ww_)) ** 400).astype(np.float32)
ang_ = np.degrees(np.mean(thk_))
dust = cv2.GaussianBlur(dust, (0, 0), 0.9) * 30
dust = np.clip(dust * (0.4 + blot), 0, 1)
grime_a = cv2.GaussianBlur(np.clip(0.30 * blot * lowb + 0.30 * edge, 0, 0.45), (0, 0), 2.0) * capin
grime = np.dstack([np.full((hh_, ww_), 52.0), np.full((hh_, ww_), 46.0), np.full((hh_, ww_), 38.0), grime_a * 255])
dustl = np.dstack([np.full((hh_, ww_), 150.0), np.full((hh_, ww_), 144.0), np.full((hh_, ww_), 134.0), dust * 0.35 * capin * 255])
wear2 = KL['wear'].copy(); wear2[..., 3] = np.clip(wear2[..., 3] * 1.35, 0, 255)
for l in (grime, dustl, wear2, KL['index']):
    a2 = l[..., 3:4] / 255.0
    topl[..., :3] = topl[..., :3] * (1 - a2) + l[..., :3] * a2
    topl[..., 3:4] = topl[..., 3:4] + (255 - topl[..., 3:4]) * a2
trgb, ta = place(np.dstack([np.where(topl[..., 3:4] > 0.5, topl[..., :3] * 255.0 / np.maximum(topl[..., 3:4], 1e-3), 0), topl[..., 3:4]]), KC0, k_px, nd)
Image.fromarray(np.dstack([np.clip(trgb, 0, 255), ta * 255]).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'knob_top.png'))
KNOB_SPR = nd / AS

# ------------------------------------------------------------------ 4. boutons LEARN / BASS, LED, footswitch (photos)
bt = load('design/source/src_art/button.png')
BT_C, BT_R = (618.5, 628.5), 532.0
for c in (LEARN, BASS):
    n = int(round(2 * BTN_R * 1.45 * AS)); k = BTN_R * AS / BT_R
    rgb, a = place(bt, BT_C, k, n)
    occlusion(disc(c, BTN_R), 2.0, 8.0, 1.0, 0.5)
    over(img, shadowed(rgb, a, 2 * BTN_R * AS, 0.55), c[0] * AS - n / 2, c[1] * AS - n / 2)

LDg, LDGON, LS = PC.led_sprites(LED_LENS, AS, colour='green')
LDo, LDOON, _ = PC.led_sprites(LED_LENS, AS, colour='orange')
for c, spr_ in ((OPEN_LED, LDg), (GATE_LED, LDo)):
    occlusion(disc(c, LED_LENS * 1.07) * 0.6, 2.0, 6.0)
    over(img, spr_, (c[0] - LS / 2) * AS, (c[1] - LS / 2) * AS)
Image.fromarray(np.clip(LDGON, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'led_green_on.png'))
Image.fromarray(np.clip(LDOON, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'led_orange_on.png'))

FSPR, FSREFL, FS_W, FS_BTN = PC.footswitch_sprite(FS_FLATS, AS)
_n = FSPR.shape[0]; _x0 = int(round((FS[0] - _n / AS / 2) * AS)); _y0 = int(round((FS[1] - _n / AS / 2) * AS))
_fa = np.zeros((H, W), np.float32); _fa[_y0:_y0 + _n, _x0:_x0 + _n] = np.clip((FSPR[..., 3] / 255.0 - 0.86) / 0.14, 0, 1)
occlusion(_fa)
over(img, FSPR, (FS[0] - FS_W / 2) * AS, (FS[1] - FS_W / 2) * AS)

TFR = TH.frames(TOG_R, TOG_S, AS * 2)              # [HARD (levier a droite), milieu, SOFT (levier a gauche)]
Image.fromarray(np.concatenate(TFR, 0), 'RGBA').save(os.path.join(ROOT, 'toggle_strip.png'), optimize=True)

# ------------------------------------------------------------------ 5. embases jack (kit) : OUT a gauche, IN a droite
alpha = body.copy()
for side in (-1, 1):
    j, jw_u, jh_u = PC.jack_sprite(JACK_LEN, AS, side)
    jh, jw = j.shape[:2]
    x0 = 0 if side < 0 else BXP + BW_PX - IN_OV
    y0 = int(round(JACK_Y * AS - jh / 2))
    over(img, j, x0, y0)
    ja = np.zeros((H, W), np.float32); ja[y0:y0 + jh, x0:x0 + jw] = j[..., 3] / 255.0
    alpha = np.maximum(alpha, ja)

out = np.dstack([np.clip(img, 0, 255), np.clip(alpha, 0, 1) * 255]).astype(np.uint8)
Image.fromarray(out, 'RGBA').save(os.path.join(ROOT, 'background.png'), optimize=True)

# ------------------------------------------------------------------ 6. halos des LED (la facade recoit la lumiere)
GR = 70.0
def glow(c, fn, col):
    x0p, y0p = round((c[0] - GR) * AS), round((c[1] - GR) * AS)
    size = round(2 * GR * AS)
    reg = img[y0p:y0p + size, x0p:x0p + size].astype(np.float64)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float64)
    d = np.hypot((xx + 0.5) / AS - GR, (yy + 0.5) / AS - GR)
    h1, h2 = 7.0, 24.0
    E = 1.1 * h1 ** 3 / (d ** 2 + h1 ** 2) ** 1.5 + 0.17 * h2 ** 3 / (d ** 2 + h2 ** 2) ** 1.5
    E *= np.clip((GR - d) / 20.0, 0, 1)
    E[d < LED_LENS * 1.07] *= 0.0
    lum = reg.mean(2, keepdims=True)
    lit = reg + (reg * 2.0 + 12.0 * np.clip(lum / 40.0, 0.3, 1.6)) * E[..., None] * np.array(col)
    add = lit - reg
    a = np.clip(np.abs(add).max(-1) / 12.0, 0, 1)
    rgb = np.where(a[..., None] > 1e-3, reg + add / np.maximum(a, 1e-3)[..., None], reg)
    Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, fn))
    return (x0p / AS, y0p / AS, size / AS, size / AS)
GLG = glow(OPEN_LED, 'glow_green.png', (0.25, 1.0, 0.35))
GLO = glow(GATE_LED, 'glow_orange.png', (1.0, 0.48, 0.10))

# ------------------------------------------------------------------ 7. serigraphie vectorielle (dessinee par le plugin ; ici pour l'apercu)
FONT = {0: os.path.join(ROOT, 'Poppins-Medium.ttf'), 1: os.path.join(ROOT, 'Poppins-Bold.ttf'),
        2: os.path.join(ROOT, 'Poppins-Light.ttf')}
WHITE, GREY, ORANGE = (234, 234, 231), (196, 198, 200), (236, 122, 44)
TEXTS = []            # (texte, police, em, espacement, x, y, rotation, couleur, ancrage)
def T(s, fnt, em, track, x, y, col=WHITE, rot=0.0, anchor='c'):
    TEXTS.append((s, fnt, em, track, x, y, rot, col, anchor))
def fit_track(s, fnt, em, width):
    f = ImageFont.truetype(FONT[fnt], 400)
    w0 = sum(f.getlength(ch) for ch in s) * em / 400.0
    return (width - w0) / max(1, len(s) - 1)
T('NOISE GATE', 0, 11.6, fit_track('NOISE GATE', 0, 11.6, DX(370) - DX(197)), DX(197), DY(177), ORANGE, anchor='l')
T('THRESHOLD', 0, 12.6, fit_track('THRESHOLD', 0, 12.6, DX(653) - DX(461)), CX, DY(201))
T('dB', 0, 11.0, 1.0, DX(806), DY(180), GREY)
T('LEARN', 0, 11.0, fit_track('LEARN', 0, 11.0, DX(906) - DX(823)), LEARN[0], LEARN[1] + BTN_R + 13.5)
T('-95', 0, 11.5, 0.6, DX(331), DY(705), GREY)
T('0', 0, 11.5, 0.6, DX(786), DY(707), GREY)
T('SOFT', 0, 12.6, fit_track('SOFT', 0, 12.6, DX(369) - DX(305)), DX(337), TOG[1])
T('HARD', 0, 12.6, fit_track('HARD', 0, 12.6, DX(810) - DX(740)), DX(775), TOG[1])
T('OPEN', 0, 12.6, fit_track('OPEN', 0, 12.6, DX(300) - DX(232)), DX(266), ROW_Y)
T('GATE', 0, 12.6, fit_track('GATE', 0, 12.6, DX(886) - DX(819)), DX(852), ROW_Y)
T('BASS', 0, 11.0, fit_track('BASS', 0, 11.0, DX(589) - DX(528)), BASS[0], BASS[1] + BTN_R + 13.5)
T('OUT', 0, 13.0, 2.0, BX0 + 26.0, JACK_Y, GREY, 90.0)
T('IN', 0, 13.0, 2.0, BX0 + BW - 26.0, JACK_Y, GREY, 90.0)
RULES = [(DX(393), DX(502), ROW_Y), (DX(615), DX(724), ROW_Y),   # traits OPEN - BASS - GATE
         (DX(337) + 32.0, TOG[0] - TOG_R - 18.0, TOG[1]), (TOG[0] + TOG_R + 18.0, DX(775) - 34.0, TOG[1])]   # SOFT - inverseur - HARD
TITLE = ('NGATE', 1, 0.0, 0.0, DX(344), DY(114.5))                 # lettres en relief (em ajuste plus bas)
_f = ImageFont.truetype(FONT[1], 400); _bb = _f.getbbox('NGATE')
TITLE_EM = (DX(452) - DX(233)) / ((_bb[2] - _bb[0]) / 400.0) * 0.93
TITLE_TRACK = 1.2

# ------------------------------------------------------------------ 8. Layout.h + layout.json
def f(v): return f"{v:.2f}f"
def PT(p): return "{ %s, %s }" % (f(p[0]), f(p[1]))
def RC(r): return "{ %s, %s, %s, %s }" % (f(r[0]), f(r[1]), f(r[2]), f(r[3]))
FW, FH = W / AS, H / AS
geo = {"frame": [FW, FH], "box": [BX0, 0, BW, BH], "knob": list(KNOB), "capR": CAP_R, "knobSpr": KNOB_SPR,
       "dotsR": DOTS_R, "dotA": DOT_A, "nDots": N_DOTS, "learn": list(LEARN), "bass": list(BASS), "btnR": BTN_R,
       "toggle": list(TOG), "togR": TOG_R, "togS": TOG_S, "openLed": list(OPEN_LED), "gateLed": list(GATE_LED), "ledS": LS,
       "glowG": list(GLG), "glowO": list(GLO), "fs": list(FS), "footR": FS_BTN, "fsS": FS_W, "preset": list(PRESET),
       "win": list(WIN), "plate": list(PLATE), "jackY": JACK_Y, "logo": [LOGO_C[0], LOGO_C[1], LOGO_W],
       "title": [TITLE[4], TITLE[5], TITLE_EM, TITLE_TRACK],
       "texts": [list(t[:7]) + [list(t[7]), t[8]] for t in TEXTS], "rules": [[a, b, y, 1.3] for a, b, y in RULES]}
json.dump(geo, open(os.path.join(ROOT, 'tools', 'layout.json'), 'w'), indent=1)
with open(os.path.join(ROOT, 'Layout.h'), 'w') as fo:
    fo.write(f"// genere par tools/make_art.py - ne pas modifier a la main (repere {FW} x {FH} = fond {W} x {H} px / 2)\n#pragma once\n#include <juce_graphics/juce_graphics.h>\nnamespace layout\n{{\n")
    fo.write(f"    constexpr float frameW = {f(FW)}, frameH = {f(FH)};   // pedale plein cadre (jacks aux bords gauche / droit)\n")
    fo.write(f"    const juce::Rectangle<float> boxRect {RC((BX0, 0, BW, BH))};\n")
    fo.write(f"    const juce::Point<float> knobPos {PT(KNOB)}; const float capR = {f(CAP_R)}, knobSprite = {f(KNOB_SPR)};   // usure + index (knob_top.png), tourne\n")
    fo.write(f"    const float dotsR = {f(DOTS_R)}, dotAngle = {f(DOT_A)}; const int numDots = {N_DOTS};\n")
    fo.write(f"    const juce::Point<float> learnPos {PT(LEARN)}, bassPos {PT(BASS)}; const float btnR = {f(BTN_R)}, btnCapR = {f(BTN_R * 0.74)};\n")
    fo.write(f"    const juce::Point<float> togglePos {PT(TOG)}; const float togS = {f(TOG_S)}, togR = {f(TOG_R)};\n")
    fo.write(f"    const juce::Point<float> openLedPos {PT(OPEN_LED)}, gateLedPos {PT(GATE_LED)}; const float ledS = {f(LS)};\n")
    fo.write(f"    const juce::Rectangle<float> glowGreenRect {RC(GLG)}, glowOrangeRect {RC(GLO)};\n")
    fo.write(f"    const juce::Point<float> fsPos {PT(FS)}; const float footR = {f(FS_BTN)}, fsS = {f(FS_W)};\n")
    fo.write(f"    const juce::Rectangle<float> presetRect {RC(PRESET)}, readoutRect {RC(WIN)}, plateRect {RC(PLATE)};\n")
    fo.write(f"    const float presetFont = 23.0f, jackY = {f(JACK_Y)};\n")
    fo.write("    struct Txt { const char* s; int font; float em, track, x, y, rot; juce::uint32 colour; int anchor; };   // police 0 medium, 1 bold, 2 light ; ancrage 0 centre, 1 gauche\n")
    fo.write("    const Txt texts[] = {\n" + ",\n".join(
        f'        {{ "{t[0]}", {t[1]}, {f(t[2])}, {f(t[3])}, {f(t[4])}, {f(t[5])}, {f(t[6])}, 0xff{t[7][0]:02x}{t[7][1]:02x}{t[7][2]:02x}, {1 if t[8] == "l" else 0} }}'
        for t in TEXTS) + "\n    };\n")
    fo.write("    struct Rule { float x0, x1, y, w; };\n")
    fo.write("    const Rule rules[] = { " + ", ".join(f"{{ {f(a)}, {f(b)}, {f(y)}, 1.3f }}" for a, b, y in RULES) + " };\n")
    fo.write(f"    const juce::Point<float> titlePos {PT(TITLE[4:6])}; const float titleEm = {f(TITLE_EM)}, titleTrack = {f(TITLE_TRACK)};   // NGATE en relief\n")
    fo.write(f"    const juce::Point<float> logoPos {PT(LOGO_C)}; const float logoW = {f(LOGO_W)};\n")
    fo.write("}\n")
print('ok', W, H, 'potard sprite', nd)
