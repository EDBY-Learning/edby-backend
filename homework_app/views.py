import json

from django.shortcuts import render
from core.models import *
from core.views import has_session_expired_and_update
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,JsonResponse
import django.utils.dateparse as dp
from datetime import datetime
import pytz
from django.conf import settings as conf_settings
from django.views.decorators.http import require_http_methods

BACKEND_TIME_ZONE = pytz.timezone(conf_settings.TIME_ZONE)
MAX_FILE_SIZE_ALLOWED = conf_settings.MAX_FILE_SIZE_ALLOWED
ALLOWED_DELAY_UPLOAD_IN_MINUTES = 5
ALLOWED_LATE_SUBMISSION_IN_MINUTES = 5

@csrf_exempt
def is_logged_as_student(user):
    try:
        is_student = user.student
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
    
# Create your views here.
@csrf_exempt
@require_http_methods(["POST"])
def create_or_update_homework(request):
    #print(request.FILES.keys())
    #print(dir(request))
    #print(request.POST)
    
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    if not is_teacher:
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
    else:
        teacher = user.teacher

    #print(json.loads(request.body)['file'])
    if len(request.FILES.keys())!=0:
        key = list(request.FILES.keys())[0]
        file_handle = request.FILES[key]
        #check for maximum allowed file size
        if file_handle.size>float(MAX_FILE_SIZE_ALLOWED):
            return JsonResponse({'status':'unsuccessful', 
                            'message':'File size is greater than allowed size( %s Kb )'%(float(MAX_FILE_SIZE_ALLOWED)/1024)})
    
    try:
        homework_name = request.POST.get('homework_name',None)
        description = request.POST.get('description',"")
        start_time = request.POST.get('start_time',None)
        end_time = request.POST.get('end_time',None)
        is_graded = request.POST.get('is_graded',None)
        if is_graded:
            if is_graded=='False' or is_graded=='false':
                is_graded = False
            elif is_graded == 'True' or is_graded=='true':
                is_graded = True

        maximum_marks = request.POST.get('maximum_marks',None)
        is_published = request.POST.get('is_published',None)
        year = request.POST.get('year',None)
        subject_id = request.POST.get('subject_id',None)
        homework_id = request.POST.get('homework_id',None)

        if homework_id==None:
            try:
                subject = Subject.objects.filter(id=subject_id)[0]
            except Exception as e:
                print(str(e))
                return JsonResponse({"status":'unsuccessful','message':'No such subject.'})
            if teacher.id!=subject.teacher.id:
                return JsonResponse({'status':'unsuccessful', 'message':'subject teacher does not match.'})

        #homework_id none implies homework create
        if homework_id==None:
            try:                

                if start_time==None or end_time==None:
                    return JsonResponse({'status':'unsuccessful', 'message':'Provide start/end time.'})

                start_time = dp.parse_datetime(start_time)

                end_time = dp.parse_datetime(end_time)
                if start_time<datetime.now().astimezone(BACKEND_TIME_ZONE):
                    return JsonResponse({'status':'unsuccessful', 'message':'Select future start_time'})
                if end_time<start_time:
                    return JsonResponse({'status':'unsuccessful', 'message':'Select start_time should be past end_time.'})
                print('abc')
                homework = Homework.objects.create(subject=subject, homework_name=homework_name,
                                                    description=description, start_time=start_time,
                                                    end_time=end_time, is_graded=is_graded, maximum_marks=maximum_marks,year=year)
                                            
                print('cde')
                key = list(request.FILES.keys())[0]
                homework_file = request.FILES[key]
                homework.homework_file = homework_file
                if is_published!=None:
                    homework.is_published = is_published
                    if is_published==True:
                        homework.start_time = datetime.now().astimezone(BACKEND_TIME_ZONE)
                homework.save()

                return JsonResponse({"status":'success', 'message':'Created Homework'})
            except Exception as e:
                print('here is error',str(e))
                message = 'Cannot create homework. Make sure to send datetime in iso format with timezone. ex 2020-07-16T19:07:56.059532+00:00'
                return JsonResponse({"status":'unsuccessful','message':message})
        #for update
        homework_query = Homework.objects.filter(id=homework_id)
        if len(homework_query)!=0:
            homework = homework_query[0]
            if homework.subject.teacher.id!=user.teacher.id:
                return JsonResponse({"status":'unsuccessful','message':'Could not update. Subject teacher does not match.'})
        else:
            return JsonResponse({"status":'unsuccessful','message':'No such homework exists'})
        if homework_name!=None:
            homework.homework_name = homework_name
        if description!=None:
            homework.description = description

        if start_time!=None:
            start_time = dp.parse_datetime(start_time)
            if start_time<datetime.now().astimezone(BACKEND_TIME_ZONE):
                    return JsonResponse({'status':'unsuccessful', 'message':'start_time should be in future.'})
            if end_time!=None:
                end_time = dp.parse_datetime(end_time)
                if end_time<start_time:
                    return JsonResponse({'status':'unsuccessful', 'message':'start_time should be past end_time.'})
            else:
                if homework.end_time<start_time:
                    return JsonResponse({'status':'unsuccessful', 'message':'start_time should be past end_time.'})
            homework.start_time = start_time

        if end_time!=None:
            if start_time==None:
                end_time = dp.parse_datetime(end_time)
                if end_time<homework.start_time:
                    return JsonResponse({'status':'unsuccessful', 'message':'start_time should be past end_time.'})
            homework.end_time = end_time

        if is_graded!=None:
            homework.is_graded = is_graded
        if maximum_marks!=None:
            homework.maximum_marks = maximum_marks
        if is_published!=None:
            homework.is_published = is_published
            if is_published==True:
                homework.start_time = datetime.now().astimezone(BACKEND_TIME_ZONE)
        if  True:
            homework.year = datetime.now().astimezone(BACKEND_TIME_ZONE).year
        if len(request.FILES.keys())!=0:
            key = list(request.FILES.keys())[0]
            homework_file = request.FILES[key]
            #delete old file.
            homework.homework_file.delete(False) 
            homework.homework_file = homework_file

        homework.save()

        return JsonResponse({'status':'success', 'message':'Updated homework'})
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})

