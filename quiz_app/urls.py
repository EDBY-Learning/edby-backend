from django.urls import path
from . import views

urlpatterns = [
    path('create_quiz/',views.create_quiz),
    path('update_quiz/',views.update_quiz),
    path('delete_quiz/',views.delete_quiz),
    path('publish_quiz/',views.publish_quiz),
    path('read_quiz_teacher/',views.read_quiz_teacher),
    path('read_quiz_student/',views.read_quiz_student),
    path('create_question/',views.create_question),
    path('update_question/',views.update_question),
    path('delete_question/',views.delete_question),
    path('read_question_teacher/',views.read_question_teacher),
    path('get_quiz_list_teacher/',views.get_quiz_list_teacher),
    path('get_quiz_list_student/',views.get_quiz_list_student),
    path('get_quiz_list_student_unpublished/',views.get_quiz_list_student_unpublished),
    path('grade_quiz_all/',views.grade_quiz_all),
    path('grade_quiz_student/',views.grade_quiz_student),
    path('get_quiz_submission/',views.get_quiz_submission),
    path('grade_subjective_question/',views.grade_subjective_question),
    path('save_question_response/',views.save_question_response),
    path('submit_quiz/',views.submit_quiz),
    path('get_quiz_submission_list/',views.get_quiz_submission_list),
    path('read_quiz_student_correct_answer/',views.read_quiz_student_correct_answer),
]
