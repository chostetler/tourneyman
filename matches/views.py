from django.shortcuts import render
from .models import Region, Team, Room, Matchup, MatchupSource

# Create your views here.
def home(request):
    return render(request, 'home.html')

def teams_list(request):
    t = Team.objects.all().order_by('name')
    return render(request, 'teams.html', {'teams': t})

def team_detail(request, team_id):
    try:
        t = Team.objects.get(pk=team_id)
        m = t.all_matchups().order_by('match_number')
        
    except Team.DoesNotExist:
        raise Http404("Team does not exist")
    return render(request, 'team.html', {'team': t, 'matchups': m})

def region_detail(request, region_id):
    try:
        r = Region.objects.get(pk=region_id)
        t = r.team_set.all()
    except Region.DoesNotExist:
        raise Http404("Region does not exist")
    return render(request, 'region.html', {'region': r, 'teams': t})

def room_detail(request, room_id):
    try:
        r = Room.objects.get(pk=room_id)
        m = r.all_matchups().order_by('match_number')
    except Region.DoesNotExist:
        raise Http404("Room does not exist")
    return render(request, 'room.html', {'room': r, 'matchups': m})

def scorekeeper(request):
    """View for scorekeepers, allowing them to enter results for active games"""
    m = Matchup.objects.all().filter(is_complete=False).order_by('match_number')
    return render(request, 'scorekeeper.html', {'matchups': m})

