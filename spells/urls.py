from django.urls import path
from . import views

urlpatterns = [
    path("", views.spellList, name="spell_list"),
]
