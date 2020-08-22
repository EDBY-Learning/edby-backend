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
        return 

@csrf_exempt
def is_logged_as_class_teacher(user):
    try:
        is_teacher = user.teacher
        if user.teacher.is_class_teacher==True:
            return True
        else:
            return False
    except:
        return False

@csrf_exempt
def is_logged_as_authority(user):
    try:
        is_authority = user.authority
        return True
    except:
        return False

    
# Create your views here.
@csrf_exempt
@require_http_methods(["POST"])
def create_notice(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    is_authority = is_logged_as_authority(user)
    if (not is_teacher) and (not is_authority):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
    else:
        if is_teacher:
            issuer = user
        else:
            issuer = user

    #print(json.loads(request.body)['file'])
    if len(request.FILES.keys())!=0:
        key = list(request.FILES.keys())[0]
        file_handle = request.FILES[key]
        #check for maximum allowed file size
        if file_handle.size>float(MAX_FILE_SIZE_ALLOWED):
            return JsonResponse({'status':'unsuccessful', 
                            'message':'File size is greater than allowed size( %s Kb )'%(float(MAX_FILE_SIZE_ALLOWED)/1024)})
    
    try:
        category_description = request.POST.get('category_description',None)
        notice_heading = request.POST.get('notice_heading',"")
        notice_text = request.POST.get('notice_text',None)

        #notes_id none implies notes create
        try:
            print(issuer.id)
            category,created = Category.objects.get_or_create(classification = category_description)
            notice = Notice.objects.create(issuer=issuer, heading=notice_heading, text=notice_text)
            print(notice.issuer.id)
            notice.save()
            notice.category.add(category)

            
            if len(request.FILES.keys())!=0:
                key = list(request.FILES.keys())[0]
                file = request.FILES[key]
                notice.file = file
            #print("Hello")
            notice.save()

            return JsonResponse({"status":'success', 'message':'Created notice',"notice_id":notice.id})
        except Exception as e:
            print('here is error',str(e))
            message = 'Cannot create notice.'
            return JsonResponse({"status":'unsuccessful','message':message})
        
    except:
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})

@csrf_exempt
@require_http_methods(["POST"])
def update_notice(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    is_authority = is_logged_as_authority(user)
    if (not is_teacher) and (not is_authority):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
    else:
        if is_teacher:
            issuer = user
        else:
            issuer = user

    #print(json.loads(request.body)['file'])
    if len(request.FILES.keys())!=0:
        key = list(request.FILES.keys())[0]
        file_handle = request.FILES[key]
        #check for maximum allowed file size
        if file_handle.size>float(MAX_FILE_SIZE_ALLOWED):
            return JsonResponse({'status':'unsuccessful', 
                            'message':'File size is greater than allowed size( %s Kb )'%(float(MAX_FILE_SIZE_ALLOWED)/1024)})
    
    try:
        category_description = request.POST.get('category_description',None)
        notice_heading = request.POST.get('notice_heading',None)
        notice_text = request.POST.get('notice_text',None)
        notice_id = request.POST.get('notice_id',None)

        if notice_id==None:
            return JsonResponse({'status':'unsuccessful', 'message':'Provide notice id to update.'})
        else:
            #check ownership
            notice_query = Notice.objects.filter(id=notice_id)
            if len(notice_query)==0:
                return JsonResponse({'status':'unsuccessful', 'message':'No such notice exists.'})
            notice = notice_query[0]
            print(issuer.id)
            print(notice.issuer.id)
            if  notice.issuer.id!=issuer.id:
                return JsonResponse({'status':'unsuccessful', 'message':'No proper ownership.'})

        #for update
        if category_description!=None:
            category,created = Category.objects.get_or_create(classification = category_description)
            notice.category.add(category)
        if notice_heading!=None:
            notice.heading = notice_heading
        if notice_text!=None:
            notice.text = notice_text
        
        if len(request.FILES.keys())!=0:
            key = list(request.FILES.keys())[0]
            file = request.FILES[key]
            #delete old file.
            notice.file.delete(False) 
            notice.file = file

        notice.save()

        return JsonResponse({'status':'success', 'message':'Updated notice'})
    except Exception as e:
        print(str(e))
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})

@csrf_exempt
@require_http_methods(["POST"])
def delete_notice(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    is_authority = is_logged_as_authority(user)
    if (not is_teacher) and (not is_authority):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
    else:
        if is_teacher:
            issuer = user.teacher
        else:
            issuer = user.authority
    
    try:
        notice_id = request.POST.get('notice_id',None)
        if notice_id==None:
            
            return JsonResponse({'status':'unsuccessful', 'message':'Provide notice id to delete.'})
        else:
            #check ownership
            notice = Notice.objects.filter(id=notice_id)
            print(issuer.user.id)
            print(notice[0].issuer.id)
            if len(notice)==0:
                return JsonResponse({'status':'unsuccessful', 'message':'No such notice exists.'})
            elif notice[0].issuer.id!=issuer.user.id:
                return JsonResponse({'status':'unsuccessful', 'message':'No proper ownership.'})

        notice[0].file.delete(False) 
        notice[0].delete()

        return JsonResponse({'status':'success', 'message':'Deleted notice'})
    except Exception as e:
        print(str(e))
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})

