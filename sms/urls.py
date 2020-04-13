from django.urls import path

from .views import LoadView, AboutView, HomeView, SendView, MesajeView, modify
urlpatterns = [
    path('', HomeView.as_view(), name='sms-home'),    
    path('sendSMS/', SendView.as_view(), name='sms-send'),
    path('incarca/', LoadView.as_view(), name='sms-incarca'),    
    path('despre/', AboutView.as_view(), name='sms-about'),    
    path('mesaje/', MesajeView.as_view(), name='sms-mesaje'),    
    path('modify/', modify, name='sms-modify')
]