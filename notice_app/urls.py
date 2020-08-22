from django.urls import path
from . import views


urlpatterns = [
    path('create_notice/',views.create_notice),
    path('update_notice/',views.update_notice),
    path('delete_notice/',views.delete_notice),
    path('publish_notice/',views.publish_notice),
    path('read_notice/',views.read_notice),
    path('get_issued_notice_list/',views.get_issued_notice_list),
    path('get_notice_list/',views.get_notice_list),
    ]