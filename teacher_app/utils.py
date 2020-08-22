from django.contrib.auth.models import User
from core.models import Authority, School, Teacher, Class
import random
import string
from authority_app.utils import create_class

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
    teacher = Teacher.objects.filter(id=teacher_id)[0]
    return teacher


def create_teacher(name, mob_no, email, is_class_teacher, school_id):
    print(name, mob_no, email, is_class_teacher, school_id)
    password = random_string(8)
    school = get_school_by_id(school_id)

    username_namepart = ''.join(map(str.title, name.lower().split()))
    username = username_namepart + '@' +str(mob_no)
    user, created_new = create_user(name, username, password)
    if created_new==False:
        return {'info':{},'status':'unsuccesssful','message':'user already exists.'}
    if email!=None:
        user.email = email
        user.save()
    try:
        is_teacher = user.teacher
        return {'info':{},'status':'unsuccesssful','message':'teacher already exists.'}
    except:
        pass 
    if False:
        return {'info':{},'message':'unsuccessful, user already exists','status':'unsuccessful'} 
    else:
        print(is_class_teacher, ' param')
        teacher = Teacher.objects.create(user=user,school=school, is_class_teacher=is_class_teacher)
        teacher.first_password = password
        teacher.mob_no = mob_no
        teacher.save()

        return {"info":{'school_id':school_id, "teacher_id":teacher.id, "name":name
                , "email":email, 'username':username, 'password':password},
                'message':'successful, created teacher',
                'status':'success'}

def update_teacher_info(new_info, teacher_id, is_authority):
    teacher = get_teacher_by_id(teacher_id)
    school_id = teacher.school.id


    # if new_info.get('email'):
    #     teacher.user.email = new_info['email']
    user = teacher.user
    if new_info.get('email'):
       user.email = new_info['email']
       user.save()
    if new_info.get('mob_no'):
        teacher.mob_no = new_info['mob_no']
    if new_info.get('addr'):
        teacher.addr = new_info['addr']
    if new_info.get('city'):
        teacher.city = new_info['city']
    if new_info.get('state'):
        teacher.state = new_info['state']
    if new_info.get('nation'):
        teacher.nation = new_info['nation']
    if new_info.get('pincode'):
        teacher.pincode = new_info['pincode']
    

    if(is_authority):
        if teacher.is_class_teacher == True and (new_info['is_class_teacher'] == "False" or new_info['is_class_teacher'] == "false"):
            class_ = Class.objects.get(class_teacher__id=teacher_id)
            class_.class_teacher = None
            class_.save()
            teacher.is_class_teacher = False

        if new_info['is_class_teacher'] == "True" or new_info['is_class_teacher'] == "true":

            if teacher.is_class_teacher:

                class_ = Class.objects.get(class_teacher__id=teacher_id)
                class_.class_teacher = None
                class_.save()
                print('removed class from teacher')
            else:
                pass
            if not Class.objects.filter(school__id=school_id,class_name=new_info['class_name'],section=new_info['section']).exists():
                create_class(new_info['class_name'], new_info['section'], school_id, teacher_id)
            else:
                class_ = Class.objects.get(school__id=school_id,class_name=new_info['class_name'],section=new_info['section'])
                if not class_.class_teacher:
                    class_.class_teacher = teacher
                    class_.save()
                if class_.class_teacher.id == teacher_id:
                    pass
                else:
                    prev_class_teacher = class_.class_teacher
                    prev_class_teacher.is_class_teacher = False
                    prev_class_teacher.save()
                    class_.class_teacher = None
                    class_.save()
                    class_.class_teacher = teacher
                    class_.save()
            teacher.is_class_teacher = True
        else:
            teacher.is_class_teacher = False
    
    teacher.save()

    return {"message":"successful, updated teacher info",'status':'success'}
