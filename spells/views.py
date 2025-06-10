from django.shortcuts import render
from .models import Spell2014, SpellList2014, Spell2024, SpellList2024


def spellList(request):
    version = request.GET.get('version', '2024')
    selectedSpellList = request.GET.getlist('spellList')

    if version == '2024':
        spells = Spell2024.objects.all()
        if selectedSpellList:
            spells = Spell2024.filter(spellList__name__in=selectedSpellList)
        spellListOptions = SpellList2024.objects.all()
    else:
        spells = Spell2014.objects.all()
        if selectedSpellList:
            spells = Spell2014.filter(spellList__name__in=selectedSpellList)
        spellListOptions = SpellList2014.objects.all()

    return render(request, 'spells/spellList.html', {
        'version': version,
        'spells': spells,
        'spellListOptions': spellListOptions,
        'selectedList': selectedSpellList,
    })
