from django.db import models
from django.contrib.auth.models import User 
from django.core.validators import RegexValidator,MaxValueValidator
from datetime import date

PHONE_REGEX = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

class Demo_applicant(models.Model):
    institute_name = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    mob_no = models.CharField(validators=[PHONE_REGEX], max_length=17)
    email = models.EmailField()
    institute_type = models.CharField(max_length=25)
    designation = models.CharField(max_length=50)

#Applicant model#
class Applicant(models.Model):
    registrar_name = models.CharField(max_length=50)
    registrar_email = models.EmailField()
    registrar_mob_no = models.CharField(validators=[PHONE_REGEX], max_length=17) # validators 
    registrar_tel_no = models.CharField(validators=[PHONE_REGEX], max_length=17, blank=True) # validators 
    school_name = models.CharField(max_length=100)
    school_mob_no_1 = models.CharField(validators=[PHONE_REGEX], max_length=17) # validators 
    school_mob_no_2 = models.CharField(validators=[PHONE_REGEX], max_length=17) # validators     
    school_tel_no = models.CharField(validators=[PHONE_REGEX], max_length=17, blank=True) # validators 
    school_email = models.EmailField(blank=True)
    school_code = models.CharField(max_length=20)
    addr = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    nation = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)
    board = models.CharField(max_length=50)

    def __str__(self):
        return self.school_name
    

#school model#
class School(models.Model):
    #registrar_name = models.CharField(max_length=50)
    #registrar_email = models.EmailField()
    #registrar_mob_no = models.CharField(validators=[PHONE_REGEX], max_length=17) # validators 
    #registrar_tel_no = models.CharField(validators=[PHONE_REGEX], max_length=17, blank=True) # validators 
    school_name = models.CharField(max_length=100)
    school_mob_no_1 = models.CharField(validators=[PHONE_REGEX], max_length=17) # validators 
    school_mob_no_2 = models.CharField(validators=[PHONE_REGEX], max_length=17) # validators     
    school_tel_no = models.CharField(validators=[PHONE_REGEX], max_length=17, blank=True) # validators 
    school_email = models.EmailField(blank=True)
    school_code = models.CharField(max_length=20)
    addr = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    nation = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)
    board = models.CharField(max_length=50)

    def __str__(self):
        return self.school_name


#class model#
class Class(models.Model):
    # CLASS_CHOICES = (
    #     ('NS','Nursery'),
    #     ('UKG','UKG'),
    #     ('LKG','LKG'),
    #     ('1','1'),
    #     ('2','2'),
    #     ('3','3')
    # )
    # class_name = models.CharField(max_length=4, choices=CLASS_CHOICES)
    class_name = models.CharField(max_length=4)
    section = models.CharField(max_length=2)
    
    #relations#
    school = models.ForeignKey('School', on_delete=models.CASCADE)
    class_teacher = models.OneToOneField('Teacher',blank=True,null=True,on_delete=models.SET_NULL, related_name="class_is")

    def __str__(self):
        return self.class_name + " " + self.section
    
    def get_summary(self):
        summary_dict = {}
        summary_dict['class_id'] =self.id
        summary_dict['class_name'] = self.class_name
        summary_dict['section'] = self.section
        summary_dict['school_id'] = self.school.id
        summary_dict['school_name'] = self.school.school_name
        summary_dict['class_teacher_id'] = ""
        summary_dict['class_teacher_name'] = ""
        if self.class_teacher:
            summary_dict['class_teacher_id'] = self.class_teacher.id
            summary_dict['class_teacher_name'] = self.class_teacher.user.first_name
        return summary_dict

