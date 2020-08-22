from core.models import * 
import random
import string



def random_string(string_length):
    letters = string.ascii_letters + "#"*5 + "!"*5
    return ''.join(random.choice(letters) for i in range(string_length))

def is_parent(user):
    try:
        parent = user.parent
        return True
    except:
        return False

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
        
        return user, created_new

def create_parent(name, parent_mob_no_1, email=None):
    print(name, parent_mob_no_1)
    password = random_string(8)
    
    username_namepart = 'parent'
    username = username_namepart + '@' +str(parent_mob_no_1)
    user, created_new = create_user(name, username, password)
    if created_new==False and is_parent(user):
        parent = user.parent
        message = "parent already exists. use already existing parent"
        status  = "successful"
        info = {"parent_username":user.username,"parent_name":user.first_name,"parent_id":parent.id,'parent_password':password}
    else:
        if email!=None:
            user.email = email
            user.save()
        parent = Parent.objects.create(user=user, mob_no=parent_mob_no_1)
        parent.first_password = password
        parent.save()
        message = "New parent created"
        status  = "successful"
        info = {"parent_username":user.username,"parent_name":user.first_name,"parent_id":parent.id,'parent_password':password}

    
    return {"info":info,
            'message':message,
            'status':status}