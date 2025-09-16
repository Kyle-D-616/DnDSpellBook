from spells.models import Spells, SpellList

class WriteSpellToDataBase:
    def __init__(self, spell_fields):
        if not spell_fields or not isinstance(spell_fields, dict):
            raise ValueError("spell_fields must be a valid dictionary")
        self.spell_fields = spell_fields
    
    def save_spell_to_database(self):
        # Generate the spell key that matches your validation logic
        spell_key = str(self.spell_fields.get('version', '')) + self.spell_fields['name'].replace(" ", "").replace("'", "")
        
        spell = Spells(
            name=self.spell_fields['name'],
            spellKey=spell_key,
            source=self.spell_fields['source'],
            spellLevel=self.spell_fields['spellLevel'],
            spellSchool=self.spell_fields['spellSchool'],
            castingTime=self.spell_fields['castingTime'],
            spellRange=self.spell_fields['spellRange'],
            components=self.spell_fields['components'],
            duration=self.spell_fields['duration'],
            description=self.spell_fields['description'],
        )
        spell.save()
        list_objs = []
        for list_name in self.spell_fields.get('spellLists', []):
            list_name = list_name.strip()
            if not list_name:
                continue
            spell_list_obj, _ = SpellList.objects.get_or_create(name=list_name)
            list_objs.append(spell_list_obj)
        spell.spellList.set(list_objs)
        return spell
