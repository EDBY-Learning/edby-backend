import os

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from .utils import create_teacher, update_teacher_info
import json

from core.models import *
from core.views import has_session_expired_and_update
from authority_app.utils import create_class
from django.views.decorators.http import require_http_methods
from datetime import datetime, date, timedelta

from .cal_setup import get_calendar_service


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


def send_draft_to_email(email,draft):
    ##have to write in future 
    print("sending details to email",email)
    print(draft)

@csrf_exempt
def is_logged_as_staff_or_admin(user):
    #staff or admin is server controller 
    return user.is_staff or user.is_superuser

@csrf_exempt
@require_http_methods(["POST"])
def create_new_teacher_by_authority(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_authority = is_logged_as_authority(user)
    if not is_authority:
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
    
    try:
        name = request.POST.get('name',None)
        mob_no = request.POST.get('mob_no',None)
        if request.POST.get('email',None):
            email = request.POST.get('email',None)
        class_name = request.POST.get('class_name',None)
        section = request.POST.get('section',None)
        
        school_id = user.authority.school.id
        is_class_teacher =  request.POST.get('is_class_teacher',None)
        if is_class_teacher==None:
            is_class_teacher = False
        elif is_class_teacher=='True' or is_class_teacher==True:
            is_class_teacher = True
            if not (class_name and section):
                return JsonResponse({"status":"unsuccessful","message":"Please provide class and section"})
        else:
            is_class_teacher = False
        
        info_status = create_teacher(name, mob_no, email, is_class_teacher, school_id)
        if info_status.get('status')=='success':
            teacher_id = info_status.get('info').get('teacher_id')
            teacher = Teacher.objects.get(id=teacher_id)
            if teacher.is_class_teacher:
                create_class(class_name, section, school_id, teacher_id)
            send_draft_to_email(email,info_status['info'])
        else:
            return JsonResponse({"status":"unsuccessful", "message":"Could not create teacher. "+ info_status.get('message')})


        return JsonResponse({"status":info_status['status'], 'info':info_status['info']})
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})

    
    

