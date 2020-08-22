from django.urls import path
from . import views

urlpatterns = [
	path('get_teacher_summary_self/',views.get_teacher_summary_self),
    path('create_new_teacher/',views.create_new_teacher_by_authority),
    path('update_teacher_info/',views.update_teacher_details_by_self_or_authority),
    path('get_student_list/',views.get_student_list),
    path('create_or_update_subject_by_teacher/',views.create_or_update_subject_by_teacher),
    path('create_or_update_schedule/',views.create_or_update_schedule),
    path('delete_schedule/',views.delete_schedule),
    path('get_teacher_list/',views.get_teacher_list),
    path('get_slot_list/',views.get_slot_list),
    path('get_schedule_list/',views.get_schedule_list),
    path('get_class_subject_list/',views.get_class_subject_list),
    path('get_subject_list/',views.get_subject_list),
    path('get_schedule_list_for_teacher/',views.get_schedule_list_for_teacher),
    path('get_class_teacher_dashboard/',views.get_class_teacher_dashboard),
    path('get_teacher_dashboard/',views.get_teacher_dashboard),
    path('generate_subject_links/',views.generate_subject_links),
    path('get_dashboard_class_details_for_ct/',views.get_dashboard_class_details_for_ct),
    path('get_dashboard_student_details_for_ct/',views.get_dashboard_student_details_for_ct),
    path('get_dashboard_subject_list/',views.get_dashboard_subject_list),
    path('get_dashboard_subject_details/',views.get_dashboard_subject_details),
    path('reset_student_password/',views.reset_student_password),
    path('set_alternate_link/',views.set_alternate_link),
    path('delete_subject_teacher/',views.delete_subject_teacher),
]