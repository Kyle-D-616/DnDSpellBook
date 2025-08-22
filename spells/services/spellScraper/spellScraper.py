from requests_html import HTMLSession
from bs4 import BeautifulSoup
import re
from spells.models import Spells, SpellList
from spells.services.spellSaver import WriteSpellToDataBase


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

    def get_spell_lists(self, spell_body_elements):
        for p in spell_body_elements:
            if p.name == 'p':
                for em in p.find_all('em'):
                    match = re.search(r'\((.*?)\)', em.get_text(strip=True))
                    if match:
                        self.spell_list.update(s.strip() for s in match.group(1).split(","))
        return self.spell_list

class SpellValidator:
    @staticmethod
    def spell_exists(spell_key):
        return Spells.objects.filter(spellKey=spell_key).exists()  # check spellKey

    @staticmethod
    def generate_spell_key(version, spell_name):
        return str(version) + spell_name.replace(" ", "").replace("'", "")
    def extract_from_paragraph(self, p_element):
        for br in p_element.find_all('br'):
            br.replace_with('|')
        parts = p_element.get_text(strip=True).split('|')
        for part in parts:
            self.attributes[f'atr{self.attr_index}'] = part.strip()
            self.attr_index += 1

    def extract_from_list(self, ul_element):
        for item in ul_element.find_all('li'):
            self.attributes[f'atr{self.attr_index}'] = item.get_text(strip=True)
            self.attr_index += 1

    def process_spell_body(self, spell_body_elements):
        for element in spell_body_elements:
            if element.name == 'p':
                self.extract_from_paragraph(element)
            elif element.name == 'ul':
                self.extract_from_list(element)
        return self.attributes


class SpellDataMapper:
    def __init__(self, attributes, version):
        self.attributes = attributes
        self.version = version

    def map_to_spell_fields(self, spell_name, spell_lists):
        # Handle spell level and school
        spell_school = ''
        spell_level = ''
        spell_level_type_text = self.attributes.get('atr2', '')

        if "cantrip" in spell_level_type_text.lower():
            parts = spell_level_type_text.split()
            spell_school = ' '.join(parts[:1])
            spell_level = parts[1]
        else:
            parts = spell_level_type_text.split(' ', 3)
            spell_level = parts[0] + ' ' + parts[1]
            spell_school = parts[2] if len(parts) > 2 else ''

        # Build description text (ignoring spell list lines)
        spell_description = "\n".join(
            self.attributes.get(f'atr{i}', '') for i in range(7, len(self.attributes) + 1)
            if 'Spell Lists' not in self.attributes.get(f'atr{i}', '')
        )

        return {
            'name': spell_name,
            'source': self.attributes.get('atr1', '').replace("Source:", "").strip(),
            'spellLevel': spell_level,
            'spellSchool': spell_school,
            'castingTime': self.attributes.get('atr3', '').replace("Casting Time:", "").strip(),
            'spellRange': self.attributes.get('atr4', '').replace("Range:", "").strip(),
            'components': self.attributes.get('atr5', '').replace("Components:", "").strip(),
            'duration': self.attributes.get('atr6', '').replace("Duration:", "").strip(),
            'description': spell_description,
            'version': str(self.version),
            'spellLists': list(spell_lists)
        }


class SpellScraper:
    def __init__(self, version):
        self.session = HTMLSession()
        self.version = version
        self.spellUrls = []

    def get_spell_urls(self):
        base_url = (
            'https://dnd5e.wikidot.com/spells'
            if self.version == 2014
            else 'http://dnd2024.wikidot.com/spell:all'
        )
        response = self.session.get(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        for table in soup.find_all('table'):
            for url in table.find_all('a'):
                full_url = (
                    'https://dnd5e.wikidot.com' + url.get('href')
                    if self.version == 2014
                    else 'http://dnd2024.wikidot.com' + url.get('href')
                )
                self.spellUrls.append(full_url)

    def process_spells(self):
        for spell_url in self.spellUrls:
            print(f"Processing: {spell_url}")
            response = self.session.get(spell_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            parser = SpellParser(soup)
            spell_name = parser.get_spell_name()
            spell_key = SpellValidator.generate_spell_key(self.version, spell_name)

            if SpellValidator.spell_exists(spell_key):
                print(f"Spell '{spell_name}' already exists, skipping...")
                continue

            spell_body_elements = parser.get_spell_body_elements()
            spell_lists = parser.get_spell_lists(spell_body_elements)

            extractor = AttributeExtractor()
            attributes = extractor.process_spell_body(spell_body_elements)

            mapper = SpellDataMapper(attributes, self.version)
            spell_fields = mapper.map_to_spell_fields(spell_name, spell_lists)

            print(f"Saving Spell: {spell_name}")
            print(f"Mapped Fields: {spell_fields}")
            print("=" * 50)

            saver = WriteSpellToDataBase(spell_fields)
            saver.save_spell_to_database()

