# NGATE (NINE HANDS | DSP) - notice PDF en francais, illustree avec le rendu reel du plugin (tools/render).
# Usage : python3 tools/manual.py <dossier des captures (design/renders)> <fichier PDF de sortie>
import os, sys, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, NextPageTemplate, Frame, Paragraph, Spacer, Image as RLImage,
                                Table, TableStyle, PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = sys.argv[1]
OUT = sys.argv[2]
VERSION = "2.0.0"
TMP = os.path.join(os.path.dirname(os.path.abspath(OUT)), "_notice_tmp")
os.makedirs(TMP, exist_ok=True)
FONTS = os.path.join(ROOT, "assets", "fonts")

for n, f in (("Pop", "Poppins-Regular"), ("PopL", "Poppins-Light"), ("PopM", "Poppins-Medium"), ("PopB", "Poppins-Bold"),
             ("Title", "BarlowCondensed-ExtraBold")):
    pdfmetrics.registerFont(TTFont(n, os.path.join(FONTS, f + ".ttf")))

ACC = colors.HexColor("#EC7A2C"); ACC_L = colors.HexColor("#F6A56C")       # orange de NOISE GATE
DARK = colors.HexColor("#1C1A18"); GREY = colors.HexColor("#6A645E"); LIGHT = colors.HexColor("#F6EEE6")

# ---------- logo blanc (SVG officiel -> PNG transparent) ----------
LOGO_PNG = os.path.join(TMP, "nine_hands_logo_blanc.png")
svg = open(os.path.join(ROOT, "NineHandsLogo.svg")).read()
def render_logo():
    try:
        subprocess.run(["rsvg-convert", "-w", "1200", os.path.join(ROOT, "NineHandsLogo.svg"), "-o", LOGO_PNG], check=True)
        return
    except Exception:
        pass
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 113})
        pg.set_content("<html><body style='margin:0;background:transparent'>" +
                       svg.replace("<svg ", "<svg width='1200' height='112.5' preserveAspectRatio='xMidYMid meet' ", 1) + "</body></html>")
        pg.screenshot(path=LOGO_PNG, omit_background=True, clip={"x": 0, "y": 0, "width": 1200, "height": 113}); b.close()
render_logo()

# ---------- captures ----------
def shot(name): return Image.open(os.path.join(SHOTS, name)).convert("RGB")
src = shot("ngate_open.png")
k = src.height / 900.0                      # repere du plugin : 603 x 900 unites (fond 1206 x 1800 / 2)

marks = [(1, 303, 395), (2, 98, 290), (3, 368, 62), (4, 556, 150), (5, 360, 506), (6, 169, 604), (7, 436, 604),
         (8, 248, 684), (9, 82, 713), (10, 386, 792), (11, 40, 330), (12, 563, 330)]
ann = src.copy(); dr = ImageDraw.Draw(ann)
fnt = ImageFont.truetype(os.path.join(FONTS, "Poppins-Bold.ttf"), 32)
for n, x, y in marks:
    cx, cy, r = x * k, y * k, 25
    dr.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255), outline=(236, 122, 44), width=5)
    dr.text((cx, cy + 1), str(n), font=fnt, fill=(28, 26, 24), anchor="mm")
annotated = os.path.join(TMP, "ngate_annotated.png"); ann.save(annotated)

def crop_u(im, box): return im.crop(tuple(int(v * k) for v in box))
gap = 18
def strip(parts, path):
    s = Image.new("RGB", (sum(p.width for p in parts) + gap * (len(parts) - 1), max(p.height for p in parts)), (255, 255, 255))
    x = 0
    for p in parts: s.paste(p, (x, 0)); x += p.width + gap
    s.save(path); return path

learn_img = strip([crop_u(shot(n), (372, 22, 562, 232)) for n in ("ngate_open.png", "ngate_learn.png", "ngate_learn_done.png")],
                  os.path.join(TMP, "ngate_learn_seq.png"))
tog_img = strip([crop_u(shot(n), (112, 506, 492, 572)) for n in ("anim_2_soft.png", "anim_0_hard.png")], os.path.join(TMP, "ngate_toggle.png"))
leds_img = strip([crop_u(shot(n), (62, 600, 542, 745)) for n in ("ngate_open.png", "ngate_gate_bass_soft.png", "ngate_bypass.png")],
                 os.path.join(TMP, "ngate_leds.png"))
