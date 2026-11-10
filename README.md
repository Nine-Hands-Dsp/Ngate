# Ngate (NINE HANDS | DSP) — VST3

Noise gate pour guitare et basse au **format pédale simple** (même gabarit qu'Echoflex), Windows et macOS : un grand potard THRESHOLD avec sa couronne-vumètre, un bouton LEARN qui règle le seuil en écoutant le bruit de fond, un inverseur SOFT / HARD, un mode BASS et deux LED OPEN / GATE.

<p align="center">
  <a href="https://github.com/Nine-Hands-Dsp/Ngate/releases/latest/download/Ngate-VST3-Windows.zip"><img alt="Télécharger pour Windows" src="https://img.shields.io/badge/%E2%AC%87%20T%C3%A9l%C3%A9charger-Windows-0078D6?style=for-the-badge"></a>
  <a href="https://github.com/Nine-Hands-Dsp/Ngate/releases/latest/download/Ngate-VST3-macOS.zip"><img alt="Télécharger pour macOS" src="https://img.shields.io/badge/%E2%AC%87%20T%C3%A9l%C3%A9charger-macOS-111111?style=for-the-badge&logo=apple&logoColor=white"></a>
  <br>
  <a href="https://github.com/Nine-Hands-Dsp/Ngate/releases/latest/download/Ngate-Notice.pdf"><img alt="Télécharger la notice (PDF)" src="https://img.shields.io/badge/%F0%9F%93%96%20Notice-PDF-919496?style=for-the-badge"></a>
  <br>
  <a href="https://github.com/Nine-Hands-Dsp/Ngate/releases/latest"><img alt="Dernière version" src="https://img.shields.io/github/v/release/Nine-Hands-Dsp/Ngate?label=derni%C3%A8re%20version&color=919496"></a>
</p>

## Installation

- **Windows** : dézipper puis copier `Ngate.vst3` dans `C:\Program Files\Common Files\VST3\`
- **macOS** : dézipper puis copier `Ngate.vst3` dans `~/Library/Audio/Plug-Ins/VST3/` (si macOS le bloque : `xattr -cr ~/Library/Audio/Plug-Ins/VST3/Ngate.vst3`)
- Relancer l'analyse des plugins dans le DAW. Le plugin apparaît comme **Ngate (NINE HANDS | DSP)**.

## Commandes

| Commande | Rôle |
|---|---|
| THRESHOLD | Seuil d'ouverture, de **−95 dB à 0 dB**, affiché en haut à droite. Double-clic = −60 dB, molette = réglage fin |
| Couronne de points | Vumètre d'entrée en direct : orange = sous le seuil (coupé), vert = au-dessus (passe) |
| LEARN | Mesure le bruit de fond pendant 1,5 s (cordes étouffées) puis place le seuil juste au-dessus : +3 dB en SOFT, +5 dB en HARD. Nouveau clic = annuler |
| SOFT / HARD (inverseur) | **SOFT** : expansion douce 1:3, relâchement 180 ms (300 ms en BASS). **HARD** : attaque 0,3 ms, fermeture 15 ms (35 ms en BASS). Clic sur le levier ou directement sur SOFT / HARD |
| BASS | Détection jusqu'à 22 Hz (au lieu de 75 Hz), maintien plus long : les notes graves ne sont pas hachées |
| LED OPEN / GATE | Verte = le signal passe, orange = gate fermé |
| Footswitch | Effet actif / bypass, fondu de 8 ms sans clic |
| Clic droit > Gate settings | Soft / Hard, Guitar / Bass, **Range** : coupure totale, −40 dB ou −20 dB gate fermé |

## Fenêtre et menus

- Fenêtre par défaut à **60 %**, jamais plus petite, jusqu'à 150 %. Clic droit > **Plugin size** : 60 / 75 / 100 % et *Default size (new windows)*.
- Menus clic droit au style Octopus, ouverts à l'endroit du clic : sur une commande, son MIDI Learn ; ailleurs, le menu général.
- Barre de presets (flèches, clic sur le nom) et ligne d'état dans la même pastille.

## MIDI

Aucun CC assigné par défaut : clic droit sur une commande > **MIDI Learn**, ou clic droit > MIDI > Learn.

| Commande | Fonction |
|---|---|
| Threshold | 0 = −95 dB, 127 = 0 dB |
| Soft / Hard | ≥ 64 HARD |
| Bass | ≥ 64 BASS |
| LEARN button | LEARN à chaque appui |
| Footswitch | ≥ 64 actif, < 64 bypass |
| Footswitch toggle | bascule à chaque appui |
| Program Change 1-10 | Presets d'usine |

## Presets d'usine

1. Clean Single Coils · 2. Crunch Humbuckers · 3. High Gain Tight · 4. Metal Chug · 5. Djent Staccato · 6. Fuzz Tamer · 7. Ambient Natural Decay · 8. Bass Clean · 9. Bass Drive · 10. Studio Silence. Presets utilisateur 1 à 9 au clic droit.

## Placement dans Reaper

En **premier** dans la chaîne, avant le simulateur d'ampli (Ampire puis Impulse) : le gate coupe le bruit de la guitare avant qu'il soit amplifié par la saturation.

## Fichiers

- `background.png` (1206 × 1800, pédale plein cadre), `knob_top.png`, `toggle_strip.png`, `led_*_on.png`, `glow_*.png` : visuel v2, généré par `tools/make_art.py` à partir de `design/source/` et du kit photo `assets/kit/`.
- `Layout.h` : positions des commandes (repère 603 × 900, image / 2).
- `NineHandsMenu.h`, `Poppins-*.ttf`, `NineHandsLogo.svg` : menus Octopus, polices et logo vectoriel.
- `tools/render/` : outil de captures du vrai plugin ; `tools/manual.py` : notice PDF (`docs/Ngate_Notice_FR_v2.0.0.pdf`).

## Nouveautés v2.0.0

- Refonte complète du visuel selon les règles NINE HANDS | DSP : façade photo, potard en calques (usure et index qui tournent, reflets fixes), boutons poussoirs photo, inverseur horizontal photo, LED et footswitch du kit, menus style Octopus, logo NINE HANDS | DSP vectoriel.
- Notice refaite, en français.
