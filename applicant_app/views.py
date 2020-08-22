import json

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.models import Demo_applicant, Applicant, School
from core.views import has_session_expired_and_update
from django.views.decorators.http import require_http_methods

# Create your views here.

@csrf_exempt
def is_logged_as_staff_or_admin(user):
    #staff or admin is server controller
    if user.is_authenticated:
        return user.is_staff
    else:
        return False

@csrf_exempt
@require_http_methods(["POST"])
def apply_for_demo(request):
    if request.method != 'POST':
        return JsonResponse({"status":"failure","message":"Invalid Request"})

    try:
        data = {}
        data['institute_name'] = request.POST.get('institute_name')
        data['name'] = request.POST.get('name')
        data['mob_no'] = request.POST.get('mob_no')
        data['email'] = request.POST.get('email')
        data['institute_type'] = request.POST.get('institute_type')
        data['designation'] = request.POST.get('designation')

        demo_applicant = Demo_applicant(**data)
        demo_applicant.save()
        return JsonResponse({"status":"success","message":"Your request has been received. We will get in touch with you soon."})
    except Exception as e:
        print(e)
        return JsonResponse({"status":"failure","message":"Your request could not be recorded. Please try again."})


@csrf_exempt
@require_http_methods(["POST"])
def apply(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        applicant = Applicant(**data)
        applicant.save()
        return JsonResponse({'status':'success',"message":"Applicant recorded","applicant_id":applicant.id},status=201)
    else:
        return JsonResponse({"message":"Invalid Request Method"},status=405)

@csrf_exempt
@require_http_methods(["POST"])
def approve(request):
    if request.method != 'POST':
        return JsonResponse({"status":"unsuccessful", "message":"Invalid request"})

    token = request.POST.get('token',None)
    user = has_session_expired_and_update(token)
    if user==None:
        return JsonResponse({"status":"failure","message":"No authentication."})

    try:
        if not is_logged_as_staff_or_admin(user):
            return JsonResponse({"message":"Unauthorized"},status=401)

        applicant_id = request.POST.get('id')
        registrar_email = request.POST.get('registrar_email')
        try:
            applicant = Applicant.objects.values().get(id=applicant_id)
        # detailed except?
        except:
            return JsonResponse({"message":"Invalid Applicant ID"})
        if applicant['registrar_email'] == registrar_email:
            del applicant['id']
            school = School(**applicant)
            school.save()
            return JsonResponse({"status":"success","message":"Applicant approved","school_id":school.id})
        else:
            return JsonResponse({"message":"Registrar email and Applicant ID mismatch"})
        
    except:
        return JsonResponse({"status":"unsuccessful","message":"Server Error"})