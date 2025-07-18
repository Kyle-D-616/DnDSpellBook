import os
import django
from django.core.management.base import BaseCommand
from spells.models import Spell2014, SpellList2014

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DnDSpellBook.settings")
django.setup()

class Command(BaseCommand):
    help = 'Fetches spells and updates the database'

    def handle(self, *args, **kwargs):
        session = HTMLSession()
        version = int(input("Which version: [1] 2014, [2] 2024"))
               urlResponse = session.get(baseUrl)

        for spellUrl in spellUrls:
           # Spell body
            spellBodyDiv = soup.find('div', {'id': 'page-content'})
            spellBody = spellBodyDiv.find_all(['p', 'ul'])  # Now include <ul> elements

            attributes = {}
            attr_index = 1

            # Process each element in spell body
            for p in spellBody:
                if p.name == 'p':  # If it's a <p> tag, process it as a paragraph
                    # Replace <br> tags with a unique placeholder
                    for br in p.find_all('br'):
                        br.replace_with('|')

                    # Split text by the placeholder
                    parts = p.get_text(strip=True).split('|')

                    # Save each part as an attribute
                    for part in parts:
                        attributes[f'atr{attr_index}'] = part.strip()
                        attr_index += 1

                elif p.name == 'ul':  # If it's a <ul> tag, process list items
                    list_items = p.find_all('li')
                    for item in list_items:
                        attributes[f'atr{attr_index}'] = item.get_text(strip=True)
                        attr_index += 1

            # Extract "Spell Lists" separately
            spell_lists = set()
            for p in spellBody:
                if p.name == 'p' and 'Spell Lists' in p.get_text():
                    text = p.get_text(strip=True).replace("Spell Lists.", "").replace("Spell Lists:","").replace(" (Optional)", "")
                    spell_lists.update(s.strip() for s in text.split(","))

            #Extract spell level and spell type
            spell_school = ''
            spell_level = ''
            spellLevelTypeText = attributes.get('atr2', '')
            if "cantrip" in spellLevelTypeText.lower():
                parts = spellLevelTypeText.split()
                spell_school = ' '.join(parts[:-1])
                spell_level = parts[-1]
            else:
                parts = spellLevelTypeText.split(' ', 1)
                spell_level = parts[0]
                spell_school = parts[1] if len(parts) > 1 else ''
            #Create the description (excluding spell lists)
            spell_description = "\n".join(
                attributes.get(f'atr{i}', '') for i in range(7, attr_index) if 'Spell Lists' not in attributes.get(f'atr{i}', '')
            )

            # Convert attributes dict into structured fields
            spell_source = attributes.get('atr1', '').replace("Source:", "").strip()
            casting_time = attributes.get('atr3', '').replace("Casting Time:", "").strip()
            spell_range  = attributes.get('atr4', '').replace("Range:","").strip()
            components   = attributes.get('atr5', '').replace("Components:","").strip()
            duration     = attributes.get('atr6', '').replace("Duration:","").strip()

            # create or update the spell
            spell = Spell2014(
                name=spellName,
                source=spell_source,
                spellLevel=spell_level,
                spellSchool=spell_school,
                castingTime=casting_time,
                spellRange=spell_range,
                components=components,
                duration=duration,
                description=spell_description,
            )
            #print(vars(spell))
            # save the spell to the database
            spell.save()

            list_objs = []
            for list_name in spell_lists:
                list_name = list_name.strip()
                if not list_name:
                    continue
                spell_list_obj, _ = SpellList2014.objects.get_or_create(name=list_name)
                list_objs.append(spell_list_obj)

            spell.spellList.set(list_objs)

            self.stdout.write(self.style.SUCCESS(f"successfully added spell '{spellName}'"))

        self.stdout.write(self.style.SUCCESS('successfully updated the database with new spells'))
