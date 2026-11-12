#pragma once

#include "PluginProcessor.h"
#include <juce_gui_basics/juce_gui_basics.h>
#include "Layout.h"
#include "NineHandsMenu.h"
#include "NineHandsWindow.h"

//==============================================================================
// NGATE v2 (NINE HANDS | DSP) : visuel photo plein cadre (1206 x 1800 px), repere du plugin = image / 2.
// Fond : facade, vis, plaque, fenetre, potard (ombre, jupe, chapeau et ses reflets FIXES), boutons, LED eteintes,
// footswitch, jacks. Par-dessus : usure + index du potard (knob_top.png, tourne), couronne de points (vumetre),
// LED allumees + lumiere sur la facade, inverseur (3 images), textes / NGATE / logo en vectoriel, pastille presets.
//==============================================================================

// Potard THRESHOLD : seul le calque usure + index tourne ; chapeau et reflets restent dans le fond.
class ThresholdKnob : public juce::Slider
{
public:
    void paint (juce::Graphics&) override;
    bool hitTest (int x, int y) override;
    juce::Image top, topScaled;          // knob_top.png et sa copie a la taille d'affichage (preparee par le timer)
    void prepare (float physScale);
};

// Bouton poussoir (LEARN, BASS) : photo dans le fond ; on dessine l'appui, le survol et la couronne orange.
class PushButton : public juce::Component
{
public:
    std::function<void()> onClick, onRightClick;
    float glow = 0.0f, progress = -1.0f;
    PushButton() { setMouseCursor (juce::MouseCursor::PointingHandCursor); }
    void paint (juce::Graphics&) override;
    bool hitTest (int x, int y) override;
    void mouseDown (const juce::MouseEvent&) override;
    void mouseUp (const juce::MouseEvent&) override;
    void mouseEnter (const juce::MouseEvent&) override { repaint(); }
    void mouseExit (const juce::MouseEvent&) override  { repaint(); }
private:
    bool pressed = false;
};

// Inverseur horizontal SOFT / HARD (photos : levier a droite = HARD, a gauche = SOFT, milieu ~55 ms pendant la bascule)
class LeverSwitch : public juce::Component
{
public:
    explicit LeverSwitch (juce::RangedAudioParameter& p);
    void paint (juce::Graphics&) override;
    bool hitTest (int x, int y) override;
    void mouseDown (const juce::MouseEvent&) override;
    void mouseWheelMove (const juce::MouseEvent&, const juce::MouseWheelDetails&) override;
    void tick (double nowMs);
    void set (bool hard);
    juce::Image strip;                        // HARD / milieu / SOFT empiles (carres)
    std::function<void()> onRightClick, onUserChange;
private:
    juce::ParameterAttachment attachment;
    int frame = 0, shown = 0;                 // 0 = HARD, 1 = milieu, 2 = SOFT
    double transitionUntil = 0.0;
};

// Footswitch (photo d'Echoflex, dans le fond) : fonctionnement d'Echoflex
class FootSwitchArea : public juce::Component
{
public:
    explicit FootSwitchArea (juce::RangedAudioParameter& p);
    void paint (juce::Graphics&) override;
    void mouseDown (const juce::MouseEvent&) override;
    void mouseUp (const juce::MouseEvent&) override;
    bool hitTest (int x, int y) override;
    std::function<void()> onRightClick, onUserChange;
private:
    bool value = true, pressed = false;
    juce::ParameterAttachment attachment;
};

struct RightClickForwarder : public juce::MouseListener
{
    std::function<void()> callback;
    void mouseDown (const juce::MouseEvent& e) override { if (e.mods.isPopupMenu() && callback) callback(); }
};