menus_img = os.path.join(SHOTS, "ngate_menus.png")

# ---------- couverture : pedale detouree (canal alpha du fond), reflet au sol, halo orange tres doux ----------
bg_a = Image.open(os.path.join(ROOT, "background.png")).split()[3].resize(src.size, Image.LANCZOS)
cut = Image.new("RGBA", src.size, (0, 0, 0, 0)); cut.paste(src, (0, 0), bg_a)
cut = cut.crop(cut.getbbox())
cw, ch = cut.size
pad = int(cw * 0.16)
canvas = Image.new("RGBA", (cw + 2 * pad, int(ch * 1.30) + pad), (0, 0, 0, 255))
yy, xx = np.mgrid[0:canvas.height, 0:canvas.width].astype(np.float64)
gcx, gcy = canvas.width / 2, pad + ch * 0.45
glow = np.exp(-(((xx - gcx) / (cw * 0.62)) ** 2 + ((yy - gcy) / (ch * 0.48)) ** 2)) * 30
edge = np.clip(np.minimum.reduce([xx, canvas.width - 1 - xx, yy, canvas.height - 1 - yy]) / (pad * 0.9), 0, 1)
glow *= edge ** 2
halo = np.dstack([glow * 0.95, glow * 0.48, glow * 0.17, np.full_like(glow, 255)]).astype(np.uint8)
canvas = Image.alpha_composite(canvas, Image.fromarray(halo, "RGBA"))
refl = cut.transpose(Image.FLIP_TOP_BOTTOM)
ra = np.array(refl).astype(np.float64)
fade = np.clip(1 - np.arange(refl.height) / (refl.height * 0.22), 0, 1) ** 1.6 * 0.22
ra[..., 3] *= fade[:, None]
canvas.alpha_composite(Image.fromarray(ra.astype(np.uint8), "RGBA"), (pad, pad + ch + 6))
canvas.alpha_composite(cut, (pad, pad))
canvas = canvas.crop((0, 0, canvas.width, pad + int(ch * 1.20)))
cover = os.path.join(TMP, "ngate_cover_cutout.png"); canvas.convert("RGB").save(cover)

def img(path, width):
    im = Image.open(path); h = width * im.height / im.width
    return RLImage(path, width=width, height=h)

