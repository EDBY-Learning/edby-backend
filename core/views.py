import json

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from .models import *
import django.utils.dateparse as dp
from datetime import datetime
import pytz
from django.conf import settings as conf_settings
from uuid import uuid1
from django.views.decorators.http import require_http_methods

BACKEND_TIME_ZONE = pytz.timezone(conf_settings.TIME_ZONE)
SESSION_COOKIE_AGE = (conf_settings.SESSION_COOKIE_AGE)

import sys

def bloackPrint():
    sys.stdout = open(os.devnull,'w')

bloackPrint()

def enablePrint():
    sys.stdout = sys.__stdout__

def get_user_info(user):

    user_type = None
    user_id = user.id
    username = user.username
    name = user.first_name
    
    if user.is_staff:
        user_type = "staff"
        school = ""
    else:
        pass
    try:
        user_type = user.authority
        user_type = "authority"
        school = user.authority.school.school_name
    except:
        pass
    try:
        user_type = user.teacher
        user_type = "teacher"
        if user.teacher.is_class_teacher:
            user_type = "class_teacher"

        school = user.teacher.school.school_name
    except:
        pass
    try:
        user_type = user.student
        user_type = "student"
        school = user.student.class_is.school.school_name
    except:
        pass

    return {"user_type":user_type,"user_id":user_id,"username":username,"name":name,"school":school}

@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    status = "failure"
    if request.method!='POST':
        message = "Invalid request method"
        return JsonResponse({"status":status,"data":message})
    if request.user.is_authenticated:
        message = "You are already logged in"
        return JsonResponse({"status":status,"data":message})
    else:
        pass 
        # print("not logged in ")
    username = request.POST.get('username',None)
    password = request.POST.get('password',None)

    if username and password:
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            message = get_user_info(user)
            status = "success"
        else:
            message = "Username and password do not match"
    else:
        message = "Please provide username and password"

    return JsonResponse({"status":status,"data":message})


