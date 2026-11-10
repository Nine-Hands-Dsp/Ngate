// Captures PNG de la fenetre reelle de NGATE (meme code que le plugin), pour l'apercu et la notice.
#include "PluginProcessor.h"
#include "PluginEditor.h"
#include "BinaryData.h"
using namespace juce;

int main (int argc, char** argv)
{
    ScopedJuceInitialiser_GUI init;
    const String out = argc > 1 ? argv[1] : ".";
    NgateAudioProcessor proc;
    proc.prepareToPlay (48000.0, 256);
    std::unique_ptr<AudioProcessorEditor> ed (proc.createEditor());
    auto* ned = static_cast<NgateAudioProcessorEditor*> (ed.get());
    std::printf ("taille par defaut : %d x %d\n", ed->getWidth(), ed->getHeight());

    auto pump = [] (int n) { for (int i = 0; i < n; ++i) MessageManager::getInstance()->runDispatchLoopUntil (34); };
    auto setP = [&] (const char* id, float v) { auto* p = proc.apvts.getParameter (id); p->setValueNotifyingHost (p->convertTo0to1 (v)); };
    Random rng (3);
    double t = 0.0;
    // signal : note (sinus) au niveau noteDb + bruit au niveau noiseDb
    auto feed = [&] (float noteDb, float noiseDb, int blocks)
    {
        AudioBuffer<float> b (2, 256); MidiBuffer m;
        const float na = Decibels::decibelsToGain (noteDb, -200.0f), nn = Decibels::decibelsToGain (noiseDb, -200.0f);
        for (int k = 0; k < blocks; ++k)
        {
            for (int i = 0; i < 256; ++i)
            {
                const float x = na * (float) std::sin (2.0 * MathConstants<double>::pi * 220.0 * t) + nn * (rng.nextFloat() * 2.0f - 1.0f);
                b.setSample (0, i, x); b.setSample (1, i, x); t += 1.0 / 48000.0;
            }
            proc.processBlock (b, m);
        }
    };
    auto save = [&] (const String& name, float scale)
    {
        auto img = ed->createComponentSnapshot (ed->getLocalBounds(), true, scale);
        File f (out + "/" + name + ".png"); f.deleteFile();
        FileOutputStream os (f); PNGImageFormat().writeImageToStream (img, os);
        std::printf ("%s (%d x %d)\n", f.getFullPathName().toRawUTF8(), img.getWidth(), img.getHeight());
    };
    // etat : seuil, mode, basse, bypass, niveau de note, ligne d'etat visible
    auto state = [&] (int preset, float thr, bool hard, bool bass, bool active, float noteDb, bool status)
    {
        if (preset >= 0) proc.applyFactoryPreset (preset);
        setP ("threshold", thr); setP ("hard", hard ? 1.f : 0.f); setP ("bass", bass ? 1.f : 0.f); setP ("active", active ? 1.f : 0.f);
        if (preset >= 0) proc.currentPreset = preset;
        for (int k = 0; k < 40; ++k) { feed (noteDb, -78.0f, 6); pump (1); }
        if (! status) { ned->tickForCapture(); pump (100); for (int k = 0; k < 10; ++k) { feed (noteDb, -78.0f, 6); pump (1); } }
        else ned->showStatus();
        pump (6);
    };
    auto exact = [&] (const String& name)
    {
        ned->setScaledHeight (900); ned->forceRenderScale (2.0f); pump (8);
        save (name, 1800.0f / (float) ed->getHeight());
    };

    ned->setScaledHeight (900); ned->forceRenderScale (2.0f);
    state (0, -53.5f, true, false, true, -30.0f, false);  exact ("ngate_open");
    state (-1, -40.0f, false, true, true, -200.0f, true);  exact ("ngate_gate_bass_soft");
    state (1, -92.0f, true, false, true, -20.0f, false);  exact ("ngate_min");
    state (2, -4.0f, true, false, false, -20.0f, false);  exact ("ngate_bypass");
    // LEARN en cours
    setP ("active", 1.f); setP ("threshold", -60.f); proc.startLearn();
    for (int k = 0; k < 30; ++k) { feed (-200.0f, -70.0f, 6); pump (1); }
    exact ("ngate_learn");
    for (int k = 0; k < 40; ++k) { feed (-200.0f, -70.0f, 6); pump (1); }
    exact ("ngate_learn_done");
    std::printf ("LEARN : bruit %.1f dB -> seuil %.1f dB\n", proc.learnedNoiseDb.load(), proc.apvts.getRawParameterValue ("threshold")->load());

    // taille par defaut (60 %)
    ned->setScaledHeight (NgateAudioProcessorEditor::defaultH); ned->forceRenderScale (2.0f);
    state (0, -53.5f, true, false, true, -30.0f, false);
    save ("ngate_default_60", 2.0f);

    // inverseur : HARD, milieu (avant 55 ms), SOFT
    ned->setScaledHeight (900); ned->forceRenderScale (2.0f);
    setP ("hard", 1.f); pump (10); exact ("anim_0_hard");
    setP ("hard", 0.f); save ("anim_1_milieu", 1800.0f / (float) ed->getHeight());
    pump (10); exact ("anim_2_soft");

    // menus (design Octopus) rendus hors ecran
    {
        NineHandsMenu::MenuLnf lnf;
        lnf.f = { Typeface::createSystemTypefaceFor (BinaryData::PoppinsRegular_ttf, BinaryData::PoppinsRegular_ttfSize),
                  Typeface::createSystemTypefaceFor (BinaryData::PoppinsMedium_ttf, BinaryData::PoppinsMedium_ttfSize),
                  Typeface::createSystemTypefaceFor (BinaryData::PoppinsBold_ttf, BinaryData::PoppinsBold_ttfSize) };
        struct It { String text; bool sep, sub, ticked, active; };
        auto render = [&] (const String& name, const String& title, const String& subtitle, int ico, const std::vector<It>& items, int hiIndex)
        {
            NineHandsMenu::Header hd (lnf.f, ico, Colour (0xffec7a2c), title, subtitle);
            int w = 0, h = 0; hd.getIdealSize (w, h);
            const int border = lnf.getPopupMenuBorderSize();
            int totalH = border * 2 + h + 11, maxW = w;
            for (auto& it : items) { int iw, ih; lnf.getIdealPopupMenuItemSize (it.text, it.sep, 0, iw, ih); totalH += ih; maxW = jmax (maxW, iw + (it.sub ? 20 : 0)); }
            maxW += border * 2;
            Image img (Image::ARGB, maxW * 2, totalH * 2, true);
            Graphics g (img); g.addTransform (AffineTransform::scale (2.0f));
            lnf.drawPopupMenuBackground (g, maxW, totalH);
            int y = border;
            hd.setSize (maxW - border * 2, h);
            { Graphics::ScopedSaveState ss (g); g.setOrigin (border, y); hd.paint (g); }
            y += h;
            lnf.drawPopupMenuItem (g, { border, y, maxW - border * 2, 11 }, true, true, false, false, false, {}, {}, nullptr, nullptr); y += 11;
            for (size_t i = 0; i < items.size(); ++i)
            {
                const auto& it = items[i]; int iw, ih; lnf.getIdealPopupMenuItemSize (it.text, it.sep, 0, iw, ih);
                lnf.drawPopupMenuItem (g, { border, y, maxW - border * 2, ih }, it.sep, it.active, (int) i == hiIndex, it.ticked, it.sub, it.text, {}, nullptr, nullptr);
                y += ih;
            }
            File f (out + "/" + name + ".png"); f.deleteFile();
            FileOutputStream os (f); PNGImageFormat().writeImageToStream (img, os);
            std::printf ("%s\n", f.getFullPathName().toRawUTF8());
        };
        render ("ngate_menu", "Ngate", "Noise gate  v2.0.0", NineHandsMenu::icoPedal,
                { { "Plugin size", false, true, false, true }, { "", true }, { "Factory presets", false, true, false, true },
                  { "Load user preset", false, true, false, true }, { "Save user preset", false, true, false, true }, { "", true },
                  { "LEARN noise floor (1.5 s)", false, false, false, true }, { "Gate settings", false, true, false, true },
                  { "MIDI", false, true, false, true }, { "", true }, { "Ngate v2.0.0  NINE HANDS | DSP", false, false, false, false } }, 2);
        render ("ngate_menu_knob", "Threshold", "MIDI: not assigned", NineHandsMenu::icoKnob,
                { { "MIDI Learn: Threshold", false, false, false, true }, { "Clear MIDI: Threshold", false, false, false, false }, { "", true },
                  { "Plugin size", false, true, false, true }, { "", true }, { "Factory presets", false, true, false, true } }, 0);
        render ("ngate_menu_gate", "Gate settings", "Hard  Guitar  Full mute", NineHandsMenu::icoGate,
                { { "Soft (natural decay)", false, false, false, true }, { "Hard (tight, fast)", false, false, true, true }, { "", true },
                  { "Guitar", false, false, true, true }, { "Bass", false, false, false, true }, { "", true },
                  { "Full mute", false, false, true, true }, { "-40 dB (keeps a breath)", false, false, false, true }, { "-20 dB (gentle)", false, false, false, true } }, 4);
    }

    // pedale d'expression sur THRESHOLD via MIDI Learn (CC 11)
    {
        proc.ccMap[0].store (11);
        auto sendCC = [&] (int v)
        {
            AudioBuffer<float> b (2, 256); MidiBuffer m; m.addEvent (MidiMessage::controllerEvent (1, 11, v), 0);
            proc.processBlock (b, m);
            pump (4);
            return proc.apvts.getRawParameterValue ("threshold")->load();
        };
        const float a = sendCC (0), c = sendCC (127), mid = sendCC (64);
        std::printf ("CC 11 : 0 -> %.1f dB, 127 -> %.1f dB, 64 -> %.1f dB\n", a, c, mid);
    }
    ed.reset();
    return 0;
}
