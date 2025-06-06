from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('teams/<int:team_id>/', views.team_detail, name='team_detail'),
    path('teams/', views.teams_list, name='teams_list'),
    path('regions/<int:region_id>/', views.region_detail, name='region_detail'),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('matchups/<int:matchup_id>/', views.matchup_detail, name='matchup_detail'),
    path('scorekeeper', views.scorekeeper, name='scorekeeper'),
]
