import json

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import django.utils.dateparse as dp
from datetime import datetime
import pytz
from django.conf import settings as conf_settings

from core.models import *
from core.views import has_session_expired_and_update
from django.views.decorators.http import require_http_methods

BACKEND_TIME_ZONE = pytz.timezone(conf_settings.TIME_ZONE)
MAX_FILE_SIZE_ALLOWED = conf_settings.MAX_FILE_SIZE_ALLOWED
ALLOWED_DELAY_UPLOAD_IN_MINUTES = 5
ALLOWED_LATE_SUBMISSION_IN_MINUTES = 5

@csrf_exempt
def is_logged_as_student(user):
    if user.is_authenticated:
        try:
            is_student = user.student
            return True
        except:
            return False
    else:
        return False

@csrf_exempt
def is_logged_as_teacher(user):
    if user.is_authenticated:
        try:
            is_teacher = user.teacher
            return True
        except:
            return False
    else:
        return False

# Create your views here.
@csrf_exempt
@require_http_methods(["POST"])
def create_or_update_class_test(request):
    if request.method != 'POST':
        return JsonResponse({"status":"unsuccessful", "message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if len(request.FILES.keys())!=0:
        key = list(request.FILES.keys())[0]
        file_handle = request.FILES[key]
        #check for maximum allowed file size
        if file_handle.size>float(MAX_FILE_SIZE_ALLOWED):
            return JsonResponse({'status':'unsuccessful', 
                            'message':'File size is greater than allowed size( %s Kb )'%(float(MAX_FILE_SIZE_ALLOWED)/1024)})
    try:
        is_teacher = is_logged_as_teacher(user)
        if not is_teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
        else:
            teacher = user.teacher

        class_test_name = request.POST.get('class_test_name',None)
        description = request.POST.get('description',"")
        start_time = request.POST.get('start_time',None)
        buffer_time = request.POST.get('buffer_time',None)
        duration = request.POST.get('duration',None)
        is_graded = request.POST.get('is_graded',None)
        if is_graded:
            if is_graded=='False':
                is_graded = False
            elif is_graded == 'True':
                is_graded = True
        maximum_marks = request.POST.get('maximum_marks',None)
        is_published = request.POST.get('is_published',None)
        year = request.POST.get('year',None)
        subject_id = request.POST.get('subject_id',None)
        class_test_id = request.POST.get('class_test_id',None)

        if class_test_id==None:
            try:
                subject = Subject.objects.filter(id=subject_id)[0]
            except Exception as e:
                print(str(e))
                return JsonResponse({"status":'unsuccessful','message':'No such subject.'})
            if teacher.id!=subject.teacher.id:
                return JsonResponse({'status':'unsuccessful', 'message':'subject teacher does not match.'})

        #homework_id none implies homework create
        if class_test_id==None:
            try:
                if start_time==None or buffer_time==None or duration==None:
                    return JsonResponse({'status':'unsuccessful', 'message':'Provide all required time parameters'})
                start_time = dp.parse_datetime(start_time)
                buffer_time = dp.parse_duration(buffer_time)
                duration = dp.parse_duration(duration)
                if start_time<datetime.now().astimezone(BACKEND_TIME_ZONE):
                    return JsonResponse({'status':'unsuccessful', 'message':'start_time should be in future.'})

                

                class_test = Class_test.objects.create(subject=subject, class_test_name=class_test_name,
                                                    description=description,
                                                    start_time=start_time,
                                                    buffer_time=buffer_time,
                                                    duration=duration,
                                                    is_graded=is_graded, maximum_marks=maximum_marks,
                                                    year=year)
                                            
                #print(request.FILES.keys())
                
                key = list(request.FILES.keys())[0]
                class_test_file = request.FILES[key]
                class_test.class_test_file = class_test_file
                class_test.save()

                return JsonResponse({"status":'success', 'info':{"class_test_id":class_test.id}})
            except Exception as e:
                print(str(e))
                return JsonResponse({"status":'unsuccessful','message':'Cannot create class test'})
        
        try:

            #for update
            class_test_query = Class_test.objects.filter(id=class_test_id)
            if len(class_test_query)!=0:
                class_test = class_test_query[0]
                if class_test.subject.teacher.id!=user.teacher.id:
                    return JsonResponse({"status":'unsuccessful','message':'Could not update. Subject teacher does not match.'})
            else:
                return JsonResponse({"status":'unsuccessful','message':'No such class test exists'})
            if class_test_name!=None:
                class_test.class_test_name = class_test_name
            if description!=None:
                class_test.description = description
            if start_time!=None:
                start_time = dp.parse_datetime(start_time)
                if start_time<datetime.now().astimezone(BACKEND_TIME_ZONE):
                        return JsonResponse({'status':'unsuccessful', 'message':'Select appropriate start_time'})
                class_test.start_time = start_time
            if buffer_time!=None:
                class_test.buffer_time = dp.parse_duration(buffer_time)
            if duration!=None:
                class_test.duration =  dp.parse_duration(duration)
            if is_graded!=None:
                class_test.is_graded = is_graded
            if maximum_marks!=None:
                class_test.maximum_marks = maximum_marks
            if is_published!=None:
                class_test.is_published = is_published
                class_test.start_time = datetime.now().astimezone(BACKEND_TIME_ZONE)
            if year!=None:
                class_test.year = year
            if len(request.FILES.keys())!=0:
                key = list(request.FILES.keys())[0]
                class_test_file = request.FILES[key]
                #delete old file.
                class_test.class_test_file.delete(False) 
                class_test.class_test_file = class_test_file

            class_test.save()

            return JsonResponse({'status':'success', 'message':'Updated class test'})
        except:
            return JsonResponse({'status':'unsuccessful', 'message':'Could not updated class test'})
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})