#student model#
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #middle_name = models.CharField(max_length=30)
    roll = models.CharField(max_length=10)
    mob_no = models.CharField(validators=[PHONE_REGEX], max_length=17, blank=True) # validators 
    addr = models.CharField(max_length=100)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    nation = models.CharField(max_length=20)
    pincode = models.CharField(max_length=6)
    parent_mob_no_1 = models.CharField(validators=[PHONE_REGEX], max_length=17) # validators 
    parent_mob_no_2 = models.CharField(validators=[PHONE_REGEX], max_length=17, blank=True) # validators 
    parent_email = models.EmailField(blank=True)
    first_password = models.CharField(max_length=10, blank=True)
    #relations#
    class_is = models.ForeignKey('Class', on_delete=models.CASCADE)
    parent = models.ForeignKey('Parent', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.first_name

    def get_summary(self):
        summary_dict = {}
        summary_dict['student_id'] = self.id
        summary_dict['student_name'] = self.user.first_name
        summary_dict['school_id'] = self.class_is.school.id
        summary_dict['school_name'] = self.class_is.school.school_name
        summary_dict['class_name'] = self.class_is.class_name
        summary_dict['section'] = self.class_is.section
        summary_dict['mob_no'] = self.mob_no
        summary_dict['email'] = self.user.email
        summary_dict['addr'] = self.addr
        summary_dict['city'] = self.city
        summary_dict['state'] = self.state
        summary_dict['nation'] = self.nation
        summary_dict['pincode'] = self.pincode
        summary_dict['parent_mob_no_1'] = self.parent_mob_no_1
        summary_dict['parent_mob_no_2'] = self.parent_mob_no_2
        summary_dict['parent_email'] = self.parent_email
        if self.class_is.class_teacher:
            summary_dict['class_teacher'] = self.class_is.class_teacher.user.first_name
        summary_dict['roll'] = self.roll
        return summary_dict

    def get_priviledged_summary(self):
        summary_dict = {}
        summary_dict['student_id'] = self.id
        summary_dict['username'] = self.user.username
        summary_dict['student_name'] = self.user.first_name
        summary_dict['school_id'] = self.class_is.school.id
        summary_dict['school_name'] = self.class_is.school.school_name
        summary_dict['class_name'] = self.class_is.class_name
        summary_dict['section'] = self.class_is.section
        summary_dict['mob_no'] = self.mob_no
        summary_dict['email'] = self.user.email
        summary_dict['addr'] = self.addr
        summary_dict['city'] = self.city
        summary_dict['state'] = self.state
        summary_dict['nation'] = self.nation
        summary_dict['pincode'] = self.pincode
        summary_dict['parent_mob_no_1'] = self.parent_mob_no_1
        summary_dict['parent_mob_no_2'] = self.parent_mob_no_2
        summary_dict['parent_email'] = self.parent_email
        if self.class_is.class_teacher:
            summary_dict['class_teacher'] = self.class_is.class_teacher.user.first_name
        summary_dict['roll'] = self.roll
        summary_dict['first_password'] = self.first_password
        return summary_dict

#teacher model#
#Fields: Name, email, School F
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # middle_name = models.CharField(max_length=30)
    #email = models.EmailField()
    mob_no = models.CharField(validators=[PHONE_REGEX], max_length=17, blank=True) # validators 
    addr = models.CharField(max_length=100)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    nation = models.CharField(max_length=20)
    pincode = models.CharField(max_length=6)
    is_class_teacher = models.BooleanField(blank=True)
    first_password = models.CharField(max_length=10, blank=True)

    #relations#
    school = models.ForeignKey('School', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name

    def get_summary(self):
        summary_dict = {}
        summary_dict['teacher_id'] = self.id
        summary_dict['teacher_name'] = self.user.first_name
        summary_dict['school_id'] = self.school.id
        summary_dict['school_name'] = self.school.school_name
        summary_dict['mob_no'] = self.mob_no
        summary_dict['email'] = self.user.email
        summary_dict['addr'] = self.addr
        summary_dict['city'] = self.city
        summary_dict['state'] = self.state
        summary_dict['nation'] = self.nation
        summary_dict['pincode'] = self.pincode
        if self.is_class_teacher:
            summary_dict['is_class_teacher'] = 'True'
        else:
            summary_dict['is_class_teacher'] = 'False'
        summary_dict['class_name'] = ""
        summary_dict['section'] = ""
        if self.is_class_teacher:
            try:
                class_ = Class.objects.get(class_teacher__id=self.id)
                summary_dict['class_name'] = class_.class_name
                summary_dict['section'] = class_.section
            except:
                pass
        return summary_dict

    def get_priviledged_summary(self):
        summary_dict = {}
        summary_dict['teacher_id'] = self.id
        summary_dict['username'] = self.user.username
        summary_dict['teacher_name'] = self.user.first_name
        summary_dict['school_id'] = self.school.id
        summary_dict['school_name'] = self.school.school_name
        summary_dict['mob_no'] = self.mob_no
        summary_dict['email'] = self.user.email
        summary_dict['addr'] = self.addr
        summary_dict['city'] = self.city
        summary_dict['state'] = self.state
        summary_dict['nation'] = self.nation
        summary_dict['pincode'] = self.pincode
        if self.is_class_teacher:
            summary_dict['is_class_teacher'] = 'True'
        else:
            summary_dict['is_class_teacher'] = 'False'
        summary_dict['class_name'] = ""
        summary_dict['section'] = ""
        if self.is_class_teacher:
            try:
                class_ = Class.objects.get(class_teacher__id=self.id)
                summary_dict['class_name'] = class_.class_name
                summary_dict['section'] = class_.section
            except:
                pass
        summary_dict['first_password'] = self.first_password
        return summary_dict


    def get_summary_for_teacher(self):
        summary_dict = {}
        summary_dict['teacher_id'] = self.id
        summary_dict['teacher_name'] = self.user.first_name
        summary_dict['school_id'] = self.school.id
        summary_dict['school_name'] = self.school.school_name
        summary_dict['mob_no'] = self.mob_no
        return summary_dict

#authority model#
class Authority(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # middle_name = models.CharField(max_length=30)
    designation = models.CharField(max_length=20)
    power_level = models.CharField(max_length=1, blank=True)
    mob_no = models.CharField(validators=[PHONE_REGEX], max_length=17, blank=True) # validators 
    addr = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=20, blank=True)
    nation = models.CharField(max_length=20, blank=True)
    pincode = models.CharField(max_length=6, blank=True)
    first_password = models.CharField(max_length=10, blank=True)

    #relations#
    school = models.ForeignKey('School', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name

    def get_summary(self):
        summary_dict = {}
        summary_dict['username'] = self.user.username
        summary_dict['first_password'] = self.first_password
        summary_dict['authority_id'] = self.id
        summary_dict['authority_name'] = self.user.first_name
        summary_dict['school_id'] = self.school.id
        summary_dict['school_name'] = self.school.school_name
        summary_dict['designation'] = self.designation
        summary_dict['mob_no'] = self.mob_no
        summary_dict['email'] = self.user.email
        summary_dict['addr'] = self.addr
        summary_dict['city'] = self.city
        summary_dict['state'] = self.state
        summary_dict['nation'] = self.nation
        summary_dict['pincode'] = self.pincode
        return summary_dict

#slot model#
class Slot(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    day = models.CharField(max_length=9)
    start_time = models.TimeField(auto_now=False, auto_now_add=False)
    end_time = models.TimeField(auto_now=False, auto_now_add=False)
    period_number = models.PositiveIntegerField(validators=[MaxValueValidator(10)])

    def __str__(self):
        return 'School : ' + str(self.school) + ', Day : ' + self.day + ', Period no : ' +str(self.period_number)

    def get_summary(self):
        summary_dict = {}
        summary_dict['slot_id'] = self.id
        summary_dict['school_id'] = self.school.id
        summary_dict['school_name'] = self.school.school_name
        summary_dict['start_time'] = self.start_time
        summary_dict['end_time'] = self.end_time
        summary_dict['day'] = self.day
        summary_dict['period_number'] = self.period_number
        return summary_dict


#subject model
class Subject(models.Model):
    subject_name = models.CharField(max_length=20)
    link = models.CharField(max_length=200,blank=True)
    event_id = models.CharField(max_length=1024,blank=True)
    alternate_link = models.CharField(max_length=200,blank=True)
    alternate_password = models.CharField(max_length=100,blank=True)
    alternate_description = models.CharField(max_length=100,blank=True)
    #relations
    teacher = models.ForeignKey(Teacher, null=True, blank=True, on_delete=models.SET_NULL)
    class_is = models.ForeignKey(Class, on_delete=models.CASCADE)

    def __str__(self):
        return self.subject_name

    def get_summary(self):
        summary_dict = {}
        summary_dict['subject_id'] = self.id
        summary_dict['subject_name'] = self.subject_name
        if self.teacher:
            summary_dict['teacher_id'] = self.teacher.id
            summary_dict['teacher_name'] = self.teacher.user.first_name
        else:
            summary_dict['teacher_id'] = ""
            summary_dict['teacher_name'] = ""
        summary_dict['class_id'] = self.class_is.id
        summary_dict['class_name'] = self.class_is.class_name
        summary_dict['section'] = self.class_is.section
        summary_dict['link'] = self.link
        summary_dict['password'] = ""
        summary_dict['description'] = "Google Meet"
        if self.alternate_link:
            summary_dict['link'] = self.alternate_link
            summary_dict['password'] = self.alternate_password
            summary_dict['description'] = self.alternate_description
        return summary_dict

    def get_summary_for_class_teacher(self):
        summary_dict = {}
        summary_dict['subject_id'] = self.id
        summary_dict['subject_name'] = self.subject_name
        summary_dict['teacher_id'] = self.teacher.id
        summary_dict['teacher_name'] = self.teacher.user.first_name
        summary_dict['teacher_mob_no'] = self.teacher.mob_no
        return summary_dict

#schedule model
class Schedule(models.Model):
    #relations
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    subject = models.ManyToManyField(Subject)

    def __str__(self):
        return str(self.subject) + "  " + str(self.slot) 

    def get_summary(self):
        summary_dict = {}
        summary_dict['schedule_id'] = self.id
        summary_dict['slot_id'] = self.slot.id
        summary_dict['day'] = self.slot.day
        summary_dict['period_number'] = self.slot.period_number
        subject_id = []
        subject_name = []
        teacher_id = []
        teacher_name = []
        links = []
        passwords = []
        descriptions = []
        for subject in self.subject.all():
            subject_id.append(subject.id)
            subject_name.append(subject.subject_name)
            if subject.teacher:
                teacher_id.append(subject.teacher.id)
                teacher_name.append(subject.teacher.user.first_name)
            else:
                teacher_id.append("")
                teacher_name.append("")
            if subject.alternate_link:
                links.append(subject.alternate_link)
                passwords.append(subject.alternate_password)
                descriptions.append(subject.alternate_description)
            else:
                links.append(subject.link)
                passwords.append("")
                descriptions.append("Google Meet")
        summary_dict['subject_id'] = subject_id
        summary_dict['subject_name'] = subject_name
        summary_dict['teacher_id'] = teacher_id
        summary_dict['teacher_name'] = teacher_name
        summary_dict['links'] = links
        summary_dict['passwords'] = passwords
        summary_dict['descriptions'] = descriptions
        return summary_dict

    def get_summary_for_teacher(self,teacher):
        summary_dict = {}
        summary_dict['schedule_id'] = self.id
        summary_dict['slot_id'] = self.slot.id
        summary_dict['day'] = self.slot.day
        summary_dict['period_number'] = self.slot.period_number
        try:
            subject = self.subject.all().get(teacher=teacher)
            summary_dict['class_name'] = subject.class_is.class_name
            summary_dict['section'] = subject.class_is.section
            summary_dict['subject_id'] = subject.id
            summary_dict['subject_name'] = subject.subject_name
            summary_dict['link'] = subject.link
        except:
            summary_dict['class_name'] = ""
            summary_dict['section'] = ""
            summary_dict['subject_id'] = ""
            summary_dict['subject_name'] = ""
            summary_dict['link'] = ""
        return summary_dict


import os
from uuid import uuid4
#https://stackoverflow.com/a/15141228/8773779

# def path_and_rename(path):
#     def wrapper(instance, filename):
#         ext = filename.split('.')[-1]
#         # get filename
#         if instance.pk:
#             filename = '{}.{}'.format(instance.pk, ext)
#         else:
#             # set filename as random string
#             filename = '{}.{}'.format(uuid4().hex, ext)
#         # return the whole path to the file
#         return os.path.join(path, filename)
#     return wrapper

def homework_files_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(str(instance.pk)+uuid4().hex,ext)
    # return the whole path to the file
    return os.path.join('homework/', filename)

def homework_submission_files_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(str(instance.pk)+uuid4().hex,ext)
    # return the whole path to the file
    return os.path.join('homework_submission/', filename)

def homework_checked_files_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(str(instance.pk)+uuid4().hex,ext)
    # return the whole path to the file
    return os.path.join('homework_submission_checked/', filename)

def class_test_files_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(str(instance.pk)+uuid4().hex,ext)
    # return the whole path to the file
    return os.path.join('class_test/', filename)

def class_test_submission_files_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(str(instance.pk)+uuid4().hex,ext)
    # return the whole path to the file
    return os.path.join('class_test_submission/', filename)

def class_test_checked_files_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(str(instance.pk)+uuid4().hex,ext)
    # return the whole path to the file
    return os.path.join('class_test_submission_checked/', filename)

def notes_files_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(str(instance.pk)+uuid4().hex,ext)
    # return the whole path to the file
    return os.path.join('notes/', filename)


class Homework(models.Model):
    homework_name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    homework_file = models.FileField(upload_to=homework_files_path, max_length=200)
    start_time = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    end_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    is_graded = models.BooleanField(default=False)
    maximum_marks = models.PositiveIntegerField(validators=[MaxValueValidator(500)], blank=True, null=True)
    is_published = models.BooleanField(default=False)
    year = models.PositiveIntegerField(validators=[MaxValueValidator(3000)], blank=True, null=True)

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return "Subject : " +str(self.subject) + ", Homework Name : " + (self.homework_name)

    def get_summary(self):
        summary_dict = {}
        summary_dict['homework_id'] = self.id
        summary_dict['homework_name'] = self.homework_name
        summary_dict['subject_id'] = self.subject.id
        summary_dict['subject_name'] = self.subject.subject_name
        summary_dict['description'] = self.description
        try:
            summary_dict['homework_file'] = self.homework_file.url
        except:
            summary_dict['homework_file'] = None
        summary_dict['start_time'] = self.start_time
        summary_dict['end_time'] = self.end_time
        summary_dict['is_graded'] = self.is_graded
        summary_dict['maximum_marks'] = self.maximum_marks
        summary_dict['is_published'] = self.is_published
        summary_dict['year'] = self.year
        return summary_dict

    def get_summary_for_teacher(self):
        summary_dict = self.get_summary()
        summary_dict['number_of_submissions'] = Homework_submission.objects.filter(homework=self.id).count()
        return summary_dict

    def get_summary_for_student(self,student_id):
        summary_dict = self.get_summary()
        summary_dict['is_submitted'] = Homework_submission.objects.filter(homework=self.id,student=student_id).exists()
        return summary_dict

class Homework_submission(models.Model):
    submission_file = models.FileField(upload_to=homework_submission_files_path, max_length=200)
    submission_time = models.DateTimeField(auto_now=True, auto_now_add=False)
    marks = models.PositiveIntegerField(validators=[MaxValueValidator(500)], blank=True, null=True)
    checked_file = models.FileField(upload_to=homework_checked_files_path, max_length=200, blank=True, null=True)
    is_checked = models.BooleanField(default=False)

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE)

    def __str__(self):
        return "Student : " +str(self.student) + ", Homework : " + (self.homework)

    def get_summary(self):
        summary_dict = {}
        summary_dict['submission_id'] = self.id
        summary_dict['student_id'] = self.student.id
        summary_dict['student_name'] = self.student.user.first_name
        summary_dict['homework_id'] = self.homework.id
        summary_dict['homework_name'] = self.homework.homework_name
        if(self.submission_file):
            summary_dict['submission_file'] = self.submission_file.url
        else:
            summary_dict['submission_file'] = ''
        summary_dict['submission_time'] = self.submission_time
        #summary_dict['submission_file'] = self.submission_file.url
        summary_dict['marks'] = self.marks
        summary_dict['is_checked'] = self.is_checked
        try:
            summary_dict['checked_file'] = self.checked_file.url
        except:
            summary_dict['checked_file'] = None
        return summary_dict

class Class_test(models.Model):
    class_test_name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True, null=True)
    class_test_file = models.FileField(upload_to=class_test_files_path, max_length=200)
    start_time = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    # DurationField check karna arithmetic with DateTimeField Postgres
    buffer_time = models.DurationField(blank=True, null=True)
    duration = models.DurationField()
    is_graded = models.BooleanField(default=True)
    maximum_marks = models.PositiveIntegerField(validators=[MaxValueValidator(500)], blank=True, null=True)
    is_published = models.BooleanField(default=False)
    year = models.PositiveIntegerField(validators=[MaxValueValidator(3000)], blank=True, null=True)

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return "Subject : " +str(self.subject) + ", Class test Name : " + (self.class_test_name)

    def get_summary(self):
        summary_dict = {}
        summary_dict['class_test_id'] = self.id
        summary_dict['class_test_name'] = self.class_test_name
        summary_dict['subject_id'] = self.subject.id
        summary_dict['subject_name'] = self.subject.subject_name
        summary_dict['description'] = self.description
        try:
            summary_dict['class_test_file'] = self.class_test_file.url
        except:
            summary_dict['class_test_file'] = None
        summary_dict['start_time'] = self.start_time
        summary_dict['buffer_time'] = self.buffer_time
        summary_dict['duration'] = self.duration
        summary_dict['is_graded'] = self.is_graded
        summary_dict['maximum_marks'] = self.maximum_marks
        summary_dict['is_published'] = self.is_published
        summary_dict['year'] = self.year
        return summary_dict

    def get_summary_for_teacher(self):
        summary_dict = self.get_summary()
        summary_dict['number_of_submissions'] = Class_test_submission.objects.filter(class_test=self.id).count()
        return summary_dict

    def get_summary_for_student(self,student_id):
        summary_dict = self.get_summary()
        summary_dict['is_submitted'] = Class_test_submission.objects.filter(class_test=self.id,student=student_id).exists()
        return summary_dict


class Class_test_submission(models.Model):
    submission_file = models.FileField(upload_to=class_test_submission_files_path, max_length=200)
    start_time = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    upload_start_time = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    submission_time = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    marks = models.PositiveIntegerField(validators=[MaxValueValidator(500)], blank=True, null=True)
    checked_file = models.FileField(upload_to=class_test_checked_files_path, max_length=200, blank=True, null=True)
    is_checked = models.BooleanField(default=False)
    is_submitted = models.BooleanField(default=False)

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_test = models.ForeignKey(Class_test, on_delete=models.CASCADE)

    def __str__(self):
        return "Student : " +str(self.student) + ", class_test : " + (self.class_test)

    def get_summary(self):
        summary_dict = {}
        summary_dict['submission_id'] = self.id
        summary_dict['student_id'] = self.student.id
        summary_dict['student_name'] = self.student.user.first_name
        summary_dict['class_test_id'] = self.class_test.id
        summary_dict['class_test_name'] = self.class_test.class_test_name
        if(self.submission_file):
            summary_dict['submission_file'] = self.submission_file.url
        else:
            summary_dict['submission_file'] = ''
        #summary_dict['submission_file'] = self.submission_file.url
        summary_dict['start_time'] = self.start_time
        summary_dict['upload_start_time'] = self.upload_start_time
        summary_dict['submission_time'] = self.submission_time
        summary_dict['marks'] = self.marks
        summary_dict['is_checked'] = self.is_checked
        try:
            summary_dict['checked_file'] = self.checked_file.url
        except:
            summary_dict['checked_file'] = None
        summary_dict['is_submitted'] = self.is_submitted
        return summary_dict


class Session(models.Model):
    token = models.CharField(max_length=32, null=True)
    last_request = models.DateTimeField(auto_now=False)

    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Attendance(models.Model):
    date = models.DateField(auto_now=False, auto_now_add=True)#(auto_now=False, auto_now_add=False, blank=True, null=True)#
    total_questions = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)], default=0)
    answered_questions = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)], default=0)

    student = models.ForeignKey(Student, on_delete=models.CASCADE)



