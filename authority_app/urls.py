from django.urls import path
from . import views

urlpatterns = [
    path('create_new_authority/',views.create_new_authority_by_authority_or_admin),
    path('update_authority_info/',views.update_authority_details_by_self_or_admin),
    path('get_authority_summary_self/',views.get_authority_summary_self),
    path('get_authority_list/',views.get_authority_list),
    path('create_new_class/',views.create_new_class),
    path('get_entire_student_list/',views.get_entire_student_list),
    path('assign_class_teacher/',views.assign_class_teacher),
    path('get_entire_student_list/',views.get_entire_student_list),
    path('get_class_list/',views.get_class_list),
    path('get_teacher_list/',views.get_teacher_list),
    path('get_class_teacher_list/',views.get_class_teacher_list),
    path('get_student_list/',views.get_student_list),
    path('create_or_update_slot/',views.create_or_update_slot),
    path('get_slot_list/',views.get_slot_list),
    path('get_schedule_list/',views.get_schedule_list),
    path('get_dashboard_summary/',views.get_dashboard_summary),
    path('get_dashboard_class_details/',views.get_dashboard_class_details),
    path('get_dashboard_student_details/',views.get_dashboard_student_details),
    path('reset_teacher_password/',views.reset_teacher_password),
]