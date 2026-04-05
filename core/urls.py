"""Маршруты приложения core."""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout, name='logout'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('problems/', views.problem_list, name='problem_list'),
    path('problem/<int:problem_id>/', views.problem_detail, name='problem_detail'),
    path('problem/create/', views.problem_create, name='problem_create'),
    path('tests/', views.test_list, name='test_list'),
    path('test/<int:test_id>/', views.test_take, name='test_take'),
    path('test/<int:test_id>/result/', views.test_result, name='test_result'),
    path('brainstorm/', views.brainstorm_form, name='brainstorm_form'),
    path('brainstorm/take/', views.brainstorm_take, name='brainstorm_take'),
    path('brainstorm/result/', views.brainstorm_result, name='brainstorm_result'),
]