class Notes(models.Model):
    notes_name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    notes_file = models.FileField(upload_to=notes_files_path, max_length=200)
    publish_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_edit_time = models.DateTimeField(auto_now=True, auto_now_add=False)
    year = models.PositiveIntegerField(validators=[MaxValueValidator(3000)], blank=True, null=True)

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return "Subject : " + str(self.subject) + ", Name:" + self.notes_name

    def get_summary(self):
        summary_dict = {}
        summary_dict['notes_id'] = self.id
        summary_dict['notes_name'] = self.notes_name
        summary_dict['subject_id'] = self.subject.id
        summary_dict['subject_name'] = self.subject.subject_name
        summary_dict['description'] = self.description
        try:
            summary_dict['notes_file'] = self.notes_file.url
        except:
            summary_dict['notes_file'] = ''
        summary_dict['publish_time'] = self.publish_time
        summary_dict['last_edit_time'] = self.last_edit_time
        return summary_dict
    
class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # middle_name = models.CharField(max_length=30)
    #email = models.EmailField()
    mob_no = models.CharField(validators=[PHONE_REGEX], max_length=17, blank=True) # validators 
    first_password = models.CharField(max_length=10, blank=True)

def notice_files_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(str(instance.pk)+uuid4().hex,ext)
    # return the whole path to the file
    return os.path.join('notice/', filename)

