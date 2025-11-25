from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand)
    @transaction.atomic
    def create_bracket_from_file(self, filepath):
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                print(row)