@csrf_exempt
@require_http_methods(["POST"])
def publish_homework(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        is_teacher = is_logged_as_teacher(user)
        if not is_teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
        else:
            teacher = user.teacher

        homework_id = request.POST.get('homework_id',None)
        if homework_id:
            homework = Homework.objects.get(id=homework_id)
            if homework.subject.teacher.id!=user.teacher.id:
                return JsonResponse({"status":'unsuccessful','message':'Could not update. Subject teacher does not match.'})
            else:
                homework.is_published = True
                homework.start_time = datetime.now().astimezone(BACKEND_TIME_ZONE)
                homework.save()
            return JsonResponse({"status":"success","message":"Homework published"})
        else:
            return JsonResponse({"status":"unsuccessful","message":"Please select homework"})
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def create_or_update_homework_submission(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_student = is_logged_as_student(user)
    if not is_student:
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
    else:
        student = user.student

    if len(request.FILES.keys())!=0:
        key = list(request.FILES.keys())[0]
        file_handle = request.FILES[key]
        #check for maximum allowed file size
        if file_handle.size>float(MAX_FILE_SIZE_ALLOWED):
            return JsonResponse({'status':'unsuccessful', 
                            'message':'File size is greater than allowed size( %s Kb )'%(float(MAX_FILE_SIZE_ALLOWED)/1024)})

    try:
        homework_id = request.POST.get('homework_id',None)
        submission_time = request.POST.get('submission_time',None)
        submission_id = request.POST.get('submission_id',None)
        print(submission_time,' sub time')
        if homework_id==None and submission_id==None:
            return JsonResponse({'status':'unsuccessful', 'message':'Please provide homework id or submission id.'})

        #submission id is none implies create new submission
        if submission_id==None:
            homework_query = Homework.objects.filter(id=homework_id)
            if len(homework_query)!=0:
                homework = homework_query[0]
            else:
                return JsonResponse({"status":'unsuccessful','message':'No such homework.'})
            if homework.is_published==False:
                return JsonResponse({"status":'unsuccessful','message':'Homework is not published yet.'})

            #check if already there is submission
            try:
                homework_submission =  Homework_submission.objects.get(student=student, homework=homework)
            except:
                homework_submission = Homework_submission.objects.create(student=student, homework=homework)
            try:
                # if homework.subject.class_is.id!=student.class_is.id:
                #     return JsonResponse({"status":'unsuccessful','message':'Student is not of same class'})
                if submission_time!=None:
                    submission_time = dp.parse_datetime(submission_time)
                else:
                    submission_time = datetime.now().astimezone(BACKEND_TIME_ZONE)

                if submission_time>datetime.now().astimezone(BACKEND_TIME_ZONE):
                    return JsonResponse({"status":'unsuccessful','message':'Submission time is not valid.'})
                else:
                    delta = datetime.now().astimezone(BACKEND_TIME_ZONE)-submission_time
                    if delta.seconds>ALLOWED_DELAY_UPLOAD_IN_MINUTES*60:
                        return JsonResponse({"status":'unsuccessful','message':'Submission time is too late than current time.'})
                    if homework.start_time>submission_time:
                        return JsonResponse({"status":'unsuccessful','message':'Submission is not open yet.'})
                    if homework.end_time<submission_time:
                        delta = submission_time - homework.end_time
                        if delta.seconds>ALLOWED_LATE_SUBMISSION_IN_MINUTES*60:
                            return JsonResponse({"status":'unsuccessful','message':'Late submission.'})
                homework_submission.submission_time = submission_time
                #print(request.FILES.keys())
                key = list(request.FILES.keys())[0]
                submission_file = request.FILES[key]
                homework_submission.submission_file.delete(False)
                homework_submission.submission_file = submission_file
                homework_submission.save()
                return JsonResponse({"status":'success', 'info':{"submission_id":homework_submission.id}})
            except Exception as e:
                print(str(e))
                return JsonResponse({"status":'unsuccessful','message':'Cannot create homework submission'})
        
        #for update
        """
        homework_submission_query = Homework_submission.objects.filter(id=submission_id)
        if len(homework_submission_query)!=0:
            homework_submission = homework_submission_query[0]
            if homework_submission.student.id!=student.id:
                return JsonResponse({"status":'unsuccessful','message':'Could not update. Not same student'})
        else:
            return JsonResponse({"status":'unsuccessful','message':'No such homework submission exists'})
        
        homework = homework_submission.homework
        if len(request.FILES.keys())!=0:
            key = list(request.FILES.keys())[0]
            submission_file = request.FILES[key]
            #delete old file.
            homework_submission.submission_file.delete(False) 
            homework_submission.submission_file = submission_file
        if submission_time!=None:
            submission_time = dp.parse_datetime(submission_time)
        else:
            submission_time = datetime.now().astimezone(BACKEND_TIME_ZONE)
        if submission_time>datetime.now().astimezone(BACKEND_TIME_ZONE):
            return JsonResponse({"status":'unsuccessful','message':'Submission time is not valid.'})
        else:
            delta = datetime.now().astimezone(BACKEND_TIME_ZONE)-submission_time
            if delta.seconds>ALLOWED_DELAY_UPLOAD_IN_MINUTES*60:
                return JsonResponse({"status":'unsuccessful','message':'Submission time is too late than current time.'})
            if homework.end_time<submission_time:
                delta = submission_time - homework.end_time
                if delta.seconds>ALLOWED_LATE_SUBMISSION_IN_MINUTES*60:
                    return JsonResponse({"status":'unsuccessful','message':'Late submission.'})
        homework_submission.submission_time = submission_time
        homework_submission.save()
        return JsonResponse({'status':'successful', 'message':'Updated homework submission.'})
        """
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})


