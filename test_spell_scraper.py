#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DnDSpellBook.settings')
django.setup()

from spells.services.spellScraper.spellScraper import SpellScraper

def test_spell_scraper():
    print("Testing SpellScraper...")
    
    # Create scraper instance
    version = int(input("Which version?"))
    if version == 2014:
        baseUrl = 'https://dnd5e.wikidot.com/spells:'
    else:
        baseUrl = 'http://dnd2024.wikidot.com/spell:'
    scraper = SpellScraper(version)

    
    # Get all spell URLs
    print("Getting all spell URLs...")
    scraper.getSpellUrls('https://dnd5e.wikidot.com/spells')
    #print(f"Found {len(scraper.spellUrls)} spell URLs")
    
    # Call getSpellData to process all URLs
    print("Processing all spells...")
    scraper.getSpellData()
    print("Test completed!")

if __name__ == "__main__":
    test_spell_scraper()
