from django.urls import path

from . import views
from .views import LoadView, AboutView, HomeView, SendView
urlpatterns = [
    path('', HomeView.as_view(), name='sms-home'),    
    path('sendSMS/', SendView.as_view(), name='sms-send'),
    path('loadData/', LoadView.as_view(), name='sms-incarca'),    
    path('about/', AboutView.as_view(), name='sms-about'),    

]