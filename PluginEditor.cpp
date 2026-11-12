#include "PluginEditor.h"
#include "BinaryData.h"
#include "WigaWindowSize.h"

using namespace juce;

namespace
{
    // course du potard = couronne de points du visuel (-133,85 a +133,85 degres)
    const float startAng = MathConstants<float>::twoPi - degreesToRadians (layout::dotAngle);
    const float endAng   = MathConstants<float>::twoPi + degreesToRadians (layout::dotAngle);

    const Colour accent (0xffec7a2c);          // orange de NOISE GATE : en-tetes de menu, LEARN, BASS
    const Colour cream  (0xffefd9b0);          // chiffres de l'afficheur
    const Colour dotOrange (0xffff8a1e), dotGreen (0xff36e05c);
    const Colour barInk (0xffe8e8e6);

    const Rectangle<float> barRect = layout::presetRect;
    constexpr float barFont = 23.0f, arrowW = 34.0f;

    float dotDb (int i) { return NgateAudioProcessor::minThreshold + (NgateAudioProcessor::maxThreshold - NgateAudioProcessor::minThreshold) * (float) i / (float) (layout::numDots - 1); }
    float angleFor (float db)
    {
        const float t = jlimit (0.0f, 1.0f, (db - NgateAudioProcessor::minThreshold) / (NgateAudioProcessor::maxThreshold - NgateAudioProcessor::minThreshold));
        return startAng + (endAng - startAng) * t;
    }
    Point<float> onCircle (Point<float> c, float r, float a) { return { c.x + r * std::sin (a), c.y - r * std::cos (a) }; }

    const char* const watchIds[4] = { "threshold", "hard", "bass", "range" };
}

//==============================================================================
// POTARD : calque usure + index (fourni par l'utilisateur), tourne autour du centre du chapeau
//==============================================================================
void ThresholdKnob::prepare (float physScale)
{
    if (! top.isValid() || getWidth() <= 0) return;
    const float sprite = (float) getWidth() * (layout::knobSprite / (layout::capR * 2.0f + 10.0f));
    const int px = jmax (8, roundToInt (sprite * physScale));
    if (topScaled.isValid() && topScaled.getWidth() == px) return;
    topScaled = px >= top.getWidth() ? top : top.rescaled (px, px, Graphics::highResamplingQuality);
}

void ThresholdKnob::paint (Graphics& g)
{
    const auto& img = topScaled.isValid() ? topScaled : top;
    if (! img.isValid()) return;
    const auto rp = getRotaryParameters();
    const float pos = (float) valueToProportionOfLength (getValue());
    const float a = rp.startAngleRadians + pos * (rp.endAngleRadians - rp.startAngleRadians);
    const auto c = getLocalBounds().toFloat().getCentre();
    const float side = (float) getWidth() * (layout::knobSprite / (layout::capR * 2.0f + 10.0f));
    const float k = side / (float) img.getWidth();
    g.setImageResamplingQuality (Graphics::highResamplingQuality);
    g.drawImageTransformed (img, AffineTransform::translation (-img.getWidth() * 0.5f, -img.getHeight() * 0.5f)
                                     .scaled (k).rotated (a).translated (c.x, c.y));
}

bool ThresholdKnob::hitTest (int x, int y)
{
    return getLocalBounds().toFloat().getCentre().getDistanceFrom ({ (float) x, (float) y }) <= (float) getWidth() * 0.5f;
}

//==============================================================================
// BOUTONS POUSSOIRS
//==============================================================================
bool PushButton::hitTest (int x, int y)
{
    return getLocalBounds().toFloat().getCentre().getDistanceFrom ({ (float) x, (float) y }) <= (float) getWidth() * 0.5f;
}

void PushButton::mouseDown (const MouseEvent& e)
{
    if (e.mods.isPopupMenu()) { if (onRightClick) onRightClick(); return; }
    pressed = true; repaint();
}

void PushButton::mouseUp (const MouseEvent& e)
{
    if (! pressed) return;
    pressed = false; repaint();
    if (contains (e.getPosition()) && onClick) onClick();
}

void PushButton::paint (Graphics& g)
{
    const auto b = getLocalBounds().toFloat();
    const auto c = b.getCentre();
    const float k = b.getWidth() / ((layout::btnR + 10.0f) * 2.0f);     // pixels par unite
    const float R = layout::btnR * k, cap = layout::btnCapR * k;
    if (glow > 0.003f)
    {
        ColourGradient gl (accent.withAlpha (0.0f), c.x, c.y, accent.withAlpha (0.0f), c.x + b.getWidth() * 0.5f, c.y, true);
        gl.addColour (R / (b.getWidth() * 0.5f) - 0.06, accent.withAlpha (0.0f));
        gl.addColour (R / (b.getWidth() * 0.5f) + 0.03, accent.withAlpha (0.50f * glow));
        g.setGradientFill (gl);
        g.fillEllipse (b);
        g.setColour (accent.withAlpha (0.85f * glow));
        g.drawEllipse (c.x - R, c.y - R, R * 2.0f, R * 2.0f, 1.3f * k);
    }
    if (progress >= 0.0f)
    {
        Path arc;
        arc.addCentredArc (c.x, c.y, R + 4.5f * k, R + 4.5f * k, 0.0f, 0.0f, MathConstants<float>::twoPi * progress, true);
        g.setColour (accent);
        g.strokePath (arc, PathStrokeType (2.2f * k, PathStrokeType::curved, PathStrokeType::rounded));
    }
    if (pressed)
    {
        g.setColour (Colours::black.withAlpha (0.38f));
        g.fillEllipse (c.x - cap, c.y - cap, cap * 2.0f, cap * 2.0f);
        ColourGradient in (Colours::black.withAlpha (0.5f), c.x, c.y - cap, Colours::black.withAlpha (0.0f), c.x, c.y - cap * 0.2f, false);
        g.setGradientFill (in);
        g.fillEllipse (c.x - cap, c.y - cap, cap * 2.0f, cap * 2.0f);
    }
    else if (isMouseOver())
    {
        g.setColour (Colours::white.withAlpha (0.05f));
        g.fillEllipse (c.x - cap, c.y - cap, cap * 2.0f, cap * 2.0f);
    }
}

//==============================================================================
// INVERSEUR SOFT / HARD
//==============================================================================
LeverSwitch::LeverSwitch (RangedAudioParameter& p)
    : attachment (p, [this] (float v)
                  {
                      const int nf = v > 0.5f ? 0 : 2;
                      if (nf != frame)
                      {
                          frame = nf; shown = 1;                      // position du milieu ~55 ms
                          transitionUntil = Time::getMillisecondCounterHiRes() + 55.0;
                          repaint();
                      }
                  })
{
    attachment.sendInitialUpdate();
    shown = frame;
    setMouseCursor (MouseCursor::PointingHandCursor);
}