//==============================================================================
class NgateAudioProcessorEditor : public juce::AudioProcessorEditor,
                                  private juce::Timer
{
public:
    explicit NgateAudioProcessorEditor (NgateAudioProcessor&);
    ~NgateAudioProcessorEditor() override;

    void paint (juce::Graphics&) override;
    void resized() override;
    void parentHierarchyChanged() override;
    void mouseDown (const juce::MouseEvent&) override;
    void mouseMove (const juce::MouseEvent&) override;
    void mouseExit (const juce::MouseEvent&) override;

    static constexpr float baseW = layout::frameW;
    static constexpr float baseH = layout::frameH;
    static constexpr int defaultH = 493;     // « 60 % » = taille minimale
    static constexpr int refH = 958;         // 100 %
    static constexpr int maxH = refH * 3 / 2;
    static constexpr int numSizes = 3;
    static int sizeHeight (int idx);
    void setScaledHeight (int h);

    // outil de rendu (captures)
    void forceRenderScale (float sc) { forcedScale = sc; rebuildCaches (sc); }
    void openMainMenu() { showContextMenu (-1); }
    void tickForCapture() { timerCallback(); }
    void showStatus();

private:
    void timerCallback() override;
    void useSoftwareRenderer();
    void visibilityChanged() override;
    void askRepaint (juce::Rectangle<int> r);
public:
    juce::PopupMenu buildContextMenu (int learnIdx = -1);   // menu clic droit (aussi pour l'outil de controle des menus)
    void setGlowPercent (int pc);                            // clic droit > Glow intensity
private:
    int glowPc = 100;                      // clic droit > Glow intensity : lumiere des LED sur la facade (25 a 100 %)
    double lastGlowReadMs = 0.0;
    float glowAmt() const { return (float) glowPc / 100.0f; }
    void showContextMenu (int learnIdx);
    void showPresetMenu();
    void stepPreset (int delta);
    void rebuildCaches (float scale = 0.0f);
    float physicalScale() const;
    juce::Rectangle<int> scaled (juce::Rectangle<float> r) const;
    void toggleParam (const char* id);
    void setParamValue (const char* id, float plain);

    juce::String buildStatusLine() const;
    juce::String buildPresetLine() const;
    juce::String readoutText() const;
    void buildPrint();
    void renderPrint (juce::Graphics&);
    void drawMeter (juce::Graphics&);
    void drawLeds (juce::Graphics&);
    void drawReadout (juce::Graphics&);
    void drawBar (juce::Graphics&);
    int litDots() const;

    NgateAudioProcessor& proc;
    NineHandsMenu::MenuLnf menuLnf;
    NineHandsWindow::HostLock hostLock;    // fenetre du DAW : jamais sous 60 %, jamais au-dela de 150 %
    RightClickForwarder rightClickFwd;

    juce::Image background, bgScaled, printLayer, glowG, glowO, ledG, ledO;
    juce::Typeface::Ptr medFace, boldFace, lightFace, regFace;
    juce::Path printPath, titlePath;
    std::unique_ptr<juce::Drawable> logo;
    int cacheW = 0, cacheH = 0;
    float cacheScale = 0.0f, forcedScale = 0.0f;
    int resizeSettle = 0;
    void* lastPeer = nullptr;
    double lastPaintMs = 0.0, repaintAskedMs = 0.0, lastScaleCheckMs = 0.0, lastRendererCheckMs = 0.0;

    ThresholdKnob threshold;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> aThreshold;
    PushButton learnBtn, bassBtn;
    LeverSwitch lever;
    FootSwitchArea footswitch;

    // animation
    double lastTime = 0.0, phase = 0.0;
    float meterDb = -120.0f, openLevel = 0.0f, gateLevel = 0.0f, bassLevel = 0.0f, powerLevel = 1.0f;
    float learnGlow = 0.0f, learnDone = 0.0f;
    int lastLearnCount = 0;
    int drawnDots = -1;
    float drawnOpen = -1.0f, drawnGate = -1.0f, drawnPower = -1.0f, drawnStatus = -1.0f;
    juce::String drawnReadout;

    // ligne d'etat / barre de presets (meme pastille)
    float statusAlpha = 0.0f;
    double statusUntil = 0.0;
    juce::String statusLine, presetLine, learnLine;
    double learnLineUntil = 0.0;
    float lastValues[4] { -1.0f, -1.0f, -1.0f, -1.0f };
    int lastPresetSeen = -999, lastMidiCount = 0, midiFlash = 0;
    int hoverZone = 0, drawnHover = -1;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (NgateAudioProcessorEditor)
};
