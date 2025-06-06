from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# Create your models here.

class Region(models.Model):
    name = models.CharField(unique=True, max_length=100)
    color = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(unique=True, max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    rank = models.IntegerField(default=0)

    def all_matchups(self):
        """Returns all matchups where this team participates"""
        return Matchup.objects.filter(
            models.Q(home_team=self) | models.Q(away_team=self)
        ).distinct().order_by('start_time')



    
    class Meta:
        ordering = ['region', 'rank']
    
    def __str__(self):
        return self.name

class Room(models.Model):
    name = models.CharField(unique=True, max_length=100)
    map = models.ImageField(upload_to='images/', null=True, blank=True)

    def all_matchups(self):
        """Returns all matchups where this team participates"""
        return Matchup.objects.filter(
            models.Q(room=self)
        ).distinct().order_by('start_time')

    def __str__(self):
        return self.name

class TournamentRound(models.Model):
    name = models.CharField(unique=True, max_length=100, null=False, blank=False)
    

class Matchup(models.Model):
    match_number = models.IntegerField(unique=True, validators=[MinValueValidator(1)])
    start_time = models.DateTimeField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    tournament_round = models.ForeignKey(TournamentRound, on_delete=models.CASCADE, null=True, blank=True)

    # Info about how each team gets to this match
    home_from_match = models.ForeignKey('self', null=True, blank=True, related_name='home_for_matchup', on_delete=models.SET_NULL)
    home_from_result = models.CharField(max_length=10, choices=[('winner', 'Winner'), ('loser', 'Loser')], null=True, blank=True)
    away_from_match = models.ForeignKey('self', null=True, blank=True, related_name='away_for_matchup', on_delete=models.SET_NULL)
    away_from_result = models.CharField(max_length=10, choices=[('winner', 'Winner'), ('loser', 'Loser')], null=True, blank=True)

    home_team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.SET_NULL, related_name='home_matchups')
    away_team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.SET_NULL, related_name='away_matchups')

    is_complete = models.BooleanField(default=False)

    home_score = models.IntegerField(blank=True, null=True)
    away_score = models.IntegerField(blank=True, null=True)

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
        """Returns true if the given team won the matchup"""
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
        home_destination = Matchup.objects.filter(
                home_from_match=self,
                home_from_result='winner'
                ).first()
        if home_destination:
            return home_destination
        
        # Then, if not found, look for the same thing but with away
        away_destination = Matchup.objects.filter(
                away_from_match=self,
                away_from_result='winner'
                ).first()
        if away_destination:
            return away_destination
    
    @property
    def loser_destination(self):
        # First, look for matches where this loser goes to home slot
        home_destination = Matchup.objects.filter(
                home_from_match=self,
                home_from_result='loser'
                ).first()
        if home_destination:
            return home_destination
        
        # Then, if not found, look for the same thing but with away
        away_destination = Matchup.objects.filter(
                away_from_match=self,
                away_from_result='loser'
                ).first()
        if away_destination:
            return away_destination
        pass


    def __str__(self):
        return str(f"{self.match_number}: {self.home_team} vs. {self.away_team}")