void LeverSwitch::tick (double now)
{
    if (shown != frame && now >= transitionUntil) { shown = frame; repaint(); }
}

void LeverSwitch::paint (Graphics& g)
{
    if (! strip.isValid()) return;
    const int fs = strip.getWidth();
    g.setImageResamplingQuality (Graphics::highResamplingQuality);
    g.drawImage (strip, 0, 0, getWidth(), getHeight(), 0, shown * fs, fs, fs);   // meme rectangle pour les 3 images
}

bool LeverSwitch::hitTest (int x, int y)
{
    const auto c = getLocalBounds().toFloat().getCentre();
    const float r = (float) getWidth() * (layout::togR / layout::togS);
    return std::abs ((float) x - c.x) <= r * 1.7f && std::abs ((float) y - c.y) <= r * 1.1f;
}

void LeverSwitch::set (bool hard)
{
    if ((frame == 0) == hard) return;
    attachment.setValueAsCompleteGesture (hard ? 1.0f : 0.0f);
    if (onUserChange) onUserChange();
}

void LeverSwitch::mouseDown (const MouseEvent& e)
{
    if (e.mods.isPopupMenu()) { if (onRightClick) onRightClick(); return; }
    set (frame != 0);
}

void LeverSwitch::mouseWheelMove (const MouseEvent&, const MouseWheelDetails& w)
{
    if (std::abs (w.deltaY) > 0.0f) set (w.deltaY < 0.0f);     // molette vers le bas = vers la droite (HARD)
}

//==============================================================================
// FOOTSWITCH (fonctionnement d'Echoflex)
//==============================================================================
FootSwitchArea::FootSwitchArea (RangedAudioParameter& p)
    : attachment (p, [this] (float v) { value = v > 0.5f; repaint(); })
{
    attachment.sendInitialUpdate();
    setMouseCursor (MouseCursor::PointingHandCursor);
}

bool FootSwitchArea::hitTest (int x, int y)
{
    const auto c = getLocalBounds().toFloat().getCentre();
    return c.getDistanceFrom ({ (float) x, (float) y }) <= (float) getWidth() * (layout::footR * 1.35f / layout::fsS);
}

void FootSwitchArea::paint (Graphics& g)
{
    if (! pressed) return;
    const auto b = getLocalBounds().toFloat();
    const float r = b.getWidth() * (layout::footR / layout::fsS) * 0.98f;
    const auto c = b.getCentre();
    g.setColour (Colours::black.withAlpha (0.25f));
    g.fillEllipse (c.x - r, c.y - r, r * 2.0f, r * 2.0f);
}

void FootSwitchArea::mouseDown (const MouseEvent& e)
{
    if (e.mods.isPopupMenu()) { if (onRightClick) onRightClick(); return; }
    pressed = true; repaint();
    attachment.setValueAsCompleteGesture (value ? 0.0f : 1.0f);
    if (onUserChange) onUserChange();
}

void FootSwitchArea::mouseUp (const MouseEvent& e)
{
    if (e.mods.isPopupMenu()) return;
    pressed = false; repaint();
}

//==============================================================================
// EDITEUR
//==============================================================================
NgateAudioProcessorEditor::NgateAudioProcessorEditor (NgateAudioProcessor& p)
    : AudioProcessorEditor (&p), proc (p),
      lever (*p.apvts.getParameter ("hard")),
      footswitch (*p.apvts.getParameter ("active"))
{
    background = ImageCache::getFromMemory (BinaryData::background_png, BinaryData::background_pngSize);
    glowG = ImageCache::getFromMemory (BinaryData::glow_green_png, BinaryData::glow_green_pngSize);
    glowO = ImageCache::getFromMemory (BinaryData::glow_orange_png, BinaryData::glow_orange_pngSize);
    ledG  = ImageCache::getFromMemory (BinaryData::led_green_on_png, BinaryData::led_green_on_pngSize);
    ledO  = ImageCache::getFromMemory (BinaryData::led_orange_on_png, BinaryData::led_orange_on_pngSize);
    threshold.top = ImageCache::getFromMemory (BinaryData::knob_top_png, BinaryData::knob_top_pngSize);
    lever.strip   = ImageCache::getFromMemory (BinaryData::toggle_strip_png, BinaryData::toggle_strip_pngSize);
    medFace  = Typeface::createSystemTypefaceFor (BinaryData::PoppinsMedium_ttf,  BinaryData::PoppinsMedium_ttfSize);
    boldFace = Typeface::createSystemTypefaceFor (BinaryData::PoppinsBold_ttf,    BinaryData::PoppinsBold_ttfSize);
    lightFace = Typeface::createSystemTypefaceFor (BinaryData::PoppinsLight_ttf,  BinaryData::PoppinsLight_ttfSize);
    regFace  = Typeface::createSystemTypefaceFor (BinaryData::PoppinsRegular_ttf, BinaryData::PoppinsRegular_ttfSize);
    menuLnf.f = { regFace, medFace, boldFace };
    glowPc = NineHandsGlow::percent (JucePlugin_Name);
    if (auto xml = XmlDocument::parse (String::fromUTF8 (BinaryData::NineHandsLogo_svg, BinaryData::NineHandsLogo_svgSize)))
        logo = Drawable::createFromSVG (*xml);
    buildPrint();

    rightClickFwd.callback = [this] { showContextMenu (0); };
    threshold.setSliderStyle (Slider::RotaryHorizontalVerticalDrag);
    threshold.setTextBoxStyle (Slider::NoTextBox, false, 0, 0);
    threshold.setRotaryParameters (startAng, endAng, true);
    threshold.setMouseDragSensitivity (360);
    threshold.setMouseCursor (MouseCursor::PointingHandCursor);
    threshold.addMouseListener (&rightClickFwd, false);
    threshold.onDragStart = [this] { proc.currentPreset = -1; };
    addAndMakeVisible (threshold);
    aThreshold = std::make_unique<AudioProcessorValueTreeState::SliderAttachment> (proc.apvts, "threshold", threshold);
    threshold.setDoubleClickReturnValue (true, -60.0);

    learnBtn.onClick = [this] { if (proc.learning.load()) proc.cancelLearn(); else proc.startLearn(); showStatus(); };
    learnBtn.onRightClick = [this] { showContextMenu (3); };
    addAndMakeVisible (learnBtn);
    bassBtn.onClick = [this] { toggleParam ("bass"); };
    bassBtn.onRightClick = [this] { showContextMenu (2); };
    addAndMakeVisible (bassBtn);

    lever.onRightClick = [this] { showContextMenu (1); };
    lever.onUserChange = [this] { proc.currentPreset = -1; };
    addAndMakeVisible (lever);
    footswitch.onRightClick = [this] { showContextMenu (4); };
    addAndMakeVisible (footswitch);

    for (int i = 0; i < 4; ++i) lastValues[i] = proc.apvts.getRawParameterValue (watchIds[i])->load();
    lastPresetSeen = proc.currentPreset.load();
    lastMidiCount = proc.midiCounter.load();
    lastLearnCount = proc.learnCounter.load();
    powerLevel = proc.apvts.getRawParameterValue ("active")->load() > 0.5f ? 1.0f : 0.0f;
    bassLevel = proc.apvts.getRawParameterValue ("bass")->load() > 0.5f ? powerLevel : 0.0f;

    const int defaultW = roundToInt ((float) defaultH * baseW / baseH);
    setResizable (true, true);
    setResizeLimits (defaultW, defaultH, roundToInt ((float) maxH * baseW / baseH), maxH);
    hostLock.setLimits (defaultW, defaultH, roundToInt ((float) maxH * baseW / baseH), maxH);
    if (auto* cons = getConstrainer()) cons->setFixedAspectRatio ((double) baseW / (double) baseH);
    setOpaque (true);
    setSize (defaultW, defaultH);
    setScaledHeight (sizeHeight (NineHandsWindow::openIndex (JucePlugin_Name, proc.uiSizeIdx.load(), numSizes)));   // taille du projet, sinon taille par defaut
    rebuildCaches();
    lastTime = Time::getMillisecondCounterHiRes();
    startTimerHz (30);
}

