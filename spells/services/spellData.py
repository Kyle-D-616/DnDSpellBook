class SpellData:
    def __init__(self, name, source='', spellLevel='', spellSchool='', castingTime='', spellRange='', components='', duration='', description='', spellList=None):
        self.name = name
        self.source = source
        self.spellLevel = spellLevel
        self.spellSchool = spellSchool
        self.castingTime = castingTime
        self.spellRange = spellRange
        self.components = components
        self.duration = duration
        self.description = description
        self.spellList = spellList or set()