@csrf_exempt
@require_http_methods(["POST"])
def update_teacher_details_by_self_or_authority(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_authority = is_logged_as_authority(user)
    is_teacher = is_logged_as_teacher(user)
    if not (is_teacher or is_authority):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    if is_authority:
        teacher_id = request.POST.get('teacher_id',None)
    else:
        teacher_id = user.teacher.id 
    
    if teacher_id==None:
        return JsonResponse({"status":"unsuccessful", "message":"Please provide teacher_id."})

    #try:
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
    if request.POST.get('is_class_teacher',None):
        new_info['is_class_teacher'] = request.POST.get('is_class_teacher',None)
    if request.POST.get('class_name',None):
        new_info['class_name'] = request.POST.get('class_name',None)
    if request.POST.get('section',None):
        new_info['section'] = request.POST.get('section',None)
    info_status = update_teacher_info(new_info, teacher_id, is_authority)
        
    return JsonResponse(info_status)

@csrf_exempt
@require_http_methods(["POST"])
def get_teacher_summary_self(request):
    if request.method != 'POST':
        return JsonResponse({"status":"unsuccessful", "message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        is_teacher = is_logged_as_teacher(user)
        if not is_teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
        
        teacher = user.teacher
        message = teacher.get_summary()
        return JsonResponse({"status":"success", "message":message})
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def get_student_list(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        if not is_logged_as_teacher(user):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        if not user.teacher.is_class_teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
        
        class_teacher_id = user.teacher.id
        #print(class_teacher_id)
        class_ = Class.objects.get(class_teacher_id=class_teacher_id)
        #print(class_)
        message = [student.get_priviledged_summary() for student in class_.student_set.all()]
        return JsonResponse({"status":"success","message":message})
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})



def get_class_of_class_teacher(teacher):
    class_is = Class.objects.filter(class_teacher=teacher)
    if len(class_is)==0:
        has_class = False
        class_is = None
    else:
        has_class = True
        class_is = class_is[0]
    return has_class, class_is

def get_teacher_by_id(teacher_id):
    teacher = Teacher.objects.filter(id=teacher_id)[0]
    return teacher
    

@csrf_exempt
@require_http_methods(["POST"])
def create_or_update_subject_by_teacher(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    #is_authority = is_logged_as_authority(request)
    try:
        if is_teacher:
            teacher = user.teacher
            is_class_teacher = teacher.is_class_teacher
            if is_class_teacher:
                has_class, class_is = get_class_of_class_teacher(teacher)
            else:
                return JsonResponse({"status":"unsuccessful", "message":"You are not class teacher."})
        else:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
        if not has_class:
            return JsonResponse({"status":"unsuccessful", "message":"You have not been assigned any class. Kindly contact school authority."})

        create_or_update = request.POST.get('create_or_update',None)
        if create_or_update=='create':
            subject_name = request.POST.get('subject_name',None)
            teacher_id = request.POST.get('teacher_id',None)
            #print(subject_name,teacher_id)
            info_status = {}
            try:
                if teacher_id!=None:
                    teacher = get_teacher_by_id(teacher_id)
                    subject = Subject.objects.create(subject_name=subject_name,teacher=teacher,
                                            class_is=class_is)
                else:
                    subject = Subject.objects.create(subject_name=subject_name,class_is=class_is)
                
                subject.save()
                info_status['status'] = 'success'
                info_status['message'] = 'Created subject'
            except:
                info_status['status'] = 'unsuccessful'
                info_status['message'] = "cannot create subject"
        else:
            #update
            subject_id = request.POST.get('subject_id',None)
            teacher_id = request.POST.get('teacher_id',None)
            subject_name = request.POST.get('subject_name',None)
            # link = request.POST.get('link',None)

            info_status = {}
            try:
                subject = Subject.objects.filter(id=subject_id)[0]
                if teacher_id!=None:
                    teacher = get_teacher_by_id(teacher_id)
                    subject.teacher = teacher 
                if subject_name!=None:
                    subject.subject_name = subject_name
        
                
                
                subject.save()
                #print("here 1")
                info_status['status'] = 'success'
                info_status['message'] = 'Updated subject'
            except:
                info_status['status'] = 'unsuccessful'
                info_status['message'] = "cannot update subject"
        

        

        return JsonResponse(info_status)
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})
    


def create_or_update_schedule_for_class(schedule_data_list, class_id):
    try:
        for schedule_data in schedule_data_list:
            #print(schedule_data)
            slot_id = schedule_data[0]
            subject_ids = schedule_data[1]
            try:
                schedule = Schedule.objects.filter(subject__class_is=class_id).filter(slot=slot_id)[0]
            except:
                #print("going to create")
                slot = Slot.objects.filter(id=slot_id)[0]
                #print("going to create")
                schedule = Schedule(slot=slot)
                schedule.save()
            schedule.subject.clear()
            for subject_id in subject_ids:
                subject = Subject.objects.filter(id=subject_id)[0]
                # add does not cause duplication in many to many
                schedule.subject.add(subject)
            
                
            
        return {"info":"created schedule successfully",'status':'success'}
    except Exception as e:
        print(str(e))
        return {'info':'failed to create schedule','status':'unsuccessful'}
 



@csrf_exempt
@require_http_methods(["POST"])
def create_or_update_schedule(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    try:
        token = json.loads(request.body)['token']
    except:
        token = None
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    #is_authority = is_logged_as_authority(request)
    try:
        if is_teacher:
            teacher = user.teacher
            is_class_teacher = teacher.is_class_teacher
            if is_class_teacher:
                has_class, class_is = get_class_of_class_teacher(teacher)
            else:
                return JsonResponse({"status":"unsuccessful", "message":"You are not class teacher."})
        else:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
        if not has_class:
            return JsonResponse({"status":"unsuccessful", "message":"You have not been assigned any class. Kindly contact school authority."})

        
        schedule_data_list = json.loads(request.body)['schedule_data_list']
        #print(schedule_data_list, 'schedule_data_list')
        if len(schedule_data_list)==0:
            return JsonResponse({"status":'unsuccessful','message':'no schedule data provided.'})
        
        # current_slots_for_school = Slot.objects.filter(school=school)
        # if len(current_slots_for_school)>0:
        #     return JsonResponse({"status":"unsuccessful","info":"slot already exists. kindly use modify slots."})

        class_id = class_is.id
        info_status = create_or_update_schedule_for_class(schedule_data_list, class_id)

        if info_status.get('status')=='success':
            return JsonResponse({"status":info_status['status'], 'message':info_status['info']})
        else:
            return JsonResponse({"status":"unsuccessful", "message":"Could not create schedule. "+ info_status.get('info')})
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})

