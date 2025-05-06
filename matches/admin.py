from django.contrib import admin
from .models import Region, Team, Room, Matchup, MatchupSource

# Register your models here.

admin.site.register(Region)
admin.site.register(Room)
admin.site.register(Matchup)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'rank')
    list_filter = ('region',)
    search_fields = ('name',)

