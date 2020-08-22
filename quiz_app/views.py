import os
import json
import pytz
from datetime import datetime, date, timedelta

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
import django.utils.dateparse as dp
from django.views.decorators.http import require_http_methods
from django.conf import settings as conf_settings

from core.models import *
from core.views import has_session_expired_and_update

BACKEND_TIME_ZONE = pytz.timezone(conf_settings.TIME_ZONE)
MAX_FILE_SIZE_ALLOWED = conf_settings.MAX_FILE_SIZE_ALLOWED
ALLOWED_LATE_SUBMISSION_IN_MINUTES = 5
# Create your views here.

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


@csrf_exempt
@require_http_methods(["POST"])
def create_quiz(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        subject_id = request.POST.get('subject_id')
        subject = Subject.objects.get(id=subject_id)
        if subject.teacher != user.teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        quiz_heading = request.POST.get('quiz_heading',"")
        quiz_type = request.POST.get('quiz_type',"")
        duration = request.POST.get('duration')
        if duration:
            duration = dp.parse_duration(duration)
        marks = request.POST.get('marks')
        start_dt = request.POST.get('start_dt')

        quiz = Quiz(subject=subject,heading=quiz_heading,kind=quiz_type,duration=duration,normalized_marks=marks,start_dt=start_dt)
        quiz.save()
        return JsonResponse({"status":"success","quiz_id":quiz.id})
    
    except Exception as e:
        print(e)
        return JsonResponse({"status":"failure","message":"Server Error"})

@csrf_exempt
@require_http_methods(["POST"])
def update_quiz(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        quiz_id = request.POST.get('quiz_id')
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid quiz selected."})
        subject = quiz.subject
        if subject.teacher != user.teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        quiz_heading = request.POST.get('quiz_heading',"")
        quiz_type = request.POST.get('quiz_type',"")
        duration = request.POST.get('duration')
        duration = dp.parse_duration(duration)
        marks = request.POST.get('marks')
        start_dt = request.POST.get('start_dt')

        quiz.normalized_marks = marks
        quiz.heading = quiz_heading

        if not quiz.is_published:
            quiz.kind = quiz_type
            quiz.duration = duration
            quiz.start_dt = start_dt

        quiz.save()
        return JsonResponse({"status":"success"})
    
    except:
        return JsonResponse({"status":"failure","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def delete_quiz(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        quiz_id = request.POST.get('quiz_id')
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid quiz selected."})
        subject = quiz.subject
        if subject.teacher != user.teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        if quiz.is_published:
            return JsonResponse({"status":"unsuccessful", "message":"Publshed quiz cannot be deleted."})

        quiz.delete()
        return JsonResponse({"status":"success"})
    
    except:
        return JsonResponse({"status":"failure","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def publish_quiz(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        quiz_id = request.POST.get('quiz_id')
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid quiz selected."})
        subject = quiz.subject
        if subject.teacher != user.teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        if quiz.is_published:
            return JsonResponse({"status":"unsuccessful", "message":"Quiz is already published"})

        quiz.is_published = True
        quiz.start_dt = datetime.now().astimezone(BACKEND_TIME_ZONE)
        quiz.save()
        return JsonResponse({"status":"success"})
    
    except:
        return JsonResponse({"status":"failure","message":"Server Error"})

@csrf_exempt
@require_http_methods(["POST"])
def read_quiz_teacher(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        quiz_id = request.POST.get('quiz_id')
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid quiz selected."})
        subject = quiz.subject
        if subject.teacher != user.teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
        message = quiz.get_full_summary_teacher()

        return JsonResponse({"status":"success","message":message})

    except Exception as e:
        print(e)
        return JsonResponse({"status":"failure","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def read_quiz_student(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_student(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        quiz_id = request.POST.get('quiz_id')
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid quiz selected."})
        if quiz.subject.class_is != user.student.class_is:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        if not quiz.is_published:
            return JsonResponse({"status":"unsuccessful", "message":"Access denied"})

        message = quiz.get_summary_student(user.student)

        return JsonResponse({"status":"success","message":message})

    except:
        return JsonResponse({"status":"failure","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def create_question(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})


    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    parsed_data = json.loads(request.POST.get('data'))['data']
    
    try:
        quiz_id = parsed_data.get('quiz_id') 
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid quiz selected."})
        subject = quiz.subject
        if subject.teacher != user.teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        if quiz.is_published:
            return JsonResponse({"status":"unsuccessful", "message":"Cannot add questions to published quiz."})

        
        id_dict = {}

        

        question_type = parsed_data.get('question_type',"")
        question_number = parsed_data.get('number')
        question_text = parsed_data.get('question_text',"")
        marks = parsed_data.get('marks')
        option_list = parsed_data.get('option_list')
        answer_list = parsed_data.get('answer_list')
        
        question = Question(quiz=quiz,kind=question_type,number=question_number,text=question_text,maximum_marks=marks)
        #### question file ####
        if len(request.FILES.keys())!=0:
            key = list(request.FILES.keys())[0]
            print(key)
            file_handle = request.FILES[key]
            #check for maximum allowed file size
            if file_handle.size>float(MAX_FILE_SIZE_ALLOWED):
                return JsonResponse({'status':'unsuccessful', 
                                'message':'File size is greater than allowed size( %s Kb )'%(float(MAX_FILE_SIZE_ALLOWED)/1024)})
            question_file = request.FILES[key]
            question.file = question_file
        #######################
        question.save()
        id_dict['question_id'] = question.id

        id_dict['option_id_list'] = []
        if question_type == "mcq" or question_type == "scq":
            for option_dict in option_list:
                option_code = option_dict.get('option_code',"")
                option_text = option_dict.get('option_text',"")
                option = Option(question=question,code=option_code,text=option_text)
                #### option file ####
                #####################
                option.save()
                id_dict['option_id_list'].append(option.id)
                
        for answer in answer_list:
            if answer:
                Correct_answer.objects.create(question=question,text=answer)
        

        return JsonResponse({"status":"success","id_list":id_dict})

    except Exception as e:
        print(e)
        return JsonResponse({"status":"failure","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def update_question(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
    
    parsed_data = json.loads(request.POST.get('data'))['data']
    #print(parsed_data)
 

    try:
        question_id = parsed_data.get('question_id')
        try:
            question = Question.objects.get(id=question_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid question selected."})
        subject = question.quiz.subject
        if subject.teacher != user.teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        question_type = parsed_data.get('question_type',"")
        question_number = parsed_data.get('number')
        question_text = parsed_data.get('question_text',"")
        marks = parsed_data.get('marks')
        option_list = parsed_data.get('option_list')
        answer_list = parsed_data.get('answer_list')
        
        if not question.quiz.is_published:
            question.kind = question_type
            question.number = question_number
            question.text = question_text
            question.maximum_marks = marks
            #### question file ####
            if len(request.FILES.keys())!=0:
                key = list(request.FILES.keys())[0]
                print(key)
                file_handle = request.FILES[key]
                #check for maximum allowed file size
                if file_handle.size>float(MAX_FILE_SIZE_ALLOWED):
                    return JsonResponse({'status':'unsuccessful', 
                                    'message':'File size is greater than allowed size( %s Kb )'%(float(MAX_FILE_SIZE_ALLOWED)/1024)})
                question_file = request.FILES[key]
                question.file = question_file
            #######################
            question.save()

            if question_type == "mcq" or question_type == "scq":
                for option_dict in option_list:
                    option_code = option_dict.get('option_code',"")
                    option_text = option_dict.get('option_text',"")
                    try:
                        option = Option.objects.get(question=question,code=option_code)
                    except:
                        option = Option(question=question,code=option_code)
                    option.text = option_text
                    #### option file ####
                    #####################
                    option.save()

        answer_qs = [c_a for c_a in Correct_answer.objects.filter(question=question)]
        count = 0
        for answer in answer_list:
            if answer:
                try:
                    correct_answer = answer_qs[count]
                    count += 1
                except:
                    correct_answer = Correct_answer(question=question)
                correct_answer.text = answer
                correct_answer.save()
        while count<len(answer_qs):
            answer_qs[count].delete()
            count += 1

        return JsonResponse({"status":"success"})

    except Exception as e:
        print(e)
        return JsonResponse({"status":"failure","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def delete_question(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        question_id = request.POST.get('question_id')
        #print(question_id)
        try:
            question = Question.objects.get(id=question_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid question selected."})
        subject = question.quiz.subject
        if subject.teacher != user.teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        if question.quiz.is_published:
            return JsonResponse({"status":"unsuccessful", "message":"Question cannot be deleted after quiz is published."})

        question.delete()
        return JsonResponse({"status":"success"})
    
    except:
        return JsonResponse({"status":"failure","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def read_question_teacher(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        question_id = request.POST.get('question_id')
        try:
            question = Question.objects.get(id=question_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid question selected."})
        subject = question.quiz.subject
        if subject.teacher != user.teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        message = question.get_summary_teacher()
        return JsonResponse({"status":"success", "message":message})
    
    except Exception as e:
        print(e)
        return JsonResponse({"status":"failure","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def get_quiz_list_teacher(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        subject_id = request.POST.get('subject_id')
        subject = Subject.objects.get(id=subject_id)
        if subject.teacher != user.teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        quiz_list = []
        for quiz in Quiz.objects.filter(subject=subject):
            quiz_dict = quiz.get_summary_teacher()
            quiz_list.append(quiz_dict)

        return JsonResponse({"status":"success", "quiz_list":quiz_list})

    except Exception as e:
        print(e)
        return JsonResponse({"status":"failure","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def get_quiz_list_student(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_student(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        subject_id = request.POST.get('subject_id')
        try:
            subject = Subject.objects.get(id=subject_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid subject selected."})
        if subject.class_is != user.student.class_is:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        quiz_list = []
        for quiz in Quiz.objects.filter(subject=subject):
            if quiz.is_published:
                quiz_dict = quiz.get_summary_student(user.student)
                quiz_list.append(quiz_dict)

        return JsonResponse({"status":"success", "quiz_list":quiz_list})

    except Exception as e:
        print(e)
        return JsonResponse({"status":"failure","message":"Server Error"})

@csrf_exempt
@require_http_methods(["POST"])
def get_quiz_list_student_unpublished(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_student(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        subject_id = request.POST.get('subject_id')
        try:
            subject = Subject.objects.get(id=subject_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid subject selected."})
        if subject.class_is != user.student.class_is:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        quiz_list = []
        for quiz in Quiz.objects.filter(subject=subject):
            if not quiz.is_published:
                quiz_dict = quiz.get_summary_student_unpublished(user.student)
                quiz_list.append(quiz_dict)

        return JsonResponse({"status":"success", "quiz_list":quiz_list})

    except Exception as e:
        print(e)
        return JsonResponse({"status":"failure","message":"Server Error"})


def grade_quiz_util(quiz_submission):
    try:
        student = quiz_submission.student
        quiz = quiz_submission.quiz
        submission_marks = 0
        is_graded = True
        for response in Question_response.objects.filter(student=student,question__quiz=quiz):
            question = response.question
            if question.kind == "mcq":
                response_answer = [r_a.text.lower() for r_a in Response_answer.objects.filter(question_response=response)]
                correct_answer = [c_a.text.lower() for c_a in Correct_answer.objects.filter(question=question)]
                response_answer.sort()
                correct_answer.sort()
                if response_answer == correct_answer:
                    response.marks = question.maximum_marks
                else:
                    response.marks = 0
            elif question.kind == "Detail":
                pass
            else:
                response_answer = Response_answer.objects.get(question_response=response).text.lower() 
                correct_answer = Correct_answer.objects.get(question=question).text.lower()
                if response_answer == correct_answer:
                    response.marks = question.maximum_marks
                else:
                    response.marks = 0
            response.save()
            if response.marks != None:
                submission_marks += response.marks
            else:
                is_graded = False
        quiz_submission.marks = submission_marks
        quiz_submission.is_graded = is_graded
        quiz_submission.save()
        return "success"
    
    except:
        return "failure"

@csrf_exempt
@require_http_methods(["POST"])
def grade_quiz_all(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        quiz_id = request.POST.get('quiz_id')
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid quiz selected."})
        subject = quiz.subject
        if subject.teacher != user.teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        for quiz_submission in Quiz_submission.objects.filter(quiz=quiz):
            status = grade_quiz_util(quiz_submission)
            if status == "failure":
                return JsonResponse({"status":"failure", "message":"Failed to grade quiz."})

        return JsonResponse({"status":"success"})

    except Exception as e:
        print(e)
        return JsonResponse({"status":"failure","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def grade_quiz_student(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        quiz_id = request.POST.get('quiz_id')
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid quiz selected."})
        subject = quiz.subject
        if subject.teacher != user.teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        student_id = request.POST.get('student_id')
        try:
            student = Student.objects.get(id=student_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid student selected."})

        try:
            quiz_submission = Quiz_submission.objects.get(quiz=quiz,student=student)
        except:
            return JsonResponse({"status":"unsuccessful", "message":"Student has not submitted quiz."})
        
        status = grade_quiz_util(quiz_submission)
        
        if status == "success":
            return JsonResponse({"status":"success"})
        else:
            return JsonResponse({"status":"failure","message":"Failed to grade quiz."})

    except Exception as e:
        print(e)
        return JsonResponse({"status":"failure","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def get_quiz_submission(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    is_teacher = is_logged_as_teacher(user)
    is_student = is_logged_as_student(user)
    if not (is_teacher or is_student):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        quiz_id = request.POST.get('quiz_id')
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid quiz selected."})

        subject = quiz.subject
        if is_teacher:
            if subject.teacher != user.teacher:
                return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})
        if is_student:
            if subject.class_is != user.student.class_is:
                return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        if is_teacher:
            student_id = request.POST.get('student_id')
            try:
                student = Student.objects.get(id=student_id)
            except:
                return JsonResponse({"status":"failure","message":"Invalid student selected."})
        if is_student:
            student = user.student

        try:
            quiz_submission = Quiz_submission.objects.get(quiz=quiz,student=student)
        except:
            return JsonResponse({"status":"unsuccessful", "message":"Student has not submitted quiz."})

        message = quiz_submission.get_summary()
        return JsonResponse({"status":"success", "message":message})

    except Exception as e:
        print(e)
        return JsonResponse({"status":"failure","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def grade_subjective_question(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        response_id = request.POST.get('response_id')
        try:
            response = Question_response.objects.get(id=response_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid response selected."})
        subject = response.question.quiz.subject
        if subject.teacher != user.teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        question = response.question
        quiz = question.quiz
        if question.kind != "Detail":
            return JsonResponse({"status":"unsuccessful", "message":"Only subjective questions can be manually graded."})

        marks = request.POST.get('marks')
        if int(marks) > question.maximum_marks:
            return JsonResponse({"status":"failure","message":"Assigned marks exceed maximum marks"})
        response.marks = marks
        response.save()

        student = response.student
        quiz_submission = Quiz_submission.objects.get(quiz=quiz,student=student)
        submission_marks = 0
        is_graded = True
        for response in Question_response.objects.filter(student=student,question__quiz=quiz):
            if response.marks:
                submission_marks += response.marks
            else:
                is_graded = False
        quiz_submission.marks = submission_marks
        quiz_submission.is_graded = is_graded
        quiz_submission.save()

        return JsonResponse({"status":"success"})

    except Exception as e:
        print(e)
        return JsonResponse({"status":"failure","message":"Server Error"})


def submit_quiz_util(quiz_submission):
    try:
        quiz_submission.is_submitted = True
        quiz_submission.save()
        return "success"
    except:
        return "failure"


@csrf_exempt
@require_http_methods(["POST"])
def save_question_response(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)


    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_student(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        student = user.student

        parsed_data = json.loads(request.POST.get('data'))['data']

        question_id = parsed_data.get('question_id')
        try:
            question = Question.objects.get(id=question_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid question selected."})
        quiz = question.quiz
        
        if quiz.subject.class_is != student.class_is:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        if quiz.is_published==False:
            return JsonResponse({"status":"unsuccessful", "message":"Quiz is not published yet."})
        
        #get or create quiz_submission
        quiz_submission_query = Quiz_submission.objects.filter(student=student, quiz=quiz)
        if len(quiz_submission_query) == 0:
            quiz_submission = Quiz_submission.objects.create(student=student, quiz=quiz)
        else:
            quiz_submission = quiz_submission_query[0]
        
        if quiz_submission.is_submitted:
            return JsonResponse({"status":"unsuccessful", "message":"Cannot add/update answer since quiz is already submitted."})

        #check submission time
        submission_dt = datetime.now().astimezone(BACKEND_TIME_ZONE)
        #print(quiz.start_dt + quiz.duration, submission_dt)
        if quiz.start_dt + quiz.duration < submission_dt:
                    delta = submission_dt - quiz.start_dt - quiz.duration
                    if delta.seconds>ALLOWED_LATE_SUBMISSION_IN_MINUTES*60:
                        status = "failure"
                        count = 0
                        while status != "success" and count < 10:
                            status = submit_quiz_util(quiz_submission)
                            count += 1
                        return JsonResponse({"status":"unsuccessful","message":"Time up. Quiz has ended. All your saved responses have been stored."})


        #get or create question response
        question_response_query = Question_response.objects.filter(student=student, question=question)
        if len(question_response_query)==0:
            question_response = Question_response.objects.create(student=student, question=question)
        else:
            question_response = question_response_query[0]

        response_answer_list = parsed_data.get('response_answer_list')
        response_answer_qs = [r_a for r_a in Response_answer.objects.filter(question_response=question_response)]
        
        if question.kind == "mcq":
            count = 0
            for response_answer in response_answer_list:
                if response_answer:
                    #print(response_answer)
                    try:
                        stored_response_answer = response_answer_qs[count]
                        count += 1
                        #print(response_answer+"1")
                    except:
                        #print(response_answer+"2")
                        stored_response_answer = Response_answer(question_response=question_response)
                    stored_response_answer.text = response_answer
                    stored_response_answer.save()
                    #print("saved"+stored_response_answer.text)
            while count<len(response_answer_qs):
                response_answer_qs[count].delete()
                #print("deleted"+response_answer_qs[count].text)
                count += 1

        elif question.kind == "Detail":
            if len(response_answer_qs) == 0:
                response_answer = Response_answer.objects.create(question_response=question_response)
            else:
                response_answer = response_answer_qs[0]

            response_answer.text = response_answer_list[0]
            if len(request.FILES.keys())!=0:
                key = list(request.FILES.keys())[0]
                file_handle = request.FILES[key]
                #check for maximum allowed file size
                if file_handle.size>float(MAX_FILE_SIZE_ALLOWED):
                    return JsonResponse({'status':'unsuccessful', 
                                    'message':'File size is greater than allowed size( %s Kb )'%(float(MAX_FILE_SIZE_ALLOWED)/1024)})
                response_answer_file = request.FILES[key]
                response_answer.file = response_answer_file
            response_answer.save()
        else:
            if len(response_answer_qs) == 0:
                response_answer = Response_answer.objects.create(question_response=question_response)
            else:
                response_answer = response_answer_qs[0]
            response_answer.text = response_answer_list[0]
            response_answer.save()

        return JsonResponse({"status":"success"})

    except Exception as e:
        print(e)
        return JsonResponse({"status":"failure","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def submit_quiz(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token')
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_student(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        student = user.student
        quiz_id = request.POST.get('quiz_id')
        quiz = Quiz.objects.get(id=quiz_id)
        
        quiz_submission_query = Quiz_submission.objects.filter(student=student, quiz=quiz)
        if len(quiz_submission_query)==0:
            quiz_submission = Quiz_submission.objects.create(student=student, quiz=quiz)
        else:
            quiz_submission = quiz_submission_query[0]

        if quiz_submission.is_submitted:
            return JsonResponse({"status":"failure", "message":"You have already submitted the quiz."})

        status = submit_quiz_util(quiz_submission)
        if status == "success":
            return JsonResponse({"status":"success"})
        else:
            return JsonResponse({"status":"failure","message":"Failed to submit quiz."})

    except Exception as e:
        print(e)
        return JsonResponse({"status":"failure","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def get_quiz_submission_list(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_teacher(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        quiz_id = request.POST.get('quiz_id')
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid quiz selected."})
        subject = quiz.subject
        if subject.teacher != user.teacher:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        quiz_submission_list = [submission.get_brief_summary() for submission in Quiz_submission.objects.filter(quiz=quiz)]

        return JsonResponse({"status":"success", "quiz_submission_list":quiz_submission_list})

    except Exception as e:
        print(e)
        return JsonResponse({"status":"failure","message":"Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
def read_quiz_student_correct_answer(request):
    if request.method!='POST':
        return JsonResponse({"message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    if not is_logged_as_student(user):
        return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

    try:
        quiz_id = request.POST.get('quiz_id')
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except:
            return JsonResponse({"status":"failure","message":"Invalid quiz selected."})
        if quiz.subject.class_is != user.student.class_is:
            return JsonResponse({"status":"unsuccessful", "message":"No proper authentication."})

        if not quiz.is_published:
            return JsonResponse({"status":"unsuccessful", "message":"Access denied"})

        student = user.student
        try:
            submission = Quiz_submission.objects.get(quiz=quiz,student=student)
            if not submission.is_submitted:
                return JsonResponse({"status":"failure","message":"Quiz not submitted."})
        except:
            return JsonResponse({"status":"failure","message":"Quiz not submitted."})

        message = quiz.get_summary_student_correct_answer()

        return JsonResponse({"status":"success","message":message})

    except:
        return JsonResponse({"status":"failure","message":"Server Error"})
