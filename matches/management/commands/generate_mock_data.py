from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
import random
from datetime import timedelta
import faker
import math
import csv

# Import your models
from matches.models import Team, Region, Room, Match

class Command(BaseCommand):
    help = 'Generates mock data for tournament development'

    def add_arguments(self, parser):
        parser.add_argument('--regions', type=int, default=5, help='Number of regions to create')
        parser.add_argument('--teams', type=int, default=16, help='Number of teams to create (preferably a power of 2)')
        parser.add_argument('--rooms', type=int, default=3, help='Number of rooms to create')
        parser.add_argument('--file', type=str, default="", help='CSV file to create tournament from')
        parser.add_argument('--clear', action='store_true', help='Clear existing data before generating new data')
        parser.add_argument('--tournament', action='store_true', help='Create a tournament bracket structure')
    
    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()
        
        # Create fake data generator
        fake = faker.Faker()
        
        if options['file'] != "":
            matches = self.create_bracket_from_file(options['file'])
            if (matches > 0):
                self.stdout.write(self.style.SUCCESS(f'Created tournament bracket with {len(matches)} matches'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Created tournament bracket with {len(matches)} matches'))
            return

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
        if options['tournament']:
            matches = self.create_tournament_bracket(teams, rooms, fake)
            self.stdout.write(self.style.SUCCESS(f'Created tournament bracket with {len(matches)} matches'))
        else:
            matches = self.create_matches(options['teams'] * 2, teams, rooms, fake)
            self.stdout.write(self.style.SUCCESS(f'Created {len(matches)} individual matches'))

    def clear_data(self):
        """Clear all data from the models"""
        self.stdout.write('Clearing existing data...')
        Match.objects.all().delete()
        Team.objects.all().delete()
        Region.objects.all().delete()
        Room.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All data cleared'))
        
    def create_regions(self, count, fake):
        """Create regions with random colors"""
        region_names = [fake.unique.state() for _ in range(count)]
        regions = []
        
        # Sample colors
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
        team_emojis = [fake.unique.emoji() for _ in range(count)]
        teams = []
        
        for i in range(count):
            region = random.choice(regions)
            team = Team.objects.create(
                name=team_names[i],
                emoji=team_emojis[i],
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
        """Create individual matches between teams"""
        matches = []
        
        # Start time base (beginning of a tournament day)
        start_date = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        match_numbers = random.sample(range(1, 300), count)  # Unique match numbers
        
        for i, match_number in enumerate(match_numbers):
            # Calculate a match time
            day_offset = i // 10  # Every 10 matches move to next day
            time_slot = i % 10    # 10 matches per day
            
            match_time = start_date + timedelta(days=day_offset, minutes=time_slot*30)
            
            # Select two different teams
            available_teams = list(teams)
            home_team = random.choice(available_teams)
            available_teams.remove(home_team)
            away_team = random.choice(available_teams)
            
            # Select a room
            room = random.choice(rooms)
            
            # Create the match
            match = Match.objects.create(
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

    @transaction.atomic
    def create_tournament_bracket(self, teams, rooms, fake):
        """Create a tournament bracket structure with dependent matches"""
        all_matches = []
        
        # Start time base for the tournament
        start_date = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Use teams in powers of 2 for a proper bracket
        team_count = len(teams)
        team_power = 2 ** math.floor(math.log2(team_count))
        if team_power < team_count:
            self.stdout.write(f"Using {team_power} teams for a clean bracket (original count: {team_count})")
            teams = teams[:team_power]
            team_count = team_power
        
        # Calculate tournament structure
        rounds_needed = int(math.log2(team_count))
        matches_per_round = []
        for r in range(rounds_needed):
            matches_per_round.append(team_count // (2**(r+1)))
        
        self.stdout.write(f"Creating a tournament with {rounds_needed} rounds")
        self.stdout.write(f"Teams per round: {team_count} -> {matches_per_round}")
        
        # Create first round matches with teams assigned
        round1_matches = []
        for i in range(matches_per_round[0]):
            match_time = start_date + timedelta(minutes=i*45)
            room = rooms[i % len(rooms)]
            
            # Get the teams for this match
            home_team = teams[i*2]
            away_team = teams[i*2 + 1]
            
            match = Match.objects.create(
                match_number=i+1,  # Start with match 1, 2, 3, etc.
                start_time=match_time,
                room=room,
                home_team=home_team,
                away_team=away_team
            )
            round1_matches.append(match)
            all_matches.append(match)
        
        # Create subsequent rounds with dependencies
        last_round_matches = round1_matches
        match_number = len(round1_matches) + 1
        
        for round_idx in range(1, rounds_needed):
            current_round_matches = []
            match_count = matches_per_round[round_idx]
            day_offset = round_idx  # Each round happens on a new day
            
            for i in range(match_count):
                match_time = start_date + timedelta(days=day_offset, minutes=i*45)
                room = rooms[i % len(rooms)]
                
                # Previous round matches that feed into this one
                feed_idx_1 = i*2
                feed_idx_2 = i*2 + 1
                
                if feed_idx_1 < len(last_round_matches) and feed_idx_2 < len(last_round_matches):
                    match = Match.objects.create(
                        match_number=match_number,
                        start_time=match_time,
                        room=room,
                        home_from_match=last_round_matches[feed_idx_1],
                        home_from_result='winner',
                        away_from_match=last_round_matches[feed_idx_2],
                        away_from_result='winner'
                    )
                    current_round_matches.append(match)
                    all_matches.append(match)
                    match_number += 1
            
            # Update for next round
            last_round_matches = current_round_matches
        
        # Add some consolation matches using losers
        for i in range(min(4, len(round1_matches))):
            source_match = round1_matches[i]
            
            consolation_match = Match.objects.create(
                match_number=900 + i,
                start_time=start_date + timedelta(days=1, hours=i),
                room=random.choice(rooms),
                home_from_match=source_match,
                home_from_result='loser'
            )
            all_matches.append(consolation_match)
        
        # Complete some first round matches to trigger advancement
        for i, match in enumerate(round1_matches):
            if i < len(round1_matches) // 2:  # Complete half of the first round
                if random.random() > 0.5:
                    # Home team wins
                    match.home_score = random.randint(50, 100)
                    match.away_score = random.randint(0, 49)
                else:
                    # Away team wins
                    match.home_score = random.randint(0, 49)
                    match.away_score = random.randint(50, 100)
                
                match.is_complete = True
                match.save()

                # Manually update next match since we can't rely on the model method yet
                # self.update_next_matches(match)
        
        return all_matches

    @transaction.atomic
    def create_bracket_from_file(self, filepath):
        matches = []
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                # For each row - first, get the match ID. Just assume unique
                match_id = row['match']

                # Then, find the two teams
                away = row['away']
                match = Match.objects.create(
                    match_number=match_id,
                    home_team=home,
                    away_team=away,
                )
                matches.append(match)
                
                print(row)
        return matches

    
    def update_next_matches(self, match):
        """Manually update the next matches based on match result"""
        if not match.is_complete:
            return
        
        winning_team = None
        losing_team = None
        
        # Determine winner and loser
        if match.home_score > match.away_score:
            winning_team = match.home_team
            losing_team = match.away_team
        elif match.away_score > match.home_score:
            winning_team = match.away_team
            losing_team = match.home_team
        
        if not winning_team:
            return
        
        # Find matches where this match is the source
        winner_destinations = Match.objects.filter(
            (models.Q(home_from_match=match) & models.Q(home_from_result='winner')) |
            (models.Q(away_from_match=match) & models.Q(away_from_result='winner'))
        )
        
        loser_destinations = Match.objects.filter(
            (models.Q(home_from_match=match) & models.Q(home_from_result='loser')) |
            (models.Q(away_from_match=match) & models.Q(away_from_result='loser'))
        )
        
        # Update winner destinations
        for dest in winner_destinations:
            if dest.home_from_match == match and dest.home_from_result == 'winner':
                dest.home_team = winning_team
            
            if dest.away_from_match == match and dest.away_from_result == 'winner':
                dest.away_team = winning_team
            
            dest.save()
        
        # Update loser destinations
        for dest in loser_destinations:
            if dest.home_from_match == match and dest.home_from_result == 'loser':
                dest.home_team = losing_team
            
            if dest.away_from_match == match and dest.away_from_result == 'loser':
                dest.away_team = losing_team
            
            dest.save()