@csrf_exempt
@require_http_methods(["POST"])
def publish_class_test(request):
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
        else:
            teacher = user.teacher

        class_test_id = request.POST.get('class_test_id',None)
        if class_test_id:
            class_test = Class_test.objects.get(id=class_test_id)
            if class_test.subject.teacher.id!=user.teacher.id:
                return JsonResponse({"status":'unsuccessful','message':'Could not update. Subject teacher does not match.'})
            else:
                class_test.is_published = True
                class_test.start_time = datetime.now().astimezone(BACKEND_TIME_ZONE)
                class_test.save()
            return JsonResponse({"status":"success","message":"Class test published"})
        else:
            return JsonResponse({"status":"unsuccessful","message":"Please select class test"})
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})



@csrf_exempt
@require_http_methods(["POST"])
def create_or_submit_class_test_submission(request):
    if request.method != 'POST':
        return JsonResponse({"status":"unsuccessful", "message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})
    if len(request.FILES.keys())!=0:
        key = list(request.FILES.keys())[0]
        file_handle = request.FILES[key]
        #check for maximum allowed file size
        if file_handle.size>float(MAX_FILE_SIZE_ALLOWED):
            return JsonResponse({'status':'unsuccessful', 
                            'message':'File size is greater than allowed size( %s Kb )'%(float(MAX_FILE_SIZE_ALLOWED)/1024)})
    try:
        is_student = is_logged_as_student(user)
        if not is_student:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
        else:
            student = user.student

        
        class_test_id = request.POST.get('class_test_id',None)
        if class_test_id==None:
           return JsonResponse({'status':'unsuccessful', 'message':'Please provide class test ID.'})

        class_test_query = Class_test.objects.filter(id=class_test_id)
        if len(class_test_query)!=0:
            class_test = class_test_query[0]
        else:
            return JsonResponse({"status":'unsuccessful','message':'No such homework.'})
        if class_test.is_published==False:
            return JsonResponse({"status":'unsuccessful','message':'Class test is not published yet.'})
        
        try:
            class_test_submission = Class_test_submission.objects.get(student=student, class_test=class_test)
            try:
                #for submission            
                if class_test_submission.student.id!=student.id:
                    return JsonResponse({"status":'unsuccessful','message':'Could not submit. Not same student'})

                class_test = class_test_submission.class_test

                if class_test_submission.is_submitted:
                    return JsonResponse({'status':'unsuccessful', 'message':'Already submitted.'})

                upload_start_time = datetime.now().astimezone(BACKEND_TIME_ZONE)
                submission_time = datetime.now().astimezone(BACKEND_TIME_ZONE)
                
                #check for correct submission
                delta = datetime.now().astimezone(BACKEND_TIME_ZONE)-submission_time
                if delta.seconds>ALLOWED_DELAY_UPLOAD_IN_MINUTES*60:
                    return JsonResponse({"status":'unsuccessful','message':'Submission time is too late than current time.'})
                if class_test_submission.start_time + class_test.duration <submission_time:
                    delta = submission_time - class_test_submission.start_time + class_test.duration
                    if delta.seconds>ALLOWED_LATE_SUBMISSION_IN_MINUTES*60:
                        return JsonResponse({"status":'unsuccessful','message':'Late submission.'})

                
                if len(request.FILES.keys())!=0:
                    key = list(request.FILES.keys())[0]
                    submission_file = request.FILES[key]
                    #delete old file if there
                    class_test_submission.submission_file.delete(False) 
                    class_test_submission.submission_file = submission_file
                else:
                    return JsonResponse({'status':'unsuccessful', 'message':'No submission file.'})


                class_test_submission.is_submitted = True
                class_test_submission.upload_start_time = upload_start_time
                class_test_submission.submission_time = submission_time

                class_test_submission.save()

                return JsonResponse({'status':'success', 'message':'successful Class test submission.','info':{"submission_id":class_test_submission.id}})
            except:
                return JsonResponse({'status':'unsuccessful', 'message':'could not do Class test submission.','info':{"submission_id":class_test_submission.id}})
            
        except:
            class_test_submission = Class_test_submission.objects.create(student=student, class_test=class_test)
            try:
                start_time = datetime.now().astimezone(BACKEND_TIME_ZONE)
                if start_time < class_test.start_time:
                    return JsonResponse({"status":'unsuccessful','message':'Test has not started yet.'})
                if start_time > class_test.start_time + class_test.buffer_time + class_test.duration:
                    return JsonResponse({"status":'unsuccessful','message':'Test has ended.'})

                if start_time>class_test.start_time + class_test.buffer_time:
                    start_time = class_test.start_time + class_test.buffer_time

                class_test_submission.start_time = start_time
                    
                #print(request.FILES.keys()
                class_test_submission.save()
                return JsonResponse({"status":'successful', 'info':{"submission_id":class_test_submission.id}})
            except Exception as e:
                print(str(e))
                return JsonResponse({"status":'unsuccessful','message':'Cannot create class test submission'})

    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})