@csrf_exempt
@require_http_methods(["POST"])
def delete_schedule(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})


    is_teacher = is_logged_as_teacher(user)
    #is_authority = is_logged_as_authority(request)
    try:
        if is_teacher:
            teacher = user.teacher
            is_class_teacher = teacher.is_class_teacher
            if is_class_teacher:
                has_class, class_is = get_class_of_class_teacher(teacher)
            else:
                return JsonResponse({"status":"unsuccessful", "message":"You are not class teacher."})
        else:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
        if not has_class:
            return JsonResponse({"status":"unsuccessful", "message":"You have not been assigned any class. Kindly contact school authority."})

        class_id = class_is.id
        Schedule.objects.filter(subject__class_is=class_id).delete()

        return JsonResponse({"status":"successful","message":"schedule deleted for class "+class_is.class_name+"-"+class_is.section})
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})


@csrf_exempt
@require_http_methods(["POST"])
def get_teacher_list(request):
    if request.method != 'POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        if not is_logged_as_teacher(user):
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        school_id = user.teacher.school.id
        message = [teacher.get_summary_for_teacher() for teacher in Teacher.objects.filter(school__id=school_id)]
        return JsonResponse({"status":"success", "message":message})
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def get_slot_list(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    
    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    #if not user.teacher.is_class_teacher:
    #    return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
    try:
        school_id = user.teacher.school.id
        school = School.objects.get(id=school_id)
        slot_list = school.slot_set.all()
        message = list(slot_list.values())
        return JsonResponse({"status":"success","message":message})
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})

@csrf_exempt
@require_http_methods(["POST"])
def get_schedule_list(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    if not user.teacher.is_class_teacher:
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
    try:
        class_teacher_id = user.teacher.id
        school = School.objects.get(id=user.teacher.school.id)
        

        class_ = Class.objects.get(class_teacher_id=class_teacher_id)
        message = [schedule.get_summary() for schedule in Schedule.objects.filter(subject__class_is=class_.id).distinct()]
        return JsonResponse({"status":"success","message":message})
        """schedule_list = []
        for schedule in Schedule.objects.filter(subject__class_is=class_.id).distinct():
            schedule_dict = {}
            schedule_dict['schedule_id'] = schedule.id
            schedule_dict['slot_id'] = schedule.slot_id
            schedule_dict['subject'] = [subject['id'] for subject in schedule.subject.all().values()]
            schedule_list.append(schedule_dict)
        return JsonResponse(dict(schedule_list=schedule_list))"""
    except Exception as e:
        print(e)
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})


@csrf_exempt
@require_http_methods(["POST"])
def get_class_subject_list(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    #is_authority = is_logged_as_authority(request)
    try:
        if is_teacher:
            teacher = user.teacher
            is_class_teacher = teacher.is_class_teacher
            if is_class_teacher:
                has_class, class_is = get_class_of_class_teacher(teacher)
            else:
                return JsonResponse({"status":"unsuccessful", "message":"You are not class teacher."})
        else:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
        if not has_class:
            return JsonResponse({"status":"unsuccessful", "message":"You have not been assigned any class. Kindly contact school authority."})

        message = [subject.get_summary_for_class_teacher() for subject in Subject.objects.filter(class_is=class_is)]
        return JsonResponse({"status":"success","message":message})
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})


@csrf_exempt
@require_http_methods(["POST"])
def get_subject_list(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    teacher_id = user.teacher.id
    try:
        #print(Subject.objects.filter(teacher=teacher_id))
        message = [subject.get_summary() for subject in Subject.objects.filter(teacher=teacher_id)]
        return JsonResponse({"status":"success","message":message})
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})

