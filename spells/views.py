from django.shortcuts import render
from .models import Spells, SpellList


def spellList(request):
    version = request.GET.get('version', '2024')
    selectedSpellList = request.GET.getlist('spellList')
    spellList = SpellList.objects.all()

    if request.method == 'POST':
        selectedSpellIds = request.POST.getlist('selectedSpells')
        print(f"POST data: {selectedSpellIds}")
        request.session['selectedSpells'] = [int(id) for id in selectedSpellIds]
        request.session.modified = True

    if version == '2024':
        spells = Spells.objects.filter(version='2024')
        if selectedSpellList:
            spells = spells.filter(spellList__name__in=selectedSpellList)
        spellListOptions = SpellList.objects.all()
    else:
        spells = Spells.objects.all()
        if selectedSpellList:
            spells = spells.filter(spellList__name__in=selectedSpellList)
        spellListOptions = SpellList.objects.all()


    selectedSpells = request.session.get('selectedSpells', [])
    return render(request, 'spells/spellList.html', {
        'version': version,
        'spells': spells,
        'spellListOptions': spellListOptions,
        'selectedList': selectedSpellList,
        'spellList': spellList,
        'selectedSpells': selectedSpells,
    })

def spellBook(request):
    selectedSpellIds = request.session.get('selectedSpells', [])
 
    if request.method == 'POST':
        removableSpells = request.POST.getlist('removableSpells')
        print(f"POST data:{removableSpells}")
        selectedSpellIds = [id for id in selectedSpellIds if str(id) not in removableSpells]
        request.session['selectedSpells'] = selectedSpellIds
        request.session.modified = True

    spellBookSpells = Spells.objects.filter(id__in=selectedSpellIds)
    return render(request, 'spells/spellBook.html', {
        'spellBookSpells': spellBookSpells,
    })