def quiz_files_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(str(instance.pk)+uuid4().hex,ext)
    # return the whole path to the file
    return os.path.join('quiz/', filename)


class Category(models.Model):
    classification = models.CharField(max_length=25, primary_key=True)

class Notice(models.Model):
    issuer = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category)
    heading = models.CharField(max_length=100, blank=True)
    text = models.CharField(max_length=500, blank=True)
    file = models.FileField(upload_to=notice_files_path, max_length=200, blank=True, null=True)
    create_dt = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_edit_dt = models.DateTimeField(auto_now_add=False, auto_now=True)
    is_published = models.BooleanField(default=False)
    issue_dt = models.DateTimeField(auto_now_add=False, auto_now=False, blank=True, null=True)

    def get_summary(self):
        summary_dict = {}
        summary_dict['notice_id'] = self.id
        summary_dict['issuer_name'] = self.issuer.first_name
        try:
            self.issuer.teacher
            is_teacher = True
        except:
            is_teacher = False
        summary_dict['issuer_designation'] = "teacher" if is_teacher else "authority"
        summary_dict['issuer_id'] = self.issuer.id
        summary_dict['category_description'] = [c.classification for c in self.category.all()]
        summary_dict['notice_heading'] = self.heading
        summary_dict['notice_text'] = self.text
        try:
            summary_dict['notice_file'] = self.file.url
        except:
            summary_dict['notice_file'] = ''
        summary_dict['is_published'] = self.is_published
        if self.issue_dt!=None:
            summary_dict['issue_dt']=self.issue_dt.isoformat()
        else:
            summary_dict['issue_dt'] = '' 
        summary_dict['last_edit_dt'] = self.last_edit_dt.isoformat()
        summary_dict['create_dt'] = self.create_dt.isoformat()
        return summary_dict

