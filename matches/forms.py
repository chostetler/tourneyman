from django import forms
from .models import Region, Team, Room, Timeslot, Match
from datetime import datetime, timedelta
from django.utils import timezone

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
    slot_selection = forms.ChoiceField(choices=[])
    class Meta:
        model = Match
        fields = [
            'match_number',
            # 'timeslot',
            #  'room',
            'slot_selection',
            'tournament_round',
            # Match source info
            'home_team', 'home_source_match', 'home_source_take_winner',
            'away_team', 'away_source_match', 'away_source_take_winner'
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        taken = Match.objects.values_list('timeslot_id', 'room_id')
        available_choices = []
        for ts in Timeslot.objects.all():
            for rm in Room.objects.all():
                if (ts.id, rm.id) not in taken:
                    available_choices.append(
                        (f"{ts.id}-{rm.id}", f"{ts} (in {rm})")
                    )
        self.fields['slot_selection'].choices=available_choices

        if not self.instance.pk: # If we have a new record...
            used_numbers = set(Match.objects.values_list('match_number', flat=True))
            next_num = 1
            while next_num in used_numbers:
                next_num += 1
            self.fields['match_number'].initial = next_num
    
    def save(self, commit=True):
        ts_id, rm_id = self.cleaned_data['slot_selection'].split('-')
        self.instance.timeslot_id = ts_id
        self.instance.room_id = rm_id
        return super().save(commit)

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

class GenerateTimeslotsForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        label="Start date"
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        required=True,
        label="Start time"
    )
    interval = forms.IntegerField(
        widget=forms.NumberInput,
        required=True,
        label="Interval (minutes)"
    )
    count = forms.IntegerField(
        widget=forms.NumberInput,
        required=True,
        label="# of time slots to generate"
    )

    def save(self):
        data = self.cleaned_data
        start_dt = datetime.combine(data['start_date'], data['start_time'])
        interval = data['interval']
        count = data['count']

        # 1. Generate aware datetimes
        target_datetimes = []
        for i in range(count):
            dt = datetime.combine(data['start_date'], data['start_time']) + timedelta(minutes=i * interval)
            # Make the datetime aware of your project's timezone
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt)
            target_datetimes.append(dt)

        # 2. Find existing (Django handles the DB comparison correctly for aware objects)
        existing = set(
            Timeslot.objects.filter(start_time__in=target_datetimes)
            .values_list('start_time', flat=True)
        )

        # 3. Filter and Bulk Create
        new_slots = [
            Timeslot(start_time=dt) 
            for dt in target_datetimes 
            if dt not in existing
        ]
        
        return Timeslot.objects.bulk_create(new_slots)

