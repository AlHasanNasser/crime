import json
from django.core.management.base import BaseCommand
from api.models import CrimeData
from django.db import transaction

class Command(BaseCommand):
    help = "Load crime data from a JSON file into the database"

    def handle(self, *args, **kwargs):
        file_path = 'api/management/data/locations_data.json'  # Path to your data file

        with open(file_path, 'r') as file:
            data = json.load(file)  # Load the JSON file

        crime_data_objects = []

        for record in data:
            crime = CrimeData(
                community_area=record['Community Area'],
                date=record['Date'],
                primary_type=record['Primary Type'],
                year=record['Year'],
                crime_count=record['Crime Count'],
                total_crimes_per_type=record['Total Crimes Per Type'],
                crime_rate=record['Crime Rate'],
                latitude=record['Coordinates']['latitude'],
                longitude=record['Coordinates']['longitude']
            )
            crime_data_objects.append(crime)

            # Insert data in batches of 10,000 to avoid memory issues
            if len(crime_data_objects) % 10000 == 0:
                CrimeData.objects.bulk_create(crime_data_objects)
                crime_data_objects = []  # Clear the list for the next batch

        # Insert any remaining records
        if crime_data_objects:
            CrimeData.objects.bulk_create(crime_data_objects)

        self.stdout.write(self.style.SUCCESS('Data successfully loaded into the database.'))