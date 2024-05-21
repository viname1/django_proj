import json
from django.core.management.base import BaseCommand, CommandError
from hrbase.models import MiniTest

class Command(BaseCommand):
    help = 'Load tests from json file'
    
    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str)

    def handle(self, *args, **options):
        with open(options['json_file'], encoding='utf-8') as f:
            data = json.load(f)
        minitests = MiniTest.create_from_json_data(data)
        for minitest in minitests:
            self.stdout.write(f'Created minitest {minitest.title}')
