import numpy as np

from typing import Dict

import torch
import pyctcdecode

from transformers import (
    Wav2Vec2Processor,
    Wav2Vec2ProcessorWithLM,
    Wav2Vec2ForCTC,
)


class PreTrainedPipeline():

    def __init__(self, model_path: str, language_model_fp: str):
        self.language_model_fp = language_model_fp

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = Wav2Vec2ForCTC.from_pretrained(model_path)
        self.model.to(self.device)

        processor = Wav2Vec2Processor.from_pretrained(model_path)
        self.sampling_rate = processor.feature_extractor.sampling_rate

        vocab = processor.tokenizer.get_vocab()
        sorted_vocab_dict = [(char, ix) for char, ix in sorted(vocab.items(), key=lambda item: item[1])]

        self.decoder = pyctcdecode.build_ctcdecoder(
            labels=[x[0] for x in sorted_vocab_dict],
            kenlm_model_path=self.language_model_fp,
        )

        self.processor_with_lm = Wav2Vec2ProcessorWithLM(
            feature_extractor=processor.feature_extractor,
            tokenizer=processor.tokenizer,
            decoder=self.decoder
        )

    def __call__(self, inputs: np.array) -> Dict[str, str]:
        """
        Args:
            inputs (:obj:`np.array`):
                The raw waveform of audio received. By default at 16KHz.
        Return:
            A :obj:`dict`:. The object return should be liked {"text": "XXX"} containing
            the detected text from the input audio.
        """

        input_values = self.processor_with_lm(
            inputs, return_tensors="pt",
            sampling_rate=self.sampling_rate
        )['input_values']

        input_values = input_values.to(self.device)

        with torch.no_grad():
            # input_values should be a 2D tensor by now. 1st dim represents audio channels.
            model_outs = self.model(input_values)
        logits = model_outs.logits.cpu().detach().numpy()

        text_predicted = self.processor_with_lm.batch_decode(logits)['text']

        return {
            "text": text_predicted
        }
