from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('yandex_gpt/', include('ya_gpt.urls')),
    path('register/', views.register, name='register'),
    path('logIn/', views.logIn, name='logIn'),
    path('logout/', views.logout, name='logout'),
    path('create_volunteer_request/', views.create_volunteer_request, name='create_volunteer_request'),
    path('view_volunteer_requests/', views.view_volunteer_requests, name='view_volunteer_requests'),
    path('accept_volunteer_request/', views.accept_volunteer_request, name='accept_volunteer_request'),
]