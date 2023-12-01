from re import compile, sub

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager


class TextScrapper:
    def __init__(self) -> None:
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(service=Service(
            GeckoDriverManager().install()), options=options)
        self.html_tags = compile('<.*?>')

    def get_text(self, url: str) -> str:
        self.driver.get(url)
        body = self.driver.find_element(By.TAG_NAME, 'body')
        return self._sanitize_text(body.text)

    def destroy(self) -> None:
        self.driver.close()

    def _sanitize_text(self, text: str) -> str:
        text = text.lower()
        text = sub(
            r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", " ", text)
        text = sub(' +', ' ', text)
        text = sub('\s+', ' ', sub('\n+', ' ', text.strip()))
        return sub(self.html_tags, '', text)
