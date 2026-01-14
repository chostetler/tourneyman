from django.urls import path, include
from . import views
from .views import TeamCreateView, RoomCreateView, MatchCreateView

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
    path('scorekeeper/', views.scorekeeper, name='scorekeeper'),

    # Import Django authentication views
    path('accounts/', include("django.contrib.auth.urls")),
    path('accounts/profile/', views.profile_view, name='profile_view'),

    # Data creation forms
    path('teams/add/', TeamCreateView.as_view(), name='team_create'),
    path('rooms/add/', RoomCreateView.as_view(), name='room_create'),
    path('matches/add/', MatchCreateView.as_view(), name='match_create'),
]
