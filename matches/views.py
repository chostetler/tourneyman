from django.shortcuts import render
from .models import Region, Team, Room, Matchup

# Create your views here.
def home(request):
    return render(request, 'home.html')

def teams_list(request):
    """View for a list of all Teams"""
    t = Team.objects.all().order_by('name')
    return render(request, 'teams.html', {'teams': t})

def team_detail(request, team_id):
    """View for details about a specific Team"""
    try:
        t = Team.objects.get(pk=team_id)
        m = t.all_matchups().order_by('match_number')
        
    except Team.DoesNotExist:
        raise Http404("Team does not exist")
    return render(request, 'team.html', {'team': t, 'matchups': m})

def regions_list(request):
    """View for a list of all Regions"""
    r = Region.objects.all().order_by('name')
    return render(request, 'regions.html', {'regions': r})

def region_detail(request, region_id):
    """View for details about a specific Region"""
    try:
        r = Region.objects.get(pk=region_id)
        t = r.team_set.all()
    except Region.DoesNotExist:
        raise Http404("Region does not exist")
    return render(request, 'region.html', {'region': r, 'teams': t})

def room_detail(request, room_id):
    """View for details about a specific Room"""
    try:
        r = Room.objects.get(pk=room_id)
        m = r.all_matchups().order_by('match_number')
    except Region.DoesNotExist:
        raise Http404("Room does not exist")
    return render(request, 'room.html', {'room': r, 'matchups': m})


def matchup_detail(request, matchup_id):
    """View for details about a specific Matchup"""
    try:
        m = Matchup.objects.get(pk=matchup_id)
    except Matchup.DoesNotExist:
        raise Http404("Matchup does not exist")
    return render(request, 'matchup.html', {'matchup': m,})



def scorekeeper(request):
    """View for scorekeepers, allowing them to enter results for active games"""
    m = Matchup.objects.all().filter(is_complete=False).order_by('match_number')
    return render(request, 'scorekeeper.html', {'matchups': m})

