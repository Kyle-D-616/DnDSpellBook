from django.db import models

class SpellList2014(models.Model):
    name =models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Spell2014(models.Model):
    name = models.CharField(max_length=255, unique=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    spellLevel = models.CharField(max_length=255, blank=True, null=True)
    spellSchool = models.CharField(max_length=255, blank=True, null=True)
    castingTime = models.CharField(max_length=50, blank=True, null=True)
    spellRange = models.CharField(max_length=50, blank=True, null=True)
    components = models.CharField(max_length=255, blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    spellList = models.ManyToManyField(SpellList2014)

    def __str__(self):
        return self.name

class SpellList2024(models.Model):
    name =models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Spell2024(models.Model):
    name = models.CharField(max_length=255, unique=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    spellLevel = models.CharField(max_length=255, blank=True, null=True)
    spellSchool = models.CharField(max_length=255, blank=True, null=True)
    castingTime = models.CharField(max_length=50, blank=True, null=True)
    spellRange = models.CharField(max_length=50, blank=True, null=True)
    components = models.CharField(max_length=255, blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    spellList = models.ManyToManyField(SpellList2014)

    def __str__(self):
        return self.name
