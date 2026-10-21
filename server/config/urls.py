from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from dealership import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("dealership.urls")),
]
