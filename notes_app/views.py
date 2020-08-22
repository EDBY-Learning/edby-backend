from django.shortcuts import render

# Create your views here.

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
def create_or_update_notes(request):
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
        notes_name = request.POST.get('notes_name',None)
        description = request.POST.get('description',"")
        subject_id = request.POST.get('subject_id',None)
        notes_id = request.POST.get('notes_id',None)

        if notes_id==None:
            try:
                subject = Subject.objects.filter(id=subject_id)[0]
            except Exception as e:
                print(str(e))
                return JsonResponse({"status":'unsuccessful','message':'No such subject.'})
            if teacher.id!=subject.teacher.id:
                return JsonResponse({'status':'unsuccessful', 'message':'subject teacher does not match.'})

        #notes_id none implies notes create
        if notes_id==None:
            try:                
                notes = Notes.objects.create(subject=subject, notes_name=notes_name,
                                                    description=description)

                key = list(request.FILES.keys())[0]
                notes_file = request.FILES[key]
                notes.notes_file = notes_file
                notes.save()

                return JsonResponse({"status":'success', 'message':'Created Notes'})
            except Exception as e:
                print('here is error',str(e))
                message = 'Cannot create notes. Make sure to send datetime in iso format with timezone. ex 2020-07-16T19:07:56.059532+00:00'
                return JsonResponse({"status":'unsuccessful','message':message})
        #for update
        notes_query = Notes.objects.filter(id=notes_id)
        if len(notes_query)!=0:
            notes = notes_query[0]
            if notes.subject.teacher.id!=user.teacher.id:
                return JsonResponse({"status":'unsuccessful','message':'Could not update. Subject teacher does not match.'})
        else:
            return JsonResponse({"status":'unsuccessful','message':'No such notes exists'})
        if notes_name!=None:
            notes.notes_name = notes_name
        if description!=None:
            notes.description = description
        
        if len(request.FILES.keys())!=0:
            key = list(request.FILES.keys())[0]
            notes_file = request.FILES[key]
            #delete old file.
            notes.notes_file.delete(False) 
            notes.notes_file = notes_file

        notes.save()

        return JsonResponse({'status':'success', 'message':'Updated notes'})
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})


@csrf_exempt
@require_http_methods(["POST"])
def get_notes_list(request):
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
    #print(subject_id)
    if not subject_id:
        message = "Please provide subject ID"
        return JsonResponse({"status":status,"message":message})

    if is_teacher or is_student:
        message = [notes.get_summary() for notes in Notes.objects.filter(subject=subject_id)]
        status = "success"
    else:
        message = "No proper authentication."

    return JsonResponse({"status":status,"message":message})