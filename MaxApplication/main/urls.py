from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('yandex_gpt/', include('ya_gpt.urls')),
    path('register/', views.register, name='register'),
    path('logIn/', views.logIn, name='logIn'),
    path('logout/', views.logout, name='logout')
]