NgateAudioProcessorEditor::~NgateAudioProcessorEditor()
{
    PopupMenu::dismissAllActiveMenus();
    stopTimer();
    threshold.removeMouseListener (&rightClickFwd);
}

int NgateAudioProcessorEditor::sizeHeight (int idx)
{
    const int h[numSizes] = { (int) defaultH, roundToInt (refH * 0.75f), (int) refH };
    return h[jlimit (0, numSizes - 1, idx)];
}

void NgateAudioProcessorEditor::setScaledHeight (int h)
{
    h = jlimit ((int) defaultH, (int) maxH, h);
    setSize (roundToInt ((float) h * baseW / baseH), h);
    hostLock.enforce();
}

Rectangle<int> NgateAudioProcessorEditor::scaled (Rectangle<float> r) const
{
    const float s = (float) getHeight() / baseH;
    return r.transformedBy (AffineTransform::scale (s)).getSmallestIntegerContainer();
}

float NgateAudioProcessorEditor::physicalScale() const
{
    if (forcedScale > 0.0f) return forcedScale;
    return jlimit (1.0f, 4.0f, (float) Component::getApproximateScaleFactorForComponent (this));
}

void NgateAudioProcessorEditor::showStatus() { statusUntil = Time::getMillisecondCounterHiRes() + 2500.0; }

void NgateAudioProcessorEditor::setParamValue (const char* id, float plain)
{
    if (auto* prm = proc.apvts.getParameter (id))
    {
        prm->beginChangeGesture();
        prm->setValueNotifyingHost (prm->convertTo0to1 (plain));
        prm->endChangeGesture();
    }
}

void NgateAudioProcessorEditor::toggleParam (const char* id)
{
    setParamValue (id, proc.apvts.getRawParameterValue (id)->load() > 0.5f ? 0.0f : 1.0f);
    proc.currentPreset = -1;
    showStatus();
}

//==============================================================================
// Serigraphie vectorielle (Poppins) : construite une fois en chemins, rendue dans un calque a la resolution de l'ecran
//==============================================================================
static Path textPath (const String& s, const Typeface::Ptr& face, float em, float track, float x, float y, float rotDeg, bool leftAnchor)
{
    const Font font (FontOptions (face).withPointHeight (em));
    float total = 0.0f;
    for (int i = 0; i < s.length(); ++i)
        total += GlyphArrangement::getStringWidth (font, String::charToString (s[i])) + (i > 0 ? track : 0.0f);
    // centre vertical = milieu de la hauteur des capitales (comme le visuel)
    GlyphArrangement h; h.addLineOfText (font, "H", 0.0f, 0.0f);
    const auto hb = h.getBoundingBox (0, -1, true);
    const float base = -(hb.getY() + hb.getHeight() * 0.5f);
    GlyphArrangement ga;
    float x0 = leftAnchor ? 0.0f : -total * 0.5f;
    for (int i = 0; i < s.length(); ++i)
    {
        const String ch = String::charToString (s[i]);
        ga.addLineOfText (font, ch, x0, base);
        x0 += GlyphArrangement::getStringWidth (font, ch) + track;
    }
    Path p; ga.createPath (p);
    p.applyTransform (AffineTransform::rotation (-rotDeg * MathConstants<float>::pi / 180.0f).translated (x, y));
    return p;
}

void NgateAudioProcessorEditor::buildPrint()
{
    printPath.clear();
    auto faceOf = [this] (int f) { return f == 1 ? boldFace : (f == 2 ? lightFace : medFace); };
    for (const auto& t : layout::texts)
        printPath.addPath (textPath (t.s, faceOf (t.font), t.em, t.track, t.x, t.y, t.rot, t.anchor == 1));
    titlePath = textPath ("NGATE", boldFace, layout::titleEm, layout::titleTrack, layout::titlePos.x, layout::titlePos.y, 0.0f, false);
}

