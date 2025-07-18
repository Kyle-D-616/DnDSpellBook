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
        table = soup.find('table')
        for url in table.find_all('a'):
            self.spellUrls.append('https://dnd5e.wikidot.com' + url.get('href'))

    def getSpellData(self, spellUrls):
        for spellUrl in self.spellUrls:
            response = self.session.get(spellUrl)
            soup = BeautifulSoup(response.content, 'html.parser')
            #make name then make spell key to do check
            # Spell name
            spellDiv = soup.find('div', {'class': 'page-title page-header'})
            spellName = spellDiv.find('span').get_text(strip=True)
            spellKey = str(self.version) + spellName.replace(" ", "")
            print(spellKey)
        # Check if the spell already exists in the database
#        if Spells.objects.filter(name=spellName).exists():
#            self.stdout.write(self.style.SUCCESS(f"Spell '{spellName}' already exists, skipping..."))
#            continue  # Skip to the next spell if it already exists
#
