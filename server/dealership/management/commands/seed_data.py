import os
from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from dealership.models import CarMake, Dealer, DealerReview


DEALERS = [
    {
        "name": "Prairie Motor Group", "city": "Wichita", "state": "Kansas",
        "address": "1200 E Central Ave, Wichita, KS", "phone": "+1-316-555-0101",
        "email": "wichita@prairiemotors.example", "zip": "67202",
        "lat": 37.6872, "long": -97.3301, "short_name": "Prairie Motors",
    },
    {
        "name": "Sunflower Auto House", "city": "Topeka", "state": "Kansas",
        "address": "2500 SW Topeka Blvd, Topeka, KS", "phone": "+1-785-555-0102",
        "email": "topeka@sunflowerauto.example", "zip": "66603",
        "lat": 39.0473, "long": -95.6752, "short_name": "Sunflower Auto",
    },
    {
        "name": "Crossroads Car Center", "city": "Overland Park", "state": "Kansas",
        "address": "8900 Metcalf Ave, Overland Park, KS", "phone": "+1-913-555-0103",
        "email": "sales@crossroadscars.example", "zip": "66204",
        "lat": 38.9822, "long": -94.6708, "short_name": "Crossroads Cars",
    },
    {
        "name": "Lone Star Automotive", "city": "Austin", "state": "Texas",
        "address": "700 Congress Ave, Austin, TX", "phone": "+1-512-555-0104",
        "email": "hello@lonestarauto.example", "zip": "78701",
        "lat": 30.2672, "long": -97.7431, "short_name": "Lone Star Auto",
    },
    {
        "name": "Golden Gate Motors", "city": "San Jose", "state": "California",
        "address": "1500 Story Rd, San Jose, CA", "phone": "+1-408-555-0105",
        "email": "team@goldengatemotors.example", "zip": "95116",
        "lat": 37.3524, "long": -121.8508, "short_name": "Golden Gate",
    },
    {
        "name": "Lakeview Auto Gallery", "city": "Chicago", "state": "Illinois",
        "address": "6400 N Lincoln Ave, Chicago, IL", "phone": "+1-773-555-0106",
        "email": "info@lakeviewauto.example", "zip": "60625",
        "lat": 41.9711, "long": -87.7030, "short_name": "Lakeview Auto",
    },
    {
        "name": "Empire State Cars", "city": "Albany", "state": "New York",
        "address": "90 Central Ave, Albany, NY", "phone": "+1-518-555-0107",
        "email": "sales@empirecars.example", "zip": "12207",
        "lat": 42.6526, "long": -73.7562, "short_name": "Empire Cars",
    },
    {
        "name": "Rocky Mountain Auto", "city": "Denver", "state": "Colorado",
        "address": "1800 W Colfax Ave, Denver, CO", "phone": "+1-303-555-0108",
        "email": "contact@rockymountainauto.example", "zip": "80204",
        "lat": 39.7392, "long": -104.9903, "short_name": "Rocky Mountain",
    },
]

PHOTO = "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=1200&q=80"
MAKES = [
    ("Audi", "A4"), ("Audi", "Q5"), ("BMW", "3 Series"), ("BMW", "X5"),
    ("Chevrolet", "Equinox"), ("Ford", "F-150"), ("Ford", "Mustang"),
    ("Honda", "Accord"), ("Honda", "CR-V"), ("Hyundai", "Tucson"),
    ("Kia", "Sportage"), ("Mercedes-Benz", "C-Class"), ("Nissan", "Altima"),
    ("Subaru", "Outback"), ("Tesla", "Model 3"), ("Toyota", "Camry"),
    ("Toyota", "RAV4"), ("Volkswagen", "Jetta"),
]


class Command(BaseCommand):
    help = "Load illustrative dealer data and an optional local demo account."

    def handle(self, *args, **kwargs):
        for dealer in DEALERS:
            defaults = {
                **dealer,
                "full_name": dealer["name"],
                "website": "https://example.com",
                "image_url": PHOTO,
            }
            Dealer.objects.update_or_create(name=dealer["name"], defaults=defaults)

        for make, model in MAKES:
            CarMake.objects.get_or_create(make=make, model=model, year=2025)

        user = None
        if os.environ.get("CREATE_DEMO_USER", "").lower() == "true":
            user, _created = User.objects.get_or_create(
                username="demo",
                defaults={
                    "email": "demo@example.com",
                    "first_name": "Demo",
                    "last_name": "User",
                },
            )
            user.set_password(os.environ["DEMO_USER_PASSWORD"])
            user.save()

        first_dealer = Dealer.objects.order_by("id").first()
        if user and first_dealer and not first_dealer.reviews.exists():
            DealerReview.objects.create(
                dealer=first_dealer,
                user=user,
                rating=5,
                review="Fantastic services and a friendly team.",
                sentiment="positive",
                purchase=True,
                purchase_date=date(2025, 7, 11),
                car_make="Toyota",
                car_model="Camry",
                car_year=2025,
            )

        user_status = "demo user available for this run" if user else "demo user disabled by default"
        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {Dealer.objects.count()} dealers, "
                f"{CarMake.objects.count()} car models; {user_status}."
            )
        )
