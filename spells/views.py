from django.shortcuts import render
from .models import Spell

def spellList(request):


    spells = Spell.object.all().order_by('name')
    return render(request, 'spells/spell_list.html', {'spells': spells})
