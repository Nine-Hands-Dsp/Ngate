# NGATE (NINE HANDS | DSP) - notice PDF bilingue (anglais puis francais), illustree avec le rendu reel du plugin.
# Usage : python3 tools/manual.py <fichier PDF de sortie>
# Images : tools/manual_assets/ (captures reprises de la notice v1.4.0, toujours justes : facade, etats, courbe ;
# aucune capture de menu). Polices : assets/fonts (Poppins).
# Contenu verifie contre PluginEditor.cpp / PluginProcessor.cpp (v1.5.1). Pas d'historique des versions dans le PDF.
import os, sys
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, NextPageTemplate, Frame, Paragraph, Spacer, Image as RLImage,
                                Table, TableStyle, PageBreak, CondPageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", "NGATE_Manual_EN-FR_v1.5.2.pdf")
VERSION = "1.5.2"
FONTS = os.path.join(ROOT, "assets", "fonts")
A = os.path.join(ROOT, "tools", "manual_assets")

for n, f in (("Pop", "Poppins-Regular"), ("PopL", "Poppins-Light"), ("PopM", "Poppins-Medium"), ("PopB", "Poppins-Bold")):
    pdfmetrics.registerFont(TTFont(n, os.path.join(FONTS, f + ".ttf")))

ACC = colors.HexColor("#E88032"); ACC_L = colors.HexColor("#F2A66C")       # orange des LED / de l'afficheur
DARK = colors.HexColor("#1D1E21"); GREY = colors.HexColor("#646A78"); LIGHT = colors.HexColor("#F6EEE6")

st = {
    "h1": ParagraphStyle("h1", fontName="PopB", fontSize=20, leading=24, textColor=DARK, spaceAfter=8, spaceBefore=4, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="PopM", fontSize=12.5, leading=16, textColor=ACC, spaceAfter=4, spaceBefore=9, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="Pop", fontSize=9.6, leading=14, textColor=DARK, spaceAfter=5),
    "note": ParagraphStyle("note", fontName="Pop", fontSize=9, leading=13, textColor=DARK, backColor=LIGHT, borderPadding=6, spaceBefore=6, spaceAfter=10),
    "cap": ParagraphStyle("cap", fontName="Pop", fontSize=8.2, leading=11, textColor=GREY, alignment=TA_CENTER),
    "cell": ParagraphStyle("cell", fontName="Pop", fontSize=8.4, leading=11, textColor=DARK),
    "cellb": ParagraphStyle("cellb", fontName="PopM", fontSize=8.4, leading=11, textColor=colors.white),
    "cover": ParagraphStyle("cover", fontName="PopB", fontSize=40, leading=48, textColor=colors.white, alignment=TA_CENTER),
    "coversub": ParagraphStyle("coversub", fontName="Pop", fontSize=12, leading=17, textColor=colors.HexColor("#BDBAB4"), alignment=TA_CENTER),
    "coverlang": ParagraphStyle("coverlang", fontName="PopM", fontSize=8.5, leading=11, textColor=ACC_L),
}
W = A4[0] - 36 * mm

def P(t, s="p"): return Paragraph(t, st[s])
def img(name, width):
    path = os.path.join(A, name); im = Image.open(path)
    return RLImage(path, width=width, height=width * im.height / im.width)
def table(rows, widths, header=True):
    data = [[P(c, "cellb" if (header and r == 0) else "cell") for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#E2D9CF")),
             ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5)]
    if header: style += [("BACKGROUND", (0, 0), (-1, 0), DARK)]
    t.setStyle(TableStyle(style)); return t
def row_of(items, total):
    n = len(items); w = total / n
    cells = [[img(f, w - 6 * mm), P(c, "cap")] for f, c in items]
    t = Table([cells], colWidths=[w] * n)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    return t