@csrf_exempt
@require_http_methods(["POST"])
def grade_homework_submission(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})
        
    is_teacher = is_logged_as_teacher(user)
    if not is_teacher:
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
    else:
        teacher = user.teacher
    
    if len(request.FILES.keys())!=0:
        key = list(request.FILES.keys())[0]
        file_handle = request.FILES[key]
        #check for maximum allowed file size
        if file_handle.size>float(MAX_FILE_SIZE_ALLOWED):
            return JsonResponse({'status':'unsuccessful', 
                            'message':'File size is greater than allowed size( %s Kb )'%(float(MAX_FILE_SIZE_ALLOWED)/1024)})
    
    try:
        submission_id = request.POST.get('submission_id',None)
        marks = request.POST.get('marks',None)
        if submission_id==None:
            return JsonResponse({'status':'unsuccessful', 'message':'Please provide submission id.'})

        #for update
        homework_submission_query = Homework_submission.objects.filter(id=submission_id)
        if len(homework_submission_query)!=0:
            homework_submission = homework_submission_query[0]
            if homework_submission.homework.subject.teacher.id!=teacher.id:
                return JsonResponse({"status":'unsuccessful','message':'Could not grade. Not same teacher'})
        else:
            return JsonResponse({"status":'unsuccessful','message':'No such homework submission exists'})
        
        if marks!=None:
            homework_submission.marks = marks
        
        if len(request.FILES.keys())!=0:
            key = list(request.FILES.keys())[0]
            checked_file = request.FILES[key]
            #delete old file.
            homework_submission.checked_file.delete(False) 
            homework_submission.checked_file = checked_file
        
        homework_submission.is_checked  = True
        homework_submission.save()

        return JsonResponse({'status':'success', 'message':'Graded homework submission.'})
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})

