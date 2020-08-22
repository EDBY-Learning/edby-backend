from django.urls import path
from . import views

urlpatterns = [
	path('apply_for_demo/',views.apply_for_demo),
    path('apply/',views.apply),
    path('approve/',views.approve),
]