@csrf_exempt
@require_http_methods(["POST"])
def get_schedule_list_for_teacher(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    teacher = user.teacher
    school = user.teacher.school
    #try:
    message = []

    for slot in Slot.objects.filter(school=school):
        summary_dict = {}
        summary_dict['slot_id'] = slot.id
        summary_dict['day'] = slot.day
        summary_dict['period_number'] = slot.period_number
        summary_dict['class_name'] = []
        summary_dict['section'] = []
        summary_dict['subject_id'] = []
        summary_dict['subject_name'] = []
        try:
            schedule_qs = Schedule.objects.filter(slot=slot,subject__teacher=teacher)
            for schedule in schedule_qs:
                subject = schedule.subject.all().get(teacher=teacher)
                summary_dict['class_name'].append(subject.class_is.class_name)
                summary_dict['section'].append(subject.class_is.section)
                summary_dict['subject_id'].append(subject.id)
                summary_dict['subject_name'].append(subject.subject_name)
            if subject.alternate_link:
                summary_dict['link'] = subject.alternate_link
                summary_dict['password'] = subject.alternate_password
                summary_dict['description'] = subject.alternate_description
            else:
                summary_dict['link'] = subject.link
                summary_dict['password'] = ""
                summary_dict['description'] = "Google Meet"
        except:
            summary_dict['link'] = ""
            summary_dict['password'] = ""
            summary_dict['description'] = "Not available"
        #print(summary_dict)
        message.append(summary_dict)
    return JsonResponse({"status":"success","message":message})
    #except:
    #    return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})



@csrf_exempt
@require_http_methods(["POST"])
def get_class_teacher_dashboard(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    
    try:
        if is_teacher:
            teacher = user.teacher
            is_class_teacher = teacher.is_class_teacher
            if is_class_teacher:
                has_class, class_is = get_class_of_class_teacher(teacher)
            else:
                return JsonResponse({"status":"unsuccessful", "message":"You are not class teacher."})
        else:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
        
        summary = {}
        summary['name'] = user.first_name
        student_list = []

        if has_class:
            summary['class_name'] = class_is.class_name
            summary['section'] = class_is.section
            summary['class_strength'] = Student.objects.filter(class_is=class_is).count()
            summary['attendance_today'] = Attendance.objects.filter(student__class_is=class_is,date=date.today()).count()
            summary['total_working_days'] = Attendance.objects.filter(student__class_is=class_is).values('date').distinct().count()

            for student in Student.objects.filter(class_is=class_is):
                summary_dict = {}
                summary_dict['roll_number'] = student.roll
                summary_dict['student_name'] = student.user.first_name
                summary_dict['present_today'] = Attendance.objects.filter(student=student,date=date.today()).exists()
                summary_dict['cumulative_attendance'] = Attendance.objects.filter(student=student).count()
                student_list.append(summary_dict)
        return JsonResponse({"status":"success","message":{"summary":summary,"student_list":student_list}})
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})


@csrf_exempt
@require_http_methods(["POST"])
def get_teacher_dashboard(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    teacher = user.teacher

    try:
        summary = {}
        summary['name'] = user.first_name

        subject_name = ""
        subject_link = ""

        subject_list = []
        for subject in Subject.objects.filter(teacher=teacher):
            summary_dict = {}
            summary_dict['subject_name'] = subject.subject_name
            summary_dict['class_name'] = subject.class_is.class_name
            summary_dict['section'] = subject.class_is.section
            subject_list.append(summary_dict)

            try:
                schedule = Schedule.objects.get(subject=subject)
                #print(schedule)
                # IST?
                current_time = datetime.now().time()
                if current_time>schedule.slot.start_time and current_time<schedule.slot.end_time:
                    subject_name = subject.subject_name
                    subject_link = subject.link
            except:
                pass

        return JsonResponse({"status":"success","message":{"summary":summary,"subject_name":subject_name,"subject_link":subject_link,"subject_list":subject_list}})

    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})


def create_calendar_events(class_is):
    try:
        service = get_calendar_service()
        
        for subject in class_is.subject_set.all():
            #print("checking for "+subject.subject_name)
            if subject.link == None or subject.link=="":
                subject_name = subject.subject_name
                #print("generating for "+subject_name)

                # working version
                today = datetime.now().date()
                start = datetime(today.year, today.month, today.day, 6)
                end = datetime(today.year, today.month, today.day, 18)
                start = start.isoformat()
                end = end.isoformat()

                attendees_list = []
                if subject.teacher:
                    if subject.teacher.user.email!=None and subject.teacher.user.email!="":
                        email_dict ={'email':subject.teacher.user.email}
                        attendees_list.append(email_dict)
                school = class_is.school
                for authority in school.authority_set.all():
                    if authority.user.email:
                        email_dict ={'email':authority.user.email}
                        attendees_list.append(email_dict)
                #print(attendees_list)
                event_result = service.events().insert(calendarId='primary',
                    body={ 
                        "summary": subject_name, 
                        "start": {"dateTime": start, "timeZone": 'Asia/Kolkata'}, 
                        "end": {"dateTime": end, "timeZone": 'Asia/Kolkata'},
                        'attendees':attendees_list,
                        'conferenceData': {
                        'conferenceId':'hangoutsMeet'
                        },
                        "recurrence": [
                            'RRULE:FREQ=DAILY'
                        ],
                        "transparency":"transparent"
                    }
                ).execute()

                print("created event")
                #print(event_result)
                #print(event_result.get('hangoutLink'))
                subject.link = event_result.get('hangoutLink')
                subject.save()
                
        return "success"

    except Exception as e:
        print(e)
        return "failure"
        

