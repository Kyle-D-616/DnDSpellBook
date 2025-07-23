from requests_html import HTMLSession
from bs4 import BeautifulSoup
import re
from spells.models import Spells, SpellList


class SpellParser:
    def __init__(self, soup):
        self.soup = soup
        self.spell_list = set()

    def get_spell_name(self):
        spell_div = self.soup.find('div', {'class': 'page-title page-header'})
        return spell_div.find('span').get_text(strip=True)

    def get_spell_body_elements(self):
        spell_body_div = self.soup.find('div', {'id': 'page-content'})
        return spell_body_div.find_all(['p', 'ul'])

    def get_spell_lists(self, spell_body_div):
        for p in spell_body_div:
            if p.name == 'p':
                for em in p.find_all('em'):
                    match = re.search(r'\((.*?)\)', em.get_text(strip=True))
                    if match:
                        self.spell_lists.update(s.strip() for s in match.group(1).split(","))


class SpellValidator:
    @staticmethod
    def spell_exists(spell_key):
        return Spells.objects.filter(name=spell_key).exists()

    @staticmethod
    def generate_spell_key(version, spell_name):
        return str(version) + spell_name.replace(" ", "").replace("'", "")


class AttributeExtractor:
    def __init__(self):
        self.attributes = {}
        self.attr_index = 1

    def extract_from_paragraph(self, p_element):
        for br in p_element.find_all('br'):
            br.replace_with('|')

        parts = p_element.get_text(strip=True).split('|')

        for part in parts:
            self.attributes[f'atr{self.attr_index}'] = part.strip()
            self.attr_index += 1

    def extract_from_list(self, ul_element):
        list_items = ul_element.find_all('li')
        for item in list_items:
            self.attributes[f'atr{self.attr_index}'] = item.get_text(strip=True)
            self.attr_index += 1

    def process_spell_body(self, spell_body_elements):
        for element in spell_body_elements:
            if element.name == 'p':
                self.extract_from_paragraph(element)
            elif element.name == 'ul':
                self.extract_from_list(element)

        return self.attributes


class SpellScraper:

    def __init__(self, version):
        self.session = HTMLSession()
        self.spellUrls = []
        self.version = version

    def getSpellUrls(self, baseUrl):
        if self.version == 2014:
            baseUrl = 'https://dnd5e.wikidot.com/spells'
        else:
            baseUrl = 'http://dnd2024.wikidot.com/spell:all'
        response = self.session.get(baseUrl)
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table')
        for table in tables:
            for url in table.find_all('a'):
                if self.version == 2014:
                    self.spellUrls.append('https://dnd5e.wikidot.com' + url.get('href'))
                else:
                    self.spellUrls.append('http://dnd2024.wikidot.com' + url.get('href'))

    def getSpellData(self, spellUrls):
        for spellUrl in self.spellUrls:
            response = self.session.get(spellUrl)
            soup = BeautifulSoup(response.content, 'html.parser')

            parser = SpellParser(soup)
            spell_name = parser.get_spell_name()
            spell_key = SpellValidator.generate_spell_key(self.version, spell_name)

            if SpellValidator.spell_exists(spell_key):
                print(f"Spell '{spell_name}' already exists, skipping...")
                continue

            spell_body_elements = parser.get_spell_body_elements()
            extractor = AttributeExtractor()
            attributes = extractor.process_spell_body(spell_body_elements)
            
            print(f"Spell: {spell_name}")
            print(f"Spell Key: {spell_key}")
            print(f"Attributes: {attributes}")
            print("=" * 50)

            # TODO: Save spell data to database using attributes
