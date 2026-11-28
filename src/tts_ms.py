"""Bahasa Melayu voice-over generator (local, CPU).

Uses mesolitica/Malaysian-TTS-0.6B-v1 (Qwen3-based speech LM) + DistilCodec decoder
(https://github.com/mesolitica/DistilCodec, imported from a local checkout).
Usage: python tts_ms.py <models_dir> <distilcodec_src_dir> <out.wav> <speaker> "<text>" [seed]
"""
import re
import sys

import numpy as np
import torch

SR = 24000
torch.set_num_threads(4)


def _cpu_only():
    # DistilCodec hardcodes .cuda(); make those calls no-ops so it runs on CPU.
    torch.Tensor.cuda = lambda self, *a, **k: self
    torch.nn.Module.cuda = lambda self, *a, **k: self


class MalayTTS:
    def __init__(self, models_dir, codec_src):
        _cpu_only()
        sys.path.insert(0, codec_src)
        import distilcodec.distil_codec as dc
        from transformers import AutoTokenizer, AutoModelForCausalLM

        orig_device = torch.device

        class _Dev:  # map 'cuda:N' -> cpu during codec construction
            def __new__(cls, *a, **k):
                if a and isinstance(a[0], str) and a[0].startswith('cuda'):
                    return orig_device('cpu')
                return orig_device(*a, **k)

        dc.torch.device = _Dev
        try:
            self.codec = dc.DistilCodec.from_pretrained(
                config_path=f'{models_dir}/codec/model_config.json',
                model_path=f'{models_dir}/codec/g_00204000',
                use_generator=True, is_debug=False).eval()
        finally:
            dc.torch.device = orig_device
        self.tok = AutoTokenizer.from_pretrained(f'{models_dir}/mtts')
        self.model = AutoModelForCausalLM.from_pretrained(
            f'{models_dir}/mtts', dtype=torch.float32).eval()

    @torch.no_grad()
    def synth(self, text, speaker='husein', seed=0, temperature=0.7):
        torch.manual_seed(seed)
        prompt = f'<|im_start|>{speaker}: {text}<|speech_start|>'
        inputs = self.tok(prompt, return_tensors='pt', add_special_tokens=False)
        out = self.model.generate(**inputs, max_new_tokens=1024, temperature=temperature,
                                  do_sample=True, repetition_penalty=1.1)
        speech = self.tok.decode(out[0]).split('<|speech_start|>')[-1].replace('<|endoftext|>', '')
        codes = list(map(int, re.findall(r'speech_(\d+)', speech)))
        y = self.codec.decode_from_codes(codes, minus_token_offset=False)
        return y[0, 0].float().cpu().numpy().astype(np.float32)


if __name__ == '__main__':
    import time
    import soundfile as sf
    models, src, out, spk, text = sys.argv[1:6]
    seed = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    t = time.time()
    tts = MalayTTS(models, src)
    print('load', round(time.time() - t, 1)); t = time.time()
    y = tts.synth(text, spk, seed)
    print('synth', round(time.time() - t, 1), 'dur', round(len(y) / SR, 2))
    sf.write(out, y, SR)
