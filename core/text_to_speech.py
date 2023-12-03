import time
from os import listdir, remove

import torch
from datasets import load_dataset
from natsort import natsorted
from pydub import AudioSegment
from scipy.io.wavfile import write as write_wav
from tqdm import tqdm
from transformers import AutoProcessor, BarkModel

MODEL_NAME = "suno/bark"
SPEAKER = "v2/en_speaker_9"
AUDIO_HOME = "./audio"


class VoiceSynthesis:
    def __init__(self, filename: str = '') -> None:
        self.device = 0 if torch.cuda.is_available() else -1
        self.model = BarkModel.from_pretrained(MODEL_NAME).to(self.device)
        self.processor = AutoProcessor.from_pretrained(
            MODEL_NAME)
        self.filename = filename

    def generate_speech(self, text: str) -> str:
        torch.cuda.empty_cache()
        text_split = text.split(" ")
        text_sections = self._chunk_list(
            text.split(" "), len(text_split) // 16)
        for i, text_section in tqdm(enumerate(text_sections), desc="Generating speech segments..."):
            inputs = self.processor(text_section, voice_preset=SPEAKER)
            speech = self.model.generate(**inputs.to(self.device))
            audio = speech[0].cpu().numpy()
            sampling_rate = self.model.generation_config.sample_rate
            self._save_speech(audio, sampling_rate, tmp_number=i)
        return self._merge_speeches()

    def _chunk_list(self, list, n) -> GeneratorExit:
        for i in range(0, len(list), n):
            yield " ".join(list[i:i + n])

    def destroy(self) -> None:
        files = listdir(f"{AUDIO_HOME}/tmp")
        for file in files:
            remove(f"{AUDIO_HOME}/tmp/{file}")

    def _save_speech(self, audio, sampling_rate, tmp_number: int = -1) -> None:
        write_wav(f"{AUDIO_HOME}/tmp/{self.filename}{'_' + str(tmp_number) if tmp_number > -1 else ''}.wav",
                  data=audio.T, rate=sampling_rate)

    def _merge_speeches(self) -> str:
        files = natsorted(listdir(f"{AUDIO_HOME}/tmp"))
        sound = AudioSegment.from_file(
            f"{AUDIO_HOME}/tmp/{files[0]}", format="wav")
        for file in tqdm(files[1:], desc="Merging speeches..."):
            sound += AudioSegment.from_file(
                f"{AUDIO_HOME}/tmp/{file}", format="wav")
            time.sleep(0.5)
        sound.export(
            f"{AUDIO_HOME}/tmp/{files[0].replace('_0', '')}", format="wav")
        return f"{AUDIO_HOME}/tmp/{files[0].replace('_0', '')}"
