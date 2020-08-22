from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.login_user),
    path('logout/',views.logout_user),
    path('change_password/',views.change_password),
    path('login_new/',views.login_with_token),
    path('logout_new/',views.logout_with_token),
    path('get_price/',views.get_price),
    path('check_login_with_token/',views.check_login_with_token),
    #path('login_with_token_test/',views.login_with_token_test),
    
]