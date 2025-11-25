from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('teams/<int:team_id>/', views.team_detail, name='team_detail'),
    path('teams/', views.teams_list, name='teams_list'),
    path('regions/<int:region_id>/', views.region_detail, name='region_detail'),
    path('regions/', views.regions_list, name='regions_list'),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('rooms/', views.rooms_list, name='rooms_list'),
    path('matches/<int:match_id>/', views.match_detail, name='match_detail'),
    path('matches/', views.matches_list, name='matches_list'),
    path('scorekeeper', views.scorekeeper, name='scorekeeper'),
]