void NgateAudioProcessorEditor::renderPrint (Graphics& g)
{
    // textes (chacun dans sa couleur)
    auto faceOf = [this] (int f) { return f == 1 ? boldFace : (f == 2 ? lightFace : medFace); };
    for (const auto& t : layout::texts)
    {
        g.setColour (Colour (t.colour).withAlpha (0.94f));
        g.fillPath (textPath (t.s, faceOf (t.font), t.em, t.track, t.x, t.y, t.rot, t.anchor == 1));
    }
    for (const auto& r : layout::rules)
    {
        g.setColour (Colour (0xffd6d6d3).withAlpha (0.88f));
        g.fillRect (Rectangle<float> (r.x0, r.y - r.w * 0.5f, r.x1 - r.x0, r.w));
    }
    // NGATE en relief : ombre portee douce, face metal brossee (degrade vertical), arete claire en haut a gauche
    {
        const auto b = titlePath.getBounds();
        DropShadow (Colours::black.withAlpha (0.8f), 3, { 1, 2 }).drawForPath (g, titlePath);
        ColourGradient face (Colour (0xffe6e6e3), b.getX(), b.getY(), Colour (0xff9a9b9c), b.getX(), b.getBottom(), false);
        face.addColour (0.45, Colour (0xffc9cac9));
        face.addColour (0.55, Colour (0xffb3b4b4));
        g.setGradientFill (face);
        g.fillPath (titlePath);
        Graphics::ScopedSaveState ss (g);
        g.reduceClipRegion (titlePath);
        g.setColour (Colours::white.withAlpha (0.55f));
        g.strokePath (titlePath, PathStrokeType (0.9f), AffineTransform::translation (0.5f, 0.6f));
        g.setColour (Colours::black.withAlpha (0.45f));
        g.strokePath (titlePath, PathStrokeType (0.9f), AffineTransform::translation (-0.5f, -0.6f));
    }
    if (logo != nullptr)
    {
        const auto vb = logo->getDrawableBounds();
        const float w = layout::logoW, h = w * vb.getHeight() / jmax (1.0f, vb.getWidth());
        logo->drawWithin (g, { layout::logoPos.x - w * 0.5f, layout::logoPos.y - h * 0.5f, w, h }, RectanglePlacement::centred, 0.92f);
    }
    // couronne de points : perles eteintes (allumees dessinees en direct)
    for (int i = 0; i < layout::numDots; ++i)
    {
        const auto c = onCircle (layout::knobPos, layout::dotsR, angleFor (dotDb (i)));
        g.setColour (Colours::black.withAlpha (0.45f));
        g.fillEllipse (c.x - 2.0f, c.y - 1.5f, 4.6f, 4.6f);
        ColourGradient pg (Colour (0xffd8d8d5), c.x - 0.8f, c.y - 0.9f, Colour (0xff76767a), c.x + 2.2f, c.y + 2.2f, true);
        g.setGradientFill (pg);
        g.fillEllipse (c.x - 2.2f, c.y - 2.2f, 4.4f, 4.4f);
    }
}

//==============================================================================
// Caches (reconstruits par le timer seulement : anti-gel v2)
//==============================================================================
void NgateAudioProcessorEditor::rebuildCaches (float sc)
{
    if (sc <= 0.0f) sc = cacheScale > 0.0f ? cacheScale : physicalScale();
    const int w = getWidth(), h = getHeight();
    if (w <= 0 || h <= 0) return;
    if (w == cacheW && h == cacheH && std::abs (sc - cacheScale) < 0.01f && bgScaled.isValid()) return;
    cacheW = w; cacheH = h; cacheScale = sc;
    const int pw = roundToInt ((float) w * sc), ph = roundToInt ((float) h * sc);
    bgScaled = (pw >= background.getWidth()) ? background : background.rescaled (pw, ph, Graphics::highResamplingQuality);
    printLayer = Image (Image::ARGB, pw, ph, true);
    {
        Graphics g (printLayer);
        g.addTransform (AffineTransform::scale ((float) ph / baseH));
        renderPrint (g);
    }
    threshold.prepare (sc);
    repaint();
}

void NgateAudioProcessorEditor::resized()
{
    // anti-gel : jamais de setSize ici
    const float kr = layout::capR + 5.0f;
    threshold.setBounds (scaled ({ layout::knobPos.x - kr, layout::knobPos.y - kr, kr * 2.0f, kr * 2.0f }));
    const float bb = layout::btnR + 10.0f;
    learnBtn.setBounds (scaled ({ layout::learnPos.x - bb, layout::learnPos.y - bb, bb * 2.0f, bb * 2.0f }));
    bassBtn.setBounds  (scaled ({ layout::bassPos.x - bb,  layout::bassPos.y - bb,  bb * 2.0f, bb * 2.0f }));
    {
        const float s = (float) getHeight() / baseH, hs = layout::togS * 0.5f;
        const int side = roundToInt (layout::togS * s);
        lever.setBounds (roundToInt ((layout::togglePos.x - hs) * s), roundToInt ((layout::togglePos.y - hs) * s), side, side);
    }
    const float fr = layout::fsS * 0.5f;
    footswitch.setBounds (scaled ({ layout::fsPos.x - fr, layout::fsPos.y - fr, fr * 2.0f, fr * 2.0f }));
    resizeSettle = 4;
}

//==============================================================================
// Anti-gel v2
//==============================================================================
void NgateAudioProcessorEditor::useSoftwareRenderer()
{
    auto* peer = getPeer();
    if (peer != lastPeer) { lastPeer = peer; repaint(); }
   #if JUCE_WINDOWS
    if (peer != nullptr)
    {
        int sw = peer->getAvailableRenderingEngines().indexOf ("Software Renderer");
        if (sw < 0) sw = 0;
        if (peer->getCurrentRenderingEngine() != sw) peer->setCurrentRenderingEngine (sw);
    }
   #endif
}

void NgateAudioProcessorEditor::parentHierarchyChanged() { useSoftwareRenderer(); hostLock.track (*this); }
void NgateAudioProcessorEditor::visibilityChanged()      { useSoftwareRenderer(); if (isShowing()) repaint(); }

void NgateAudioProcessorEditor::askRepaint (Rectangle<int> r)
{
    if (repaintAskedMs <= 0.0) repaintAskedMs = Time::getMillisecondCounterHiRes();
    repaint (r);
}

//==============================================================================
// Textes
//==============================================================================
String NgateAudioProcessorEditor::readoutText() const
{
    if (proc.learning.load()) return "LEARN";
    return String (proc.apvts.getRawParameterValue ("threshold")->load(), 1);
}

String NgateAudioProcessorEditor::buildStatusLine() const
{
    auto raw = [this] (const char* id) { return proc.apvts.getRawParameterValue (id)->load(); };
    if (proc.learning.load()) return "LEARN  mute the strings";
    if (learnDone > 0.0f)
        return "Noise " + String (proc.learnedNoiseDb.load(), 1) + " dB  >  " + String (raw ("threshold"), 1) + " dB";
    static const char* ranges[] = { "", "  -40 dB", "  -20 dB" };
    String s = String (raw ("threshold"), 1) + " dB  " + (raw ("hard") > 0.5f ? "HARD" : "SOFT")
             + (raw ("bass") > 0.5f ? "  BASS" : "") + ranges[jlimit (0, 2, roundToInt (raw ("range")))];
    if (raw ("active") < 0.5f) s = "BYPASS";
    return s;
}

