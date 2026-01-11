from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import csv

class Command(BaseCommand):
    @transaction.atomic
    def generate_from_file(self, filepath):
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                print(row)

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default="", help='CSV file to create tournament from')

    def handle(self, *args, **options):
        if options['file']:
            self.generate_from_file(options['file'])
