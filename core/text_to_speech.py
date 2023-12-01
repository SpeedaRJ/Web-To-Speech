import time
from os import listdir, remove

import soundfile as sf
import torch
from datasets import load_dataset
from natsort import natsorted
from pydub import AudioSegment
from tqdm import tqdm
from transformers import pipeline

MODEL_NAME = "microsoft/speecht5_tts"
SPEAKER = 7306
AUDIO_HOME = "./audio"


class VoiceSynthesis:
    def __init__(self, filename: str = '') -> None:
        self.synthesiser = pipeline(
            "text-to-speech", "microsoft/speecht5_tts", device=0 if torch.cuda.is_available() else -1)
        self.embeddings_dataset = load_dataset(
            "Matthijs/cmu-arctic-xvectors", split="validation")
        self.speaker_embeddings = torch.tensor(
            self.embeddings_dataset[SPEAKER]["xvector"]).unsqueeze(0)
        self.filename = filename

    def generate_speech(self, text: str) -> str:
        torch.cuda.empty_cache()
        text_split = text.split(" ")
        text_sections = self._chunk_list(
            text.split(" "), len(text_split) // 16)
        for i, text_section in enumerate(text_sections):
            speech = self.synthesiser(
                text_section, forward_params={"speaker_embeddings": self.speaker_embeddings})
            self._save_speech(speech["audio"], speech["sampling_rate"],
                              tmp_number=i)
        return self._merge_speeches()

    def _chunk_list(self, list, n) -> GeneratorExit:
        for i in range(0, len(list), n):
            yield " ".join(list[i:i + n])

    def destroy(self) -> None:
        files = listdir(f"{AUDIO_HOME}/tmp")
        for file in files:
            remove(f"{AUDIO_HOME}/tmp/{file}")

    def _save_speech(self, audio, sampling_rate, tmp_number: int = -1) -> None:
        sf.write(f"{AUDIO_HOME}/tmp/{self.filename}{'_' + str(tmp_number) if tmp_number > -1 else ''}.wav",
                 audio, samplerate=sampling_rate)

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
