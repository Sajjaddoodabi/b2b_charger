from django.urls import include, path
from rest_framework import routers

from user import views

router = routers.DefaultRouter()
router.register("users", views.UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
]
