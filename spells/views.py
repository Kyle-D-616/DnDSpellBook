from django.shortcuts import render
from .models import Spell


def spellList(request):
    selectedList = request.GET.get('spellList')

    if selectedList:
        spells = Spell.objects.filter(spellList__incontains=selectedList)
    else:
        spells = spells.objects.all()

    spellListOptions = Spell.objects.values_list('spellList', flat=True).distinct()

    return render(request, 'spells/spellList.html', {
        'spells': spells,
        'spellListOptions': spellListOptions,
        'selectedList': selectedList
    })
