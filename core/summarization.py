import re

import torch
from transformers import logging, pipeline

logging.set_verbosity_error()


SUMMARIZE_MODEL_NAME = "pszemraj/led-base-book-summary"
TITLE_GENERATION_MODEL_NAME = "czearing/article-title-generator"


class TextSummarizer:
    def __init__(self, max_length: int, min_length: int) -> None:
        self.summarizer = pipeline(
            "summarization", model=SUMMARIZE_MODEL_NAME, device=0 if torch.cuda.is_available() else -1)
        self.title_generator = pipeline(
            "text2text-generation", model=TITLE_GENERATION_MODEL_NAME, device=0 if torch.cuda.is_available() else -1)
        self.max_length = max_length
        self.min_length = min_length
        self.html_tags = re.compile('<.*?>')

    def summarize(self, text: str) -> str:
        torch.cuda.empty_cache()
        summary = self.summarizer(text, 
                                  max_length=self.max_length,
                                  min_length=self.min_length, 
                                  do_sample=False, 
                                  truncation=True, 
                                  no_repeat_ngram_size=3,
                                  encoder_no_repeat_ngram_size=3,
                                  repetition_penalty=3.5,
                                  num_beams=4,
                                  early_stopping=True)[0]["summary_text"]
        return re.sub(self.html_tags, '', summary)

    def generate_title(self, text: str) -> str:
        torch.cuda.empty_cache()
        title = self.title_generator(text)[0]['generated_text']
        return re.sub(self.html_tags, '', title)
