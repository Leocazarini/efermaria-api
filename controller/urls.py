from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [

    path('', views.index, name='index'),
    path('logout/', views.logout, name='logout'),
    path('get_user/', views.get_user_info, name='get_user_info'),
    path('get_chart_data/', views.get_chart_data, name='chart_data'),


]