class Quiz(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    heading = models.CharField(max_length=100, blank=True)
    kind = models.CharField(max_length=10)
    duration = models.DurationField()
    normalized_marks = models.PositiveSmallIntegerField(validators=[MaxValueValidator(500)], blank=True, null=True)
    is_published = models.BooleanField(default=False)
    last_edit_dt = models.DateTimeField(auto_now_add=False, auto_now=True)
    start_dt = models.DateTimeField(auto_now_add=False, auto_now=False, blank=True, null=True)

    def get_summary(self):
        quiz_summary = {}
        quiz_summary['quiz_id'] = self.id
        quiz_summary['quiz_heading'] = self.heading
        quiz_summary['quiz_type'] = self.kind
        quiz_summary['duration'] = self.duration
        quiz_summary['is_published'] = self.is_published
        quiz_summary['start_dt'] = self.start_dt
        quiz_summary['last_edit_dt'] = self.last_edit_dt
        quiz_summary['normalized_marks'] = self.normalized_marks

        return quiz_summary

    def get_summary_teacher(self):
        quiz_summary = self.get_summary()

        #question_list = []
        #print(Question.objects.filter(quiz=self))
        #for question in Question.objects.filter(quiz=self):
        #    question_list.append(question.get_summary_teacher())
        
        #print(question_list)
        return {"quiz_summary":quiz_summary}#, "question_list":question_list}

    def get_full_summary_teacher(self):
        quiz_summary = self.get_summary()

        question_list = []
        #print(Question.objects.filter(quiz=self))
        for question in Question.objects.filter(quiz=self):
            question_list.append(question.get_summary_teacher())
        
        #print(question_list)
        return {"quiz_summary":quiz_summary, "question_list":question_list}

    def get_summary_student_correct_answer(self):
        quiz_summary = self.get_summary()

        question_list = []
        #print(Question.objects.filter(quiz=self))
        for question in Question.objects.filter(quiz=self):
            question_list.append(question.get_summary_teacher())
        
        #print(question_list)
        return {"quiz_summary":quiz_summary, "question_list":question_list}

    def get_summary_student(self,student):
        if not self.is_published:
            return {}

        quiz_summary = self.get_summary()
        quiz_summary['is_submitted'] = False
        quiz_submission = Quiz_submission.objects.filter(quiz=self, student=student)
        if len(quiz_submission) != 0:
            quiz_summary['is_submitted'] = quiz_submission[0].is_submitted

        question_list = []
        for question in Question.objects.filter(quiz=self):
            question_dict = question.get_summary_student(student)
            question_list.append(question_dict)

        return {"quiz_summary":quiz_summary, "question_list":question_list}

    def get_summary_student_unpublished(self,student):
        if self.is_published:
            return {}
        quiz_summary = self.get_summary()
        quiz_summary['is_submitted'] = False
        return {"quiz_summary":quiz_summary}

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    number = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])
    kind = models.CharField(max_length=10)
    text = models.CharField(max_length=500, blank=True)
    file = models.ImageField(upload_to=quiz_files_path, max_length=200, blank=True, null=True)
    maximum_marks = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])

    def get_summary(self):
        question_dict = {}
        question_dict['question_id'] = self.id
        question_dict['number'] = self.number
        question_dict['question_type'] = self.kind
        question_dict['question_text'] = self.text
        question_dict['question_file'] = ""
        try:
            question_dict['question_file_link'] = self.file.url
        except:
            question_dict['question_file_link'] = ""
        question_dict['marks'] = self.maximum_marks
        question_dict['option_list'] = []
        
        for option in Option.objects.filter(question=self):
            option_dict = {}
            option_dict['option_id'] = option.id
            option_dict['option_code'] = option.code
            option_dict['option_text'] = option.text
            option_dict['option_file'] = ""
            try:
                option_dict['option_file_link'] = option.file.url
            except:
                option_dict['option_file_link'] = ""
            question_dict['option_list'].append(option_dict)

        return question_dict

    def get_summary_student(self,student):
        if not self.quiz.is_published:
            return {}
        question_dict = self.get_summary()
        response = Question_response.objects.filter(student=student,question=self)
        question_dict['answer_list'] = []
        question_dict['response_file'] = ''
        question_dict['response_file_link'] = ''
        response_qs = Response_answer.objects.filter(question_response__question=self)
        if len(response_qs) != 0:
            if self.kind == "mcq":
                answer_list = [response.text for response in response_qs]
                for alphabet in ["A","B","C","D"]:
                    if alphabet in answer_list:
                        question_dict['answer_list'].append(alphabet)
                    else:
                        question_dict['answer_list'].append("")
            else:
                response = response_qs[0]
                #print(response.text)
                question_dict['answer_list'].append(response.text)
                try:
                    question_dict['response_file_link'] = response.file.url
                except:
                    pass
        return question_dict

    def get_summary_teacher(self):
        question_dict = self.get_summary()

        question_dict['answer_list'] = []
        if question_dict['question_type'] == "mcq":
            answer_code_list = [answer.text for answer in Correct_answer.objects.filter(question=self)]
            for alphabet in ["A","B","C","D"]:
                if alphabet in answer_code_list:
                    question_dict['answer_list'].append(alphabet)
                else:
                    question_dict['answer_list'].append("")
        else:
            try:
                correct_answer = Correct_answer.objects.filter(question=self)[0]
                question_dict['answer_list'].append(correct_answer.text)
            except:
                question_dict['answer_list'].append("")
        return question_dict


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    code = models.CharField(max_length=1)
    text = models.CharField(max_length=100, blank=True)
    file = models.ImageField(upload_to=quiz_files_path, max_length=200, blank=True, null=True)

