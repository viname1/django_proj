import json
from django.core.management.base import BaseCommand, CommandError
from hrbase.models import SpecialityTag

class Command(BaseCommand):
    help = 'Load tags from json file'

    def handle(self, *args, **options):
        with open('speciality_tags.json', encoding='utf-8') as f:
            data = json.load(f)
        for tag in data['tags']:
            speciality_tag, created = SpecialityTag.objects.get_or_create(
                codename=tag['codename'],
                name=tag['name'],
                parent=SpecialityTag.objects.get(
                    codename=tag['parent']
                ) if 'parent' in tag and tag['parent'] else None,
            )
            if created:
                self.stdout.write(f'Created tag {speciality_tag.name} with codename {speciality_tag.codename}')