@csrf_exempt
@require_http_methods(["POST"])
def generate_subject_links(request):
    status = "failure"
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    
    try:
        if is_teacher:
            teacher = user.teacher
            is_class_teacher = teacher.is_class_teacher
            if is_class_teacher:
                has_class, class_is = get_class_of_class_teacher(teacher)
            else:
                return JsonResponse({"status":"unsuccessful", "message":"You are not class teacher."})
        else:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        status = create_calendar_events(class_is)
        if status == "success":
            status = sync_schedule(teacher.school)
        return JsonResponse({"status":status})

    except:
        return JsonResponse({"status":"unsuccessful", "message":"Server Error"})

@csrf_exempt
@require_http_methods(["POST"])
def get_dashboard_class_details_for_ct(request):
    status = "failure"
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    
    try:
        if is_teacher:
            teacher = user.teacher
            is_class_teacher = teacher.is_class_teacher
            if is_class_teacher:
                has_class, class_ = get_class_of_class_teacher(teacher)
            else:
                return JsonResponse({"status":"unsuccessful", "message":"You are not class teacher."})
        else:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        class_id = class_.id

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
            attendance_ = Attendance.objects.filter(date=date,student__class_is=class_).count()
            denominator = 0
            numerator = 0
            attentiveness = None
            for attendance in Attendance.objects.filter(date=date,student__class_is=class_):
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
        print(e)
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def get_dashboard_student_details_for_ct(request):
    status = "failure"
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    
    try:
        if is_teacher:
            teacher = user.teacher
            is_class_teacher = teacher.is_class_teacher
            if is_class_teacher:
                has_class, class_is = get_class_of_class_teacher(teacher)
            else:
                return JsonResponse({"status":"unsuccessful", "message":"You are not class teacher."})
        else:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        student_id = request.POST.get('student_id')
        student = Student.objects.get(id=student_id)

        if student.class_is != class_is:
            return JsonResponse({"status":"unsuccessful", "message":"Student does not belong to your class"})

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
        print(e)
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def get_dashboard_subject_list(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    teacher = user.teacher

    try:
        performance_list = []
        for subject in Subject.objects.filter(teacher=teacher):
            performance_dict = {}
            performance_dict['subject_id'] = subject.id
            performance_dict['subject_name'] = subject.subject_name
            performance_dict['class_name'] = subject.class_is.class_name
            performance_dict['section'] = subject.class_is.section

            denominator = 0
            numerator = 0
            average_performance = None
            for submission in Class_test_submission.objects.filter(class_test__subject=subject):
                if submission.marks and submission.class_test.maximum_marks:
                    denominator += submission.class_test.maximum_marks
                    numerator += submission.marks
            if denominator != 0:
                average_performance = round(numerator/denominator*100, 2)

            performance_dict['average_performance'] = str(average_performance)
            performance_list.append(performance_dict)

        return JsonResponse({"status":"success", "performance_list":performance_list})

    except Exception as e:
        print(e)
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def get_dashboard_subject_details(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    teacher = user.teacher
    subject_id = request.POST.get('subject_id')
    subject = Subject.objects.get(id=subject_id)

    try:
        summary = {}
        summary['subject_id'] = subject.id
        summary['subject_name'] = subject.subject_name
        summary['class_name'] = subject.class_is.class_name
        summary['section'] = subject.class_is.section

        student_list = []
        for student in subject.class_is.student_set.all():
            #print(student)
            student_dict = {}
            student_dict['student_id'] = student.id
            student_dict['student_name'] = student.user.first_name
            student_dict['roll_number'] = student.roll
            student_dict['parent_mob_no'] = student.parent_mob_no_1


            total_denominator = 0
            total_numerator = 0
            average_performance = None
            performance_list = []
            for class_test in Class_test.objects.filter(subject=subject):
                performance_dict = {}
                performance_dict['class_test_name'] = class_test.class_test_name
                performance_dict['date'] = class_test.start_time.date()
                performance = None
                try:
                    submission = Class_test_submission.objects.get(class_test=class_test,student=student)
                    if submission.marks and submission.class_test.maximum_marks:
                        denominator = submission.class_test.maximum_marks
                        numerator = submission.marks
                        total_denominator += submission.class_test.maximum_marks
                        total_numerator += submission.marks
                    if denominator != 0:
                        performance = round(numerator/denominator*100, 2)
                except:
                    pass
                performance_dict['performance'] = str(performance)
                performance_list.append(performance_dict)
            if total_denominator != 0:
                average_performance = round(total_numerator/total_denominator*100, 2)

            student_dict['average_performance'] = str(average_performance)
            student_dict['performance_list'] = performance_list
            #print('student_dict',student_dict)
            #print('student_list',student_list)
            student_list.append(student_dict)
        #print(student_list)
        return JsonResponse({"status":"success", "summary":summary, "student_list":student_list})

    except Exception as e:
        print(e)
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})

