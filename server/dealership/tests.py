import json
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from .models import CarMake, Dealer, DealerReview


class DealershipApiTests(TestCase):
    def setUp(self):
        self.dealer = Dealer.objects.create(
            name="Test Dealer",
            short_name="Test Motors",
            full_name="Test Dealer LLC",
            city="Wichita",
            state="Kansas",
            address="1 Main St",
            zip="67202",
            lat=37.6872,
            long=-97.3301,
            phone="555-0100",
            email="test@example.com",
        )
        self.user = User.objects.create_user(username="testuser", password="TestPass123!")
        CarMake.objects.create(make="Toyota", model="Camry", year=2025)

    def test_dealers_endpoint_lists_dealers(self):
        response = self.client.get("/djangoapp/api/dealers/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

    def test_state_filter(self):
        response = self.client.get("/djangoapp/api/dealers/?state=Kansas")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

    def test_login_and_logout(self):
        response = self.client.post(
            "/djangoapp/api/login/",
            data=json.dumps({"username": "testuser", "password": "TestPass123!"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "testuser")
        logout = self.client.post("/djangoapp/api/logout/", data="{}", content_type="application/json")
        self.assertEqual(logout.status_code, 200)

    def test_sentiment_fantastic_services(self):
        response = self.client.post(
            "/djangoapp/api/analyze-review/",
            data=json.dumps({"review": "Fantastic services"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sentiment"], "positive")

    def test_review_requires_login(self):
        response = self.client.post(
            "/djangoapp/api/reviews/",
            data=json.dumps({"dealer_id": self.dealer.pk, "rating": 5, "review": "Excellent"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_capstone_dealer_endpoints_include_required_fields(self):
        all_dealers = self.client.get("/fetchDealers")
        self.assertEqual(all_dealers.status_code, 200)
        dealer = all_dealers.json()[0]
        for field in ("zip", "lat", "long", "short_name", "full_name"):
            self.assertIn(field, dealer)

        one_dealer = self.client.get(f"/fetchDealer/{self.dealer.pk}")
        self.assertEqual(one_dealer.status_code, 200)
        self.assertEqual(one_dealer.json()[0]["id"], self.dealer.pk)

        kansas = self.client.get("/fetchDealers/Kansas")
        self.assertEqual(kansas.status_code, 200)
        self.assertEqual(len(kansas.json()), 1)

    def test_capstone_review_endpoint_includes_purchase_and_vehicle_details(self):
        DealerReview.objects.create(
            dealer=self.dealer,
            user=self.user,
            review="Fantastic services",
            purchase=True,
            purchase_date=date(2025, 7, 11),
            car_make="Toyota",
            car_model="Camry",
            car_year=2025,
        )
        response = self.client.get(f"/fetchReviews/dealer/{self.dealer.pk}")
        self.assertEqual(response.status_code, 200)
        review = response.json()[0]
        for field in ("review", "purchase", "purchase_date", "car_make", "car_model", "car_year"):
            self.assertIn(field, review)

    def test_capstone_cars_endpoint_groups_makes_and_models(self):
        response = self.client.get("/djangoapp/get_cars")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["CarMakes"][0]["name"], "Toyota")
        self.assertEqual(response.json()["CarMakes"][0]["models"][0]["name"], "Camry")
