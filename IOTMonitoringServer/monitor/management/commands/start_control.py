from django.core.management.base import BaseCommand
from monitor import monitor


class Command(BaseCommand):
    help = 'Starts actuators control'

    def handle(self, *args, **kwargs):
        monitor.analyze_data()
