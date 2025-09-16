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

    def get_spell_lists(self, spell_body_elements):
        # Define what are actual class names vs other terms
        valid_classes = {
            'artificer', 'bard', 'cleric', 'druid', 'paladin', 'ranger', 
            'sorcerer', 'warlock', 'wizard'
        }
        
        for element in spell_body_elements:
            if element.name == 'p':
                element_text = element.get_text()
                
                # 2024 format: Level X School (Class1, Class2)
                # Look in em tags for parentheses with class names
                # BUT only if it starts with "Level" (not "1st-level" which is 2014 format)
                for em in element.find_all('em'):
                    em_text = em.get_text(strip=True)
                    # Only process if it starts with "Level" (2024 format)
                    if em_text.startswith('Level'):
                        paren_match = re.search(r'\(([^)]+)\)', em_text)
                        if paren_match:
                            classes_text = paren_match.group(1)
                            # Split by comma and clean up
                            classes = [cls.strip() for cls in classes_text.split(',')]
                            for cls in classes:
                                # Only add if it's a valid class name
                                if cls.lower() in valid_classes:
                                    self.spell_list.add(cls)
                
                # 2014 format: "Spell Lists." followed by links or text
                if 'Spell Lists' in element_text:
                    # Extract text after "Spell Lists."
                    spell_lists_text = element_text.split('Spell Lists.')[-1].strip()
                    # Get the link text which contains the actual class names
                    links = element.find_all('a')
                    for link in links:
                        class_name = link.get_text(strip=True)
                        if class_name.lower() in valid_classes:
                            self.spell_list.add(class_name)
                    
                    # Fallback: parse the text directly if no links
                    if not links and spell_lists_text:
                        # Split by common separators and clean
                        for separator in [',', ';', ' and ', ' & ']:
                            spell_lists_text = spell_lists_text.replace(separator, ',')
                        
                        for spell_list in spell_lists_text.split(','):
                            cleaned = spell_list.strip(' .,')
                            if cleaned.lower() in valid_classes:
                                self.spell_list.add(cleaned)
        
        return self.spell_list


class SpellValidator:
    @staticmethod
    def spell_exists(spell_key):
        return Spells.objects.filter(spellKey=spell_key).exists()

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
            # Format: "Conjuration cantrip" or "Conjuration cantrip (ritual)"
            # Remove anything in parentheses first
            clean_text = re.sub(r'\s*\([^)]*\)', '', spell_level_type_text).strip()
            parts = clean_text.split()
            if len(parts) >= 2:
                spell_school = parts[0]  # "Conjuration"
                spell_level = "Cantrip"
            else:
                spell_level = "Cantrip"
                spell_school = clean_text if clean_text != "cantrip" else ''
        elif spell_level_type_text.startswith('Level'):
            # 2024 format: "Level 1 Abjuration (Ranger, Wizard)"
            # Remove anything in parentheses first
            clean_text = re.sub(r'\s*\([^)]*\)', '', spell_level_type_text).strip()
            parts = clean_text.split()
            if len(parts) >= 3:
                spell_level = f"{parts[1]}{self._get_ordinal_suffix(parts[1])}-level"  # "1st-level"
                spell_school = ' '.join(parts[2:])  # "Abjuration"
        else:
            # 2014 format: "1st-level divination" or "2nd-level abjuration (ritual)"
            # Remove anything in parentheses first
            clean_text = re.sub(r'\s*\([^)]*\)', '', spell_level_type_text).strip()
            parts = clean_text.split()
            
            # Find where "-level" appears
            level_part = ""
            school_parts = []
            found_level = False
            
            for part in parts:
                if "-level" in part:
                    level_part = part
                    found_level = True
                elif not found_level:
                    level_part += (" " + part if level_part else part)
                else:
                    school_parts.append(part)
            
            if found_level:
                spell_level = level_part
                spell_school = ' '.join(school_parts)
            else:
                # Fallback
                spell_level = spell_level_type_text
                spell_school = ''
    
    def _get_ordinal_suffix(self, number_str):
        """Convert number to ordinal suffix (1->st, 2->nd, 3->rd, etc)"""
        try:
            num = int(number_str)
            if 10 <= num % 100 <= 20:
                return "th"
            else:
                return {1: "st", 2: "nd", 3: "rd"}.get(num % 10, "th")
        except:
            return "th"

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
    def __init__(self, version, database_writer_class=None):
        self.session = HTMLSession()
        self.version = version
        self.spellUrls = []
        self.database_writer_class = database_writer_class

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

            saver = self.database_writer_class(spell_fields)
            saver.save_spell_to_database()
