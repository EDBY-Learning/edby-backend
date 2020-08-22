from django.contrib.auth.models import User
from core.models import *
from parent_app.utils import create_parent
import random
import string

def random_string(string_length):
    letters = string.ascii_letters + "#"*5 + "!"*5
    return ''.join(random.choice(letters) for i in range(string_length))

def create_user(name, username, password):
    user, created_new = User.objects.get_or_create(username=username)
    if created_new:
        print('New user created')
        created_new = True

        user.first_name = name
        user.set_password(password)

        user.save()
        
        return user, created_new
    else:
        #user already exists
        #user.set_password(password)
        print("user already exists")
        
        return None, created_new
def get_authority_by_id(authority_id):
    authority = Authority.objects.filter(id=authority_id)[0]
    return authority

def get_school_by_id(school_id):
    school = School.objects.filter(id=school_id)[0]
    return school

def get_teacher_by_id(teacher_id):
    school = Teacher.objects.filter(id=teacher_id)[0]
    return school

def get_student_by_id(student_id):
    student = Student.objects.filter(id=student_id)[0]
    return student
def get_class_by_id(class_id):
    class_is = Class.objects.filter(id=class_id)[0]
    return class_is
def get_parent_by_id(parent_id):
    parent = Parent.objects.filter(id=parent_id)[0]
    return parent


def create_student(name, roll, parent_mob_no_1, email, class_id,parent_name=None,parent_email=None):
    #print(name, roll, parent_mob_no_1, email, class_id)
    password = random_string(8)
    class_is = get_class_by_id(class_id)
    
    username_namepart = ''.join(map(str.title, name.lower().split()))
    username = username_namepart + '@' +str(parent_mob_no_1)
    user, created_new = create_user(name, username, password)
    if created_new==False:
        return {'info':{},'status':'unsuccesssful','message':'user already exists.'}
    if email!=None:
        user.email = email
        user.save()
    try:
        is_student = user.student
        return {'info':{},'status':'unsuccesssful','message':'teacher already exists.'}
    except:
        pass 

    if False:
        return {'info':{},'message':'unsuccessful, user already exists','status':'unsuccessful'} 
    else:
        #print('herer')
        student = Student.objects.create(user=user, class_is=class_is)
        student.first_password = password
        student.parent_mob_no_1 = parent_mob_no_1
        student.save()
        #print('herer')
        #create parent
        #response = create_parent(parent_name, parent_mob_no_1, parent_email)
        #parent = get_parent_by_id(response['info']['parent_id'])
        #student.parent = parent
        #student.save()

        class_name = class_is.class_name
        section = class_is.section
        print('herer')
        return {"info":{'class_name':class_name, 'section':section,
                'class_id':class_id, "name":name,"student_id":student.id
                , "email":email, 'username':username, 'password':password, #'parent_info':response['info']
                },
                'message':'successful, created student',
                'status':'success'}

def update_student_info(new_info, student_id):
    student = get_student_by_id(student_id)

    # if new_info.get('email'):
    #     student.user.email = new_info['email']
    user = student.user
    if new_info.get('email'):
       user.email = new_info['email']
       user.save()
    if new_info.get('mob_no'):
        student.mob_no = new_info['mob_no']
    if new_info.get('addr'):
        student.addr = new_info['addr']
    if new_info.get('city'):
        student.city = new_info['city']
    if new_info.get('state'):
        student.state = new_info['state']
    if new_info.get('nation'):
        student.nation = new_info['nation']
    if new_info.get('pincode'):
        student.pincode = new_info['pincode']
    
    if new_info.get('parent_mob_no_1'):
        student.parent_mob_no_1 = new_info['parent_mob_no_1']
    if new_info.get('parent_mob_no_2'):
        student.parent_mob_no_2 = new_info['parent_mob_no_2']
    if new_info.get('parent_email'):
        student.parent_email = new_info['parent_email']
    
    
    student.save()

    return {"message":"successful, updated student info",'status':'success'}