class Correct_answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=100)
    #option = models.OneToOneField(Option, on_delete=models.CASCADE)

class Question_response(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    marks = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)], blank=True, null=True)

class Response_answer(models.Model):
    question_response = models.ForeignKey(Question_response, on_delete=models.CASCADE, blank=True, null=True)
    text = models.CharField(max_length=500, blank=True)
    file = models.ImageField(upload_to=quiz_files_path, max_length=200, blank=True, null=True)

class Quiz_submission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz,on_delete=models.CASCADE)
    marks = models.PositiveSmallIntegerField(validators=[MaxValueValidator(500)], blank=True, null=True)
    is_submitted = models.BooleanField(default=False)
    is_graded = models.BooleanField(default=False)
    submission_dt = models.DateTimeField(auto_now_add=False, auto_now=True)

    def get_summary(self):
        submission_dict ={}
        submission_dict['student_id'] = self.student.id
        submission_dict['student_name'] = self.student.user.first_name
        submission_dict['student_roll'] = self.student.roll
        submission_dict['quiz_id'] = self.quiz.id
        submission_dict['quiz_heading'] = self.quiz.heading
        submission_dict['marks'] = self.marks
        submission_dict['is_submitted'] = self.is_submitted
        submission_dict['is_graded'] = self.is_graded
        submission_dict['submission_dt'] = self.submission_dt
        submission_dict['response_list'] = []
        for response in Question_response.objects.filter(student=self.student,question__quiz=self.quiz):
            response_dict = {}
            response_dict['response_id'] = response.id
            response_dict['response_file'] = ""
            response_dict['response_file_link'] = ""
            
                
            question = response.question
            response_dict['question_id'] = question.id
            response_dict['marks'] = ""
            if response.marks:
                response_dict['marks'] = response.marks
            response_answer = []
            response_answer_qs = Response_answer.objects.filter(question_response=response)
            if len(response_answer_qs) != 0:
                if question.kind == "mcq":
                    response_answer_list = [r_a.text for r_a in response_answer_qs]
                    for alphabet in ["A","B","C","D"]:
                        if alphabet in response_answer_list:
                            response_answer.append(alphabet)
                        else:
                            response_answer.append("")
                else:
                    r_a = response_answer_qs[0]
                    response_answer.append(r_a.text)
                    try:
                        response_dict['response_file_link'] = r_a.file.url
                    except:
                        pass
            response_dict['response_answer'] = response_answer
            submission_dict['response_list'].append(response_dict)
        return submission_dict

    def get_brief_summary(self):
        submission_dict ={}
        submission_dict['student_id'] = self.student.id
        submission_dict['student_name'] = self.student.user.first_name
        submission_dict['student_roll'] = self.student.roll
        submission_dict['marks'] = self.marks
        submission_dict['is_submitted'] = self.is_submitted
        submission_dict['is_graded'] = self.is_graded
        submission_dict['submission_dt'] = self.submission_dt
        return submission_dict
