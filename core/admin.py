from django.contrib import admin
from .models import *
# Register your models here.



class SchoolAdmin(admin.ModelAdmin):
    list_filter = ('school_name','city','state','board' )
    list_display = ('school_name','city','school_mob_no_1','board')

admin.site.register(School, SchoolAdmin)
 
class DemoApplicantAdmin(admin.ModelAdmin):
    list_display = ('institute_name','name','mob_no','email','designation')

admin.site.register(Demo_applicant, DemoApplicantAdmin)

class TeacherAdmin(admin.ModelAdmin):
    list_filter = ['city','state','school']
    list_display = ('user','name','school','mob_no','city','is_class_teacher')
    def name(self, obj):
        return obj.user.first_name

admin.site.register(Teacher, TeacherAdmin)

class ClassAdmin(admin.ModelAdmin):
    list_filter = ('school','class_name')
    list_display = ('school','class_name','section','class_teacher')

admin.site.register(Class, ClassAdmin)

class StudentAdmin(admin.ModelAdmin):
    list_filter = ['city','state','pincode','class_is']
    list_display = ('user','name','roll','mob_no','parent_mob_no_1')
    def name(self, obj):
        return obj.user.first_name

admin.site.register(Student, StudentAdmin)


class AuthorityAdmin(admin.ModelAdmin):
    list_display = ['name'] +[field.name for field in Authority._meta.get_fields() if (not field.many_to_many) and (not field.one_to_many) ]
    def name(self, obj):
        return obj.user.first_name
    pass

admin.site.register(Authority, AuthorityAdmin)

class SlotAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Slot._meta.get_fields() if (not field.many_to_many) and (not field.one_to_many)]
    pass

admin.site.register(Slot, SlotAdmin)

class SubjectAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Subject._meta.get_fields() if (not field.many_to_many) and (not field.one_to_many)]
    pass

admin.site.register(Subject, SubjectAdmin)

class ScheduleAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Schedule._meta.get_fields() if (not field.many_to_many) and (not field.one_to_many)]
    pass

admin.site.register(Schedule, ScheduleAdmin)

class HomeworkAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Homework._meta.get_fields() if (not field.many_to_many) and (not field.one_to_many)]
    pass

admin.site.register(Homework, HomeworkAdmin)

class Homework_submissionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Homework_submission._meta.get_fields() if (not field.many_to_many) and (not field.one_to_many)]
    pass

admin.site.register(Homework_submission, Homework_submissionAdmin)

class Class_testAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Class_test._meta.get_fields() if (not field.many_to_many) and (not field.one_to_many)]
    pass

admin.site.register(Class_test, Class_testAdmin)


class Class_test_submissionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Class_test_submission._meta.get_fields() if (not field.many_to_many) and (not field.one_to_many)]
    pass

admin.site.register(Class_test_submission, Class_test_submissionAdmin)

class SessionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Session._meta.get_fields() if (not field.many_to_many) and (not field.one_to_many)]
    pass

admin.site.register(Session, SessionAdmin)

class AttendanceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Attendance._meta.get_fields() if (not field.many_to_many) and (not field.one_to_many)]
    pass

admin.site.register(Attendance, AttendanceAdmin)


class NotesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Notes._meta.get_fields() if (not field.many_to_many) and (not field.one_to_many)]
    pass

admin.site.register(Notes, NotesAdmin)

class NoticeAdmin(admin.ModelAdmin):
    pass

admin.site.register(Notice, NoticeAdmin)

class ParentAdmin(admin.ModelAdmin):
    list_display = ['name'] + [field.name for field in Parent._meta.get_fields() if (not field.many_to_many) and (not field.one_to_many)]
    def name(self, obj):
        return obj.user.first_name
    pass

admin.site.register(Parent, ParentAdmin)

class QuizAdmin(admin.ModelAdmin):
    pass

admin.site.register(Quiz, QuizAdmin)

class QuestionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Question, QuestionAdmin)

class OptionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Option, OptionAdmin)

class Correct_answerAdmin(admin.ModelAdmin):
    pass

admin.site.register(Correct_answer, Correct_answerAdmin)

class Question_responseAdmin(admin.ModelAdmin):
    pass

admin.site.register(Question_response, Question_responseAdmin)

class Response_answerAdmin(admin.ModelAdmin):
    pass

admin.site.register(Response_answer, Response_answerAdmin)

class Quiz_submissionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Quiz_submission, Quiz_submissionAdmin)


# Register your models here.

def approve_applicant(modeladmin, request, queryset):
    for query in queryset.values():
        del query['id']
        school = School(**query)
        school.save()

class ApplicantAdmin(admin.ModelAdmin):
    actions = [approve_applicant]
    list_display = [field.name for field in Applicant._meta.get_fields() if (not field.many_to_many) and (not field.one_to_many)]

admin.site.register(Applicant, ApplicantAdmin)

admin.site.site_header = "EDBY Learning"

