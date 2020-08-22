from django.contrib.auth.models import User
from core.models import Authority, School, Class, Teacher
import random
import string

def random_string(string_length):
    letters = string.ascii_letters + "#"*5 + "!"*5
    return ''.join(random.choice(letters) for i in range(string_length))

def create_user(name, username, password):
    user, created_new = User.objects.get_or_create(username=username)
    if created_new:
        #print('New user created')
        created_new = True

        user.first_name = name
        user.set_password(password)

        user.save()
        
        return user, created_new
    else:
        #user already exists
        #user.set_password(password)
        #print("user already exists")
        
        return None, created_new
def get_authority_by_id(authority_id):
    authority = Authority.objects.filter(id=authority_id)[0]
    return authority

def get_class_by_id(class_id):
    class_is = Class.objects.filter(id=class_id)[0]
    return class_is

def get_teacher_by_id(teacher_id):
    teacher = Teacher.objects.filter(id=teacher_id)[0]
    return teacher

def get_school_by_id(school_id):
    school = School.objects.filter(id=school_id)[0]
    return school

def get_info(authority_id):
    authority = get_authority_by_id(authority_id)
    is_present = False
    if not authority:
        return {},is_present
    is_present = True
    info = {}
    info['name'] = authority.user.first_name
    info['email'] = authority.user.email
    info['designation'] = authority.designation
    
    return info, is_present

def create_authority(name, email, designation, mob_no, school_id, addr,city,state,nation,pincode):
    
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
        is_authority = user.authority
        return {'info':{},'status':'unsuccesssful','message':'authority already exists.'}
    except:
        pass 
    if False:
        #print('here')
        return {'info':{},'message':'unsuccessful, user already exists','status':'unsuccessful'} 
    else:
        authority = Authority.objects.create(user=user,school=school)
        authority.designation = designation
        authority.mob_no = mob_no
        authority.first_password = password
        authority.addr = addr
        authority.city = city
        authority.state = state
        authority.nation = nation
        authority.pincode = pincode
        #print(dir(authority))
        authority.save()
        #print('1')

        return {"info":{'school_id':school_id, "name":name
                , "email":email, 'username':username, 'password':password},
                'message':'successful, created authority',
                'status':'success'}

def update_authority_info(new_info, authority_id):
    #print(authority_id)
    authority = get_authority_by_id(authority_id)
    #print('authority',authority.get_summary())
    #print(authority.user.mob_no)
    if new_info.get('email'):
        authority.user.email = new_info['email']
    if new_info.get('mob_no'):
        authority.mob_no = new_info['mob_no']
    if new_info.get('addr'):
        authority.addr = new_info['addr']
    if new_info.get('city'):
        authority.city = new_info['city']
    if new_info.get('state'):
        authority.state = new_info['state']
    if new_info.get('nation'):
        authority.nation = new_info['nation']
    if new_info.get('pincode'):
        authority.pincode = new_info['pincode']
    authority.user.save()
    authority.save()
    #print('here2',authority.get_summary())
    #print(authority.user.mob_no)

    return {"message":"successful, updated authority info",'status':'success'}

def create_class(class_name, section, school_id, teacher_id):
    school = get_school_by_id(school_id)
    if not (class_name or section or school):
        return {'info':{},'status':'unsuccesssful','message':'Please provide both class and section'}
    
   
    class_is = Class.objects.create(class_name=class_name ,section=section, school=school)
    if teacher_id!=None:
        teacher = get_teacher_by_id(teacher_id)
    else:
        teacher = None
    if teacher!=None:
        teacher.is_class_teacher = True
        teacher.save()
    class_is.class_teacher = teacher
    class_is.save()
    

    return {"info":{'school_id':school_id, "class_name":class_name
            , "section":section},
            'message':'successful, created class',
            'status':'successful'}

def assign_class_teacher_to_class(class_id, teacher_id):
    class_is = get_class_by_id(class_id)
    teacher = get_teacher_by_id(teacher_id)
    if not (class_is or teacher):
        return {'info':{},'status':'unsuccesssful','message':'Please provide both class and teacher'}
    

    teacher.is_class_teacher = True
    class_is.class_teacher = teacher
    class_is.save()
    teacher.save()

    return {"info":{ "class_id":class_id, "class_name":class_is.class_name
            , "section":class_is.section, 'class_teacher':teacher.user.first_name,'class_teacher_id':teacher_id},
            'message':'successful, assigned class teacher',
            'status':'successful'}