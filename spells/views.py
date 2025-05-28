from django.shortcuts import render
from .models import Spell, SpellList


def spellList(request):
    selectedList = request.GET.getlist('spellList')

    if selectedList:
        spellsDisplayed = Spell.objects.filter(spellList__name__in=selectedList).distinct()
    else:
        spellsDisplayed = Spell.objects.all()

    spellListOptions = SpellList.objects.all()

    return render(request, 'spells/spellList.html', {
        'spells': spellsDisplayed,
        'spellListOptions': spellListOptions,
        'selectedList': selectedList
    })
