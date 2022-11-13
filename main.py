from googlesearch import search
from gtts import gTTS
from huggingface_hub import hf_hub_download
from playsound import playsound
from pipeline import PreTrainedPipeline
from pyowm import OWM
from pyowm.utils import config as cfg
from termcolor import colored
from TTSsynth_loader import synthesizer # importing a synthesizer for our model

import googletrans
import json
import librosa
import os
import random
import speech_recognition
import subprocess
import traceback
import webbrowser
import wikipediaapi

from lang_BE import num2words # Convert numbers to text

HF_HUB_URL = 'ales/wav2vec2-cv-be'
LM_HUB_FP = 'language_model/cv8be_5gram.bin'
MODEL_SAMPLING_RATE = 16_000  # 16kHz

# download Language Model from HF Hub
lm_fp = hf_hub_download(repo_id=HF_HUB_URL, filename=LM_HUB_FP)

# init pipeline
pipeline = PreTrainedPipeline(model_path=HF_HUB_URL, language_model_fp=lm_fp)

class Translation:
    with open('translations.json', 'r', encoding='UTF-8') as file:
        translations = json.load(file)

    def get(self, text: str):
        if text in self.translations:
            return self.translations[text]['be']
        else:
            print(colored('Адбылася памылка падчас пераклада тэксту: {}'.format(text), 'red'))
            return text


class OwnerPerson:
    home_city, home_city_be, name, target_language = '', '', '', ''

def record_and_recognize_audio(*args: tuple):
    with microphone:
        recognized_data = ""

        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        try:
            print(colored("Праслухоўванне...", "red"))
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            play_voice_assistant_speech('Праверце, калі ласка, ці працуе Ваш мікрафон')
            traceback.print_exc()
            return

        try:
            print(colored('Пазнанне маўлення...', 'cyan'))

            inputs = librosa.load('microphone-results.wav', sr=MODEL_SAMPLING_RATE, mono=True)[0]

            # recognize speech
            pipeline_res = pipeline(inputs=inputs)
            recognized_data = pipeline_res['text'][0].lower()  # unpack batch of size 1

        except speech_recognition.UnknownValueError:
            play_voice_assistant_speech('Можаце, калі ласка, паўтарыць Ваш запыт?')

        return recognized_data

      
def play_voice_assistant_speech(text_to_speech):
    # This function play the speech of the voice assistant
    wav = synthesizer.tts(
        text=str(text_to_speech),
    )
    synthesizer.save_wav(wav, 'output.wav')
    playsound('output.wav')

def play_greetings(*args: tuple):
    # Play greetings
    greetings = [
        "Вітаю, {}! Які Ваш план на сёння?".format(person.name),
        "Добрага дня Вам, {}! Як я магу Вам дапамагчы?".format(person.name)
    ]
    play_voice_assistant_speech(greetings[random.randint(0, len(greetings) - 1)])


def play_farewell_and_quit(*args: tuple):
    # Play farewell and end the session
    farewells = [
        "Да сувязі, {}! Добрага Вам дня!".format(person.name),
        "Да сустрэчы, {}!".format(person.name)
    ]
    play_voice_assistant_speech(farewells[random.randint(0, len(farewells) - 1)])
    quit()


def word_meaning(*args: tuple):
    # Open the tab with the results of searching words from slounik.org in browser
    if not args[0]: return
    search_term = " ".join(args[0])
    url = 'https://slounik.org/search?dict=&search=' + search_term
    webbrowser.get().open(url)

    play_voice_assistant_speech("Вось што мне здалося знайсці па запыту {} ў энцыклапедыі Слоўнік".format(search_term))


def search_for_term_on_google(*args: tuple):
    # Search your query in Google and visit the links on the first page of searching
    if not args[0]: return
    search_term = " ".join(args[0])

    url = "https://google.com/search?q=" + search_term
    webbrowser.get().open(url)

    search_results = []
    try:
        for _ in search(search_term, lang='be'):
            search_results.append(_)
            webbrowser.get().open(_)

    except:
        play_voice_assistant_speech("Здаецца, адбылася памылка. Праглядзіце, калі ласка, логі для дадатковай інфармацыі")
        traceback.print_exc()
        return

    print(search_results)
    play_voice_assistant_speech("Вось што мне здалося знайсці па запыту {} у гугле".format(search_term))


