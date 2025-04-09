import os
import django
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from spells.models import Spell

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DnDSpellBook.settings")
django.setup()

class Command(BaseCommand):
    help = 'Fetches spells and updates the database'

    def handle(self, *args, **kwargs):
        session = HTMLSession()
        baseUrl = 'https://dnd5e.wikidot.com/spells'
        urlResponse = session.get(baseUrl)

        soup = BeautifulSoup(urlResponse.content, 'html.parser')
        table = soup.find('div', {'class': 'yui-content'})
        spellUrls = []
        for url in table.find_all('a'):
            spellUrls.append('https://dnd5e.wikidot.com' + url.get('href'))

        for spellUrl in spellUrls:
            urlResponse = session.get(spellUrl)
            soup = BeautifulSoup(urlResponse.content, 'html.parser')

            # Spell name
            spellDiv = soup.find('div', {'class': 'page-title page-header'})
            spellName = spellDiv.find('span').get_text(strip=True)

            # Check if the spell already exists in the database
            if Spell.objects.filter(name=spellName).exists():
                self.stdout.write(self.style.SUCCESS(f"Spell '{spellName}' already exists, skipping..."))
                continue  # Skip to the next spell if it already exists

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
            spell_lists = ""
            for p in spellBody:
                if p.name == 'p' and 'Spell Lists' in p.get_text():
                    spell_lists = p.get_text(strip=True)

            # Create the description (excluding spell lists)
            spell_description = "\n".join(
                attributes.get(f'atr{i}', '') for i in range(7, attr_index) if 'Spell Lists' not in attributes.get(f'atr{i}', '')
            )

            # Convert attributes dict into structured fields
            spell_source = attributes.get('atr1', '')
            spell_level  = attributes.get('atr2', '')
            casting_time = attributes.get('atr3', '')
            spell_range  = attributes.get('atr4', '')
            components   = attributes.get('atr5', '')
            duration     = attributes.get('atr6', '')

            # Create or update the spell
            spell = Spell(
                name=spellName,
                source=spell_source,
                spellLevelType=spell_level,
                castingTime=casting_time,
                spellRange=spell_range,
                components=components,
                duration=duration,
                description=spell_description,
                spellList=spell_lists
            )

            # Save the spell to the database
            spell.save()
            self.stdout.write(self.style.SUCCESS(f"Successfully added spell '{spellName}'"))
        
        self.stdout.write(self.style.SUCCESS('Successfully updated the database with new spells'))
