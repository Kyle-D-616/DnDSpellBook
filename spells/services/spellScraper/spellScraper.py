from requests_html import HTMLSession
from bs4 import BeautifulSoup

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
            # Spell name
            spellDiv = soup.find('div', {'class': 'page-title page-header'})
            spellName = spellDiv.find('span').get_text(strip=True)
            spellKey = str(self.version) + spellName.replace(" ", "")
            print(spellKey)
            #spell keys are returning, need to take symbols out of key tho, ' ( ) and / are the ones i noticed, go see what the (UA) is, maybe i want to keep it?

        # Check if the spell already exists in the database
#        if Spells.objects.filter(name=spellName).exists():
#            self.stdout.write(self.style.SUCCESS(f"Spell '{spellName}' already exists, skipping..."))
#            continue  # Skip to the next spell if it already exists
#