def search_for_video_on_youtube(*args: tuple):
    # Open a tab with the results of searching on YouTube
    if not args[0]: return
    search_term = " ".join(args[0])
    url = "https://www.youtube.com/results?search_query=" + search_term
    webbrowser.get().open(url)
    play_voice_assistant_speech("Вось што мне здалося знайсці па запыту {} у ютубе".format(search_term))


def search_for_definition_on_wikipedia(*args: tuple):
    # Search in the Belarusian Wikipedia
    if not args[0]: return

    search_term = " ".join(args[0])

    wiki = wikipediaapi.Wikipedia('be')

    wiki_page = wiki.page(search_term)
    try:
        if wiki_page.exists():
            play_voice_assistant_speech("Вось што мне здалося знайсці па запыту {} ў Вікіпедыі".format(search_term))
            webbrowser.get().open(wiki_page.fullurl)

            play_voice_assistant_speech(wiki_page.summary.split(".")[:2])
        else:
            play_voice_assistant_speech(translator.get(
                "На жаль, па запыту {} нічога не здалося знайсці ў Вікіпедыі, але вось што мне здалося знайсці ў гугле").format(search_term))
            url = "https://google.com/search?q=" + search_term
            webbrowser.get().open(url)

    except:
        play_voice_assistant_speech("Здаецца, адбылася памылка. Праглядзіце, калі ласка, логі для дадатковай інфармацыі")
        traceback.print_exc()
        return


def get_translation(*args: tuple):
    # Get translation from the Belarusian to any another one language
    if not args[0]: return

    search_term = ' '.join(args[0])
    google_translator = googletrans.Translator()

    try:
        translation_result = google_translator.translate(search_term,
                                                         src='be',
                                                         dest=person.target_language)

        tts = gTTS(translation_result.text)
        tts.save('peraklad.mp3')

        play_voice_assistant_speech("Па-ангельску {} будзе як".format(search_term))
        playsound('peraklad.mp3')


    except:
        play_voice_assistant_speech("Здаецца, адбылася памылка. Праглядзіце, калі ласка, логі для дадатковай інфармацыі")
        traceback.print_exc()

def get_weather_forecast(*args: tuple):
    # Get the weather forecast from openweathermap.org (API key is required)
    if args[0]:
        city_name = args[0][0]
    else:
        city_name = person.home_city

    try:
        config = cfg.get_default_config()
        config['language'] = 'be'
        open_weather_map = OWM('YOUR_API_KEY', config) # Here you have to insert your API key

        weather_manager = open_weather_map.weather_manager()
        observation = weather_manager.weather_at_place(city_name)
        weather = observation.weather


    except:
        play_voice_assistant_speech("Здаецца, адбылася памылка. Праглядзіце, калі ласка, логі для дадатковай інфармацыі")
        traceback.print_exc()
        return

    status = weather.detailed_status
    temperature = weather.temperature('celsius')["temp"]
    wind_speed = int(weather.wind()["speed"])
    pressure = int(weather.pressure["press"] / 1.333)

    city_name = person.home_city_be

    print(colored("Weather in " + city_name +
                  ":\n * Status: " + status +
                  "\n * Wind speed (m/sec): " + str(wind_speed) +
                  "\n * Temperature (Celsius): " + str(temperature) +
                  "\n * Pressure (mm Hg): " + str(pressure), "yellow"))

    temperature = num2words(str(int(weather.temperature('celsius')["temp"])))
    wind_speed = num2words(str(int(weather.wind()["speed"])))
    pressure = num2words(str(int(weather.pressure["press"] / 1.333)))

    play_voice_assistant_speech("Зараз {0} у населеным пункту {1}".format(status, city_name))
    play_voice_assistant_speech("Тэмпература складае {} градусаў цэльсія".format(str(temperature)))
    play_voice_assistant_speech("Хуткасць паветру дасягае {} метраў за секунду".format(str(wind_speed)))
    play_voice_assistant_speech("Атмасферны ціск складае {} міліметраў ртутнага стаўба".format(str(pressure)))