T = {
"en": dict(
 lang="ENGLISH", sub="Noise gate pedal for guitar &amp; bass - VST3", ver="User manual &nbsp;·&nbsp; version " + VERSION,
 intro_t="1. Introduction",
 intro="NGATE is a single-format pedal noise gate for guitar and bass, inspired by the classic noise gate pedals with a big THRESHOLD knob and a LEARN button (NG-1 type). One big brushed-aluminium <b>THRESHOLD</b> knob, a <b>LEARN</b> button that measures your noise floor and sets the threshold for you, a <b>SOFT / HARD</b> switch, a <b>BASS</b> mode, OPEN / GATE LEDs and a footswitch. It kills hum, hiss and amp noise between phrases, without chopping the end of your notes.",
 intro_note="<b>Anti-stutter</b>: hysteresis (3 dB in HARD, 6 dB in SOFT) and a hold time (25 / 60 ms HARD, 50 / 90 ms SOFT, guitar / bass), so a sustained note hovering around the threshold does not open and close in bursts. Both stereo channels are always gated together.",
 inst_t="2. Installation",
 inst=["<b>Windows</b>: copy <b>Ngate.vst3</b> into <b>C:\\Program Files\\Common Files\\VST3\\</b>.",
       "<b>macOS</b> (universal binary): unzip, then copy <b>Ngate.vst3</b> into <b>~/Library/Audio/Plug-Ins/VST3/</b>. If macOS blocks it, run once in Terminal: <b>xattr -cr ~/Library/Audio/Plug-Ins/VST3/Ngate.vst3</b>.",
       "<b>Reaper</b>: Options &gt; Preferences &gt; Plug-ins &gt; VST &gt; Re-scan. The plug-in appears as <b>Ngate (NINE HANDS | DSP)</b>."],
 ov_t="3. The interface",
 ov_cap="Numbers refer to the table below and to sections 4 and 5.",
 ov_hdr=["No.", "Element", "Function"],
 ov=[["1", "Readout", "Threshold in dB. Shows LEARN and a progress bar while learning."],
     ["2", "LEARN", "Measures the noise floor (1.5 s) and sets the threshold."],
     ["3", "Dot ring", "Live input meter: orange = below threshold (muted), green = above (passes)."],
     ["4", "THRESHOLD", "Opening threshold, -95 dB to 0 dB."], ["5", "SOFT / HARD", "Gate character (mini toggle)."],
     ["6/8", "OPEN / GATE", "Green = signal passes, orange = gate closed."], ["7", "BASS", "Bass mode (orange ring when on)."],
     ["9", "Footswitch", "Effect on / off."], ["10", "Status line", "Over the logo: appears only when something changes, stays 2.5 s, then fades."],
     ["11 / 12", "INPUT / OUTPUT", "Input on the right side, output on the left (female jack sockets)."]],
 ctl_t="4. Controls",
 thr_h="THRESHOLD (4)",
 thr="Opening threshold from -95 dB to 0 dB (default -60 dB), shown on the readout. Drag the knob, use the mouse wheel for fine tuning, double-click = -60 dB. The aluminium cap really turns (scratches and wear move with it) while the machined reflections stay under the light. The dot ring around it is a live input meter: the change from orange to green marks the threshold.",
 lrn_h="Setting the gate with LEARN (2)",
 lrn=["Plug in, set your amp sim and pedals as you will play, turn the guitar volume fully up.",
      "Mute the strings with your hand (do not play) and click <b>LEARN</b>.",
      "For 1.5 s the readout shows LEARN with an orange progress bar and an orange ring fills around the button. Click again to cancel.",
      "NGATE sets the threshold just above the loudest noise it heard: <b>+5 dB in HARD, +3 dB in SOFT</b>. Mains hum (50 / 60 Hz) is ignored by the detector.",
      "The status line shows the result, e.g. “Noise floor -70.0 dB -&gt; threshold -65.0 dB”. Fine-tune with the knob or the wheel."],
 sh_h="SOFT or HARD? (5)",
 sh=["<b>HARD</b> (default): a real gate, opens in 0.3 ms and closes fast (15 ms guitar / 35 ms bass). Tight high-gain rhythm, metal chugs, djent stops.",
     "<b>SOFT</b>: a downward expander (1:3 below the threshold) with a slow release (180 ms guitar / 300 ms bass): the note fades out naturally. Cleans, crunch, ambient.",
     "Click the lever to flip it, or click the SOFT or HARD word to choose directly."],
 curve="curve_en.png",
 curve_cap="Output level against input level, threshold -50 dB, full mute range: HARD drops to silence, SOFT slopes down.",
 bass_h="BASS mode (7)",
 bass="Low notes have long cycles (41 Hz low E = 24 ms per cycle; 31 Hz low B = 32 ms). In BASS mode the detector listens down to 22 Hz instead of 75 Hz, and envelope and hold times are longer, so long bass notes are not chopped. An orange ring lights around the button.",
 rng_h="Range (right-click)",
 rng="What the closed gate leaves: <b>Full mute</b> (default), <b>-40 dB</b> (keeps a breath of the room) or <b>-20 dB</b> (gentle noise reduction). Saved in presets.",
 fs_t="5. Footswitch, LEDs and status line",
 fs=["<b>Footswitch</b>: effect on / off with an 8 ms click-free fade. In bypass everything goes dark (dot ring, LEDs, BASS ring) and the readout dims.",
     "<b>OPEN</b> LED green = signal passes; <b>GATE</b> LED orange = gate closed. In SOFT both cross-fade.",
     "<b>Status line</b> (under the footswitch, over the logo): appears only when something changes (threshold, mode, input level, gate state, preset, MIDI), stays 2.5 s then fades. During a MIDI Learn it shows the prompt."],
 caps=["Signal passing: green dots above the threshold, OPEN lit.", "BASS + SOFT, gate closed: only the noise (orange) shows.",
       "LEARN in progress: the status line shows the measurement.", "Bypass: everything goes dark."],
 midi_t="6. MIDI",
 midi_intro="NGATE listens to every MIDI channel (omni). <b>No CC is assigned by default</b>: every control is assigned with <b>MIDI Learn</b> to your controller (M-Vave Chocolate Plus, expression pedal...).",
 midi=["<b>Right-click a control</b> (THRESHOLD, SOFT / HARD, BASS, LEARN or the footswitch) and choose <b>MIDI Learn: &lt;control&gt; (none)</b> (or the learnt CC, e.g. <b>(CC 64)</b>). The footswitch offers its two entries: <b>Footswitch</b> (latching) and <b>Footswitch toggle</b> (each press).",
       "The status line shows <b>MIDI LEARN: move a control for X</b>. Move a pedal or press a footswitch on your controller: the first CC received is assigned (it does not act on the sound) and the status line confirms <b>X = CC n</b> for 2 seconds.",
       "<b>Clear MIDI: &lt;control&gt;</b> frees the CC; <b>Cancel MIDI learn</b> (or choosing the same Learn again) stops waiting. A CC already used by another control is taken away from it.",
       "<b>Right-click elsewhere &gt; MIDI</b>: Learn for every control with its current CC (<b>none</b> until learnt), <b>Cancel MIDI learn</b> (while waiting) and <b>Clear all MIDI assignments</b>, which removes every assignment.",
       "Assignments are <b>saved with the project</b>. A project made with an earlier version that still used the former factory numbers (CC 20 to 25) opens with no assignment: learn the controls you need again. A project in which you had changed an assignment keeps its assignments as saved. Every parameter can also be automated or MIDI-learned in the DAW."],
 mt_hdr=["Control", "Type"],
 mt=[["THRESHOLD", "Continuous: 0 = -95 dB, 127 = 0 dB."], ["SOFT / HARD", "Switch: ≥ 64 = HARD, &lt; 64 = SOFT."],
     ["BASS", "Switch: ≥ 64 = Bass, &lt; 64 = Guitar."], ["LEARN button", "Trigger: each press (value rising over 64) starts a LEARN."],
     ["Footswitch", "Latching footswitch: ≥ 64 = ON, &lt; 64 = OFF."], ["Footswitch toggle", "Momentary footswitch: each press toggles on / off."],
     ["Program Change 1-10", "Factory presets 1 to 10 (program 0 = preset 1); always active, nothing to learn."]],
 win_t="7. Window",
 win=["NGATE opens at <b>60 %</b>, the same sizes as Echoflex, and the window can never be made smaller than 60 %. Right-click &gt; <b>Plugin size</b>: <b>60 %</b>, <b>75 %</b> or <b>100 %</b> resizes this window, with <b>(default)</b> shown next to the default size you chose.",
      "At the bottom of the same menu, <b>Default size (new windows)</b> chooses the size at which every new NGATE window opens (a setting shared by all instances and saved on the computer, in NINE HANDS | DSP/Ngate/settings.xml of your user data folder); the open window takes that size at once. NGATE does not store a size in the project: every window, new or reopened, opens at the default size. Drag the bottom-right corner to enlarge it further (aspect ratio locked, up to 150 %)."],
 rc_hdr=["Right-click entry", "Content"],
 rc=[["MIDI Learn (on a control)", "MIDI Learn / Clear MIDI / Cancel MIDI learn"],
     ["Plugin size", "60 % · 75 % · 100 % (“(default)” next to the default size) · Default size (new windows)"],
     ["Factory presets", "1 to 10 (section 8)"], ["Load / Save user preset", "User 1 ... 9"],
     ["LEARN noise floor (1.5 s)", "same as the LEARN button (Cancel LEARN while measuring)"],
     ["Gate mode / Instrument", "Soft / Hard · Guitar / Bass"], ["Range (closed gate)", "Full mute · -40 dB · -20 dB"],
     ["MIDI", "Learn x6 · Cancel MIDI learn · Clear all MIDI assignments · Program Change 1-10 (reminder)"]],
 pre_t="8. Presets",
 pre="10 factory presets (right-click &gt; Factory presets, the DAW preset menu, or Program Change). 9 user presets (Load / Save user preset) are shared by all instances (%APPDATA%\\NINE HANDS | DSP\\Ngate\\UserPresets.xml / ~/Library/Application Support/NINE HANDS | DSP/Ngate/).",
 pre_hdr=["Preset", "Thresh.", "Mode", "Instr.", "Range", "Use"],
 presets=[["1. Clean Single Coils", "-66 dB", "Soft", "Guitar", "Full", "Single coils in clean: keeps the tails."],
          ["2. Crunch Humbuckers", "-58 dB", "Soft", "Guitar", "Full", "Crunch with humbuckers."],
          ["3. High Gain Tight", "-48 dB", "Hard", "Guitar", "Full", "Tight high-gain rhythm."],
          ["4. Metal Chug", "-42 dB", "Hard", "Guitar", "Full", "Palm-muted chugs, fast stops."],
          ["5. Djent Staccato", "-36 dB", "Hard", "Guitar", "Full", "Very tight staccato silences."],
          ["6. Fuzz Tamer", "-52 dB", "Soft", "Guitar", "-40 dB", "Tames a noisy fuzz, keeps a breath."],
          ["7. Ambient Natural Decay", "-74 dB", "Soft", "Guitar", "-20 dB", "Gentle reduction under long tails."],
          ["8. Bass Clean", "-68 dB", "Soft", "Bass", "Full", "Clean bass, long notes."],
          ["9. Bass Drive", "-55 dB", "Hard", "Bass", "Full", "Overdriven bass, tight."],
          ["10. Studio Silence", "-78 dB", "Hard", "Guitar", "Full", "Silent background for recording."]],
 tips_t="9. Tips",
 tips=["Put NGATE <b>first</b> in the Reaper chain, before the other NINE HANDS | DSP plug-ins and before Ampire: it removes the guitar's noise before it gets amplified.",
       "For very high gain, a second NGATE in HARD <b>after</b> the distortion (still before Ampire) tightens the silences even more.",
       "Low-tuned 7-string (drop G...) or bass: switch BASS on so long low notes are not chopped, and run LEARN with the strings muted at playing volume.",
       "Learn the LEARN button on a spare footswitch of your controller: one press between songs re-measures the noise floor when you change guitar or amp channel."],
 tech_t="10. Specifications",
 tech_hdr=["Item", "Value"],
 tech=[["Format", "VST3 - Windows 11 (64-bit), macOS universal binary"],
       ["Inspired by", "noise gate pedals with THRESHOLD knob + LEARN button (NG-1 type)"], ["Threshold", "-95 ... 0 dB (-60 dB)"],
       ["HARD", "open 0.3 ms, close 15 ms (guitar) / 35 ms (bass), hysteresis 3 dB, hold 25 / 60 ms"],
       ["SOFT", "1:3 downward expansion, release 180 ms / 300 ms, hysteresis 6 dB, hold 50 / 90 ms"],
       ["Detector", "from 75 Hz (guitar) or 22 Hz (bass); mains hum ignored by LEARN"],
       ["LEARN", "1.5 s measurement, threshold = noise + 5 dB (HARD) / + 3 dB (SOFT)"], ["Range", "Full mute · -40 dB · -20 dB"],
       ["Bypass", "8 ms fade, click-free"], ["Channels", "mono or stereo, both channels gated together"], ["Presets", "10 factory + 9 user"],
       ["MIDI", "MIDI Learn on every control, no CC assigned by default, omni, Program Change 1-10; assignments saved with the project"],
       ["Window", "60 % / 75 % / 100 % (Plugin size), default size of new windows to choose, corner resize up to 150 %, never smaller than 60 %"],
       ["Windows stability", "anti-freeze v2: the audio thread never calls the host, window refresh driven by a timer with a watchdog"]]),
"fr": dict(
 lang="FRANÇAIS", sub="Pédale noise gate pour guitare &amp; basse - VST3", ver="Notice d'utilisation &nbsp;·&nbsp; version " + VERSION,
 intro_t="1. Présentation",
 intro="NGATE est un noise gate au format pédale simple, pour guitare et basse, inspiré des pédales noise gate classiques à gros potard THRESHOLD et bouton LEARN (type NG-1). Un gros potard <b>THRESHOLD</b> en aluminium brossé, un bouton <b>LEARN</b> qui mesure le bruit de fond et règle le seuil à votre place, un switch <b>SOFT / HARD</b>, un mode <b>BASS</b>, des LED OPEN / GATE et un footswitch. Il coupe ronflement, souffle et bruit d'ampli entre les phrases, sans hacher la fin des notes.",
 intro_note="<b>Anti-« bégaiement »</b> : hystérésis (3 dB en HARD, 6 dB en SOFT) et temps de maintien (25 / 60 ms HARD, 50 / 90 ms SOFT, guitare / basse) : une note tenue qui passe autour du seuil n'ouvre et ne ferme pas en rafale. Les deux voies stéréo sont toujours coupées ensemble.",
 inst_t="2. Installation",
 inst=["<b>Windows</b> : copiez <b>Ngate.vst3</b> dans <b>C:\\Program Files\\Common Files\\VST3\\</b>.",
       "<b>macOS</b> (binaire universel) : dézippez puis copiez <b>Ngate.vst3</b> dans <b>~/Library/Audio/Plug-Ins/VST3/</b>. Si macOS le bloque, lancez une fois dans le Terminal : <b>xattr -cr ~/Library/Audio/Plug-Ins/VST3/Ngate.vst3</b>.",
       "<b>Reaper</b> : Options &gt; Préférences &gt; Plug-ins &gt; VST &gt; Re-scan. Le plugin apparaît sous le nom <b>Ngate (NINE HANDS | DSP)</b>."],
 ov_t="3. L'interface",
 ov_cap="Les numéros renvoient au tableau ci-dessous et aux sections 4 et 5.",
 ov_hdr=["N°", "Élément", "Fonction"],
 ov=[["1", "Afficheur", "Seuil en dB. Affiche LEARN et une barre de progression pendant la mesure."],
     ["2", "LEARN", "Mesure le bruit de fond (1,5 s) et règle le seuil."],
     ["3", "Couronne de points", "Vumètre d'entrée : orange = sous le seuil (coupé), vert = au-dessus (passe)."],
     ["4", "THRESHOLD", "Seuil d'ouverture, de -95 dB à 0 dB."], ["5", "SOFT / HARD", "Caractère du gate (mini-inverseur)."],
     ["6/8", "OPEN / GATE", "Verte = le signal passe, orange = gate fermé."], ["7", "BASS", "Mode basse (couronne orange quand actif)."],
     ["9", "Footswitch", "Effet marche / arrêt."], ["10", "Ligne d'état", "Par-dessus le logo : n'apparaît que lorsqu'un réglage bouge, reste 2,5 s puis s'efface."],
     ["11 / 12", "INPUT / OUTPUT", "Entrée à droite, sortie à gauche (embases jack femelles)."]],
 ctl_t="4. Les commandes",
 thr_h="THRESHOLD (4)",
 thr="Seuil d'ouverture de -95 dB à 0 dB (défaut -60 dB), affiché sur l'afficheur. Tirez le potard, molette pour le réglage fin, double-clic = -60 dB. Le chapeau en aluminium tourne vraiment (rayures et usure tournent avec lui) tandis que les reflets d'usinage restent sous la lumière. La couronne de points est un vumètre d'entrée en direct : le passage de l'orange au vert marque le seuil.",
 lrn_h="Régler le gate avec LEARN (2)",
 lrn=["Branchez-vous, réglez simulateur et pédales comme pour jouer, volume de la guitare à fond.",
      "Étouffez les cordes avec la main (sans jouer) et cliquez sur <b>LEARN</b>.",
      "Pendant 1,5 s, l'afficheur indique LEARN avec une barre orange et un anneau orange se remplit autour du bouton. Nouveau clic = annuler.",
      "NGATE place le seuil juste au-dessus du bruit le plus fort entendu : <b>+5 dB en HARD, +3 dB en SOFT</b>. Le ronflement secteur (50 / 60 Hz) est ignoré par le détecteur.",
      "La ligne d'état donne le résultat, par ex. « Noise floor -70.0 dB -&gt; threshold -65.0 dB ». Affinez au potard ou à la molette."],
 sh_h="SOFT ou HARD ? (5)",
 sh=["<b>HARD</b> (défaut) : un vrai gate, ouverture en 0,3 ms, fermeture rapide (15 ms guitare / 35 ms basse). Rythmiques high-gain serrées, chugs metal, arrêts djent.",
     "<b>SOFT</b> : un expandeur vers le bas (1:3 sous le seuil) avec une retombée lente (180 ms guitare / 300 ms basse) : la note s'éteint naturellement. Clair, crunch, ambiant.",
     "Clic sur le levier = bascule, clic sur SOFT ou HARD = choix direct."],
 curve="curve_fr.png",
 curve_cap="Niveau de sortie selon le niveau d'entrée, seuil -50 dB, range Full mute : HARD tombe au silence, SOFT descend en pente.",
 bass_h="Mode BASS (7)",
 bass="Les notes graves ont des cycles longs (Mi grave 41 Hz = 24 ms par cycle ; Si grave 31 Hz = 32 ms). En mode BASS, le détecteur écoute jusqu'à 22 Hz au lieu de 75 Hz, avec une enveloppe et un maintien plus longs : les notes longues ne sont pas hachées. Une couronne orange s'allume autour du bouton.",
 rng_h="Range (clic droit)",
 rng="Ce que laisse le gate fermé : <b>Full mute</b> (coupure totale, défaut), <b>-40 dB</b> (garde un souffle de pièce) ou <b>-20 dB</b> (réduction de bruit douce). Enregistré dans les presets.",
 fs_t="5. Footswitch, LED et ligne d'état",
 fs=["<b>Footswitch</b> : effet marche / arrêt, fondu de 8 ms sans clic. En bypass tout s'éteint (couronne, LED, couronne BASS) et l'afficheur baisse.",
     "LED <b>OPEN</b> verte = le signal passe ; LED <b>GATE</b> orange = gate fermé. En SOFT, les deux se croisent en fondu.",
     "<b>Ligne d'état</b> (sous le footswitch, par-dessus le logo) : n'apparaît que lorsqu'un réglage bouge (seuil, mode, niveau d'entrée, état du gate, preset, MIDI), reste 2,5 s puis s'efface. Pendant un MIDI Learn, elle affiche l'invite."],
 caps=["Signal qui passe : points verts au-dessus du seuil, OPEN allumée.", "BASS + SOFT, gate fermé : seul le bruit (orange) apparaît.",
       "LEARN en cours : la ligne d'état affiche la mesure.", "Bypass : tout s'éteint."],
 midi_t="6. MIDI",
 midi_intro="NGATE écoute tous les canaux MIDI (omni). <b>Aucun CC n'est assigné par défaut</b> : chaque commande s'assigne par <b>MIDI Learn</b> à votre contrôleur (M-Vave Chocolate Plus, pédale d'expression...).",
 midi=["<b>Clic droit sur une commande</b> (THRESHOLD, SOFT / HARD, BASS, LEARN ou le footswitch) puis <b>MIDI Learn: &lt;commande&gt; (none)</b> (ou le CC appris, par ex. <b>(CC 64)</b>). Le footswitch propose ses deux entrées : <b>Footswitch</b> (à accrochage) et <b>Footswitch toggle</b> (à chaque appui).",
       "La ligne d'état affiche <b>MIDI LEARN: move a control for X</b>. Bougez une pédale ou appuyez sur un footswitch du contrôleur : le premier CC reçu est assigné (il n'agit pas sur le son) et la ligne d'état confirme <b>X = CC n</b> pendant 2 secondes.",
       "<b>Clear MIDI: &lt;commande&gt;</b> libère le CC ; <b>Cancel MIDI learn</b> (ou rechoisir le même Learn) arrête l'attente. Un CC déjà utilisé par une autre commande lui est retiré.",
       "<b>Clic droit ailleurs &gt; MIDI</b> : Learn de chaque commande avec son CC actuel (<b>none</b> tant qu'elle n'est pas apprise), <b>Cancel MIDI learn</b> (pendant l'attente) et <b>Clear all MIDI assignments</b>, qui efface toutes les assignations.",
       "Les assignations sont <b>enregistrées avec le projet</b>. Un projet fait avec une version précédente qui utilisait encore les anciens numéros d'usine (CC 20 à 25) s'ouvre sans aucune assignation : réapprenez les commandes voulues. Un projet où vous aviez changé une assignation garde ses assignations telles qu'enregistrées. Tous les paramètres sont aussi automatisables et assignables dans le DAW."],
 mt_hdr=["Commande", "Type"],
 mt=[["THRESHOLD", "Continu : 0 = -95 dB, 127 = 0 dB."], ["SOFT / HARD", "Bascule : ≥ 64 = HARD, &lt; 64 = SOFT."],
     ["BASS", "Bascule : ≥ 64 = Basse, &lt; 64 = Guitare."], ["Bouton LEARN", "Déclencheur : chaque appui (valeur qui passe 64) lance un LEARN."],
     ["Footswitch", "Footswitch à accrochage : ≥ 64 = ON, &lt; 64 = OFF."], ["Footswitch toggle", "Footswitch momentané : chaque appui inverse marche / arrêt."],
     ["Program Change 1-10", "Presets d'usine 1 à 10 (programme 0 = preset 1) ; toujours actif, rien à apprendre."]],
 win_t="7. Fenêtre",
 win=["NGATE s'ouvre à <b>60 %</b>, avec les mêmes tailles qu'Echoflex, et la fenêtre ne peut jamais être plus petite que 60 %. Clic droit &gt; <b>Plugin size</b> : <b>60 %</b>, <b>75 %</b> ou <b>100 %</b> redimensionne cette fenêtre, et <b>(default)</b> est indiqué à côté de la taille par défaut choisie.",
      "En bas du même menu, <b>Default size (new windows)</b> choisit la taille d'ouverture de toutes les nouvelles fenêtres de NGATE (réglage commun à toutes les instances, enregistré sur l'ordinateur, dans NINE HANDS | DSP/Ngate/settings.xml du dossier de données de l'utilisateur) ; la fenêtre ouverte prend aussitôt cette taille. NGATE n'enregistre pas de taille dans le projet : chaque fenêtre, nouvelle ou rouverte, s'ouvre à la taille par défaut. Tirez le coin inférieur droit pour l'agrandir davantage (proportions bloquées, jusqu'à 150 %)."],
 rc_hdr=["Entrée du clic droit", "Contenu"],
 rc=[["MIDI Learn (sur une commande)", "MIDI Learn / Clear MIDI / Cancel MIDI learn"],
     ["Plugin size", "60 % · 75 % · 100 % (« (default) » à côté de la taille par défaut) · Default size (new windows)"],
     ["Factory presets", "1 à 10 (section 8)"], ["Load / Save user preset", "User 1 ... 9"],
     ["LEARN noise floor (1.5 s)", "comme le bouton LEARN (Cancel LEARN pendant la mesure)"],
     ["Gate mode / Instrument", "Soft / Hard · Guitar / Bass"], ["Range (closed gate)", "Full mute · -40 dB · -20 dB"],
     ["MIDI", "Learn x6 · Cancel MIDI learn · Clear all MIDI assignments · Program Change 1-10 (rappel)"]],
 pre_t="8. Presets",
 pre="10 presets d'usine (clic droit &gt; Factory presets, menu des presets du DAW, ou Program Change). 9 presets utilisateur (Load / Save user preset) communs à toutes les instances (%APPDATA%\\NINE HANDS | DSP\\Ngate\\UserPresets.xml / ~/Library/Application Support/NINE HANDS | DSP/Ngate/).",
 pre_hdr=["Preset", "Seuil", "Mode", "Instr.", "Range", "Usage"],
 presets=[["1. Clean Single Coils", "-66 dB", "Soft", "Guitare", "Totale", "Simples en son clair : garde les fins de notes."],
          ["2. Crunch Humbuckers", "-58 dB", "Soft", "Guitare", "Totale", "Crunch avec humbuckers."],
          ["3. High Gain Tight", "-48 dB", "Hard", "Guitare", "Totale", "Rythmique high-gain serrée."],
          ["4. Metal Chug", "-42 dB", "Hard", "Guitare", "Totale", "Chugs en palm-mute, arrêts nets."],
          ["5. Djent Staccato", "-36 dB", "Hard", "Guitare", "Totale", "Silences staccato très serrés."],
          ["6. Fuzz Tamer", "-52 dB", "Soft", "Guitare", "-40 dB", "Dompte une fuzz bruyante, garde un souffle."],
          ["7. Ambient Natural Decay", "-74 dB", "Soft", "Guitare", "-20 dB", "Réduction douce sous les longues queues."],
          ["8. Bass Clean", "-68 dB", "Soft", "Basse", "Totale", "Basse claire, notes longues."],
          ["9. Bass Drive", "-55 dB", "Hard", "Basse", "Totale", "Basse saturée, serrée."],
          ["10. Studio Silence", "-78 dB", "Hard", "Guitare", "Totale", "Fond silencieux pour l'enregistrement."]],
 tips_t="9. Conseils",
 tips=["Placez NGATE <b>en premier</b> dans la chaîne Reaper, avant les autres plugins NINE HANDS | DSP et avant Ampire : il coupe le bruit de la guitare avant qu'il soit amplifié.",
       "Pour un son très saturé, un deuxième NGATE en HARD <b>après</b> la distorsion (toujours avant Ampire) resserre encore les silences.",
       "7 cordes accordée grave (drop G...) ou basse : activez BASS pour ne pas hacher les notes graves longues, et lancez LEARN cordes étouffées au volume de jeu.",
       "Apprenez le bouton LEARN sur un footswitch libre du contrôleur : un appui entre deux morceaux remesure le bruit de fond quand vous changez de guitare ou de canal d'ampli."],
 tech_t="10. Caractéristiques techniques",
 tech_hdr=["Élément", "Valeur"],
 tech=[["Format", "VST3 - Windows 11 (64 bits), macOS binaire universel"],
       ["Inspiré de", "pédales noise gate à potard THRESHOLD + bouton LEARN (type NG-1)"], ["Threshold", "-95 ... 0 dB (-60 dB)"],
       ["HARD", "ouverture 0,3 ms, fermeture 15 ms (guitare) / 35 ms (basse), hystérésis 3 dB, maintien 25 / 60 ms"],
       ["SOFT", "expansion 1:3 vers le bas, retombée 180 ms / 300 ms, hystérésis 6 dB, maintien 50 / 90 ms"],
       ["Détecteur", "dès 75 Hz (guitare) ou 22 Hz (basse) ; ronflement secteur ignoré par LEARN"],
       ["LEARN", "mesure de 1,5 s, seuil = bruit + 5 dB (HARD) / + 3 dB (SOFT)"], ["Range", "Full mute · -40 dB · -20 dB"],
       ["Bypass", "fondu de 8 ms, sans clic"], ["Canaux", "mono ou stéréo, les deux voies coupées ensemble"], ["Presets", "10 usine + 9 utilisateur"],
       ["MIDI", "MIDI Learn sur chaque commande, aucun CC assigné par défaut, omni, Program Change 1-10 ; assignations enregistrées avec le projet"],
       ["Fenêtre", "60 % / 75 % / 100 % (Plugin size), taille par défaut des nouvelles fenêtres au choix, coin jusqu'à 150 %, jamais sous 60 %"],
       ["Stabilité Windows", "anti-gel v2 : le thread audio n'appelle jamais l'hôte, rafraîchissement de la fenêtre piloté par un timer avec chien de garde"]]),
}

