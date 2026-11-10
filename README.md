# Ngate (NINE HANDS | DSP) — VST3

Noise gate au **format pédale simple** (même gabarit de fenêtre qu'Echoflex), pour guitare et basse, Windows 11 et macOS.
Inspiré du principe des pédales noise gate à gros potard THRESHOLD + bouton LEARN (type NG-1). Usage personnel.
Visuel NGATE (photo) de NINE HANDS | DSP mis à l'échelle du projet (1520 × 1916, pédale à la même taille qu'Echoflex) : fond noir uni, seulement les embases jack femelles de chaque côté (sans fiches), 4 vis (haut et bas).

<p align="center">
  <a href="https://github.com/Nine-Hands-Dsp/Ngate/releases/latest/download/Ngate-VST3-Windows.zip"><img alt="Télécharger pour Windows" src="https://img.shields.io/badge/%E2%AC%87%20T%C3%A9l%C3%A9charger-Windows-0078D6?style=for-the-badge"></a>
  <a href="https://github.com/Nine-Hands-Dsp/Ngate/releases/latest/download/Ngate-VST3-macOS.zip"><img alt="Télécharger pour macOS" src="https://img.shields.io/badge/%E2%AC%87%20T%C3%A9l%C3%A9charger-macOS-111111?style=for-the-badge&logo=apple&logoColor=white"></a>
  <br>
  <a href="https://github.com/Nine-Hands-Dsp/Ngate/releases/latest/download/Ngate-Notice.pdf"><img alt="Télécharger la notice (PDF)" src="https://img.shields.io/badge/%F0%9F%93%96%20Notice-PDF-919496?style=for-the-badge"></a>
  <br>
  <a href="https://github.com/Nine-Hands-Dsp/Ngate/releases/latest"><img alt="Dernière version" src="https://img.shields.io/github/v/release/Nine-Hands-Dsp/Ngate?label=derni%C3%A8re%20version&color=919496"></a>
</p>

## Installation via GitHub

