import os
import sys
import django

#append the system path so i can call from root
sys.path.append('/home/trinity/repos/DnDSpellBook')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DnDSpellBook.settings")
django.setup()

from spells.services.spellScraper.spellScraper import SpellScraper

scraper = SpellScraper(2024)
scraper.getSpellUrls('http://dnd2024.wikidot.com/spell:')
scraper.getSpellData(scraper.spellUrls)
