from django.urls import path
from . import views


urlpatterns = [
    path('create_new_student/',views.create_new_student_by_teacher_or_authority),
    path('get_schedule_list/',views.get_schedule_list),
    path('get_slot_list/',views.get_slot_list),
    path('get_subject_list/',views.get_subject_list),
    path('update_attendance/',views.update_attendance),
    path('get_student_summary_self/',views.get_student_summary_self),
    path('update_student_info/',views.update_student_details_by_self_or_teacher),
    path('get_dashboard_student_details/',views.get_dashboard_student_details),
]