# Outil hors plugin : compile le processeur + la fenetre de NGATE sous Linux et exporte des captures PNG (apercu, notice)
cmake_minimum_required(VERSION 3.22)
project(NgateRender VERSION 1.0.0)
set(CMAKE_CXX_STANDARD 17)
add_subdirectory(${JUCE_DIR} JUCE)
set(W ${CMAKE_CURRENT_SOURCE_DIR}/../..)
juce_add_binary_data(NgateData SOURCES
  ${W}/background.png ${W}/knob_top.png ${W}/toggle_strip.png ${W}/led_green_on.png ${W}/led_orange_on.png ${W}/glow_green.png ${W}/glow_orange.png
  ${W}/Poppins-Regular.ttf ${W}/Poppins-Medium.ttf ${W}/Poppins-Bold.ttf ${W}/Poppins-Light.ttf ${W}/NineHandsLogo.svg)
juce_add_console_app(NgateRender PRODUCT_NAME "NgateRender")
target_sources(NgateRender PRIVATE main.cpp ${W}/PluginProcessor.cpp ${W}/PluginEditor.cpp)
target_include_directories(NgateRender PRIVATE ${W})
target_compile_definitions(NgateRender PRIVATE JUCE_WEB_BROWSER=0 JUCE_USE_CURL=0 JUCE_ALSA=0 JUCE_JACK=0
  JUCE_USE_XRANDR=0 JUCE_USE_XINERAMA=0 JUCE_USE_XCURSOR=0 JUCE_USE_XSHM=0 JucePlugin_Name="Ngate" JucePlugin_Build_VST3=0
  JucePlugin_VersionString="2.0.0" JUCE_STANDALONE_APPLICATION=1 JUCE_MODAL_LOOPS_PERMITTED=1)
target_link_libraries(NgateRender PRIVATE NgateData juce::juce_audio_utils juce::juce_recommended_config_flags)
