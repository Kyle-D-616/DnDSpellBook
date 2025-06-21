from django.urls import path
from . import views

urlpatterns = [
    path("", views.spellList, name="spellList"),
    path("my-spells/", views.mySpellBook, name="mySpellBook"),
]
