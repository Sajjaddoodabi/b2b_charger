from django.urls import include, path
from rest_framework import routers

from phone_number import views

router = routers.DefaultRouter()
router.register("phone_number", views.PhoneNumberViewSet, basename="phone_number")

urlpatterns = [
    path("", include(router.urls)),
]