@csrf_exempt
@require_http_methods(["POST"])
def publish_notice(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    is_authority = is_logged_as_authority(user)
    if (not is_teacher) and (not is_authority):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
    else:
        if is_teacher:
            issuer = user
        else:
            issuer = user
    
    try:
        notice_id = request.POST.get('notice_id',None)
        if notice_id==None:
            
            return JsonResponse({'status':'unsuccessful', 'message':'Provide notice id to publish.'})
        else:
            #check ownership
            notice_query = Notice.objects.filter(id=notice_id)
            if len(notice_query)==0:
                return JsonResponse({'status':'unsuccessful', 'message':'No such notice exists.'})
            notice = notice_query[0]
            if notice.issuer.id!=issuer.id:
                return JsonResponse({'status':'unsuccessful', 'message':'No proper ownership.'})

        notice.issue_dt = datetime.now().astimezone(BACKEND_TIME_ZONE)
        notice.is_published = True
        notice.save()

        return JsonResponse({'status':'success', 'message':'Published notice'})
    except Exception as e:
        print(str(e))
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})

@csrf_exempt
@require_http_methods(["POST"])
def read_notice(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    is_authority = is_logged_as_authority(user)
    if (not is_teacher) and (not is_authority):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
    else:
        if is_teacher:
            issuer = user
        else:
            issuer = user
    
    try:
        notice_id = request.POST.get('notice_id',None)
        if notice_id==None:
            
            return JsonResponse({'status':'unsuccessful', 'message':'Provide notice id to publish.'})
        else:
            #check ownership
            notice_query = Notice.objects.filter(id=notice_id)
            if len(notice_query)==0:
                return JsonResponse({'status':'unsuccessful', 'message':'No such notice exists.'})
            notice = notice_query[0]
            if notice.issuer.id!=issuer.id:
                return JsonResponse({'status':'unsuccessful', 'message':'No proper ownership.'})
        print("hello")
        message = notice.get_summary()
        return JsonResponse({'status':'success', 'message':message})
    except Exception as e:
        print(str(e))
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})

@csrf_exempt
@require_http_methods(["POST"])
def get_issued_notice_list(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    is_authority = is_logged_as_authority(user)
    if (not is_teacher) and (not is_authority):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
    else:
        if is_teacher:
            issuer = user
        else:
            issuer = user
    
    try:
        message = [notice.get_summary() for notice in Notice.objects.filter(issuer_id=issuer.id)]
        return JsonResponse({'status':'success', 'message':message})
    except Exception as e:
        print(str(e))
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})

@csrf_exempt
@require_http_methods(["POST"])
def get_notice_list(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    is_authority = is_logged_as_authority(user)
    is_class_teacher = is_logged_as_class_teacher(user)
    is_student = is_logged_as_student(user)
    try:
        combined_message = []
        if is_student:
            category_description = "student"
            category,created = Category.objects.get_or_create(classification = category_description)
            class_teacher_id = user.student.class_is.class_teacher.user.id
            #print(class_teacher_id)
            summaries = [notice.get_summary() for notice in Notice.objects.filter(category=category,is_published=True)]
            #print(summaries)
            message = [summary for summary in summaries if summary["issuer_designation"]=='authority' or summary['issuer_id']==class_teacher_id ]
            #print(message)
            combined_message.extend(message)
        if is_authority:
            category_description = "authority"
            category,created = Category.objects.get_or_create(classification = category_description)
            summaries = [notice.get_summary() for notice in Notice.objects.filter(category=category,is_published=True)]
            message = [summary for summary in summaries]
            combined_message.extend(message)

            category_description = "student"
            category,created = Category.objects.get_or_create(classification = category_description)
            #class_teacher_id = user.class_is.class_teacher.user.id
            summaries = [notice.get_summary() for notice in Notice.objects.filter(category=category,is_published=True)]
            message = [summary for summary in summaries if summary["issuer_designation"]=='authority']
            combined_message.extend(message)

            category_description = "teacher"
            category,created = Category.objects.get_or_create(classification = category_description)
            summaries = [notice.get_summary() for notice in Notice.objects.filter(category=category,is_published=True)]
            message = [summary for summary in summaries if summary["issuer_designation"]=='authority']
            combined_message.extend(message)

            category_description = "class_teacher"
            category,created = Category.objects.get_or_create(classification = category_description)
            summaries = [notice.get_summary() for notice in Notice.objects.filter(category=category,is_published=True)]
            message = [summary for summary in summaries if summary["issuer_designation"]=='authority']
            combined_message.extend(message)


        if is_class_teacher:
            category_description = "class_teacher"
            category,created = Category.objects.get_or_create(classification = category_description)
            summaries = [notice.get_summary() for notice in Notice.objects.filter(category=category,is_published=True)]
            message = [summary for summary in summaries]
            combined_message.extend(message)
            message = [notice.get_summary() for notice in Notice.objects.filter(issuer_id=user.id,is_published=True)]
            combined_message.extend(message)

        if is_teacher:
            #print()
            class_teacher_user_ids = [subject.class_is.class_teacher.user.id for subject in Subject.objects.filter(teacher=user.teacher.id)]
            #print(2)
            category_description = "teacher"
            category,created = Category.objects.get_or_create(classification = category_description)
            summaries = [notice.get_summary() for notice in Notice.objects.filter(category=category,is_published=True)]
            message = [summary for summary in summaries if summary['issuer_id'] in class_teacher_user_ids or summary['issuer_designation']=='authority']
            combined_message.extend(message)

            category_description = "student"
            category,created = Category.objects.get_or_create(classification = category_description)
            #class_teacher_id = user.class_is.class_teacher.user.id
            summaries = [notice.get_summary() for notice in Notice.objects.filter(category=category,is_published=True)]
            message = [summary for summary in summaries if summary["issuer_designation"]=='authority']
            combined_message.extend(message)



        return JsonResponse({'status':'success', 'message':combined_message})
    
    except Exception as e:
        print(str(e))
        return JsonResponse({'status':'unsuccessful', 'message':'Server Error'})
