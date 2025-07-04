from django.shortcuts import render
from .models import Spell2014, SpellList2014, Spell2024, SpellList2024


def spellList(request):
    version = request.GET.get('version', '2024')
    selectedSpellList = request.GET.getlist('spellList')
    selectedSpells = request.session.get('selectedSpells', [])

    if request.method == 'POST':
        selectedSpellIds = request.POST.getlist('selectedSpells')
        print(f"POST data: {selectedSpellIds}")
        request.session['selectedSpells'] = [int(id) for id in selectedSpellIds]
        request.session.modified = True

    if version == '2024':
        spells = Spell2024.objects.all()
        if selectedSpellList:
            spells = spells.filter(spellList__name__in=selectedSpellList)
        spellListOptions = SpellList2024.objects.all()
    else:
        spells = Spell2014.objects.all()
        if selectedSpellList:
            spells = spells.filter(spellList__name__in=selectedSpellList)
        spellListOptions = SpellList2014.objects.all()


    return render(request, 'spells/spellList.html', {
        'version': version,
        'spells': spells,
        'spellListOptions': spellListOptions,
        'selectedList': selectedSpellList,
        'selectedSpells': selectedSpells,
    })

def spellBook(request):


    selectedSpellIds = request.session.get('selectedSpells')
    spells2024 = Spell2024.objects.filter(id__in=selectedSpellIds)
    spells2014 = Spell2014.objects.filter(id__in=selectedSpellIds)

    from itertools import chain
    spellBookSpells = list(chain(spells2024, spells2014))
    print("here are the spell id: ")
    print(request.session.get('selectedSpells', []))

    return render(request, 'spells/spellBook.html', {
        'spellBookSpells': spellBookSpells,
    })