String NgateAudioProcessorEditor::buildPresetLine() const
{
    const int cp = proc.currentPreset.load();
    String s;
    if (cp >= 0 && cp < NgateAudioProcessor::getNumFactoryPresets())
        s << (cp + 1) << "  " << NgateAudioProcessor::getFactoryPreset (cp).name;
    else if (cp > 100) s << "User " << (cp - 100);
    else               s << "Edited";
    if (proc.apvts.getRawParameterValue ("active")->load() < 0.5f) s << "  (bypass)";
    return s;
}

int NgateAudioProcessorEditor::litDots() const
{
    int n = 0;
    for (int i = 0; i < layout::numDots; ++i)
        if (dotDb (i) <= meterDb) n = i + 1;
    return powerLevel > 0.5f ? n : 0;
}

//==============================================================================
void NgateAudioProcessorEditor::timerCallback()
{
    const double now = Time::getMillisecondCounterHiRes();
    const double dt = jlimit (0.0, 0.1, (now - lastTime) * 0.001);
    lastTime = now; phase += dt;
    if (getPeer() != lastPeer || now - lastRendererCheckMs > 1000.0) { lastRendererCheckMs = now; useSoftwareRenderer(); }
    if (now - lastGlowReadMs > 3000.0)       // clic droit > Glow intensity : commun a toutes les fenetres (jamais dans paint)
    {
        lastGlowReadMs = now;
        const int pc = NineHandsGlow::percent (JucePlugin_Name);
        if (pc != glowPc) setGlowPercent (pc);
    }
    hostLock.track (*this);

    if (resizeSettle > 0 && --resizeSettle == 0) rebuildCaches();
    else if (resizeSettle == 0 && now - lastScaleCheckMs > 250.0)
    {
        lastScaleCheckMs = now;
        const float sc = physicalScale();
        if (std::abs (sc - cacheScale) > 0.01f) rebuildCaches (sc);
    }
    if (repaintAskedMs > 0.0 && isShowing() && now - repaintAskedMs > 1500.0 && lastPaintMs < repaintAskedMs)
    {
        repaintAskedMs = 0.0; lastPeer = nullptr;
        useSoftwareRenderer(); repaint();
    }

    lever.tick (now);
    auto raw = [this] (const char* id) { return proc.apvts.getRawParameterValue (id)->load(); };

    // ligne d'etat : seulement quand un reglage bouge ; puis la barre de presets revient
    for (int i = 0; i < 4; ++i)
    {
        const float v = raw (watchIds[i]);
        if (std::abs (v - lastValues[i]) > 1.0e-4f) { lastValues[i] = v; showStatus(); learnDone = 0.0f; }
    }
    if (threshold.isMouseButtonDown()) showStatus();
    const int cp = proc.currentPreset.load();
    if (cp != lastPresetSeen) { lastPresetSeen = cp; if (cp >= 0) statusUntil = 0.0; }
    const int mc = proc.midiCounter.load();
    if (mc != lastMidiCount) { lastMidiCount = mc; midiFlash = 8; }
    if (midiFlash > 0) --midiFlash;

    const int lc = proc.learnCounter.load();
    if (lc != lastLearnCount) { lastLearnCount = lc; learnDone = 1.0f; statusUntil = now + 4000.0; }
    learnDone = jmax (0.0f, learnDone - (float) dt * 0.25f);
    if (proc.learning.load()) showStatus();

    const int lt = proc.learnTarget.load();
    const int learned = proc.lastLearned.exchange (-1);
    if (learned >= 0)
    {
        learnLine = String (NgateAudioProcessor::learnDef (learned).name) + " = CC " + String (proc.ccMap[learned].load());
        learnLineUntil = now + 2000.0; statusUntil = jmax (statusUntil, learnLineUntil);
    }
    else if (lt >= 0)
    {
        learnLine = "MIDI LEARN  " + String (NgateAudioProcessor::learnDef (lt).name);
        learnLineUntil = now + 200.0; statusUntil = jmax (statusUntil, now + 200.0);
    }

    const float target = now < statusUntil ? 1.0f : 0.0f;
    statusAlpha += (target - statusAlpha) * (target > statusAlpha ? 0.45f : 0.30f);
    if (statusAlpha < 0.005f) statusAlpha = 0.0f;
    if (statusAlpha > 0.995f) statusAlpha = 1.0f;

    // bypass : couronne, LED, BASS s'eteignent, l'afficheur baisse
    const float pT = raw ("active") > 0.5f ? 1.0f : 0.0f;
    powerLevel += (pT - powerLevel) * (pT > powerLevel ? 0.45f : 0.28f);
    if (std::abs (pT - powerLevel) < 0.003f) powerLevel = pT;

    const float in = proc.inputDb.load();
    meterDb = in > meterDb ? in : meterDb + (in - meterDb) * 0.25f;

    const float openAmt = jlimit (0.0f, 1.0f, 1.0f + proc.gainDb.load() / 24.0f);
    auto fade = [] (float& v, float t) { v += (t - v) * (t > v ? 0.45f : 0.28f); if (std::abs (t - v) < 0.003f) v = t; };
    fade (openLevel, openAmt * powerLevel);
    fade (gateLevel, (1.0f - openAmt) * powerLevel);
    fade (bassLevel, raw ("bass") > 0.5f ? powerLevel : 0.0f);
    const float lg = proc.learning.load() ? 0.55f + 0.45f * (float) std::sin (phase * 9.0) : 0.0f;
    learnGlow += (lg - learnGlow) * 0.5f;

    // ne redessiner que ce qui change
    const int dots = litDots();
    if (dots != drawnDots || std::abs (powerLevel - drawnPower) > 0.003f)
    {
        drawnDots = dots;
        const float r = layout::dotsR + 14.0f;
        askRepaint (scaled ({ layout::knobPos.x - r, layout::knobPos.y - r, r * 2.0f, r * 2.0f }));
    }
    if (std::abs (powerLevel - drawnPower) > 0.003f || readoutText() != drawnReadout || learnDone > 0.0f || proc.learning.load())
    {
        drawnPower = powerLevel; drawnReadout = readoutText();
        askRepaint (scaled (layout::readoutRect.expanded (4.0f)));
    }
    if (std::abs (openLevel - drawnOpen) > 0.003f) { drawnOpen = openLevel; askRepaint (scaled (layout::glowGreenRect)); }
    if (std::abs (gateLevel - drawnGate) > 0.003f) { drawnGate = gateLevel; askRepaint (scaled (layout::glowOrangeRect)); }

    const float lgv = jmax (learnGlow, learnDone * 0.8f);
    const float lp = proc.learning.load() ? proc.learnProgress.load() : -1.0f;
    if (std::abs (learnBtn.glow - lgv) > 0.003f || std::abs (learnBtn.progress - lp) > 0.002f) { learnBtn.glow = lgv; learnBtn.progress = lp; learnBtn.repaint(); }
    if (std::abs (bassBtn.glow - bassLevel) > 0.003f) { bassBtn.glow = bassLevel; bassBtn.repaint(); }

    const auto sl = (learnLineUntil > 0.0 && now < learnLineUntil + 800.0) ? learnLine : buildStatusLine();
    const auto pl = buildPresetLine();
    if (std::abs (statusAlpha - drawnStatus) > 0.003f || sl != statusLine || pl != presetLine || hoverZone != drawnHover || midiFlash > 0)
    {
        drawnStatus = statusAlpha; statusLine = sl; presetLine = pl; drawnHover = hoverZone;
        askRepaint (scaled (barRect.expanded (3.0f)));
    }
}

