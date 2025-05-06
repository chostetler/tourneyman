from django.shortcuts import render
from .models import Region, Team, Room, Matchup, MatchupSource

# Create your views here.
def home(request):
    return render(request, 'home.html')

def team_detail(request, team_id):
    try:
        t = Team.objects.get(pk=team_id)
        m = t.all_matchups() 
        
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



