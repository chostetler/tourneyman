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
    
    def __str__(self):
        return self.name

class Room(models.Model):
    name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.name

class Matchup(models.Model):
    match_number = models.IntegerField(unique=True, validators=[MinValueValidator(100)])
    start_time = models.DateTimeField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.match_number)

class MatchupSource(models.Model):
    matchup = models.ForeignKey(Matchup, on_delete=models.CASCADE)



    
