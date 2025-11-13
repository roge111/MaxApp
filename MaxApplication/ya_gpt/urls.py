from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    
    path('yandex_gpt/', views.yandex_gpt, name='yandex_gpt'),
    
]