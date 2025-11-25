from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

# Create your models here.

class Region(models.Model):
    name = models.CharField(unique=True, max_length=100)
    color = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(unique=True, max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    emoji = models.CharField(unique=False, max_length=2, null=True, blank=False)

    def all_matches(self):
        """Returns all matches where this team participates"""
        return Match.objects.filter(
            models.Q(home_team=self) | models.Q(away_team=self)
        ).distinct().order_by('start_time')

    def clean(self):
        if self.emoji:
            if len(self.emoji) > 2:
                raise ValidationError("Emoji field should contain only one emoji")

    class Meta:
        ordering = ['region', 'name']

    @property
    def display_name(self):
        if self.emoji:
            return self.emoji + ' ' + self.name
        return self.name
    
    def __str__(self):
        return self.name

class Room(models.Model):
    name = models.CharField(unique=True, max_length=100)
    map = models.ImageField(upload_to='images/', null=True, blank=True)

    def all_matches(self):
        """Returns all matches where this team participates"""
        return Match.objects.filter(
            models.Q(room=self)
        ).distinct().order_by('start_time')

    def __str__(self):
        return self.name

class TournamentRound(models.Model):
    name = models.CharField(unique=True, max_length=100, null=False, blank=False)

    def __str__(self):
        return self.name

class Match(models.Model):
    # Basic match info
    match_number = models.IntegerField(unique=True, validators=[MinValueValidator(1)])
    start_time = models.DateTimeField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    tournament_round = models.ForeignKey(TournamentRound, on_delete=models.CASCADE, null=True, blank=True)

    # Info about how each team gets to this match
    home_source_match = models.ForeignKey('self', null=True, blank=True, related_name='home_for_match', on_delete=models.SET_NULL)
    home_source_take_winner = models.BooleanField(null=True, blank=True)
    away_source_match = models.ForeignKey('self', null=True, blank=True, related_name='away_for_match', on_delete=models.SET_NULL)
    away_source_take_winner = models.BooleanField(null=True, blank=True)

    # Set teams for starting matches, or propagated teams
    home_team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.SET_NULL, related_name='home_matches')
    away_team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.SET_NULL, related_name='away_matches')

    # Match result information
    is_complete = models.BooleanField(default=False)
    home_score = models.IntegerField(blank=True, null=True)
    away_score = models.IntegerField(blank=True, null=True)

    def clean(self):
        # what sorts of things are invalid?
        if self.home_team == self.away_team and self.home_team is not None:
            raise ValidationError("Cannot set home and away teams to same team")
        if (self.home_source_match == self.away_source_match) and (self.home_source_take_winner == self.away_source_take_winner):
            raise ValidationError("Cannot set home and away slots to be filled from the same result")
        if (self.is_complete and (self.home_score==None or self.away_score==None)):
            raise ValidationError("Home and away scores must be non-Null to mark a match complete")
        if (self.home_source_match.match_number >= self.match_number or self.away_source_match.match_number >= self.match_number):
            raise ValidationError("Source matches must have a lower match number than this match.")
        if (self.home_source_match is not None and self.home_source_take_winner is None) or (self.away_source_match is not None and self.away_source_take_winner is None):
            raise ValidationError("If a source match is set, you must choose whether to take the winner or loser")


    def winner(self):
        """Get the winning team of the match, if there is one"""
        if not self.is_complete:
            return None
        if self.home_score > self.away_score:
            return self.home_team
        elif self.away_score > self.home_score:
            return self.away_team
        else:
            return None

    def is_won_by(self, team: Team):
        """Returns true if the given team won the match"""
        if not isinstance(team, Team):
            return False
        return self.winner() == team

    @property
    def is_won_by_home_team(self):
        return self.is_won_by(self.home_team)

    @property
    def is_won_by_away_team(self):
        return self.is_won_by(self.away_team)

    @property
    def winner_destination(self):
        # First, look for matches where this winner goes to home slot
        home_destination = Match.objects.filter(
                home_source_match=self,
                home_source_take_winner=True
                ).first()
        if home_destination:
            return home_destination
        
        # Then, if not found, look for the same thing but with away
        away_destination = Match.objects.filter(
                away_source_match=self,
                away_source_take_winner=True
                ).first()
        if away_destination:
            return away_destination
    
    @property
    def loser_destination(self):
        # First, look for matches where this loser goes to home slot
        home_destination = Match.objects.filter(
                home_source_match=self,
                home_source_take_winner=False
                ).first()
        if home_destination:
            return home_destination
        
        # Then, if not found, look for the same thing but with away
        away_destination = Match.objects.filter(
                away_source_match=self,
                away_source_take_winner=False
                ).first()
        if away_destination:
            return away_destination
        pass

    @property
    def home_team_name(self):
        if self.home_team:
            return self.home_team
        if self.home_source_match:
            return 'TBD'
        return None

    @property
    def away_team_name(self):
        if self.away_team:
            return self.away_team
        if self.away_source_match:
            return 'TBD'
        return None

    class Meta:
        verbose_name_plural = "matches"

    def __str__(self):
        return str(f"{self.match_number}: {self.home_team_name} vs. {self.away_team_name}")
