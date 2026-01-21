from django.shortcuts import render, redirect, get_object_or_404
from .models import Region, Team, Room, Match
from .forms import TeamForm, RoomForm, MatchForm, MatchResultForm, GenerateTimeslotsForm
from django.http import Http404
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login

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
    view_format = request.GET.get('format', 'timeslot')
    if view_format == 'bracket':
        m = Match.objects.all().order_by('tournament_round', 'timeslot', 'match_number')
    elif view_format == 'room':
        m = Match.objects.all().order_by('room', 'timeslot', 'match_number')
    else:
        m = Match.objects.all().order_by('timeslot', 'match_number')

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

def profile_view(request):
    return redirect('home')

def is_bracket_manager(user):
    return user.groups.filter(name='Bracket Managers').exists() or user.is_staff

@user_passes_test(is_bracket_manager)
def match_result(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    
    if request.method == 'POST':
        form = MatchResultForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = MatchResultForm(instance=match)
    
    return render(request, 'match_result_form.html', {'match': match})

def generate_timeslots_view(request):
    if request.method== 'POST':
        form = GenerateTimeslotsForm(request.POST)
        if form.is_valid():
            timeslots = form.save()
            messages.success(request, f'Successfully generated {len(timeslots)} timeslots')
            return redirect('matches_list')
    else:
        form = GenerateTimeslotsForm()

    return render(request, 'timeslot_generation_form.html', {'form': form })

# def login_view(request):
#     username = request.POST["username"]
#     password = request.POST["password"]
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         return reverse('home')
#     else:
#         # Give an invalid login
#         return reverse('login')

# Form views

class TeamCreateView( LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = 'team_form.html'
    success_message = "%(name)s was created successfully!"

    def test_func(self):
            return self.request.user.is_staff # Only staff can access this view

    def get_success_url(self):
        return reverse('team_create')

class RoomCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'room_form.html'
    success_message = "%(name)s was created successfully!"

    def test_func(self):
            return self.request.user.is_staff # Only staff can access this view

    def get_success_url(self):
        return reverse('room_create')

class MatchCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Match
    form_class = MatchForm
    template_name = 'match_form.html'
    success_message = "Match %(match_number)s was created successfully!"

    def test_func(self):
            return self.request.user.is_staff # Only staff can access this view

    def get_success_url(self):
        return reverse('match_create')

class MatchResultView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Match
    form_class = MatchResultForm
    template_name = "match_result_form.html"
    success_message = "Match saved!"

    def test_func(self):
            return self.request.user.is_staff # Only staff can access this view

    def get_success_url(self):
        return reverse('matches_list')