//==============================================================================
// Dessin
//==============================================================================
void NgateAudioProcessorEditor::drawMeter (Graphics& g)
{
    if (powerLevel <= 0.003f) return;
    const float thr = proc.apvts.getRawParameterValue ("threshold")->load();
    const int n = litDots();
    for (int i = 0; i < n; ++i)
    {
        const float db = dotDb (i);
        const auto c = onCircle (layout::knobPos, layout::dotsR, angleFor (db));
        const auto col = db < thr ? dotOrange : dotGreen;
        const float gr = 10.5f, r = 3.9f;
        ColourGradient gl (col.withAlpha (0.42f * powerLevel), c.x, c.y, col.withAlpha (0.0f), c.x + gr, c.y, true);
        g.setGradientFill (gl);
        g.fillEllipse (c.x - gr, c.y - gr, gr * 2.0f, gr * 2.0f);
        ColourGradient core (col.brighter (0.6f).withAlpha (powerLevel), c.x - r * 0.25f, c.y - r * 0.3f,
                             col.darker (0.15f).withAlpha (powerLevel), c.x + r, c.y + r, true);
        g.setGradientFill (core);
        g.fillEllipse (c.x - r, c.y - r, r * 2.0f, r * 2.0f);
        g.setColour (Colours::white.withAlpha (0.75f * powerLevel));
        g.fillEllipse (c.x - 1.6f, c.y - 1.8f, 2.2f, 2.0f);
    }
}

void NgateAudioProcessorEditor::drawLeds (Graphics& g)
{
    auto one = [&] (Point<float> c, float level, const Image& glowImg, Rectangle<float> glowRect, const Image& lens)
    {
        if (level <= 0.003f) return;
        g.setOpacity (level * glowAmt());                          // halo : clic droit > Glow intensity
        if (glowImg.isValid()) g.drawImage (glowImg, glowRect);
        g.setOpacity (level);                                      // lentille : toujours pleine
        const float hs = layout::ledS * 0.5f;
        if (lens.isValid()) g.drawImage (lens, { c.x - hs, c.y - hs, hs * 2.0f, hs * 2.0f });
        g.setOpacity (1.0f);
    };
    one (layout::openLedPos, openLevel, glowG, layout::glowGreenRect, ledG);
    one (layout::gateLedPos, gateLevel, glowO, layout::glowOrangeRect, ledO);
}

void NgateAudioProcessorEditor::drawReadout (Graphics& g)
{
    const auto r = layout::readoutRect;
    Graphics::ScopedSaveState ss (g);
    g.reduceClipRegion (r.toNearestInt());
    const bool learning = proc.learning.load();
    const float dim = 0.28f + 0.72f * powerLevel;
    Colour c = learning ? accent : cream;
    if (learnDone > 0.0f && ! learning)
        c = cream.interpolatedWith (accent, learnDone * (0.5f + 0.5f * (float) std::sin (phase * 14.0)));
    g.setFont (Font (FontOptions (medFace).withHeight (34.0f)));
    const auto tr = r.reduced (10.0f, 2.0f);
    g.setColour (c.withAlpha (0.16f * dim));
    g.drawText (readoutText(), tr.translated (0.0f, 1.5f), Justification::centredRight);
    g.setColour (c.withAlpha (dim));
    g.drawText (readoutText(), tr, Justification::centredRight);
    if (learning)
    {
        const auto bar = r.reduced (10.0f, 0.0f).withTop (r.getBottom() - 7.0f).withHeight (2.5f);
        g.setColour (accent.withAlpha (0.25f)); g.fillRect (bar);
        g.setColour (accent); g.fillRect (bar.withWidth (bar.getWidth() * proc.learnProgress.load()));
    }
}

void NgateAudioProcessorEditor::drawBar (Graphics& g)
{
    // pastille unique (400 x 38) : la ligne d'etat remplace la barre de presets pendant les reglages
    const auto r = barRect;
    const float rad = r.getHeight() * 0.5f;
    g.setColour (Colour (0xff0a0a0b));
    g.fillRoundedRectangle (r.expanded (1.5f), rad + 1.5f);
    g.setColour (Colour (0xff060708));
    g.fillRoundedRectangle (r, rad);
    g.setColour (Colour (0xff4e5054).withAlpha (hoverZone != 0 && statusAlpha <= 0.0f ? 1.0f : 0.8f));
    g.drawRoundedRectangle (r.reduced (0.4f), rad, 0.9f);

    g.setFont (Font (FontOptions (medFace).withHeight (barFont)));
    if (statusAlpha > 0.0f)
    {
        g.setColour (barInk.withAlpha (statusAlpha));
        g.drawFittedText (statusLine, r.reduced (rad, 0.0f).toNearestInt(), Justification::centred, 1, 0.6f);
    }
    const float a = 1.0f - statusAlpha;
    if (a <= 0.0f) return;
    auto arrow = [&] (Rectangle<float> ar, bool left, bool hot)
    {
        Path p; const auto c = ar.getCentre(); const float sz = 5.5f;
        if (left) p.addTriangle (c.x + sz * 0.6f, c.y - sz, c.x + sz * 0.6f, c.y + sz, c.x - sz * 0.8f, c.y);
        else      p.addTriangle (c.x - sz * 0.6f, c.y - sz, c.x - sz * 0.6f, c.y + sz, c.x + sz * 0.8f, c.y);
        g.setColour (barInk.withAlpha ((hot ? 1.0f : 0.6f) * a));
        g.fillPath (p);
    };
    arrow (r.withWidth (arrowW), true, hoverZone == 1);
    arrow (r.withTrimmedLeft (r.getWidth() - arrowW), false, hoverZone == 3);
    g.setColour ((midiFlash > 0 ? accent.brighter (0.4f) : barInk).withAlpha ((hoverZone == 2 ? 1.0f : 0.92f) * a));
    g.drawFittedText (presetLine, r.reduced (arrowW, 0.0f).toNearestInt(), Justification::centred, 1, 0.7f);
}

