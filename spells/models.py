from django.db import models

class SpellList(models.Model):
    name =models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Spell(models.Model):
    name = models.CharField(max_length=255)
    source = models.CharField(max_length=255, blank=True, null=True)
    spellLevel = models.CharField(max_length=255, blank=True, null=True)
    spellSchool = models.CharField(max_length=255, blank=True, null=True)
    castingTime = models.CharField(max_length=50, blank=True, null=True)
    spellRange = models.CharField(max_length=50, blank=True, null=True)
    components = models.CharField(max_length=255, blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    version = models.CharField(max_length=50)
    spellKey = models.CharField(max_length=50, unique=True)

    spellList = models.ManyToManyField(SpellList)

    def __str__(self):
        return self.name
