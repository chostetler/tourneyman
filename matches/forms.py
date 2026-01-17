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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk: # If we have a new record...
            used_numbers = set(Match.objects.values_list('match_number', flat=True))
            next_num = 1
            while next_num in used_numbers:
                next_num += 1
            self.fields['match_number'].initial = next_num

class MatchResultForm(forms.ModelForm):
    outcome = forms.ChoiceField(
        widget=forms.RadioSelect,
        required=True,
        label="Match Outcome"
    )

    class Meta:
        model = Match
        fields = ['home_score', 'away_score', 'is_complete']
        widgets = {
            'home_score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_home_score'}),
            'away_score': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_away_score'}),
            'is_complete': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['outcome'].choices = [
                ('home_win', f'{self.instance.home_team.name} wins'),
                ('away_win', f'{self.instance.away_team.name} wins'),
                ('no_contest', 'No contest'),
                ('tie', 'Tie')
            ]
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.is_complete = True
        if commit:
            instance.save()
        return instance
