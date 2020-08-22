import json

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout

from django.views.decorators.http import require_http_methods
from core.views import has_session_expired_and_update

from .utils import create_authority, update_authority_info, create_class, assign_class_teacher_to_class
from core.models import *
from datetime import datetime, date

@csrf_exempt
def get_num(request):
    if request.user.is_authenticated:
        print('already logged in')
    return JsonResponse({"Hello":4})

@csrf_exempt
def is_logged_as_authority(user):
    if user.is_authenticated:
        try:
            is_authority = user.authority 
            return True
        except:
            return False
    else:
        return False

def send_draft_to_email(email,draft):
    ##have to write in future 
    print("sending details to email",email)
    print(draft)

@csrf_exempt
def is_logged_as_staff_or_admin(user):
    #staff or admin is server controller 
    if user.is_authenticated:
        return user.is_staff
    else:
        return False

@csrf_exempt
def login_as_authority(request):
    if request.user.is_authenticated:
        try:
            is_authority = request.user.authority 
            #print('already logged in as authority')
            return JsonResponse({"status":"successful", "message":"already logged in as authority"})
        except:
            logout(request)
            return JsonResponse({"status":"unsuccessful", "message":"you are not authority. logging you out."})
    else:
        print("not logged in ")
    username = request.POST.get('username',None)
    password = request.POST.get('password',None)

    if username and password:
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                is_authority = user.authority 
                login(request, user)
                return JsonResponse({"status":"successful", "message":"Logged in successfully as authority"})
            except:
                return JsonResponse({"status":"unsuccessful", "message":"Not registered as authority. Login through different method."})
    return JsonResponse({"status":"unsuccessful", "message":"username/password does not match"})



@csrf_exempt
@require_http_methods(["POST"])
def create_new_authority_by_authority_or_admin(request):
    if request.method != 'POST':
        return JsonResponse({"status":"unsuccessful", "message":"Invalid request"})

    #print(request.body)
    token = request.POST.get('token',None)
    #print(token)
    user = has_session_expired_and_update(token)
    #print(user)
    #print(user.is_authenticated)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        is_authority = is_logged_as_authority(user)
        is_staff_or_admin = is_logged_as_staff_or_admin(user)
        if not (is_staff_or_admin or is_authority):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        name = request.POST.get('name',None)
        email = request.POST.get('email',None)
        mob_no = request.POST.get('mob_no',None)

        #if request.POST.get('designation',None):
        designation = request.POST.get('designation',None)

        #if request.POST.get('addr',None):
        addr = request.POST.get('addr','')
        #print('Address',addr)
        #if request.POST.get('city',None):
        city = request.POST.get('city','')
        #if request.POST.get('state',None):
        state = request.POST.get('state','')
        #if request.POST.get('nation',None):
        nation = request.POST.get('nation','')
        #if request.POST.get('pincode',None):
        pincode = request.POST.get('pincode','')

        if is_staff_or_admin:
            #print(' logged in as admin')
            school_id = request.POST.get('school_id',None)
        else:
            school_id = user.authority.school.id 
        #print('a')
        info_status = create_authority(name, email, designation, mob_no, school_id, addr,city,state,nation,pincode)
        #print('b')
        if info_status.get('status')=='success':
            send_draft_to_email(email,info_status['info'])
        else:
            return JsonResponse({"status":"unsuccessful", "message":"Could not create authority. "+ info_status.get('message')})


        if is_staff_or_admin:
            return JsonResponse({"status":info_status['status'], 'info':info_status['info']})
        else:
            return JsonResponse({"status":info_status['status']})

    except Exception as e:
        #print(str(e))
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})

@csrf_exempt
@require_http_methods(["POST"])
def get_authority_summary_self(request):
    if request.method != 'POST':
        return JsonResponse({"status":"unsuccessful", "message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        is_authority = is_logged_as_authority(user)
        if not is_authority:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
        
        authority = user.authority
        message = authority.get_summary()
        return JsonResponse({"status":"success", "message":message})
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def update_authority_details_by_self_or_admin(request):
    if request.method != 'POST':
        return JsonResponse({"status":"unsuccessful", "message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        is_authority = is_logged_as_authority(user)
        is_staff_or_admin = is_logged_as_staff_or_admin(user)
        if not (is_staff_or_admin or is_authority):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        if is_staff_or_admin:
            authority_id = request.POST.get('authority_id',None)
        else:
            authority_id = user.authority.id 
        
        if authority_id==None:
            return JsonResponse({"status":"unsuccessful", "message":"Please provide authority_id."})

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
        info_status = update_authority_info(new_info, authority_id)
            
        return JsonResponse(info_status)
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def get_authority_list(request):
    if request.method != 'POST':
        return JsonResponse({"status":"unsuccessful", "message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        is_authority = is_logged_as_authority(user)
        if not is_authority:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
        school_id = user.authority.school.id

        message = [authority.get_summary() for authority in Authority.objects.filter(school__id=school_id)]
        return JsonResponse({"status":"success", "message":message})
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})

@csrf_exempt
def create_new_class(request):
    if request.method != 'POST':
        return JsonResponse({"status":"unsuccessful", "message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        is_authority = is_logged_as_authority(user)
        if not is_authority:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        class_name = request.POST.get('class_name',None)
        section = request.POST.get('section',None)
        teacher_id = request.POST.get('teacher_id',None)
        school_id = request.user.authority.school.id 

        info_status = create_class(class_name, section, school_id, teacher_id)
        if info_status.get('status')=='successful':
            return JsonResponse({"status":info_status['status'], 'info':info_status['info']})
        else:
            return JsonResponse({"status":"unsuccessful", "message":"Could not create class. "+ info_status.get('message')})
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})


def get_school_id_from_class_id(class_id):
    try:
        class_is = Class.objects.filter(id=class_id)[0]
        return class_is.school.id
    except:
        return None

def get_school_id_from_teacher_id(teacher_id):
    try:
        teacher = Teacher.objects.filter(id=teacher_id)[0]
        return teacher.school.id
    except:
        return None


@csrf_exempt
def assign_class_teacher(request):
    if request.method != 'POST':
        return JsonResponse({"status":"unsuccessful", "message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:    
        is_authority = is_logged_as_authority(user)
        if not is_authority:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        class_id = request.POST.get('class_id',None)
        teacher_id = request.POST.get('teacher_id',None)

        school_id_from_class_id = get_school_id_from_class_id(class_id)
        school_id_from_teacher_id = get_school_id_from_teacher_id(teacher_id)
        school_id_from_authority = user.authority.school.id 

        if not (school_id_from_class_id and school_id_from_teacher_id):
            return JsonResponse({"status":"unsuccessful", "message":"No proper teacher/class id."})
            return JsonResponse({"status":"unsuccessful", "message":"Mismatch between school of class and school of teacher ."})
        if school_id_from_class_id!=school_id_from_teacher_id:
            return JsonResponse({"status":"unsuccessful", "message":"Mismatch between school of class and school of teacher ."})
        if school_id_from_authority!=school_id_from_class_id:
            return JsonResponse({"status":"unsuccessful", "message":"Mismatch between school of authority and school of class ."})
        if school_id_from_authority!=school_id_from_teacher_id:
            return JsonResponse({"status":"unsuccessful", "message":"Mismatch between school of authority and school of teacher ."})
        else:
            print("authority and teacher are from same school")

        info_status = assign_class_teacher_to_class(class_id, teacher_id)
        if info_status.get('status')=='successful':
            return JsonResponse({"status":info_status['status'], 'info':info_status['info']})
        else:
            return JsonResponse({"status":"unsuccessful", "message":"Could assign class teacher. "+ info_status.get('message')})

    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})

@csrf_exempt
@require_http_methods(["POST"])
def get_class_list(request):
    if request.method != 'POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        if not is_logged_as_authority(user):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        school_id = user.authority.school.id
        
        message = [class_.get_summary() for class_ in Class.objects.filter(school__id=school_id)]
        return JsonResponse({"status":"success", "message":message})
    except Exception as e:
        #print(str(e))
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})


@csrf_exempt
def get_teacher_list(request):
    if request.method != 'POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        if not is_logged_as_authority(user):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        school_id = user.authority.school.id
        message = [teacher.get_priviledged_summary() for teacher in Teacher.objects.filter(school__id=school_id)]
        return JsonResponse({"status":"success", "message":message})
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})

@csrf_exempt
def get_class_teacher_list(request):
    if request.method != 'POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        if not is_logged_as_authority(user):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        school_id = user.authority.school.id
        message = [class_teacher.get_priviledged_summary() for class_teacher in Teacher.objects.filter(school__id=school_id,is_class_teacher=True)]
        return JsonResponse({"status":"success", "message":message})
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def get_student_list(request):
    if request.method != 'POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        if not is_logged_as_authority(user):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        school_id = user.authority.school.id
        class_name = request.POST.get('class_name')
        section = request.POST.get('section')
        try:
            class_ = Class.objects.get(school_id=school_id,class_name=class_name,section=section)
        except:
            return JsonResponse({"message":"Class matching query does not exist"})
        message = [student.get_priviledged_summary() for student in class_.student_set.all()]
        
        return JsonResponse({"status":"success", "message":message})
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})

@csrf_exempt
def get_entire_student_list(request):
    if request.method != 'POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        if not is_logged_as_authority(user):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        school_id = user.authority.school.id
        message = [student.get_priviledged_summary() for student in Student.objects.filter(class_is__school__id=school_id)]
        #print(message[0])
        return JsonResponse({"status":"success", "message":message})
    except Exception as e:
        #print(e)
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})


def create_or_update_slot_for_school(slot_data_list, school):
    try:
        for slot_data in slot_data_list:
            #print(slot_data)
            day = slot_data[0]
            period_number = slot_data[1]
            start_time = slot_data[2]
            end_time = slot_data[3]

            slot = Slot.objects.filter(day=day, period_number=period_number,
                                        school=school)
            
            if len(slot)==0:

                slot = Slot.objects.create(day=day, period_number=period_number,
                                            start_time=start_time,end_time=end_time,
                                            school=school)
                slot.save()
            else:
                slot = Slot.objects.filter(day=day, period_number=period_number,
                                        school=school)[0]
                slot.start_time = start_time
                slot.end_time = end_time
                slot.save()
                
            
        return {"info":"created slot successfully",'status':'success'}
    except Exception as e:
        #print(str(e))
        return {'info':'failed to create','status':'unsuccessful'}
 

@csrf_exempt
@require_http_methods(["POST"])
def create_or_update_slot(request):
    if request.method != 'POST':
        return JsonResponse({"message":"Invalid request"})

    try:
        token = json.loads(request.body)['token']
    except:
        token = None
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        is_authority = is_logged_as_authority(user)
        if not is_authority:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        
        slot_data_list = json.loads(request.body)['slot_data_list']
        school_id = user.authority.school.id
        school = user.authority.school 
        #print(slot_data_list, 'slot data list')
        if len(slot_data_list)==0:
            return JsonResponse({"status":'unsuccessful','message':'no slot provied.'})
        
        # current_slots_for_school = Slot.objects.filter(school=school)
        # if len(current_slots_for_school)>0:
        #     return JsonResponse({"status":"unsuccessful","info":"slot already exists. kindly use modify slots."})

        
        info_status = create_or_update_slot_for_school(slot_data_list, school)

        if info_status.get('status')=='success':
            return JsonResponse({"status":info_status['status'], 'message':info_status['info']})
        else:
            return JsonResponse({"status":"unsuccessful", "message":"Could not create slot. "+ info_status.get('info')})
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def get_slot_list(request):
    if request.method != 'POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        if not is_logged_as_authority(user):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        school_id = user.authority.school.id
        school = School.objects.get(id=school_id)
        slot_list = school.slot_set.all()
        slot_list = list(slot_list.values())
        return JsonResponse(dict(status='success',message=slot_list))
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})

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
        if not is_logged_as_authority(user):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        school_id = user.authority.school.id
        
        class_name = request.POST.get('class_name')
        section = request.POST.get('section')
        #print(class_name,section)
        try:
            class_ = Class.objects.get(school_id=school_id,class_name=class_name,section=section)
        except:
            return JsonResponse({"message":"Class matching query does not exist"})
        
        schedule_list = []
        for schedule in Schedule.objects.filter(subject__class_is=class_.id).distinct():
            schedule_dict = {}
            schedule_dict['schedule_id'] = schedule.id
            schedule_dict['slot'] = schedule.slot.get_summary()
            schedule_dict['subject'] = []
            schedule_dict['teacher_name'] = []
            for subject in schedule.subject.all():
                subject_dict = subject.get_summary()
                subject_id = subject_dict['subject_id']
                del subject_dict['subject_id']
                subject_dict['id'] = subject_id
                if subject.teacher:
                    teacher_name = subject.teacher.user.first_name
                else:
                    teacher_name = ""
                schedule_dict['subject'].append(subject_dict)
                schedule_dict['teacher_name'].append(teacher_name)

            schedule_list.append(schedule_dict)

        return JsonResponse(dict(status='success',message=schedule_list))
    except Exception as e:
        #print(e)
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})

"""
@csrf_exempt
def get_authority_dashboard(request):
    if request.method != 'POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        if not is_logged_as_authority(user):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        summary = {}
        summary['name'] = user.first_name
        summary['designation'] = user.authority.designation

        school = user.authority.school

        class_list = []
        for class_ in school.class_set.all():
            class_dict = {}
            class_dict['class_name'] = class_.class_name
            class_dict['section'] = class_.section
            class_dict['class_strength'] = Student.objects.filter(class_is=class_).count()
            class_dict['attendance_today'] = Attendance.objects.filter(student__class_is=class_,date=date.today()).count()
            class_dict['subject_name'] = []
            class_dict['subect_link'] = []
            for subject in Subject.objects.filter(class_is=class_):
                try:
                    schedule = Schedule.objects.get(subject=subject)
                    # IST?
                    current_time = datetime.now().time()
                    if current_time>schedule.slot.start_time and current_time<schedule.slot.end_time:
                        class_dict['subject_name'].append(subject.subject_name)
                        class_dict['subect_link'].append(subject.link)
                except:
                    pass
            class_list.append(class_dict)

        return JsonResponse({"status":"success","message":{"summary":summary,"class_list":class_list}})

    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})
"""

@csrf_exempt
@require_http_methods(["POST"])
def get_dashboard_summary(request):
    if request.method != 'POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        if not is_logged_as_authority(user):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        school = user.authority.school

        total_attendance = Attendance.objects.filter(student__class_is__school=school,date=date.today()).count()
        class_list = []
        school_strength = 0
        for class_ in school.class_set.all():
            class_strength = class_.student_set.all().count()
            school_strength += class_strength
            class_dict = {"class_id":class_.id, "class_name":class_.class_name, "section":class_.section}
            class_list.append(class_dict)
        summary = {"total_attendance":total_attendance, "school_strength":school_strength}

        return JsonResponse({"status":"success", "summary":summary, "class_list":class_list})
    except Exception as e:
        #print(e)
        return JsonResponse({"status":"failure", "message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def get_dashboard_class_details(request):
    if request.method != 'POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        if not is_logged_as_authority(user):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        class_id = request.POST.get('class_id')
        class_ = Class.objects.get(id=class_id)

        class_strength = class_.student_set.all().count()
        summary = {"class_id":class_id, "class_name":class_.class_name,
        "section":class_.section, "class_teacher":class_.class_teacher.user.first_name,
        "class_strength":class_strength}
        #print(summary)

        subject_performance_list = []
        for subject in class_.subject_set.all():
            denominator = 0
            numerator = 0
            average_performance = None
            for submission in Class_test_submission.objects.filter(class_test__subject=subject):
                if submission.marks and submission.class_test.maximum_marks:
                    denominator += submission.class_test.maximum_marks
                    numerator += submission.marks
            if denominator != 0:
                average_performance = round(numerator/denominator*100, 2)
            subject_dict = {"subject_id":subject.id, "subject_name":subject.subject_name,
            "average_performance":str(average_performance)}
            subject_performance_list.append(subject_dict)
        #print(subject_performance_list)

        recent_attendance_list = []
        queryset = Attendance.objects.values('date').distinct().order_by('-date')[:7]
        for date in queryset:
            date = date['date']
            attendance_ = Attendance.objects.filter(date=date, student__class_is=class_).count()
            denominator = 0
            numerator = 0
            attentiveness = None
            for attendance in Attendance.objects.filter(date=date, student__class_is=class_):
                denominator += attendance.total_questions
                numerator += attendance.answered_questions
            if denominator != 0:
                attentiveness = round(numerator/denominator*100, 2)
            recent_attendance_dict = {"date":date,"attendance":attendance_,"attentiveness":str(attentiveness)}
            recent_attendance_list.append(recent_attendance_dict)
        #print(recent_attendance_list)

        student_list = []
        for student in class_.student_set.all():
            denominator = 0
            numerator = 0
            attentiveness = None
            for attendance in Attendance.objects.filter(student=student):
                    denominator += attendance.total_questions
                    numerator += attendance.answered_questions
            if denominator != 0:
                attentiveness = round(numerator/denominator*100, 2)

            denominator = 0
            numerator = 0
            performance = None
            for submission in Class_test_submission.objects.filter(student=student):
                if submission.marks and submission.class_test.maximum_marks:
                    denominator += submission.class_test.maximum_marks
                    numerator += submission.marks
            if denominator != 0:
                performance = round(numerator/denominator*100, 2)

            student_dict = {"student_id":student.id, "student_name":student.user.first_name,
            "roll_number":student.roll, "attentiveness":str(attentiveness), "performance":str(performance)}
            student_list.append(student_dict)
        #print(student_list)

        return JsonResponse({"status": "success", "summary":summary,
            "subject_performance_list":subject_performance_list,
            "recent_attendance_list":recent_attendance_list, "student_list":student_list})

    except Exception as e:
        #print(e)
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

    try:
        if not is_logged_as_authority(user):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        student_id = request.POST.get('student_id')
        student = Student.objects.get(id=student_id)

        summary = {"student_id":student_id, "student_name":student.user.first_name,
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
            recent_attentiveness_dict = {"date":date,"attentiveness":str(attentiveness)}
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

            subject_performance_dict = {"subject_id":subject.id,
            "subject_name":subject.subject_name, "performance": str(performance)}
            subject_performance_list.append(subject_performance_dict)

        return JsonResponse({"status":"success", "summary":summary,
            "recent_attentiveness_list":recent_attentiveness_list,
            "subject_performance_list":subject_performance_list})
    
    except Exception as e:
        #print(e)
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})


@csrf_exempt
def reset_teacher_password(request):
    if request.method != 'POST':
        return JsonResponse({"status":"failure","message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        if not is_logged_as_authority(user):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            teacher = Teacher.objects.get(user__username=username)
        except:
            return JsonResponse({"status":"unsuccessful", "message":"Username does not belong to any teacher"})

        if teacher.school != user.authority.school:
            return JsonResponse({"status":"unsuccessful", "message":"Teacher does not belong to your school"})

        teacher.user.set_password(password)
        teacher.first_password = password
        teacher.user.save()
        teacher.save()
        message = "Password reset for teacher "+username
        return JsonResponse({"status":"success", "message":message})

    except Exception as e:
        #print(e)
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})

