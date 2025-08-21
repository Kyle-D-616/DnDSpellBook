from .models import Spells, SpellList

class SpellSaver:

    def __init__(self, spellData):
        self.spellData = spellData

    def save_spell_to_database(self):
        spell = Spells(
            name=self.spellData['name'],
            source=self.spellData['source'],
            spellLevel=self.spellData['spellLevel'],
            spellSchool=self.spellData['spellSchool'],
            castingTime=self.spellData['castingTime'],
            spellRange=self.spellData['spellRange'],
            components=self.spellData['components'],
            duration=self.spellData['duration'],
            description=self.spellData['description'],
        )

        spell.save()

    def save_spelllist_to_database(self):
        list_objs = []
        for list_name in self.spell_lists:
            self.list_name = self.list_name.strip()
            if not self.list_name:
                continue
            spell_list_obj, _ = SpellList.objects.get_or_create(name=list_name)
            list_objs.append(spell_list_obj)

        spell.spelllist.set(list_objs)

 
