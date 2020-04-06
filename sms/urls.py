from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='sms-home'),    
    path('sendSMS/', views.send, name='sms-send'),
    path('loadData/', views.load, name='sms-incarca'),    
    path('about/', views.about, name='sms-about'),    

]