@csrf_exempt
@require_http_methods(["POST"])
def change_password(request):
    if request.method != 'POST':
        return JsonResponse({"status":"failure","message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    current_password = request.POST.get('current_password',None)
    new_password = request.POST.get('new_password',None)

    print(current_password, new_password)

    if user.is_authenticated:
        if current_password and new_password:
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                return JsonResponse({"status":"success","message":"Password reset"})
            else:
                return JsonResponse({"status":"failure","message":"Incorrect current password"})
        else:
            return JsonResponse({"status":"failure","message":"Provide both password."})
    else:
        return JsonResponse({"status":"failure","message":"Not authenticated."})

@csrf_exempt
@require_http_methods(["GET"])
def logout_user(request):
    if request.method !='GET':
        return JsonResponse({"message":"Invalid request"})
    if request.user.is_authenticated:
        # print('user id',request.user.id)
        # print('already logged in')
        logout(request)
        return JsonResponse({"message":"successfully logged out."})
    else:
        return JsonResponse({"message":"Already logged out."})

def get_unique_token():
    #return : True,'token'
    #         status,token
    for i in range(5):
        generated_token = uuid1().hex
        session_query_for_token = Session.objects.filter(token=generated_token)
        if len(session_query_for_token)!=0:
            continue
        return True, generated_token
    return False,''

def get_current_time():
    current_time =  datetime.now().astimezone(BACKEND_TIME_ZONE)
    return current_time
    
@csrf_exempt
@require_http_methods(["POST",'OPTIONS'])
def login_with_token_test(request):
    if request.method!='POST':
        print(request.method)
        return JsonResponse({"message":"Invalid request"})
    #print(request.body)
    username = request.POST.get('username',None)
    password = request.POST.get('password',None)
    #print(username,password)

    status = "failure"
    if username and password:
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            session_query = Session.objects.filter(user=user)
            if len(session_query)==0:
                #print('new login')
                has_got_unique_token, generated_token = get_unique_token()
                if has_got_unique_token==False:
                    return JsonResponse({'status':"failure","message":"cannot login. Please try again"})
                current_time = get_current_time()
                session = Session.objects.create(user=user, token=generated_token, last_request=current_time)
                session.save()
                session_created = True
            else:
                #print('relogin')
                session = session_query[0]
                current_time = get_current_time()
                if (current_time - session.last_request).seconds > SESSION_COOKIE_AGE:
                    has_got_unique_token, generated_token = get_unique_token()
                    if has_got_unique_token==False:
                        return JsonResponse({'status':"failure","message":"cannot login. Please try again"})
                    current_time = get_current_time()
                    session = Session.objects.create(user=user, token=generated_token, last_request=current_time)
                    session.save()
                    session_created = True
                else:
                    generated_token = session.token
                    session.last_request = get_current_time()
                    session.save()
                    session_created = True
                
            message = get_user_info(user)
            status = "success"
        else:
            message = "Username and password do not match"
    else:
        message = "Please provide username and password"

    if status=='success':
        #print(generated_token)
        return JsonResponse({"status":status,"data":message, "token":generated_token})
    return JsonResponse({"status":status,"data":message})


@csrf_exempt
@require_http_methods(["POST",'OPTIONS'])
def login_with_token(request):
    if request.method!='POST':
        print(request.method)
        return JsonResponse({"message":"Invalid request"})
    #print(request.body)
    username = request.POST.get('username',None)
    password = request.POST.get('password',None)
    #print(username,password)

    status = "failure"
    if username and password:
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            session_query = Session.objects.filter(user=user)
            if len(session_query)==0:
                #print('new login')
                has_got_unique_token, generated_token = get_unique_token()
                if has_got_unique_token==False:
                    return JsonResponse({'status':"failure","message":"cannot login. Please try again"})
                current_time = get_current_time()
                session = Session.objects.create(user=user, token=generated_token, last_request=current_time)
                session.save()
                session_created = True
            else:
                #print('relogin')
                has_got_unique_token, generated_token = get_unique_token()
                if has_got_unique_token==False:
                    return JsonResponse({'status':"failure","message":"cannot login. Please try again"})
                session = session_query[0]
                session.token = generated_token
                session.last_request = get_current_time()
                session.save()
                session_created = True
                
            message = get_user_info(user)
            status = "success"
        else:
            message = "Username and password do not match"
    else:
        message = "Please provide username and password"

    if status=='success':
        #print(generated_token)
        return JsonResponse({"status":status,"data":message, "token":generated_token})
    return JsonResponse({"status":status,"data":message})


def has_session_expired_and_update(token):
    if token==None:
        return None
    if isinstance(token,str)==False:
        return None
    session_query = Session.objects.filter(token=token)
    if len(session_query)==0:
        return None
    else:
        session = session_query[0]
        #check for time difference with last login (in seconds)
        current_time = get_current_time()
        if (current_time - session.last_request).seconds > SESSION_COOKIE_AGE:
            return None
        else:
            session.last_request = current_time
            session.save()
            return session.user

@csrf_exempt
@require_http_methods(["POST"])
def logout_with_token(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    token = request.POST.get('token',None)
    
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"Already logout."})
    
    session_query = Session.objects.filter(token=token)
    if len(session_query)==0:
        return JsonResponse({"status":"Already logout."})
    #print(session_query)
    session = session_query[0]
    #print(session)
    session.token = None
    #print(session)
    session.save()
    return JsonResponse({"status":"success","message":"logged out"})

@csrf_exempt
@require_http_methods(["POST"])
def get_price(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})
    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})
    message = get_user_info(user)
    return JsonResponse({"num":"12345678",'message':message})
    

@csrf_exempt
@require_http_methods(["POST"])
def check_login_with_token(request):
    if request.method!='POST':
        return JsonResponse({"status":"failure","message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"You are not logged in"})

    return JsonResponse({"status":"success","message":"You are already logged in"})
    
