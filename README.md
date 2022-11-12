# Belarusian Voice Assistant
The first voice assistant that speaks the Belarusian Language

v0.0.0: It's a first demo version of this project. Graphic design, new functions and an improved voice model are currently being developed for the assistant and will be definitely in the next release of this project.


# Introduction
It's the voice assistant that communicate with people using the Belarusian Language. It uses the Belarusian SST (speech-to-text) && TTS (text-to-speech) models that works fully in offline-mode to recognize and generate words in this language.

The idea has come to me from the Habr article by [EnjiRouz](https://github.com/EnjiRouz) where she describes how to create your own voice assistant using Python. After reading I have catched fire with desire to try to realise my old stunning ideas connected with the popularization of the Belarusian language.
What it resulted in, you see the result before your eyes.

What does this voice assistant do:

> - recognizes and synthesizes speech in offline mode (without internet access)</br>
> - reports the weather forecast anywhere in the world</br>
> - searchs for definitions in Wikipedia with further reading of the first two sentences</br>
> - searchs for a person by first and last name in social networks VK and Facebook</br>
> - makes a search query in the Google search engine and opens the list of results and the results of this query themselves</br>
> - makes a video search query in the YouTube system and opens the list of results of this query</br>
> - translates from the belarusian language into the other language</br>
> - flips a coin</br>
> - and a bit more...</br>

First of all, you need to install all necessary libraries. It can be done by the command
```pip install requirements.txt```

This project uses the OpenWeatherMap service to get the weather forecast data. This library requires an API key. You can get an API key and get acquainted with the documentation after registration [here](https://pyowm.readthedocs.io/en/latest/v3/code-recipes.html).

# Gratitude
I want to express my appreciation to such creditable people as [yks72p](https://github.com/yks72p/stt_be) (for the STT model) and [alex73](https://github.com/alex73/belarusian-tts) (for the resources that help me to create a TTS model)
