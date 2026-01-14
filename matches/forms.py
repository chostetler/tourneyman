from django import forms
from .models import Region, Team, Room, Timeslot, Match

class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['name', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}), # Optional: color picker
        }

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'region', 'emoji']

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'map']

class TimeslotForm(forms.ModelForm):
    class Meta:
        model = Timeslot
        fields = ['start_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = [
            'match_number',
            'timeslot',
            'room',
            'tournament_round',
            # Match source info
            'home_team', 'home_source_match', 'home_source_take_winner',
            'away_team', 'away_source_match', 'away_source_take_winner'
        ]

class MatchResultForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['home_score', 'away_score', 'is_complete']
        widgets = {
            'home_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'away_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_complete': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }