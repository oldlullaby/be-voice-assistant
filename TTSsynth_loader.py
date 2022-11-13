from TTS.utils.synthesizer import Synthesizer
from TTS.utils.manage import ModelManager

MODELS = {}

manager = ModelManager()

model_path = '' # The directory to the model
config_path = '' # The directory to the config of the model

synthesizer = Synthesizer(
        model_path,
        config_path,
        use_cuda=True,
    )
