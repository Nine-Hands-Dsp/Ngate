// genere par tools/make_art.py - ne pas modifier a la main (repere 603.0 x 900.0 = fond 1206 x 1800 px / 2)
#pragma once
#include <juce_graphics/juce_graphics.h>
namespace layout
{
    constexpr float frameW = 603.00f, frameH = 900.00f;   // pedale plein cadre (jacks aux bords gauche / droit)
    const juce::Rectangle<float> boxRect { 20.50f, 0.00f, 565.00f, 900.00f };
    const juce::Point<float> knobPos { 303.00f, 330.00f }; const float capR = 143.60f, knobSprite = 288.50f;   // usure + index (knob_top.png), tourne
    const float dotsR = 174.00f, dotAngle = 133.85f; const int numDots = 31;
    const juce::Point<float> learnPos { 508.08f, 169.04f }, bassPos { 303.00f, 640.00f }; const float btnR = 26.00f, btnCapR = 19.24f;
    const juce::Point<float> togglePos { 303.00f, 538.53f }; const float togS = 75.60f, togR = 21.00f;
    const juce::Point<float> openLedPos { 169.01f, 640.00f }, gateLedPos { 435.66f, 640.00f }; const float ledS = 22.50f;
    const juce::Rectangle<float> glowGreenRect { 99.00f, 570.00f, 140.00f, 140.00f }, glowOrangeRect { 365.50f, 570.00f, 140.00f, 140.00f };
    const juce::Point<float> fsPos { 303.00f, 792.00f }; const float footR = 33.34f, fsS = 167.20f;
    const juce::Rectangle<float> presetRect { 103.00f, 694.00f, 400.00f, 38.00f }, readoutRect { 392.61f, 36.08f, 152.85f, 52.78f }, plateRect { 60.88f, 32.74f, 198.90f, 62.14f };
    const float presetFont = 23.0f, jackY = 391.54f;
    struct Txt { const char* s; int font; float em, track, x, y, rot; juce::uint32 colour; int anchor; };   // police 0 medium, 1 bold, 2 light ; ancrage 0 centre, 1 gauche
    const Txt texts[] = {
        { "NOISE GATE", 0, 11.60f, 5.46f, 62.22f, 105.57f, 0.00f, 0xffec7a2c, 1 },
        { "THRESHOLD", 0, 12.60f, 7.09f, 303.00f, 121.60f, 0.00f, 0xffeaeae7, 0 },
        { "dB", 0, 11.00f, 1.00f, 468.70f, 107.57f, 0.00f, 0xffc4c6c8, 0 },
        { "LEARN", 0, 11.00f, 5.55f, 508.08f, 208.54f, 0.00f, 0xffeaeae7, 0 },
        { "-95", 0, 11.50f, 0.60f, 151.65f, 458.35f, 0.00f, 0xffc4c6c8, 0 },
        { "0", 0, 11.50f, 0.60f, 455.35f, 459.69f, 0.00f, 0xffc4c6c8, 0 },
        { "SOFT", 0, 12.60f, 3.88f, 155.66f, 538.53f, 0.00f, 0xffeaeae7, 0 },
        { "HARD", 0, 12.60f, 4.05f, 448.00f, 538.53f, 0.00f, 0xffeaeae7, 0 },
        { "OPEN", 0, 12.60f, 4.11f, 108.27f, 640.00f, 0.00f, 0xffeaeae7, 0 },
        { "GATE", 0, 12.60f, 4.16f, 499.40f, 640.00f, 0.00f, 0xffeaeae7, 0 },
        { "BASS", 0, 11.00f, 4.28f, 303.00f, 679.50f, 0.00f, 0xffeaeae7, 0 },
        { "OUT", 0, 13.00f, 2.00f, 46.50f, 391.54f, 90.00f, 0xffc4c6c8, 0 },
        { "IN", 0, 13.00f, 2.00f, 559.50f, 391.54f, 90.00f, 0xffc4c6c8, 0 }
    };
    struct Rule { float x0, x1, y, w; };
    const Rule rules[] = { { 193.04f, 265.79f, 640.00f, 1.3f }, { 341.21f, 413.96f, 640.00f, 1.3f }, { 187.66f, 264.00f, 538.53f, 1.3f }, { 342.00f, 414.00f, 538.53f, 1.3f } };
    const juce::Point<float> titlePos { 160.33f, 63.81f }; const float titleEm = 40.19f, titleTrack = 1.20f;   // NGATE en relief
    const juce::Point<float> logoPos { 303.00f, 870.00f }; const float logoW = 160.00f;
}
