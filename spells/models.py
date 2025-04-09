from django.db import models

class Spell(models.Model):
    name = models.CharField(max_length=255, unique=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    spellLevelType = models.CharField(max_length=255, blank=True, null=True)
    castingTime = models.CharField(max_length=50, blank=True, null=True)
    spellRange = models.CharField(max_length=50, blank=True, null=True)
    components = models.CharField(max_length=255, blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    spellList = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name