@csrf_exempt
@require_http_methods(["POST"])
def get_homework_list(request):
    status = "failure"
    if request.method != 'POST':
        message = "Invalid request"
        return JsonResponse({"status":status,"message":message})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    is_student = is_logged_as_student(user)
    subject_id = request.POST.get('subject_id')
    print(subject_id)
    if not subject_id:
        message = "Please provide subject ID"

    if(is_teacher):
        message = [homework.get_summary_for_teacher() for homework in Homework.objects.filter(subject=subject_id)]
        status = "success"
    elif(is_student):
        student_id = user.student.id
        message = [homework.get_summary_for_student(student_id) for homework in Homework.objects.filter(subject=subject_id,is_published=True)]#,,
        status = "success"
    else:
        message = "No proper authentication."

    return JsonResponse({"status":status,"message":message})

@csrf_exempt
@require_http_methods(["POST"])
def get_homework_submission_list_for_homework(request):
    status = "failure"

    if request.method != 'POST':
        message = "Invalid request"
        return JsonResponse({"status":status,"message":message})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    homework_id = request.POST.get('homework_id')
    if not homework_id:
        message = "Please provide homework ID"

    if(is_teacher):
        print('adiobfda')
        message = [submission.get_summary() for submission in Homework_submission.objects.filter(homework=homework_id)]
        status = "success"
    else:
        message = "No proper authentication."

    return JsonResponse({"status":status,"message":message})

@csrf_exempt
@require_http_methods(["POST"])
def get_homework_submission_list_for_subject(request):
    status = "failure"
    if request.method != 'POST':
        message = "Invalid request"
        return JsonResponse({"status":status,"message":message})
    
    is_student = is_logged_as_student(user)
    subject_id = request.POST.get('subject_id')
    if not subject_id:
        message = "Please provide subject ID"

    if(is_student):
        student_id = user.student.id
        message = [submission.get_summary() for submission in Homework_submission.objects.filter(student=student_id,homework__subject=subject_id)]
        status = "success"
    else:
        message = "No proper authentication."

    return JsonResponse({"status":status,"message":message})