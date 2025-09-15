from django.core.management.base import BaseCommand
from spells.services.spellScraper.spellScraper import SpellScraper
from spells.services.spellSaver import WriteSpellToDataBase

class Command(BaseCommand):
    help = "Scrape spells from 2014 or 2024 version and save them to the database."
    
    def handle(self, *args, **options):
        while True:
            version_input = input("Enter spell version (2014 or 2024): ").strip()
            if version_input in ["2014", "2024"]:
                version = int(version_input)
                break
            print("Invalid version. Please enter '2014' or '2024'.")
        
        self.stdout.write(self.style.NOTICE(f"Starting spell scrape for version {version}..."))
        
        # Inject the database writer dependency
        scraper = SpellScraper(version=version, database_writer_class=WriteSpellToDataBase)
        scraper.get_spell_urls()
        
        if not scraper.spellUrls:
            self.stdout.write(self.style.ERROR("No spell URLs found. Check your scraper."))
            return
        
        # Just call process_spells once - it handles all URLs internally
        scraper.process_spells()
