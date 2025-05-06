from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('region/<int:region_id>/', views.region_detail, name='region_detail')
]
