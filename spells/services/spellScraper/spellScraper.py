from requests_html import HTMLSession
from bs4 import BeautifulSoup

class SpellScraper:

    def __init__(self):
        self.session = HTMLSession()
        self.spellUrls = []

    def getSpellUrls(self,baseUrl):
