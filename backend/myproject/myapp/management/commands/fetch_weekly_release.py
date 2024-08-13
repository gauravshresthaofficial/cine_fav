from django.core.management.base import BaseCommand
from scripts import fetch_weekly_release  # Import from scripts package

class Command(BaseCommand):
    help = 'Fetch weekly movie releases and save to MongoDB'

    def handle(self, *args, **kwargs):
        fetch_weekly_release.main()  # Call the main function in your script
        self.stdout.write(self.style.SUCCESS('Successfully fetched weekly releases'))
