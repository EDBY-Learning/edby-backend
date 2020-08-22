from datetime import date

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from .utils import create_student, update_student_info
from core.models import *
from core.views import has_session_expired_and_update
from django.views.decorators.http import require_http_methods


@csrf_exempt
def is_logged_as_authority(user):
	try:
		is_authority = user.authority 
		return True
	except:
		return False
	
@csrf_exempt
def is_logged_as_teacher(user):
	try:
		is_teacher = user.teacher  
		return True
	except:
		return False
	

@csrf_exempt
def is_logged_as_student(user):
	try:
		is_student = user.student  
		return True
	except:
		return False



def send_draft_to_email(email,draft):
	##have to write in future 
	print("sending details to email",email)
	print(draft)

def is_logged_as_staff_or_admin(user):
	#staff or admin is server controller 
	return user.is_staff or user.is_superuser


def get_class_of_class_teacher(teacher):
	class_is = Class.objects.filter(class_teacher=teacher)
	if len(class_is)==0:
		has_class = False
		class_is = None
	else:
		has_class = True
		class_is = class_is[0]
	return has_class, class_is



@csrf_exempt
@require_http_methods(["POST"])
def create_new_student_by_teacher_or_authority(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    is_authority = is_logged_as_authority(user)
    try:
        if is_teacher:
            teacher = user.teacher
            is_class_teacher = teacher.is_class_teacher
            if is_class_teacher:
                has_class, class_is = get_class_of_class_teacher(teacher)
            else:
                return JsonResponse({"status":"unsuccessful", "message":"You are not class teacher."})
            if not has_class:
                return JsonResponse({"status":"unsuccessful", "message":"You have not been assigned any class. Kindly contact school authority."})
        elif is_authority:
            pass
        else:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
        

        name = request.POST.get('name',None)
        roll = request.POST.get('roll',None)
        parent_mob_no_1 = request.POST.get('parent_mob_no_1',None)
        email = request.POST.get('email',None)
        #parent name
        parent_name = request.POST.get('parent_name',None)
        parent_email = request.POST.get('parent_email',None)
        if is_teacher:
            class_id = class_is.id
        if is_authority:
            school_id = user.authority.school.id
            class_name = request.POST.get('class_name')
            section = request.POST.get('section')
            class_ = Class.objects.get(school__id=school_id,class_name=class_name,section=section)
            class_id = class_.id

        info_status = create_student(name, roll, parent_mob_no_1, email, class_id,parent_name, parent_email)
        if info_status.get('status')=='success':
            send_draft_to_email(email,info_status['info'])
        else:
            return JsonResponse({"status":"unsuccessful", "message":"Could not create student. "+ info_status.get('message')})


        return JsonResponse({"status":info_status['status'], 'info':info_status['info']})
    except Exception as e:
        print(str(e))
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})

def get_class_id_from_student_id(student_id):
	try:
		student = Student.objects.filter(id=student_id)[0]
		return student.class_is.id
	except:
		return None

def get_class_id_from_teacher_id(teacher_id):
	try:
		class_is = Class.objects.filter(class_teacher__id=teacher_id)[0]
		return class_is.id
	except:
		return None


@csrf_exempt
@require_http_methods(["POST"])
def update_student_details_by_self_or_teacher(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_student = is_logged_as_student(user)
    is_teacher = is_logged_as_teacher(user)
    if not (is_teacher or is_student):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
    
    try:
        if is_teacher:
            student_id = request.POST.get('student_id',None)
            teacher_id = user.teacher.id
            school_id_from_student_id = get_class_id_from_student_id(student_id)
            school_id_from_teacher_id = get_class_id_from_teacher_id(teacher_id)

            if not( school_id_from_teacher_id and school_id_from_student_id):
                return JsonResponse({"status":"unsuccessful", "message":"No proper student/teacher."})

            if school_id_from_student_id!=school_id_from_teacher_id:
                return JsonResponse({"status":"unsuccessful", "message":"No proper rights of teacher."})
            else:
                print("teacher and student of the same class")
                pass
        else:
            student_id = user.student.id 
        
        if student_id==None:
            return JsonResponse({"status":"unsuccessful", "message":"Please provide student_id."})
        
        new_info = {}

        if request.POST.get('email',None):
            new_info['email'] = request.POST.get('email',None)
        if request.POST.get('mob_no',None):
            new_info['mob_no'] = request.POST.get('mob_no',None)
        if request.POST.get('addr',None):
            new_info['addr'] = request.POST.get('addr',None)
        if request.POST.get('city',None):
            new_info['city'] = request.POST.get('city',None)
        if request.POST.get('state',None):
            new_info['state'] = request.POST.get('state',None)
        if request.POST.get('nation',None):
            new_info['nation'] = request.POST.get('nation',None)
        if request.POST.get('pincode',None):
            new_info['pincode'] = request.POST.get('pincode',None)

        # if request.POST.get('parent_mob_no_1',None):
        #     new_info['parent_mob_no_1'] = request.POST.get('parent_mob_no_1',None)
        if request.POST.get('parent_mob_no_2',None):
            new_info['parent_mob_no_2'] = request.POST.get('parent_mob_no_2',None)
        if request.POST.get('parent_email',None):
            new_info['parent_email'] = request.POST.get('parent_email',None)
        
        info_status = update_student_info(new_info, student_id)
            
        return JsonResponse(info_status)
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})

@csrf_exempt
@require_http_methods(["POST"])
def get_subject_list(request):
    if request.method != 'POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        if not is_logged_as_student(user):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        class_ = user.student.class_is
        #print(class_)
        message = [subject.get_summary() for subject in Subject.objects.filter(class_is=class_).distinct()]
        #print(message)
        return JsonResponse({"status":"success","message":message})
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})

@csrf_exempt
@require_http_methods(["POST"])
def get_schedule_list(request):
    if request.method != 'POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        if not is_logged_as_student(user):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        student_id = user.student.id
        student = Student.objects.get(id=student_id)
        class_id = student.class_is.id
        class_ = Class.objects.get(id=class_id)
        #print(class_)
        message = [schedule.get_summary() for schedule in Schedule.objects.filter(subject__class_is=class_).distinct()]
        #print(message)
        return JsonResponse({"status":"success","message":message})
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})


@csrf_exempt
@require_http_methods(["POST"])
def get_slot_list(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_student(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        school = user.student.class_is.school
        #print('asdf',school)
        message = [slot.get_summary() for slot in school.slot_set.all()]
        #print(message)
        return JsonResponse({"status":"success","message":message})
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})


@csrf_exempt
@require_http_methods(["POST"])
def update_attendance(request):
    status = "unsuccessful"
    if request.method != 'POST':
        message = "Invalid request"
        return JsonResponse({"status":status,"message":message})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        if not is_logged_as_student(user):
            message = "No proper authentication."
            return JsonResponse({"status":status,"message":message})

        answered = request.POST.get('answered',None)

        try:
            attendance = Attendance.objects.get(date=date.today())
        except:
            attendance = Attendance(student=user.student)
        attendance.total_questions += 1
        if(answered=='True'):
            attendance.answered_questions += 1
        attendance.save()
        return JsonResponse({"status":'success', "message":"Attendance updated"})

    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})

@csrf_exempt
@require_http_methods(["POST"])
def get_student_summary_self(request):
    if request.method != 'POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_student(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        student = user.student
        message = student.get_summary()
        return JsonResponse({"status":"success","message":message})
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})

@csrf_exempt
@require_http_methods(["POST"])
def get_dashboard_student_details(request):
    if request.method != 'POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_student(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        student = user.student

        summary = {"student_id":student.id, "student_name":student.user.first_name,
        "class_name":student.class_is.class_name,"section":student.class_is.section,
        "roll_number":student.roll, "parent_mob_no":student.parent_mob_no_1}

        recent_attentiveness_list = []
        queryset = Attendance.objects.filter(student=student).values('date').distinct().order_by('-date')[:7]
        for date in queryset:
            date = date['date']
            denominator = 0
            numerator = 0
            attentiveness = None
            for attendance in Attendance.objects.filter(student=student,date=date):
                denominator += attendance.total_questions
                numerator += attendance.answered_questions
            if denominator != 0:
                attentiveness = round(numerator/denominator*100, 2)

            denominator = 0
            numerator = 0
            average_attentiveness = None
            for attendance in Attendance.objects.filter(date=date,student__class_is=student.class_is):
                denominator += attendance.total_questions
                numerator += attendance.answered_questions
            if denominator != 0:
                average_attentiveness = round(numerator/denominator*100, 2)

            recent_attentiveness_dict = {"date":date,"attentiveness":str(attentiveness),"average_attentiveness":str(average_attentiveness)}
            recent_attentiveness_list.append(recent_attentiveness_dict)

        subject_performance_list = []
        for subject in Subject.objects.filter(class_is=student.class_is):
            denominator = 0
            numerator = 0
            performance = None
            for submission in Class_test_submission.objects.filter(student=student,class_test__subject=subject):
                if submission.marks and submission.class_test.maximum_marks:
                    denominator += submission.class_test.maximum_marks
                    numerator += submission.marks
            if denominator != 0:
                performance = round(numerator/denominator*100, 2)

            denominator = 0
            numerator = 0
            average_performance = None
            for submission in Class_test_submission.objects.filter(class_test__subject=subject):
                if submission.marks and submission.class_test.maximum_marks:
                    denominator += submission.class_test.maximum_marks
                    numerator += submission.marks
            if denominator != 0:
                average_performance = round(numerator/denominator*100, 2)

            subject_performance_dict = {"subject_id":subject.id,
            "subject_name":subject.subject_name, "performance": str(performance),
            "average_performance": str(average_performance)}
            subject_performance_list.append(subject_performance_dict)

        return JsonResponse({"status":"success", "summary":summary,
            "recent_attentiveness_list":recent_attentiveness_list,
            "subject_performance_list":subject_performance_list})
    
    except Exception as e:
        print(e)
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})
