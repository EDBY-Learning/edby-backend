from django.urls import path
from . import views

urlpatterns = [
    path('create_or_update_notes/',views.create_or_update_notes),
    path('get_notes_list/',views.get_notes_list),
]