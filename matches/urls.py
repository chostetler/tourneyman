from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('teams/', views.teams_list, name='teams_list'),
    path('region/<int:region_id>/', views.region_detail, name='region_detail'),
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
    path('scorekeeper', views.scorekeeper, name='scorekeeper'),
]
