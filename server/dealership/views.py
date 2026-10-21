import json
from datetime import date

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import CarMake, Dealer, DealerReview
from .sentiment import analyze_sentiment


def payload(request):
    try:
        if "application/json" in (request.content_type or ""):
            return json.loads(request.body.decode("utf-8") or "{}")
        return request.POST
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def home(request):
    state = request.GET.get("state", "").strip()
    dealers = Dealer.objects.all()
    if state:
        dealers = dealers.filter(state__iexact=state)
    states = Dealer.objects.order_by("state").values_list("state", flat=True).distinct()
    return render(request, "dealership/home.html", {"dealers": dealers, "states": states, "selected_state": state})


def dealer_detail(request, dealer_id):
    dealer = get_object_or_404(Dealer, pk=dealer_id)
    return render(
        request,
        "dealership/dealer_detail.html",
        {"dealer": dealer, "reviews": dealer.reviews.select_related("user")},
    )


def login_page(request):
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "dealership/login.html")


def review_page(request, dealer_id):
    dealer = get_object_or_404(Dealer, pk=dealer_id)
    if not request.user.is_authenticated:
        return redirect(f"/login/?next=/dealer/{dealer.pk}/review/")
    car_makes = sorted(CarMake.objects.values_list("make", flat=True).distinct())
    car_models = CarMake.objects.all()
    return render(
        request,
        "dealership/review_form.html",
        {"dealer": dealer, "car_makes": car_makes, "car_models": car_models},
    )


@require_GET
def list_dealers(request):
    dealers = Dealer.objects.all()
    state = request.GET.get("state") or request.GET.get("State")
    if state:
        dealers = dealers.filter(state__iexact=state.strip())
    return JsonResponse({"dealers": [dealer.as_dict() for dealer in dealers], "count": dealers.count()})


@require_GET
def get_dealer(request, dealer_id):
    dealer = get_object_or_404(Dealer, pk=dealer_id)
    return JsonResponse({"dealer": dealer.as_dict()})


@require_GET
def get_reviews(request, dealer_id):
    dealer = get_object_or_404(Dealer, pk=dealer_id)
    reviews = [review.as_dict() for review in dealer.reviews.select_related("user")]
    return JsonResponse(
        {"dealer_id": dealer.pk, "dealer": dealer.name, "reviews": reviews, "count": len(reviews)}
    )


# Compatibility endpoints used by the IBM Full Stack Developer Capstone labs.
# These mirror the JSON contract of the original Express/MongoDB service.
@require_GET
def fetch_dealers(request, state=None):
    state = state or request.GET.get("state")
    dealers = Dealer.objects.all()
    if state and state.casefold() not in {"all", "show all"}:
        dealers = dealers.filter(state__iexact=state.strip())
    return JsonResponse([dealer.as_dict() for dealer in dealers], safe=False)


@require_GET
def fetch_dealer(request, dealer_id):
    dealer = get_object_or_404(Dealer, pk=dealer_id)
    return JsonResponse([dealer.as_dict()], safe=False)


@require_GET
def fetch_reviews(request, dealer_id):
    dealer = get_object_or_404(Dealer, pk=dealer_id)
    reviews = [review.as_dict() for review in dealer.reviews.select_related("user")]
    return JsonResponse(reviews, safe=False)


@require_GET
def get_cars(request):
    rows = list(CarMake.objects.all())
    groups = {}
    sedan_names = {"A4", "3 Series", "Accord", "Altima", "Camry", "C-Class", "Jetta", "Model 3"}

    for row in rows:
        if row.make not in groups:
            make_id = len(groups) + 1
            groups[row.make] = {
                "id": make_id,
                "name": row.make,
                "description": f"{row.make} vehicles available in the dealership network.",
                "models": [],
            }
        groups[row.make]["models"].append(
            {
                "id": row.pk,
                "name": row.model,
                "type": "Sedan" if row.model in sedan_names else "SUV",
                "year": row.year,
                "dealer_id": 1,
            }
        )

    return JsonResponse({"CarMakes": list(groups.values()), "count": len(rows)})


@csrf_exempt
@require_POST
def register_user(request):
    data = payload(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    first = str(data.get("first_name", "")).strip()
    last = str(data.get("last_name", "")).strip()
    email = str(data.get("email", "")).strip()
    if not all([username, password, first, last, email]):
        return JsonResponse({"error": "All five fields are required."}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists."}, status=409)
    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email already exists."}, status=409)
    user = User.objects.create_user(
        username=username, password=password, first_name=first, last_name=last, email=email
    )
    return JsonResponse({"message": "Registration successful.", "username": user.username}, status=201)


@csrf_exempt
@require_POST
def login_user(request):
    data = payload(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    user = authenticate(
        request,
        username=str(data.get("username", "")).strip(),
        password=str(data.get("password", "")),
    )
    if user is None:
        return JsonResponse({"error": "Invalid username or password."}, status=401)
    login(request, user)
    return JsonResponse({"message": "Login successful.", "username": user.username})


@csrf_exempt
@require_POST
def logout_user(request):
    was_authenticated = request.user.is_authenticated
    logout(request)
    return JsonResponse({"message": "Logout successful.", "was_authenticated": was_authenticated})


@csrf_exempt
@require_POST
def create_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=401)
    data = payload(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    try:
        dealer = Dealer.objects.get(pk=int(data.get("dealer_id", 0)))
        rating = int(data.get("rating", 5))
        review_text = str(data.get("review", "")).strip()
    except (Dealer.DoesNotExist, TypeError, ValueError):
        return JsonResponse({"error": "A valid dealer_id is required."}, status=400)
    if not 1 <= rating <= 5 or not review_text:
        return JsonResponse({"error": "Review text and a rating from 1 to 5 are required."}, status=400)

    purchase_value = data.get("purchase", True)
    if isinstance(purchase_value, str):
        purchase_value = purchase_value.strip().lower() in {"true", "1", "yes", "on"}
    purchase_date_text = str(data.get("purchase_date", "")).strip()
    try:
        purchase_date = date.fromisoformat(purchase_date_text) if purchase_date_text else None
        car_year = int(data.get("car_year", 2025))
    except ValueError:
        return JsonResponse({"error": "Enter a valid purchase date and car year."}, status=400)

    review = DealerReview.objects.create(
        dealer=dealer,
        user=request.user,
        rating=rating,
        review=review_text,
        sentiment=analyze_sentiment(review_text)["sentiment"],
        purchase=bool(purchase_value),
        purchase_date=purchase_date,
        car_make=str(data.get("car_make", "Toyota")).strip(),
        car_model=str(data.get("car_model", "Camry")).strip(),
        car_year=car_year,
    )
    return JsonResponse({"message": "Review posted successfully.", "review": review.as_dict()}, status=201)


@require_GET
def list_car_makes(request):
    makes = [make.as_dict() for make in CarMake.objects.all()]
    return JsonResponse({"car_makes": makes, "count": len(makes)})


@csrf_exempt
@require_POST
def analyze_review(request):
    data = payload(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    text = str(data.get("review", data.get("text", ""))).strip()
    if not text:
        return JsonResponse({"error": "Review text is required."}, status=400)
    return JsonResponse({"review": text, **analyze_sentiment(text)})