void NgateAudioProcessorEditor::paint (Graphics& g)
{
    lastPaintMs = Time::getMillisecondCounterHiRes();
    repaintAskedMs = 0.0;
    g.fillAll (Colour (0xff111112));          // autour des jacks : le fond de l'image est transparent
    const Image& bg = bgScaled.isValid() ? bgScaled : background;
    g.setImageResamplingQuality (&bg == &background ? Graphics::highResamplingQuality : Graphics::lowResamplingQuality);
    if (bg.isValid()) g.drawImage (bg, getLocalBounds().toFloat());
    if (printLayer.isValid())
    {
        g.setImageResamplingQuality (Graphics::mediumResamplingQuality);
        g.drawImage (printLayer, getLocalBounds().toFloat());
    }
    const float s = (float) getHeight() / baseH;
    g.addTransform (AffineTransform::scale (s));
    g.setImageResamplingQuality (Graphics::mediumResamplingQuality);
    drawLeds (g);
    drawMeter (g);
    drawReadout (g);
    drawBar (g);
}

//==============================================================================
// Souris : barre de presets (fleches = precedent / suivant, nom = menu), clic droit = menu (la ou l'on clique)
//==============================================================================
static int presetZoneAt (Point<float> p)
{
    if (! barRect.contains (p)) return 0;
    if (p.x < barRect.getX() + arrowW) return 1;
    if (p.x > barRect.getRight() - arrowW) return 3;
    return 2;
}

void NgateAudioProcessorEditor::mouseMove (const MouseEvent& e)
{
    const float s = (float) getHeight() / baseH;
    hoverZone = presetZoneAt (e.position / s);
    setMouseCursor (hoverZone != 0 ? MouseCursor::PointingHandCursor : MouseCursor::NormalCursor);
}

void NgateAudioProcessorEditor::mouseExit (const MouseEvent&) { hoverZone = 0; }

void NgateAudioProcessorEditor::mouseDown (const MouseEvent& e)
{
    if (e.mods.isPopupMenu()) { showContextMenu (-1); return; }
    const float s = (float) getHeight() / baseH;
    const auto p = e.position / s;
    if (statusAlpha > 0.0f && barRect.contains (p)) { statusUntil = 0.0; learnLineUntil = 0.0; learnDone = 0.0f; return; }
    // clic sur SOFT / HARD (inscriptions) = choix direct
    for (const auto& t : layout::texts)
    {
        const String txt (t.s);
        if ((txt == "SOFT" || txt == "HARD") && std::abs (p.x - t.x) < 34.0f && std::abs (p.y - t.y) < 14.0f)
        {
            lever.set (txt == "HARD");
            return;
        }
    }
    switch (presetZoneAt (p))
    {
        case 1: stepPreset (-1); break;
        case 2: showPresetMenu(); break;
        case 3: stepPreset (1); break;
        default: break;
    }
}

void NgateAudioProcessorEditor::stepPreset (int delta)
{
    const int n = NgateAudioProcessor::getNumFactoryPresets();
    int cp = proc.currentPreset.load();
    if (cp < 0 || cp >= n) cp = delta > 0 ? -1 : 0;
    proc.applyFactoryPreset ((cp + delta + n) % n);
}

void NgateAudioProcessorEditor::showPresetMenu()
{
    PopupMenu m;
    m.setLookAndFeel (&menuLnf);
    NineHandsMenu::addHeader (m, menuLnf.f, NineHandsMenu::icoPreset, accent, "Presets", buildPresetLine());
    m.addSectionHeader ("Factory presets");
    for (int i = 0; i < NgateAudioProcessor::getNumFactoryPresets(); ++i)
        m.addItem (100 + i, String (i + 1) + ". " + NgateAudioProcessor::getFactoryPreset (i).name, true, proc.currentPreset.load() == i);
    m.addSeparator();
    PopupMenu load, save;
    for (int slot = 1; slot <= 9; ++slot)
    {
        const bool exists = proc.hasUserPreset (slot);
        load.addItem (200 + slot, "User " + String (slot) + (exists ? "" : "  (empty)"), exists, proc.currentPreset.load() == 100 + slot);
        save.addItem (300 + slot, "User " + String (slot) + (exists ? "  (overwrite)" : ""));
    }
    m.addSubMenu ("Load user preset", load);
    m.addSubMenu ("Save user preset", save);
    m.showMenuAsync (PopupMenu::Options().withTargetScreenArea (localAreaToGlobal (scaled (barRect))),
        [safe = Component::SafePointer<NgateAudioProcessorEditor> (this)] (int r)
        {
            if (safe == nullptr || r == 0) return;
            auto& pr = safe->proc;
            if      (r >= 100 && r < 200) pr.applyFactoryPreset (r - 100);
            else if (r > 200 && r < 300)  pr.loadUserPreset (r - 200);
            else if (r > 300 && r < 400)  pr.saveUserPreset (r - 300);
        });
}

void NgateAudioProcessorEditor::setGlowPercent (int pc)
{
    glowPc = NineHandsGlow::sanitize (pc);
    drawnOpen = drawnGate = -1.0f;          // le timer redessine les LED
}