1. Déposer à la racine du dépôt : `background.png`, `lever.png`, `knob_light.png`, `knob_dark.png`, `CMakeLists.txt`, `PluginProcessor.h/.cpp`, `PluginEditor.h/.cpp`, `README.md`, `docs/NGATE_Manual_EN-FR_v1.4.0.pdf` (notice EN puis FR) et le dossier `.github/workflows/build.yml`.
2. Le push lance la compilation (onglet **Actions**) : Windows (`windows-2022`) et macOS (binaire universel).
3. Télécharger l'artefact :
   - **Windows** : copier `Ngate.vst3` dans `C:\Program Files\Common Files\VST3\`
   - **macOS** : dézipper puis copier `Ngate.vst3` dans `~/Library/Audio/Plug-Ins/VST3/`
4. Relancer l'analyse des plugins dans le DAW. Le plugin apparaît comme **Ngate (NINE HANDS | DSP)**.

## Commandes

| Commande | Rôle |
|---|---|
| THRESHOLD (gros potard alu brossé) | Seuil d'ouverture, de **−95 dB à 0 dB**. Valeur affichée en haut à droite. Double-clic = −60 dB. Molette = réglage fin |
| Couronne de points | **Vumètre d'entrée en direct** : orange = sous le seuil (coupé), vert = au-dessus (passe). Le passage orange → vert indique le seuil |
| LEARN (bouton en haut à droite, sous l'afficheur) | Mesure le bruit de fond pendant 1,5 s (cordes étouffées, volume de la guitare ouvert) puis place le seuil juste au-dessus : +5 dB en HARD, +3 dB en SOFT. Un anneau orange montre la progression. Nouveau clic = annuler. Le ronflement 50/60 Hz n'est pas compté |
| SOFT / HARD (mini-inverseur) | **HARD** : ouverture 0,3 ms, fermeture rapide (15 ms guitare / 35 ms basse) — idéal high-gain, metal, staccato. **SOFT** : expansion douce 1:3 sous le seuil, retombée de 180 ms / 300 ms — la note s'éteint naturellement. Clic sur le levier = bascule, clic sur SOFT ou HARD = choix direct |
| BASS (petit bouton) | Mode basse : détecteur ouvert jusqu'à 22 Hz (au lieu de 75 Hz), enveloppe et maintien plus longs → les notes graves ne sont pas hachées. Couronne orange autour du bouton quand actif |
| LED OPEN / GATE | Verte = le signal passe, orange = gate fermé (en SOFT, les deux se croisent en fondu) |
| Footswitch | Effet on/off, fondu de 8 ms sans clic. En bypass, tout s'éteint (couronne, LED, BASS) et l'afficheur baisse |

Anti-« bégaiement » : hystérésis (3 dB en HARD, 6 dB en SOFT) + temps de maintien (25/60 ms HARD, 50/90 ms SOFT) — une note tenue qui passe autour du seuil n'ouvre/ferme pas en rafale.

## Interface

- Fenêtre ouverte par défaut à **60 %**, impossible de la réduire en dessous, proportions bloquées, jusqu'à 150 % : **mêmes réglages de taille qu'Echoflex**.
- **Clic droit > Plugin size** : 60 % / 75 % / 100 % pour cette fenêtre (« (default) » marque la taille par défaut choisie), et *Default size (new windows)* pour choisir la taille d'ouverture de toutes les nouvelles fenêtres de NGATE (réglage enregistré dans `NINE HANDS | DSP/Ngate/settings.xml` du dossier de données de l'utilisateur, comme Octopus).
- **Clic droit** : taille (*Plugin size*), presets d'usine, presets utilisateur 1 à 9 (charger / sauvegarder), LEARN, mode Soft/Hard, Guitar/Bass, **Range** (coupure totale / −40 dB / −20 dB quand le gate est fermé), table MIDI.
- Potard en aluminium brossé qui tourne vraiment : la matière du chapeau (rayures, taches, usure : `knob_light.png` / `knob_dark.png`) et la rainure du repère tournent autour du centre réel du chapeau, tandis que les reflets coniques de l'usinage restent fixes sous la lumière, comme sur un vrai potard.
- Mini-inverseur SOFT/HARD animé : le levier de la photo (`lever.png`) bascule (sa projection raccourcit puis repart de l'autre côté), avec son ombre portée.
- Boutons LEARN et BASS : enfoncement au clic, couronne orange quand actifs.
- Ligne d'état sous le footswitch (par-dessus le logo) : n'apparaît que lorsqu'un réglage bouge (seuil, mode, niveau d'entrée, état du gate, preset, MIDI), reste 2,5 s puis s'efface. Après un LEARN : « Noise floor … → threshold … ».

## MIDI

Aucun CC assigné par défaut : clic droit > MIDI > Learn.

| Commande MIDI Learn | Fonction |
|---|---|
| Threshold | 0 = −95 dB, 127 = 0 dB |
| Soft / Hard | ≥ 64 Hard |
| Bass | Guitar / Bass (≥ 64 Bass) |
| LEARN button | LEARN (chaque appui) |
| Footswitch | ≥ 64 ON, < 64 OFF |
| Footswitch toggle | bascule à chaque appui |
| Program Change 1-10 | Presets d'usine |

Clic droit sur une commande → « MIDI Learn: … » puis bouger la pédale / appuyer sur le footswitch du
contrôleur pour l'assigner (« Clear MIDI: … » pour la libérer, MIDI → « Clear all MIDI assignments »
pour tout effacer). Les assignations sont sauvegardées avec le projet.

Tous les paramètres sont aussi automatisables et assignables en MIDI-learn dans le DAW.

## Presets d'usine

1. Clean Single Coils · 2. Crunch Humbuckers · 3. High Gain Tight · 4. Metal Chug · 5. Djent Staccato · 6. Fuzz Tamer · 7. Ambient Natural Decay · 8. Bass Clean · 9. Bass Drive · 10. Studio Silence

## Placement dans Reaper

En **premier** dans la chaîne, avant les autres plugins NINE HANDS | DSP et avant Ampire : le gate coupe le bruit de la guitare avant qu'il soit amplifié. Pour un son très saturé, un deuxième Ngate en HARD **après** la distorsion (et avant Ampire) resserre encore les silences. Le gate est mono-commandé : les deux voies stéréo sont toujours coupées ensemble.

## Changer le visuel ou le nom

- Visuel : remplacer `background.png` (1520 × 1916). Les positions des commandes sont en tête de `PluginEditor.cpp` (repère 760 × 958).
- Nom : `PRODUCT_NAME` dans `CMakeLists.txt` et les chemins du `build.yml`.

## Nouveautés v1.1

- Nouveau visuel photo (boîtier usé, potard alu brossé) ; fond noir uni, uniquement les embases jack femelles, vis ajoutées en bas.
- Points de la couronne, valeur de l'afficheur, LED, levier et rainure du potard redessinés par le plugin aux couleurs de la photo.
- Notice refaite avec le nouveau visuel.

## Nouveautés v1.2

- Le gros potard THRESHOLD tourne physiquement (matière du chapeau + repère), reflets d'usinage fixes.
- Vis du bas identiques à celles du haut.
- Notice : pédale détourée.

## Nouveautés v1.3

- v1.3.0 : anti-gel v2 (JUCE 8.0.15, caches refaits par le timer, chien de garde, aucun appel à l'hôte depuis le thread audio)

- v1.3.1 : menu de taille de fenêtre : « 60 % (default) », 75 %, 100 % (plus de taille en pixels)

- v1.4.0 : MIDI Learn au clic droit sur chaque commande (Clear MIDI, assignations sauvegardées avec le projet)

## Nouveautés v1.5

- v1.5.0 : clic droit > *Plugin size* > *Default size (new windows)* : taille par défaut des nouvelles fenêtres au choix (60 / 75 / 100 %), comme dans Octopus

- v1.5.1 : plus aucun CC MIDI assigné par défaut (tout passe par le MIDI Learn)
