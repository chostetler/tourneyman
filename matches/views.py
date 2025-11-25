from django.shortcuts import render
from .models import Region, Team, Room, Match
from django.http import Http404

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
        m = t.all_matches().order_by('match_number')
        
    except Team.DoesNotExist:
        raise Http404("Team does not exist")
    return render(request, 'team.html', {'team': t, 'matches': m})

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

def rooms_list(request):
    """View for a list of all Rooms"""
    r = Room.objects.all().order_by('name')
    return render(request, 'rooms.html', {'rooms': r})

def room_detail(request, room_id):
    """View for details about a specific Room"""
    try:
        r = Room.objects.get(pk=room_id)
        m = r.all_matches().order_by('match_number')
    except Region.DoesNotExist:
        raise Http404("Room does not exist")
    return render(request, 'room.html', {'room': r, 'matches': m})

def matches_list(request):
    m = Match.objects.all().order_by('match_number')
    incomplete = m.filter(is_complete=False)
    complete = m.filter(is_complete=True)
    return render(request, 'matches.html', {'complete_matches': complete, 'incomplete_matches': incomplete})

def match_detail(request, match_id):
    """View for details about a specific Match"""
    try:
        m = Match.objects.get(pk=match_id)
    except Match.DoesNotExist:
        raise Http404("Match does not exist")
    return render(request, 'match.html', {'match': m,})



def scorekeeper(request):
    """View for scorekeepers, allowing them to enter results for active games"""
    m = Match.objects.all().filter(is_complete=False).order_by('match_number')
    return render(request, 'scorekeeper.html', {'matches': m})