PopupMenu NgateAudioProcessorEditor::buildContextMenu (int learnIdx)
{
    using namespace NineHandsMenu;
    PopupMenu menu;
    menu.setLookAndFeel (&menuLnf);
    auto ccText = [this] (int i)
    {
        const int cc = proc.ccMap[i].load();
        return cc >= 0 ? "CC " + String (cc) : String ("not assigned");
    };
    const int lt = proc.learnTarget.load();
    if (learnIdx >= 0)
    {
        // menu d'une commande (tronc commun) : en-tete, MIDI Learn, Clear MIDI, Cancel MIDI learn
        const int i = learnIdx;
        const String name = NgateAudioProcessor::learnDef (i).name;
        addHeader (menu, menuLnf.f, (learnIdx == 0 ? icoKnob : (learnIdx >= 4 ? icoPedal : icoSwitch)), accent, name, "MIDI: " + ccText (learnIdx));
        menu.addItem (1000 + learnIdx, "MIDI Learn: " + name, true, lt == learnIdx);
        menu.addItem (1100 + learnIdx, "Clear MIDI: " + name, proc.ccMap[learnIdx].load() >= 0);
        menu.addItem (1200, "Cancel MIDI learn", lt >= 0);
        return menu;
    }

    // menu de la pedale (tronc commun) : presets, reglages propres, MIDI, Plugin size, Glow intensity
    addHeader (menu, menuLnf.f, icoPedal, accent, "Ngate", "Noise gate  v" + String (JucePlugin_VersionString));
    PopupMenu factory;
    for (int i = 0; i < NgateAudioProcessor::getNumFactoryPresets(); ++i)
        factory.addItem (100 + i, String (i + 1) + ". " + NgateAudioProcessor::getFactoryPreset (i).name, true, proc.currentPreset.load() == i);
    menu.addSubMenu ("Factory presets", factory);
    PopupMenu load, save;
    for (int slot = 1; slot <= 9; ++slot)
    {{
        const bool exists = proc.hasUserPreset (slot);
        load.addItem (200 + slot, "User " + String (slot) + (exists ? "" : "  (empty)"), exists, proc.currentPreset.load() == 100 + slot);
        save.addItem (300 + slot, "User " + String (slot) + (exists ? "  (overwrite)" : ""));
    }}
    menu.addSubMenu ("Load user preset", load);
    menu.addSubMenu ("Save user preset", save);
    menu.addSeparator();
    auto raw = [this] (const char* id) { return proc.apvts.getRawParameterValue (id)->load(); };
    menu.addItem (40, proc.learning.load() ? "Cancel noise floor learn" : "Learn noise floor");
    PopupMenu gate;
    gate.addItem (41, "Soft (natural decay)", true, raw ("hard") < 0.5f);
    gate.addItem (42, "Hard (tight, fast)",   true, raw ("hard") > 0.5f);
    gate.addSeparator();
    gate.addItem (43, "Guitar", true, raw ("bass") < 0.5f);
    gate.addItem (44, "Bass",   true, raw ("bass") > 0.5f);
    gate.addSeparator();
    gate.addSectionHeader ("Range (closed gate)");
    gate.addItem (45, "Full mute",               true, roundToInt (raw ("range")) == 0);
    gate.addItem (46, "-40 dB (keeps a breath)", true, roundToInt (raw ("range")) == 1);
    gate.addItem (47, "-20 dB (gentle)",         true, roundToInt (raw ("range")) == 2);
    menu.addSubMenu ("Gate settings", gate);
    menu.addSeparator();

    PopupMenu midi;
    midi.addSectionHeader ("MIDI Learn");
    for (int i = 0; i < NgateAudioProcessor::numLearn; ++i)
        midi.addItem (1000 + i, "Learn: " + String (NgateAudioProcessor::learnDef (i).name) + "  (" + ccText (i) + ")", true, lt == i);
    midi.addSeparator();
    midi.addItem (1200, "Cancel MIDI learn", lt >= 0);
    midi.addItem (1201, "Clear all MIDI assignments");
    midi.addSeparator();
    NineHandsWindow::addMidiFootswitchMode (midi, ! proc.midiFsMomentary.load());
    midi.addSeparator();
    NineHandsWindow::addProgramChangeInfo (midi);
    menu.addSubMenu ("MIDI", midi);
    menu.addSeparator();

    const char* names[numSizes] = { "60 %", "75 %", "100 %" };
    const int heights[numSizes] = { sizeHeight (0), sizeHeight (1), sizeHeight (2) };
    menu.addSubMenu ("Plugin size", NineHandsWindow::sizeMenu (JucePlugin_Name, numSizes, names, heights, getHeight()));
    menu.addSubMenu ("Glow intensity", NineHandsWindow::glowMenu (glowPc));
    return menu;
}

void NgateAudioProcessorEditor::showContextMenu (int learnIdx)
{
    auto menu = buildContextMenu (learnIdx);
    menu.showMenuAsync (PopupMenu::Options().withMousePosition(),       // menu clic droit : toujours la ou l'on clique
        [safe = Component::SafePointer<NgateAudioProcessorEditor> (this)] (int r)
        {
            if (safe == nullptr || r == 0) return;
            auto& ed = *safe;
            auto& pr = ed.proc;
            int inst = pr.uiSizeIdx.load();
            const int sz = NineHandsWindow::handleSize (r, JucePlugin_Name, numSizes, inst);
            if (sz >= 0) { pr.uiSizeIdx = inst; ed.setScaledHeight (sizeHeight (sz)); return; }
            if (const int pc = NineHandsWindow::handleGlow (r, JucePlugin_Name))
            {
                ed.setGlowPercent (pc);
                ed.learnLine = "Glow  " + String (pc) + " %";        // ligne d'etat, brievement
                ed.learnLineUntil = Time::getMillisecondCounterHiRes() + 1500.0;
                ed.statusUntil = jmax (ed.statusUntil, ed.learnLineUntil);
                return;
            }
            if (false) {}
            else if (r == NineHandsWindow::idLatch)     pr.midiFsMomentary = false;
            else if (r == NineHandsWindow::idMomentary) pr.midiFsMomentary = true;
            else if (r == 40) { if (pr.learning.load()) pr.cancelLearn(); else pr.startLearn(); }
            else if (r == 41 || r == 42) { ed.setParamValue ("hard", r == 42 ? 1.0f : 0.0f); pr.currentPreset = -1; }
            else if (r == 43 || r == 44) { ed.setParamValue ("bass", r == 44 ? 1.0f : 0.0f); pr.currentPreset = -1; }
            else if (r >= 45 && r <= 47) { ed.setParamValue ("range", (float) (r - 45)); pr.currentPreset = -1; }
            else if (r >= 100 && r < 200) pr.applyFactoryPreset (r - 100);
            else if (r > 200 && r < 300)  pr.loadUserPreset (r - 200);
            else if (r > 300 && r < 400)  pr.saveUserPreset (r - 300);
            else if (r >= 1000) { if      (r >= 1000 && r < 1000 + NgateAudioProcessor::numLearn) pr.learnTarget.store (r - 1000);
                                else if (r >= 1100 && r < 1100 + NgateAudioProcessor::numLearn) pr.ccMap[r - 1100].store (-1);
                                else if (r == 1200) pr.learnTarget.store (-1);
                                else if (r == 1201) { pr.learnTarget.store (-1); pr.resetMidiMap(); }
                                ed.showStatus(); return; }
            ed.showStatus();
        });
}
