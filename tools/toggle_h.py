"""Inverseur horizontal NGATE (photos fournies nov. 2026) : levier a droite = HARD, a gauche = SOFT.
Les deux photos sont ramenees sur leur rondelle, la photo SOFT est recalee sur la photo HARD par correlation (ECC)
sur l'ecrou / la rondelle hors du levier ; base commune = photo HARD hors du levier de SOFT.
Position du milieu (bascule ~55 ms) : levier dresse de la photo « milieu » du kit, vu dans l'axe, pose sur la base."""
import os, sys, numpy as np, cv2
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import toggle_photo as TP

def load(p): return np.asarray(Image.open(os.path.join(ROOT, p)).convert('RGBA')).astype(np.float32)

def washer_tb(a, band=110):
    """cercle de la rondelle ajuste sur ses arcs haut et bas (le levier horizontal passe au milieu)"""
    al = a[..., 3] > 128
    cs, _ = cv2.findContours(al.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)[:, 0, :].astype(np.float64)
    ys = c[:, 1]; yc = 0.5 * (ys.min() + ys.max())
    p = c[np.abs(ys - yc) > band]
    for _ in range(3):
        A = np.c_[2 * p[:, 0], 2 * p[:, 1], np.ones(len(p))]; b = (p ** 2).sum(1)
        x, y, k = np.linalg.lstsq(A, b, rcond=None)[0]; R = np.sqrt(k + x * x + y * y)
        res = np.abs(np.hypot(p[:, 0] - x, p[:, 1] - y) - R); p = p[res < 3.0]
    return x, y, R

def frames(washer_r_units, size_units, AS):
    N, R = 1400, 330.0
    hard, soft = load('design/source/src_art/toggle/hard_right.png'), load('design/source/src_art/toggle/soft_left.png')
    mid = load('assets/kit/toggle_photo_milieu.png')
    ch, cs_, cm = washer_tb(hard), washer_tb(soft), TP._washer(mid)
    H_ = TP._canon(hard, ch, N, R); S_ = TP._canon(soft, cs_, N, R); M_ = TP._canon(mid, cm, N, R)
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32); dx, dy = xx - N / 2, yy - N / 2; rr = np.hypot(dx, dy)
    mask = ((rr > 0.50 * R) & (rr < 1.03 * R) & (np.abs(dy) > 0.34 * R)).astype(np.uint8)
    gray = lambda a: cv2.GaussianBlur(a[..., :3].mean(-1) / 255.0, (0, 0), 1.5).astype(np.float32)
    Wm = np.eye(2, 3, dtype=np.float32)
    _, Wm = cv2.findTransformECC(gray(H_), gray(S_), Wm, cv2.MOTION_AFFINE,
                                 (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-7), mask, 5)
    S_ = cv2.warpAffine(S_, Wm, (N, N), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderValue=0)
    print('recalage SOFT -> HARD', np.round(Wm, 4).tolist())
    # base commune = HARD ; SOFT ne garde que son levier (moitie gauche + bague), eclairage ramene sur la base
    band = (np.abs(dy) < 0.36 * R) & (dx < 0.12 * R)
    lever = cv2.GaussianBlur((band | (rr < 0.60 * R)).astype(np.float32), (0, 0), 0.025 * R)
    ring = ((rr > 0.62 * R) & (rr < 0.97 * R) & ~band & ~((np.abs(dy) < 0.36 * R) & (dx > 0))).astype(np.float32)
    lo = lambda a: cv2.GaussianBlur(a, (0, 0), 0.18 * R)
    gb = np.stack([lo(H_[..., c] * ring) for c in range(3)], -1) / np.maximum(lo(ring)[..., None], 1e-3)
    gs = np.stack([lo(S_[..., c] * ring) for c in range(3)], -1) / np.maximum(lo(ring)[..., None], 1e-3)
    gain = np.clip(gb / np.maximum(gs, 1.0), 0.7, 1.4)
    fx = S_.copy(); fx[..., :3] = np.minimum(np.clip(S_[..., :3] * gain, 0, 255), fx[..., 3:4])
    # la base sous le levier de SOFT : la moitie gauche de HARD n'a pas de levier, mais la moitie droite si ->
    # on prend la base HARD partout sauf sur le levier de HARD (moitie droite), remplace par SOFT (sans levier a droite)
    bandH = cv2.GaussianBlur(((np.abs(dy) < 0.36 * R) & (dx > -0.12 * R) & (rr > 0.60 * R)).astype(np.float32), (0, 0), 0.025 * R)
    baseS = H_ * (1 - bandH[..., None]) + fx * bandH[..., None]          # rondelle / ecrou sans levier a droite
    soft_f = baseS * (1 - lever[..., None]) + fx * lever[..., None]
    # milieu : base sans levier (baseS hors levier gauche = base de HARD a gauche) + levier dresse du kit au centre
    base0 = baseS * 1.0
    leftband = cv2.GaussianBlur(((np.abs(dy) < 0.36 * R) & (dx < 0.12 * R) & (rr > 0.60 * R)).astype(np.float32), (0, 0), 0.025 * R)
    base0 = baseS * (1 - leftband[..., None]) + H_ * leftband[..., None]  # gauche : HARD (pas de levier) ; droite : SOFT (pas de levier)
    cen = cv2.GaussianBlur((rr < 0.62 * R).astype(np.float32), (0, 0), 0.02 * R)
    mid_f = base0 * (1 - cen[..., None]) + M_ * cen[..., None]
    res = []
    for pm in (H_, mid_f, soft_f):
        a = np.clip(pm[..., 3:4] / 255.0, 0, 1)
        st = np.dstack([np.where(a > 1e-4, pm[..., :3] / np.maximum(a, 1e-4), 0), pm[..., 3:4]])
        res.append(TP._sprite(st, (N / 2, N / 2, R), washer_r_units, size_units, AS))
    return res   # [HARD (levier a droite), milieu, SOFT (levier a gauche)]
