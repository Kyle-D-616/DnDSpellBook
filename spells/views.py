from django.shortcuts import render
#from .models import spell, spellList


def spellList(request):
    version = request.get.get('version', '2024')
    selectedspellList = request.get.getlist('spellList')
    selectedspells = request.session.get('selectedspells', [])

    if request.method == 'post':
        selectedspellids = request.post.getlist('selectedspells')
        print(f"post data: {selectedspellids}")
        request.session['selectedspells'] = [int(id) for id in selectedspellids]
        request.session.modified = true

    if version == '2024':
        spells = Spells.objects.all()
        if selectedspellList:
            spells = spells.filter(spellList__name__in=selectedspellList)
        spellListoptions = spellList2024.objects.all()
    else:
        spells = spell2014.objects.all()
        if selectedspellList:
            spells = spells.filter(spellList__name__in=selectedspellList)
        spellListoptions = spellList2014.objects.all()


    return render(request, 'spells/spellList.html', {
        'version': version,
        'spells': spells,
        'spellListoptions': spellListoptions,
        'selectedlist': selectedspellList,
        'selectedspells': selectedspells,
    })

def spellBook(request):


    selectedspellids = request.session.get('selectedspells')
    spells2024 = spell2024.objects.filter(id__in=selectedspellids)
    spells2014 = spell2014.objects.filter(id__in=selectedspellids)

    from itertools import chain
    spellBookspells = list(chain(spells2024, spells2014))
    print("here are the spell id: ")
    print(request.session.get('selectedspells', []))

    return render(request, 'spells/spellBook.html', {
        'spellBookspells': spellBookspells,
    })
