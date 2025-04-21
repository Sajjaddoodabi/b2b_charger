from django.urls import include, path
from rest_framework import routers

from vendor import views

router = routers.DefaultRouter()
router.register("vendor", views.VendorViewSet, basename="vendor")

urlpatterns = [
    path("", include(router.urls)),
]