@csrf_exempt
@require_http_methods(["POST"])
def grade_class_test_submission(request):
    if request.method != 'POST':
        return JsonResponse({"status":"unsuccessful", "message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if len(request.FILES.keys())!=0:
        key = list(request.FILES.keys())[0]
        file_handle = request.FILES[key]
        #check for maximum allowed file size
        if file_handle.size>float(MAX_FILE_SIZE_ALLOWED):
            return JsonResponse({'status':'unsuccessful', 
                            'message':'File size is greater than allowed size( %s Kb )'%(float(MAX_FILE_SIZE_ALLOWED)/1024)})
    try:
        is_teacher = is_logged_as_teacher(user)
        if not is_teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
        else:
            teacher = user.teacher
        
        submission_id = request.POST.get('submission_id',None)
        marks = request.POST.get('marks',None)
        if submission_id==None:
           return JsonResponse({'status':'unsuccessful', 'message':'Please provide submission id.'})

        #for update
        class_test_submission_query = Class_test_submission.objects.filter(id=submission_id)
        if len(class_test_submission_query)!=0:
            class_test_submission = class_test_submission_query[0]
            if class_test_submission.class_test.subject.teacher.id!=teacher.id:
                return JsonResponse({"status":'unsuccessful','message':'Could not grade. Not same teacher'})
        else:
            return JsonResponse({"status":'unsuccessful','message':'No such class test submission exists'})
        
        if marks!=None:
            class_test_submission.marks = marks
        
        if len(request.FILES.keys())!=0:
            key = list(request.FILES.keys())[0]
            checked_file = request.FILES[key]
            #delete old file if there
            class_test_submission.checked_file.delete(False) 
            class_test_submission.checked_file = checked_file
        
        class_test_submission.is_checked  = True
        class_test_submission.save()

        return JsonResponse({'status':'success', 'message':'Graded class test submission.'})
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def get_class_test_list(request):
    status = "unsuccessful"
    if request.method != 'POST':
        message = "Invalid request"
        return JsonResponse({"status":status,"message":message})
    
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        is_teacher = is_logged_as_teacher(user)
        is_student = is_logged_as_student(user)
        subject_id = request.POST.get('subject_id')
        if not subject_id:
            message = "Please provide subject ID"

        if(is_teacher):
            message = [class_test.get_summary_for_teacher() for class_test in Class_test.objects.filter(subject=subject_id)]
            status = "success"
        elif(is_student):
            student_id = user.student.id
            message = [class_test.get_summary_for_student(student_id) for class_test in Class_test.objects.filter(subject=subject_id,is_published=True)]
            status = "success"
        else:
            message = "No proper authentication."
        
        return JsonResponse({"status":status,"message":message})
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})

@csrf_exempt
@require_http_methods(["POST"])
def get_class_test_submission_list_for_class_test(request):
    status = "unsuccessful"

    if request.method != 'POST':
        message = "Invalid request"
        return JsonResponse({"status":status,"message":message})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        is_teacher = is_logged_as_teacher(user)
        class_test_id = request.POST.get('class_test_id')
        if not class_test_id:
            message = "Please provide class_test ID"

        if(is_teacher):
            message = [submission.get_summary() for submission in Class_test_submission.objects.filter(class_test=class_test_id)]
            status = "success"
        else:
            message = "No proper authentication."

        return JsonResponse({"status":status,"message":message})
    except Exception as e:
        print(str(e))
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})

@csrf_exempt
@require_http_methods(["POST"])
def get_class_test_submission_list_for_subject(request):
    status = "unsuccessful"
    
    if request.method != 'POST':
        message = "Invalid request"
        return JsonResponse({"status":status,"message":message})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:    
        is_student = is_logged_as_student(user)
        subject_id = request.POST.get('subject_id')
        if not subject_id:
            message = "Please provide subject ID"

        if(is_student):
            student_id = user.student.id
            message = [submission.get_summary() for submission in Class_test_submission.objects.filter(student=student_id,class_test__subject=subject_id)]
            status = "success"
        else:
            message = "No proper authentication."

        return JsonResponse({"status":status,"message":message})
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})
