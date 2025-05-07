from django.http import HttpResponse

def index(request):
    return HttpResponse("you are at the spells app index")