# ---------- styles ----------
st = {
    "h1": ParagraphStyle("h1", fontName="PopB", fontSize=20, leading=24, textColor=ACC, spaceAfter=8, spaceBefore=4, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="PopM", fontSize=13, leading=17, textColor=DARK, spaceAfter=4, spaceBefore=10, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="Pop", fontSize=9.6, leading=14, textColor=DARK, spaceAfter=5),
    "tip": ParagraphStyle("tip", fontName="Pop", fontSize=9.0, leading=12.4, textColor=DARK, spaceAfter=3),
    "small": ParagraphStyle("small", fontName="Pop", fontSize=8.2, leading=11.5, textColor=GREY),
    "cell": ParagraphStyle("cell", fontName="Pop", fontSize=8.4, leading=11, textColor=DARK),
    "cellb": ParagraphStyle("cellb", fontName="PopM", fontSize=8.4, leading=11, textColor=DARK),
    "cells": ParagraphStyle("cells", fontName="Pop", fontSize=7.8, leading=10, textColor=DARK),
    "cellbs": ParagraphStyle("cellbs", fontName="PopM", fontSize=7.8, leading=10, textColor=DARK),
}
def P(t, s="p"): return Paragraph(t, st[s])
def bullets(items, s="p"): return [P("&bull;&nbsp;&nbsp;" + i, s) for i in items]
def table(rows, widths, header=True, small=False):
    data = [[P(c, ("cellbs" if small else "cellb") if (header and r == 0) else ("cells" if small else "cell")) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#E6D8CB")),
             ("TOPPADDING", (0, 0), (-1, -1), 2 if small else 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 2 if small else 3)]
    if header: style += [("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACC)]
    t.setStyle(TableStyle(style)); return t

# ---------- donnees (identiques au code livre : PluginProcessor.cpp) ----------
FACTORY = [  # nom, seuil, hard, bass, range
    ("Clean Single Coils", -66, 0, 0, 0, "Simple bobinages en son clair : seuil bas et fermeture douce, les notes tenues s'éteignent naturellement, seul le souffle des micros disparaît."),
    ("Crunch Humbuckers", -58, 0, 0, 0, "Humbuckers dans un ampli légèrement saturé : coupe le souffle entre les accords sans raccourcir les fins de phrase."),
    ("High Gain Tight", -48, 1, 0, 0, "Ampli à fort gain : fermeture rapide, silence net entre les riffs."),
    ("Metal Chug", -42, 1, 0, 0, "Palm mutes serrés en metal : la note s'arrête dès que la main étouffe les cordes."),
    ("Djent Staccato", -36, 1, 0, 0, "Seuil haut pour des rythmiques très hachées : chaque coup de médiator est découpé, les silences sont absolus."),
    ("Fuzz Tamer", -52, 0, 0, 1, "Pour calmer le souffle d'une fuzz ou d'un overdrive bruyant : fermeture douce et plancher à −40 dB, le gate ne coupe jamais net."),
    ("Ambient Natural Decay", -74, 0, 0, 2, "Pour les sons longs et les effets d'ambiance : seuil très bas, plancher à −20 dB, seul le bruit de fond en dessous des notes est atténué."),
    ("Bass Clean", -68, 0, 1, 0, "Basse en son clair : mode BASS (détection du Mi et du Si grave), fermeture douce."),
    ("Bass Drive", -55, 1, 1, 0, "Basse saturée : mode BASS et fermeture rapide pour un grave tendu et des silences nets."),
    ("Studio Silence", -78, 1, 0, 0, "Pour l'enregistrement : seuil très bas, juste au-dessus du bruit de fond, qui ne touche pas au jeu."),
]
RANGE = ["coupure totale", "−40 dB", "−20 dB"]

W = A4[0] - 36 * mm
f = [NextPageTemplate("p"), Spacer(1, 1), PageBreak()]

f.append(P("1. Présentation", "h1"))
f += [P("<b>NGATE</b> est un noise gate NINE HANDS | DSP pour guitare et basse, au format pédale simple. Il coupe le ronflement et le souffle entre les notes, quand vous ne jouez pas, et laisse passer l'attaque et la fin des notes telles quelles. Il s'inspire des noise gates de pédalier à un potard : un grand potard <b>THRESHOLD</b>, un bouton <b>LEARN</b> qui règle le seuil tout seul en écoutant le bruit de fond, un inverseur <b>SOFT / HARD</b> et un mode <b>BASS</b>."),
      P("La couronne de points autour du potard est un vumètre : elle montre en direct le niveau qui arrive dans la pédale, en orange sous le seuil (le gate se ferme) et en vert au-dessus (le gate est ouvert). Deux LED, <b>OPEN</b> et <b>GATE</b>, indiquent l'état du gate.")]
f.append(P("2. Installation", "h1"))
for h, x in [("Windows", "Téléchargez <b>Ngate-VST3-Windows.zip</b> (bouton Windows du dépôt GitHub Nine-Hands-Dsp/ngate, rubrique Releases), décompressez-le et copiez le dossier <b>Ngate.vst3</b> dans <b>C:\\Program Files\\Common Files\\VST3</b>."),
             ("macOS", "Téléchargez <b>Ngate-VST3-macOS.zip</b>, décompressez-le et copiez <b>Ngate.vst3</b> dans <b>~/Bibliothèque/Audio/Plug-Ins/VST3</b>. Si macOS le bloque, tapez <b>xattr -cr ~/Library/Audio/Plug-Ins/VST3/Ngate.vst3</b> dans le Terminal. Le binaire est universel (Apple Silicon et Intel)."),
             ("Reaper", "Options &gt; Préférences &gt; Plug-ins &gt; VST &gt; <b>Re-scan</b>. Le plugin apparaît sous le nom <b>Ngate (NINE HANDS | DSP)</b>, dans la catégorie Dynamics. Pour le piloter avec des footswitchs ou une pédale d'expression MIDI, la piste doit recevoir le MIDI du contrôleur (armement ou monitoring d'entrée, entrée MIDI réglée sur votre appareil, par exemple la M-Vave Chocolate Plus).")]:
    f.append(P(h, "h2")); f.append(P(x))
f.append(PageBreak())

f.append(P("3. Vue d'ensemble de l'interface", "h1"))
ov_rows = [["#", "Commande", "Rôle"],
    ["1", "THRESHOLD", "Seuil d'ouverture du gate, de −95 dB à 0 dB. Glisser vers le haut / le bas, molette, double-clic = −60 dB, clic droit = MIDI Learn (valable pour toutes les commandes)."],
    ["2", "Couronne de points", "Vumètre du signal d'entrée : orange sous le seuil, vert au-dessus."],
    ["3", "Afficheur", "Valeur du seuil en dB ; « LEARN » et une barre de progression pendant l'apprentissage."],
    ["4", "LEARN", "Mesure le bruit de fond pendant 1,5 s et règle le seuil juste au-dessus."],
    ["5", "SOFT / HARD", "Fermeture douce et naturelle (SOFT) ou rapide et serrée (HARD)."],
    ["6", "LED OPEN", "Verte : le gate est ouvert, le son passe."],
    ["7", "LED GATE", "Orange : le gate est fermé (le bruit est coupé)."],
    ["8", "BASS", "Mode basse : la détection descend jusqu'au Si grave. Couronne orange quand il est actif."],
    ["9", "Barre de presets / ligne d'état", "Au repos : flèches = preset précédent / suivant, clic sur le nom = menu des presets. Pendant un réglage : valeur en direct."],
    ["10", "Footswitch", "Effet actif / bypass."],
    ["11", "OUT", "Jack de sortie."],
    ["12", "IN", "Jack d'entrée."]]
ov = Table([[[img(annotated, 88 * mm)], table(ov_rows, [8 * mm, 25 * mm, W - 92 * mm - 33 * mm])]], colWidths=[92 * mm, W - 92 * mm])
ov.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
f.append(ov); f.append(PageBreak())

f.append(P("4. Les commandes en détail", "h1"))
f.append(P("THRESHOLD", "h2"))
f.append(P("Le seuil au-dessus duquel le gate s'ouvre, de <b>−95 dB</b> (tout à gauche, le gate ne se ferme presque jamais) à <b>0 dB</b> (tout à droite). Tant que le signal reste au-dessus du seuil, le son passe intact ; quand il retombe en dessous (cordes étouffées, silence entre deux phrases), le gate se referme et coupe le bruit. Le bon réglage est juste au-dessus du bruit de fond quand vous ne jouez pas : regardez la couronne, les points orange qui restent allumés au repos montrent le niveau du bruit. Le seuil change en douceur (lissage de 20 ms), sans clic, même piloté par une pédale d'expression."))
f.append(P("LEARN", "h2"))
f.append(P("Étouffez les cordes, gardez le volume de la guitare comme pour jouer, puis cliquez sur <b>LEARN</b> (ou appuyez sur le footswitch MIDI qui lui est assigné). Pendant <b>1,5 seconde</b>, la pédale écoute le bruit de fond : l'afficheur affiche <b>LEARN</b> avec une barre de progression, le bouton s'entoure d'orange et la ligne d'état demande <i>mute the strings</i>. Les 120 premières millisecondes sont ignorées (le bruit du clic ou de l'appui). Le seuil est alors placé au niveau du bruit mesuré <b>+ 3 dB en SOFT</b> ou <b>+ 5 dB en HARD</b> (jamais au-dessus de −6 dB) ; la ligne d'état affiche par exemple <i>Noise −68.6 dB &gt; −63.6 dB</i>. Un second clic pendant la mesure l'annule."))
f.append(KeepTogether([Spacer(1, 2 * mm), img(learn_img, W * 0.70), P("Afficheur et LEARN : au repos, pendant la mesure, puis seuil appris.", "small")]))
f.append(P("Inverseur SOFT / HARD", "h2"))
f.append(P("<b>SOFT</b> (levier à gauche) : attaque de 2 ms, maintien de 50 ms, relâchement de 180 ms et hystérésis de 6 dB ; sous le seuil, le gate agit comme un expandeur (1:3) au lieu de couper net : les notes tenues s'éteignent naturellement. <b>HARD</b> (levier à droite) : attaque de 0,3 ms, maintien de 25 ms, relâchement de 15 ms, hystérésis de 3 dB et coupure franche : le silence tombe dès que vous étouffez les cordes, idéal pour le metal et les rythmiques hachées. Cliquez sur le levier pour le basculer, ou directement sur le mot <b>SOFT</b> ou <b>HARD</b> ; la molette fonctionne aussi."))
f.append(KeepTogether([Spacer(1, 2 * mm), img(tog_img, W * 0.80), P("Inverseur en position SOFT, puis HARD.", "small")]))
f.append(P("BASS", "h2"))
f.append(P("Un clic active le mode basse (le bouton s'entoure d'orange). La détection descend jusqu'à 22 Hz au lieu de 75 Hz, pour que le Mi grave (41 Hz) et le Si grave (31 Hz) d'une basse ouvrent bien le gate ; en mode guitare, au contraire, le ronflement secteur (50 / 60 Hz) et les infra-graves ne l'ouvrent pas. Les temps sont aussi allongés pour suivre les notes graves : maintien de 90 ms et relâchement de 300 ms en SOFT, 60 ms et 35 ms en HARD. Utile aussi pour une guitare 7 cordes accordée en Sol ou plus bas."))
f.append(P("Range (clic droit &gt; Gate settings)", "h2"))
f.append(P("Ce que devient le son quand le gate est fermé : <b>Full mute</b> (coupure totale, par défaut), <b>−40 dB</b> (il reste un léger souffle, plus naturel) ou <b>−20 dB</b> (atténuation douce, pour les sons d'ambiance). Le même sous-menu reprend SOFT / HARD et Guitar / Bass."))

f.append(P("5. Footswitch et LED", "h1"))
f += bullets(["<b>Footswitch</b> : il bascule dès l'appui, comme sur Echoflex. En bypass, le signal passe sans traitement ; le passage se fait par un fondu de 8 ms, sans clic.",
              "<b>LED OPEN et GATE</b> : la LED verte OPEN s'allume quand le gate est ouvert, la LED orange GATE quand il se ferme ; elles se croisent en fondu et éclairent la façade autour d'elles. En bypass, les LED, la couronne et le bouton BASS s'éteignent et l'afficheur baisse."])
f.append(KeepTogether([Spacer(1, 2 * mm), img(leds_img, W), P("Gate ouvert (OPEN vert) ; gate fermé en mode BASS (GATE orange, BASS entouré d'orange) ; bypass.", "small")]))

f.append(P("6. MIDI", "h1"))
f.append(P("Toutes les commandes se pilotent depuis un contrôleur MIDI (footswitchs, pédale d'expression). Ngate écoute tous les canaux MIDI. <b>Aucun CC n'est assigné d'office</b> : vous choisissez chacun avec le <b>MIDI Learn</b>, le plugin ne réagit donc jamais à un contrôleur que vous n'avez pas assigné vous-même."))
midi = [["Commande", "Assignation", "Type"],
        ["Threshold", "MIDI Learn", "Continu : 0 = −95 dB, 127 = 0 dB"],
        ["Soft / Hard", "MIDI Learn", "Bascule : 64 ou plus = HARD"],
        ["Bass", "MIDI Learn", "Bascule : 64 ou plus = BASS"],
        ["LEARN button", "MIDI Learn", "Déclencheur : chaque appui lance un LEARN"],
        ["Footswitch", "MIDI Learn", "À accrochage : 64 ou plus = effet actif"],
        ["Footswitch toggle", "MIDI Learn", "Momentané : chaque appui inverse l'état"]]
f.append(KeepTogether([table(midi, [36 * mm, 26 * mm, W - 62 * mm])]))
f.append(Spacer(1, 2 * mm))
f += bullets(["<b>MIDI Learn</b> : clic droit sur une commande, choisissez <b>MIDI Learn: &lt;nom&gt;</b>, puis bougez la pédale d'expression ou appuyez sur le bouton MIDI. La ligne d'état affiche <b>MIDI LEARN</b> et le nom de la commande, puis confirme pendant 2 secondes, par ex. <b>Threshold = CC 11</b>. Le premier CC reçu sert seulement à l'assignation, il n'agit pas sur le son. Un CC déjà utilisé par une autre commande passe à la nouvelle. <b>Clear MIDI</b> retire une assignation ; clic droit &gt; MIDI &gt; <b>Clear all MIDI assignments</b> les retire toutes. Les assignations sont sauvegardées avec le projet.",
              "<b>Footswitch</b> : deux assignations possibles, à choisir selon votre pédalier : <b>Footswitch</b> (le bouton envoie 127 puis 0) ou <b>Footswitch toggle</b> (chaque appui inverse l'état).",
              "<b>Program Change 1 à 10</b> : rappel des presets d'usine. Tous les paramètres sont aussi automatisables dans le DAW."])

f.append(P("7. Fenêtre et menus", "h1"))
f.append(P("Ngate utilise le format pédale simple d'Echoflex : la fenêtre s'ouvre à <b>60 %</b> et ne peut jamais être réduite en dessous. Clic droit &gt; <b>Plugin size</b> : <b>60 %</b>, <b>75 %</b> ou <b>100 %</b> pour cette fenêtre, « (default) » indiquant la taille par défaut ; <b>Default size (new windows)</b> choisit la taille d'ouverture de toutes les nouvelles fenêtres de Ngate (réglage commun à toutes les instances, enregistré sur l'ordinateur) et redimensionne aussitôt la fenêtre courante. La taille n'est pas sauvegardée avec le projet. Vous pouvez aussi tirer le coin en bas à droite jusqu'à 150 % (les proportions sont conservées)."))
f.append(P("La <b>barre de presets</b> et la <b>ligne d'état</b> partagent la même pastille. Au repos, elle affiche le preset en cours (ou <i>Edited</i>). Dès qu'un réglage bouge (souris, molette, automation, MIDI), la ligne d'état prend sa place et affiche la valeur en direct (par ex. <i>−40.0 dB SOFT BASS</i>) ainsi que les messages du LEARN et du MIDI Learn ; elle s'efface ensuite et la barre de presets revient."))
f.append(P("Le <b>clic droit</b> ouvre le menu à l'endroit du clic : sur une commande, ses assignations MIDI ; ailleurs, le menu général (Plugin size, presets, LEARN, Gate settings, MIDI)."))
f.append(KeepTogether([Spacer(1, 2 * mm), img(menus_img, W * 0.92), P("Menus clic droit : menu général, menu du potard THRESHOLD, sous-menu Gate settings.", "small")]))

f.append(P("8. Presets", "h1"))
f.append(P("Utilisez les flèches de la barre de presets, cliquez sur son nom, faites un clic droit n'importe où, ou passez par le menu de presets de votre DAW. Clic droit &gt; <b>Save user preset</b> enregistre jusqu'à 9 presets personnels, rappelés par <b>Load user preset</b>."))
rows = [["PC", "Preset", "Seuil", "Mode · Instrument · Range", "Description"]]
for i, (n, thr, hard, bass, rng, d) in enumerate(FACTORY):
    rows.append([str(i + 1), "<b>" + n + "</b>", f"{thr} dB".replace("-", "−"), f"{'HARD' if hard else 'SOFT'} · {'Bass' if bass else 'Guitar'} · {RANGE[rng]}", d])
f.append(table(rows, [8 * mm, 30 * mm, 14 * mm, 36 * mm, W - 88 * mm], small=True))

f.append(P("9. Conseils d'utilisation", "h1"))
f += bullets(["Dans Reaper, placez Ngate <b>en premier</b> dans la chaîne, juste après l'entrée de la guitare, <b>avant</b> votre simulateur d'ampli (par exemple avant Ampire, suivi d'Impulse pour le baffle) : il coupe le bruit de la guitare avant qu'il ne soit amplifié par la saturation.",
              "Commencez toujours par <b>LEARN</b>, cordes étouffées, puis affinez au potard : si la fin des notes est coupée, baissez le seuil ou passez en SOFT ; si du souffle passe encore entre les riffs, montez-le ou passez en HARD.",
              "Pour une 7 cordes en Sol ou plus bas, ou une basse, activez <b>BASS</b> : les notes graves ouvrent le gate franchement et ne sont pas coupées trop tôt.",
              "Pour un son clair ou des effets d'ambiance, préférez SOFT avec un Range à −40 dB ou −20 dB : le gate reste inaudible."], "tip")
tech = [["Format", "VST3 (Windows 64 bits, macOS universel)"], ["Canaux", "Mono ou stéréo (détection sur la plus forte des deux voies)"],
        ["Latence", "aucune"], ["Seuil", "−95 à 0 dB, lissé sur 20 ms"],
        ["SOFT", "attaque 2 ms, maintien 50 ms (BASS 90), relâchement 180 ms (BASS 300), hystérésis 6 dB, expansion 1:3"],
        ["HARD", "attaque 0,3 ms (BASS 0,6), maintien 25 ms (BASS 60), relâchement 15 ms (BASS 35), hystérésis 3 dB"],
        ["Détection", "Guitar : 75 Hz – 9 kHz ; Bass : 22 Hz – 6 kHz"], ["Range", "coupure totale, −40 dB ou −20 dB"],
        ["LEARN", "mesure 1,5 s ; seuil = bruit + 3 dB (SOFT) ou + 5 dB (HARD), au plus −6 dB"],
        ["Bypass", "fondu de 8 ms"],
        ["MIDI", "tous les canaux ; MIDI Learn sur 6 commandes (rien d'assigné par défaut), Program Change 1-10"],
        ["Fenêtre", "Plugin size 60 % / 75 % / 100 %, taille par défaut des nouvelles fenêtres au choix (60 % au départ), jusqu'à 150 %, jamais sous 60 %"]]
f.append(KeepTogether([P("10. Caractéristiques techniques", "h1"), table(tech, [26 * mm, W - 26 * mm], header=False, small=True)]))

def deco(c, doc):
    c.saveState()
    c.setFillColor(DARK); c.rect(0, A4[1] - 6 * mm, A4[0], 6 * mm, stroke=0, fill=1)
    c.setFillColor(ACC); c.rect(0, A4[1] - 6.8 * mm, A4[0], 0.8 * mm, stroke=0, fill=1)
    c.setFont("Pop", 7.5); c.setFillColor(GREY)
    c.drawString(18 * mm, 10 * mm, "Ngate (NINE HANDS | DSP) · v" + VERSION)
    c.drawRightString(A4[0] - 18 * mm, 10 * mm, str(doc.page))
    c.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
                      title="NGATE - Notice v" + VERSION, author="NINE HANDS | DSP")
# ---- Couverture « minimale » (modele 6) : gabarit fixe commun a toutes les notices ----
COVER_NAME, COVER_SUB = "NGATE", "Noise gate"
PEDAL_H, PEDAL_MAXW, PEDAL_TOP = 82 * mm, 115 * mm, 84 * mm
LANG_TOP = 18 * mm
NAME_TOP, NAME_PT = 194 * mm, 30
SUB_TOP, SUB_PT = 208 * mm, 10
LOGO_W, LOGO_BOTTOM = 38 * mm, 22 * mm
BAND_H = 3 * mm
def cover_bg(c, doc):
    c.saveState(); c.setFillColor(colors.black); c.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    c.setFillColor(ACC); c.rect(0, 0, A4[0], BAND_H, stroke=0, fill=1)
    def line(text, top, font, size, cs, col):
        w = pdfmetrics.stringWidth(text, font, size) + cs * (len(text) - 1)
        t = c.beginText((A4[0] - w) / 2, A4[1] - top - size * 0.8); t.setFont(font, size); t.setCharSpace(cs)
        t.setFillColor(col); t.textOut(text); c.drawText(t)
    line("FRANÇAIS", LANG_TOP, "PopM", 8.5, 0, ACC_L)
    ci = Image.open(cover); iw, ih = ci.size
    cw_ = iw / 1.32; pad_ = int(cw_ * 0.16); ch_ = (ih - pad_) / 1.2
    kk = min(PEDAL_H / ch_, PEDAL_MAXW / cw_)
    dw, dh = iw * kk, ih * kk
    y0 = A4[1] - (PEDAL_TOP + (PEDAL_H - ch_ * kk) / 2) + pad_ * kk
    c.drawImage(cover, (A4[0] - dw) / 2, y0 - dh, dw, dh)
    line(COVER_NAME, NAME_TOP - NAME_PT * 0.02, "Title", NAME_PT, NAME_PT * 0.5, colors.white)
    line(COVER_SUB, SUB_TOP, "Pop", SUB_PT, 1.5, colors.HexColor("#BDC4B8"))
    lw, lh = Image.open(LOGO_PNG).size
    c.drawImage(LOGO_PNG, (A4[0] - LOGO_W) / 2, LOGO_BOTTOM, LOGO_W, LOGO_W * lh / lw, mask="auto")
    c.restoreState()
doc.addPageTemplates([PageTemplate(id="cover", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="fc")], onPage=cover_bg),
                      PageTemplate(id="p", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")], onPage=deco)])
doc.build(f)
import shutil; shutil.rmtree(TMP, ignore_errors=True)
print(OUT)
