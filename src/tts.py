"""Local voice-over synthesis.

English : Kokoro-82M (Apache-2.0) via kokoro-onnx, male voice.
Malay   : facebook/mms-tts-zlm (VITS, CC-BY-NC-4.0) via transformers.

Both return mono float32 audio at 24 kHz.
"""
import numpy as np

SR = 24000


def _resample(y, sr_in, sr_out=SR):
    if sr_in == sr_out:
        return y.astype(np.float32)
    import librosa
    return librosa.resample(y.astype(np.float32), orig_sr=sr_in, target_sr=sr_out)


class EnglishTTS:
    def __init__(self, models_dir, voice='am_michael', speed=1.0):
        from kokoro_onnx import Kokoro
        self.k = Kokoro(f'{models_dir}/kokoro/kokoro-v1.0.onnx', f'{models_dir}/kokoro/voices-v1.0.bin')
        self.voice, self.speed = voice, speed

    def synth(self, text, speed=None, seed=0):
        y, sr = self.k.create(text, voice=self.voice, speed=speed or self.speed, lang='en-us')
        return _resample(y, sr)


class MalayTTS:
    def __init__(self, models_dir, speed=1.0):
        import torch
        from transformers import VitsModel, AutoTokenizer
        torch.set_num_threads(4)
        self.torch = torch
        self.model = VitsModel.from_pretrained(f'{models_dir}/mms-zlm').eval()
        self.tok = AutoTokenizer.from_pretrained(f'{models_dir}/mms-zlm')
        self.speed = speed

    def synth(self, text, speed=None, seed=0):
        torch = self.torch
        torch.manual_seed(seed)
        self.model.speaking_rate = speed or self.speed
        self.model.noise_scale = 0.6
        inputs = self.tok(text.lower(), return_tensors='pt')
        with torch.no_grad():
            y = self.model(**inputs).waveform[0].numpy()
        return _resample(y, self.model.config.sampling_rate)