def run_person_through_social_nets_databases(*args: tuple):
    
    # Looking for information about a person using their name and surname in such social networks as VK and Facebook
    
    if not args[0]: return

    google_search_term = " ".join(args[0])
    vk_search_term = "_".join(args[0])
    fb_search_term = "-".join(args[0])

    url = "https://google.com/search?q=" + google_search_term + " site: vk.com"
    webbrowser.get().open(url)

    url = "https://google.com/search?q=" + google_search_term + " site: facebook.com"
    webbrowser.get().open(url)

    vk_url = "https://vk.com/people/" + vk_search_term
    webbrowser.get().open(vk_url)

    fb_url = "https://www.facebook.com/public/" + fb_search_term
    webbrowser.get().open(fb_url)

    play_voice_assistant_speech("Вось, што мне здалося знайсці па запыту {} у сацыяльных сетках".format(google_search_term))


def toss_coin(*args: tuple):
    flips_count, heads, tails = 3, 0, 0

    for flip in range(flips_count):
        if random.randint(0, 1) == 0:
            heads += 1

    tails = flips_count - heads
    winner = "Выйграла рэшка" if tails > heads else "Выйграў арол"
    play_voice_assistant_speech(winner)


def thanks_func(*args: tuple):
    if not args[0]: return
    thank_s = [
        "Заўсёды да Вашых паслуг, {}".format(person.name),
        "Рады Вам дапамагчы, {}".format(person.name),
    ]
    play_voice_assistant_speech(thank_s[random.randint(0, len(thank_s) - 1)])


def execute_command_with_name(command_name: str, *args: list):
    for key in commands.keys():
        if command_name in key:
            commands[key](*args)
        else:
            pass

def shutdown(*args: tuple):
    play_voice_assistant_speech(('Выключаю Вашу прыладу, да сустрэчы, {}').format(person.name))
    os.system("poweroff")

def restart(*args: tuple):
    play_voice_assistant_speech(('Перазапускаю Вашу прыладу, {}').format(person.name))
    os.system("restart")

def logout(*args: tuple):
    play_voice_assistant_speech(('Адбываецца выхад з сістэмы, да сувязі, {}').format(person.name))
    os.system("gnome-session-quit --no-prompt")


commands = {
    ("надвор\'е", "_"): get_weather_forecast,
    ("выключэнне", "_"): shutdown,
    ("дзякуй", "малайчына"): thanks_func,
    ("перазапуск", "_"): restart,
    ("вітаю", "прывітанне", "прывіт", "добрай", "дзень добры", "добрага дня", "здароў", "добрага здароўя") : play_greetings,
    ("бывай", "да пабачэння", "да сустрэчы", "стоп"): play_farewell_and_quit,
    ("выхад з сістэмы", "выхад", "завяршэнне сеансу"): logout,
    ("пошук", "знайдзі", "гугл"): search_for_term_on_google,
    ("відэа", "глядзець"): search_for_video_on_youtube,
    ("вікіпедыя", "вікіпэдыя"): search_for_definition_on_wikipedia,
    ("пераклад", "перакладзі"): get_translation,
    ("дадзеныя", "прабіць", "прабей"): run_person_through_social_nets_databases,
    ("манета", "падкінь"): toss_coin,
    ("тлумачэнне", "патлумач слова", "патлумачце"): word_meaning,
}

if __name__ == "__main__":

    # Initialization of speech recognition and input tools #
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()

    person = OwnerPerson()
    person.name = '' # Your name
    person.home_city = "Minsk, Belarus" # Your location
    person.home_city_be = 'Мінск, Беларусь' # Your location in Belarusian
    person.target_language = 'en' # A language for which you want to get translations

    translator = Translation()

    while True:
        voice_input = record_and_recognize_audio()
        os.remove("microphone-results.wav")
        print(colored(voice_input, 'blue'))
        print()

        voice_input = voice_input.split(" ")
        command = voice_input[0]
        command_options = [str(input_part) for input_part in voice_input[1:len(voice_input)]]
        execute_command_with_name(command, command_options)
