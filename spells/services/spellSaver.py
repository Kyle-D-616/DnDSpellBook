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

        list_objs = []
        for list_name in self.spellData.get('spellLists',[]):
            list_name = list_name.strip()
            if not list_name:
                continue
            spell_list_obj, _ = SpellList.objects.get_or_create(name=list_name)
            list_objs.append(spell_list_obj)

        spell.spelllist.set(list_objs)

        return spell
