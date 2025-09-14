from django.core.management.base import BaseCommand
from core.models import VolunteerProfile

class Command(BaseCommand):
    help = 'Reset all volunteer interests to empty arrays'

    def handle(self, *args, **options):
        VolunteerProfile.objects.all().update(interests=[])
        self.stdout.write(self.style.SUCCESS('Successfully reset interests'))