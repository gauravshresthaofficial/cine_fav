from django.core.management.base import BaseCommand
from scripts import post_to_facebook  # Import from scripts package

class Command(BaseCommand):
    help = 'Post to Facebook'

    def handle(self, *args, **kwargs):
        post_to_facebook.main()  # Call the main function in your script
        self.stdout.write(self.style.SUCCESS('Successfully posted to Facebook'))