@csrf_exempt
@require_http_methods(["POST"])
def reset_student_password(request):
    status = "failure"
    if request.method!='POST':
        return JsonResponse({"status":"failure","message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    
    try:
        if is_teacher:
            teacher = user.teacher
            is_class_teacher = teacher.is_class_teacher
            if is_class_teacher:
                has_class, class_is = get_class_of_class_teacher(teacher)
            else:
                return JsonResponse({"status":"unsuccessful", "message":"You are not class teacher."})
        else:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        username = request.POST.get('username')
        password = request.POST.get('password')

        if not (username and password):
            return JsonResponse({"status":"unsuccessful", "message":"Username and new password required"})
        else:
            pass
        try:
            student = Student.objects.get(user__username=username)
        except:
            return JsonResponse({"status":"unsuccessful", "message":"Username does not belong to any student"})

        if student.class_is != class_is:
            return JsonResponse({"status":"unsuccessful", "message":"Student does not belong to your class"})

        student.user.set_password(password)
        student.first_password = password
        student.user.save()
        student.save()
        message = "Password reset for student "+username
        return JsonResponse({"status":"success", "message":message})

    except Exception as e:
        print(e)
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})

@csrf_exempt
@require_http_methods(["POST"])
def set_alternate_link(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    teacher = user.teacher
    subject_id = request.POST.get('subject_id')
    subject = Subject.objects.get(id=subject_id)

    if subject.teacher != teacher:
        return JsonResponse({"status":"unsuccessful", "message":"Subject is not taught by you"})

    alternate_link = request.POST.get('alternate_link',"")
    alternate_password = request.POST.get('alternate_password',"")
    alternate_description = request.POST.get('alternate_description',"")

    try:
        subject.alternate_link = alternate_link
        subject.alternate_password = alternate_password
        subject.alternate_description = alternate_description
        subject.save()
        return JsonResponse({"status":"success","message":"Alternate link saved"})
    except Exception as e:
        print(e)
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})

def sync_schedule(school):
    try:
        for teacher in school.teacher_set.all():
            for slot in school.slot_set.all():
                schedule_qs = Schedule.objects.filter(subject__teacher=teacher,slot=slot)
                link = ""
                alternate_link = ""
                alternate_description = ""
                alternate_password = ""
                if len(schedule_qs) > 1:
                    for schedule in schedule_qs:
                        subject = schedule.subject.all().get(teacher=teacher)
                        # give preference to the one with alternate link
                        # not really neccessary to do so
                        if subject.alternate_link:
                            if subject.link:
                                link = subject.link
                            alternate_link = subject.alternate_link
                            alternate_description = subject.alternate_description
                            alternate_password = subject.alternate_password
                        if subject.link:
                            if not link:
                                link = subject.link

                    for schedule in schedule_qs:
                        subject = schedule.subject.all().get(teacher=teacher)
                        subject.link = link
                        subject.alternate_link = alternate_link
                        subject.alternate_description = alternate_description
                        subject.alternate_password = alternate_password
                        subject.save()

        return "success"
    except Exception as e:
        print(e)
        return "failure"


@csrf_exempt
@require_http_methods(["POST"])
def delete_subject_teacher(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    
    try:
        if is_teacher:
            teacher = user.teacher
            is_class_teacher = teacher.is_class_teacher
            if is_class_teacher:
                has_class, class_is = get_class_of_class_teacher(teacher)
            else:
                return JsonResponse({"status":"unsuccessful", "message":"You are not class teacher."})
        else:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        subject_id = request.POST.get('subject_id')
    
        try:
            subject = Subject.objects.get(id=subject_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid subject."})

        if subject.class_is != class_is:
            return JsonResponse({"status":"failure","message":"Subject does not belong to your class."})

        subject.teacher = None
        subject.save()
        return JsonResponse({"status":"success","message":"Subject teacher deleted."})
    
    except Exception as e:
        print(e)
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})