def section(lang):
    t = T[lang]; f = []
    def bl(items): return [P("&bull;&nbsp;&nbsp;" + i) for i in items]
    def nl(items): return [P(f"{k + 1}.&nbsp;&nbsp;" + i) for k, i in enumerate(items)]
    f.append(NextPageTemplate("p"))
    f.append(Spacer(1, 2 * mm)); f.append(P(t["lang"], "coverlang")); f.append(Spacer(1, 4 * mm))
    f.append(img("cover.png", W * 0.52)); f.append(Spacer(1, 8 * mm))
    f.append(P("N G A T E", "cover")); f.append(Spacer(1, 2 * mm))
    f.append(P(t["sub"], "coversub")); f.append(P(t["ver"], "coversub")); f.append(Spacer(1, 9 * mm))
    f.append(img("logo_studio_wiga_blanc.png", 52 * mm)); f.append(PageBreak())
    f.append(P(t["intro_t"], "h1")); f.append(P(t["intro"])); f.append(P(t["intro_note"], "note"))
    f.append(P(t["inst_t"], "h1")); f += bl(t["inst"])
    f.append(PageBreak())
    f.append(P(t["ov_t"], "h1")); f.append(img("overview_annotated.png", W * 0.62)); f.append(P(t["ov_cap"], "cap")); f.append(Spacer(1, 4 * mm))
    f.append(table([t["ov_hdr"]] + t["ov"], [16 * mm, 34 * mm, W - 50 * mm]))
    f.append(PageBreak())
    f.append(P(t["ctl_t"], "h1")); f.append(P(t["thr_h"], "h2")); f.append(P(t["thr"]))
    f.append(P(t["lrn_h"], "h2")); f += nl(t["lrn"])
    f.append(P(t["sh_h"], "h2")); f += bl(t["sh"])
    f.append(KeepTogether([img(t["curve"], W * 0.62), P(t["curve_cap"], "cap")]))
    f.append(P(t["bass_h"], "h2")); f.append(P(t["bass"]))
    f.append(P(t["rng_h"], "h2")); f.append(P(t["rng"]))
    f.append(PageBreak())
    f.append(P(t["fs_t"], "h1")); f += bl(t["fs"]); f.append(Spacer(1, 3 * mm))
    c = t["caps"]
    f.append(row_of([("state_open.png", c[0]), ("state_bass_soft.png", c[1])], W * 0.80))
    f.append(row_of([("state_learn.png", c[2]), ("state_bypass.png", c[3])], W * 0.80))
    f.append(PageBreak())
    f.append(P(t["midi_t"], "h1")); f.append(P(t["midi_intro"])); f += bl(t["midi"])
    f.append(KeepTogether([Spacer(1, 2 * mm), table([t["mt_hdr"]] + t["mt"], [42 * mm, W - 42 * mm])]))
    f.append(PageBreak())
    f.append(P(t["win_t"], "h1")); f += [P(x) for x in t["win"]]
    f.append(KeepTogether([Spacer(1, 2 * mm), table([t["rc_hdr"]] + t["rc"], [52 * mm, W - 52 * mm])]))
    f.append(PageBreak())
    f.append(P(t["pre_t"], "h1")); f.append(P(t["pre"]))
    f.append(table([t["pre_hdr"]] + t["presets"], [42 * mm, 17 * mm, 13 * mm, 17 * mm, 16 * mm, W - 105 * mm]))
    f.append(P(t["tips_t"], "h1")); f += bl(t["tips"])
    f.append(KeepTogether([P(t["tech_t"], "h1"), table([t["tech_hdr"]] + t["tech"], [36 * mm, W - 36 * mm])]))
    # pas d'historique des versions dans la notice (demande de l'utilisateur)
    f.append(PageBreak())
    return f

def deco(c, doc):
    c.saveState()
    c.setFillColor(ACC); c.rect(0, A4[1] - 2.5 * mm, A4[0], 2.5 * mm, stroke=0, fill=1)
    c.setFont("Pop", 7.5); c.setFillColor(GREY)
    c.drawString(18 * mm, 10 * mm, "NGATE " + VERSION + " · NINE HANDS | DSP")
    c.drawRightString(A4[0] - 18 * mm, 10 * mm, str(doc.page))
    c.restoreState()

def cover_bg(c, doc):
    c.saveState(); c.setFillColor(colors.black); c.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    c.setFillColor(ACC); c.rect(0, A4[1] - 3 * mm, A4[0], 3 * mm, stroke=0, fill=1); c.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
                      title="NGATE - User manual / Notice v" + VERSION, author="NINE HANDS | DSP")
doc.addPageTemplates([PageTemplate(id="cover", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="fc")], onPage=cover_bg),
                      PageTemplate(id="p", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")], onPage=deco)])
en = section("en"); fr = section("fr")
en[-1:] = [NextPageTemplate("cover"), PageBreak()]
doc.build(en + fr[:-1])
print(OUT)
