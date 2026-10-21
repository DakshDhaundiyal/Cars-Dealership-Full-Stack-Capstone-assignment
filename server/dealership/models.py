from django.conf import settings
from django.db import models


class Dealer(models.Model):
    name = models.CharField(max_length=160)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, db_index=True)
    address = models.CharField(max_length=240)
    phone = models.CharField(max_length=40)
    email = models.EmailField()
    website = models.URLField(blank=True)
    image_url = models.URLField(blank=True)

    # Fields used by the original dealership/reviews microservice contract.
    short_name = models.CharField(max_length=100, blank=True)
    full_name = models.CharField(max_length=160, blank=True)
    zip = models.CharField(max_length=12, default="00000")
    lat = models.FloatField(default=0.0)
    long = models.FloatField(default=0.0)

    class Meta:
        ordering = ["state", "city", "name"]

    def __str__(self):
        return f"{self.name} — {self.city}, {self.state}"

    def as_dict(self):
        return {
            "id": self.pk,
            "name": self.name,
            "short_name": self.short_name or self.name,
            "full_name": self.full_name or self.name,
            "city": self.city,
            "state": self.state,
            "address": self.address,
            "zip": self.zip,
            "zip_code": self.zip,
            "lat": self.lat,
            "latitude": self.lat,
            "long": self.long,
            "longitude": self.long,
            "phone": self.phone,
            "email": self.email,
            "website": self.website,
            "image_url": self.image_url,
        }


class DealerReview(models.Model):
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dealer_reviews")
    rating = models.PositiveSmallIntegerField(default=5)
    review = models.TextField(max_length=1500)
    sentiment = models.CharField(max_length=16, default="neutral")
    created_at = models.DateTimeField(auto_now_add=True)

    # Vehicle/purchase fields returned by the IBM capstone review API.
    purchase = models.BooleanField(default=True)
    purchase_date = models.DateField(null=True, blank=True)
    car_make = models.CharField(max_length=80, blank=True, default="")
    car_model = models.CharField(max_length=80, blank=True, default="")
    car_year = models.PositiveSmallIntegerField(default=2025)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.dealer.name} review by {self.user.username}"

    def as_dict(self):
        created = self.created_at.isoformat() if self.created_at else None
        return {
            "id": self.pk,
            "user_id": self.user_id,
            "name": self.user.get_full_name() or self.user.username,
            "dealership": self.dealer_id,
            "dealer_id": self.dealer_id,
            "username": self.user.username,
            "rating": self.rating,
            "review": self.review,
            "time": created,
            "created_at": created,
            "purchase": self.purchase,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else "",
            "car_make": self.car_make,
            "car_model": self.car_model,
            "car_year": self.car_year,
            "sentiment": self.sentiment,
        }


class CarMake(models.Model):
    make = models.CharField(max_length=80, db_index=True)
    model = models.CharField(max_length=80)
    year = models.PositiveSmallIntegerField(default=2025)

    class Meta:
        ordering = ["make", "model", "year"]
        unique_together = [("make", "model", "year")]

    def __str__(self):
        return f"{self.make} {self.model}"

    def as_dict(self):
        return {"id": self.pk, "make": self.make, "model": self.model, "year": self.year}
