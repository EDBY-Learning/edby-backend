import os
import django_heroku
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

######################---------------11111111111111-----------------------------###############################
#SECRET_KEY = 't51l5p5g6m20-1hfzipz7qdnz4e497iqz99_rpj(3y%*78$a8u'#
SECRET_KEY = os.environ.get('SECRET_KEY')
#########################################################################################################

######################-----------------2222222222222--------------------------###############################
temp = os.environ.get('DEBUG', default=False)
if temp == 'True' or temp == True:
    DEBUG = True
else:
    DEBUG = False
#########################################################################################################
    
CORS_ALLOW_CREDENTIALS = True
######################---------------33333333333333333333-----------------------###############################
#ALLOWED_HOSTS = []
ALLOWED_HOSTS = [ os.environ.get('site1'), os.environ.get('site2'), os.environ.get('site3'), os.environ.get('site4'), os.environ.get('site5')]
#########################################################################################################
CORS_ORIGIN_WHITELIST = [
    os.environ.get('site1'), os.environ.get('site2'), os.environ.get('site3'), os.environ.get('site4'), os.environ.get('site5')
]
######################---------------4444444444444444444444------------------------###############################
#"""
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 86400  # 1 day
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
#"""
#########################################################################################################

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'authority_app',
    'core',
    'student_app',
    'teacher_app',
    'applicant_app',
    'homework_app',
    'class_test_app',
    'storages',
    'notes_app',
    'notice_app',
    'quiz_app'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'school_online.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'school_online.wsgi.application'


######################----------------5555555555555555555555----------------------###############################
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
"""
#"""
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('HEROKU_POSTGRESQL_ROSE_URL')#DATABASE_URL
    )
}
#"""

##########################################################################################################

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
#STATICFILES_DIRS = (
#    os.path.join(BASE_DIR, 'static'),
#)
######################-------------6666666666666666666666666----------###############################
"""
AWS_ACCESS_KEY_ID = 'AKIAJRZM75XSGUKTZOFA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'school114'
AWS_QUERYSTRING_EXPIRE = 3600 #seconds
AWS_S3_FILE_OVERWRITE = False
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
"""

#"""
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID') #'AKIAYILN2NTZ35D7HGTE'
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')#'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'
AWS_STORAGE_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')#'school114'
AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
AWS_QUERYSTRING_AUTH = True
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_EXPIRE = 3600
#"""
######################----------------------------------------------------###############################


# s3 static settings
# STATIC_LOCATION = 'static'
# STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
# STATICFILES_STORAGE = 'core.storage_backends.StaticStorage'
# s3 public media settings
PUBLIC_MEDIA_LOCATION = 'media'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
DEFAULT_FILE_STORAGE = 'core.storage_backends.PublicMediaStorage'



## session expiray ## 
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 10800 # set just 10 seconds to test
SESSION_SAVE_EVERY_REQUEST = True

#File size limit, homework, class_test etc.
ONE_MB = 1048576 # 1024KB = 1024*1024 B = 1048576
MAX_FILE_SIZE_ALLOWED = ONE_MB*10 #10MB
django_heroku.settings(locals())