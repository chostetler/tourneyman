from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
import random
from datetime import timedelta
import faker

# Import your models
from matches.models import Team, Region, Room, Matchup

class Command(BaseCommand):
    help = 'Generates mock data for development'

    def add_arguments(self, parser):
        parser.add_argument('--regions', type=int, default=5, help='Number of regions to create')
        parser.add_argument('--teams', type=int, default=20, help='Number of teams to create')
        parser.add_argument('--rooms', type=int, default=3, help='Number of rooms to create')
        parser.add_argument('--matches', type=int, default=30, help='Number of matches to create')
        parser.add_argument('--clear', action='store_true', help='Clear existing data before generating new data')
    
    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()
        
        # Create fake data generator
        fake = faker.Faker()
        
        # Create regions
        regions = self.create_regions(options['regions'], fake)
        self.stdout.write(self.style.SUCCESS(f'Created {len(regions)} regions'))
        
        # Create teams
        teams = self.create_teams(options['teams'], regions, fake)
        self.stdout.write(self.style.SUCCESS(f'Created {len(teams)} teams'))
        
        # Create rooms
        rooms = self.create_rooms(options['rooms'], fake)
        self.stdout.write(self.style.SUCCESS(f'Created {len(rooms)} rooms'))
        
        # Create matches
        matches = self.create_matches(options['matches'], teams, rooms, fake)
        self.stdout.write(self.style.SUCCESS(f'Created {len(matches)} matches'))

    def clear_data(self):
        """Clear all data from the models"""
        self.stdout.write('Clearing existing data...')
        Matchup.objects.all().delete()
        Team.objects.all().delete()
        Region.objects.all().delete()
        Room.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All data cleared'))
        
    def create_regions(self, count, fake):
        """Create regions with random colors"""
        region_names = [fake.unique.state() for _ in range(count)]
        regions = []
        
        # Sample colors in hex format
        colors = [
            'navy', 'blue', 'orange', 'black', 'indigo',
            'brown', 'gray', 'red', 'blue', 'green'
        ]
        for i in range(count):
            color = random.choice(colors)
            region = Region.objects.create(
                name=region_names[i],
                color=color
            )
            regions.append(region)
        
        return regions
        
    def create_teams(self, count, regions, fake):
        """Create teams belonging to random regions"""
        team_names = [fake.unique.city() for _ in range(count)]
        teams = []
        
        for i in range(count):
            region = random.choice(regions)
            team = Team.objects.create(
                name=team_names[i],
                region=region
            )
            teams.append(team)
            
        return teams
        
    def create_rooms(self, count, fake):
        """Create rooms for matches"""
        rooms = []
        
        for i in range(count):
            room = Room.objects.create(
                name=f"Room {chr(65 + i)}",  # Room A, Room B, etc.
            )
            rooms.append(room)
            
        return rooms
        
    @transaction.atomic
    def create_matches(self, count, teams, rooms, fake):
        """Create matches between teams"""
        matches = []
        
        # Start time base (beginning of a tournament day)
        start_date = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        match_numbers = random.sample(range(100, 300), count)  # Unique match numbers
        
        for i, match_number in enumerate(match_numbers):
            # Calculate a match time
            # Distribute matches over a few days with realistic times
            day_offset = i // 10  # Every 10 matches move to next day
            time_slot = i % 10    # 10 matches per day
            
            match_time = start_date + timedelta(days=day_offset, minutes=time_slot*45)
            
            # Select two different teams
            available_teams = list(teams)
            home_team = random.choice(available_teams)
            available_teams.remove(home_team)
            away_team = random.choice(available_teams)
            
            # Select a room
            room = random.choice(rooms)
            
            # Create the match
            match = Matchup.objects.create(
                match_number=match_number,
                start_time=match_time,
                room=room,
                home_team=home_team,
                away_team=away_team
            )
            
            # Randomly add scores to some matches (past matches)
            if random.random() < 0.7:  # 70% of matches have scores
                match.home_score = 5*random.randint(0, 30)
                match.away_score = 5*random.randint(0, 30)
                match.is_complete = True
                match.save()
                
            matches.append(match)
            
        return matches
