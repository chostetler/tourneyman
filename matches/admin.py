from django.contrib import admin
from .models import Region, Team, Room, Match

# Register your models here.

admin.site.register(Region)
admin.site.register(Room)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'region')
    list_filter = ('region',)
    search_fields = ('name',)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'match_number', 'room', 'start_time', 'is_complete', 'home_score', 'away_score')
    list_filter = ('room',)
    ordering = ('match_number',)


