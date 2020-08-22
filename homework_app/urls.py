from django.urls import path
from . import views

urlpatterns = [
    path('create_or_update_homework/',views.create_or_update_homework),
    path('create_or_update_homework_submission/',views.create_or_update_homework_submission),
    path('grade_homework_submission/',views.grade_homework_submission),
    path('get_homework_list/',views.get_homework_list),
    path('publish_homework/',views.publish_homework),
    path('get_homework_submission_list_for_homework/',views.get_homework_submission_list_for_homework),
    path('get_homework_submission_list_for_subject/',views.get_homework_submission_list_for_subject),
]