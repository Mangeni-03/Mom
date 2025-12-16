from django.core.management.base import BaseCommand
from Mom.models import Vaccination

class Command(BaseCommand):
    help = "Seed vaccination data"

    def handle(self, *args, **kwargs):
        vaccinations = [
            {
                "name": "BCG",
                "description": "Protects against tuberculosis",
                "recommended_age_days": 0,
                "dose_order": 1
            },
            {
                "name": "OPV 0",
                "description": "Oral Polio Vaccine given at birth",
                "recommended_age_days": 0,
                "dose_order": 1
            },
            {
                "name": "OPV 1",
                "description": "First dose of oral polio vaccine",
                "recommended_age_days": 42,
                "dose_order": 2
            },
            {
                "name": "Pentavalent 1",
                "description": "Protects against DPT, Hepatitis B and Hib",
                "recommended_age_days": 42,
                "dose_order": 1
            },
            {
                "name": "OPV 2",
                "description": "Second dose of oral polio vaccine",
                "recommended_age_days": 70,
                "dose_order": 3
            },
            {
                "name": "Pentavalent 2",
                "description": "Second dose of pentavalent vaccine",
                "recommended_age_days": 70,
                "dose_order": 2
            },
            {
                "name": "OPV 3",
                "description": "Third dose of oral polio vaccine",
                "recommended_age_days": 98,
                "dose_order": 4
            },
            {
                "name": "Pentavalent 3",
                "description": "Third dose of pentavalent vaccine",
                "recommended_age_days": 98,
                "dose_order": 3
            },
            {
                "name": "IPV",
                "description": "Inactivated Polio Vaccine",
                "recommended_age_days": 98,
                "dose_order": 1
            },
            {
                "name": "Measles Rubella 1",
                "description": "Protects against measles and rubella",
                "recommended_age_days": 270,
                "dose_order": 1
            },
            {
                "name": "Measles Rubella 2",
                "description": "Second dose of measles rubella vaccine",
                "recommended_age_days": 540,
                "dose_order": 2
            }
        ]

        for v in vaccinations:
            Vaccination.objects.get_or_create(
                name=v["name"],
                defaults={
                    "description": v["description"],
                    "recommended_age_days": v["recommended_age_days"],
                    "dose_order": v["dose_order"],
                }
            )

        self.stdout.write(self.style.SUCCESS("Vaccinations seeded successfully"))
