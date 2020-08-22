from django.urls import path
from . import views

urlpatterns = [
    path('create_or_update_class_test/',views.create_or_update_class_test),
    path('publish_class_test/',views.publish_class_test),
    path('create_or_submit_class_test_submission/',views.create_or_submit_class_test_submission),
    path('grade_class_test_submission/',views.grade_class_test_submission),
    path('get_class_test_list/',views.get_class_test_list),
    path('get_class_test_submission_list_for_class_test/',views.get_class_test_submission_list_for_class_test),
    path('get_class_test_submission_list_for_subject/',views.get_class_test_submission_list_for_subject),
]