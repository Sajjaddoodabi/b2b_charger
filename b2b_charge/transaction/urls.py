from django.urls import include, path
from rest_framework import routers

from transaction import views

router = routers.DefaultRouter()
router.register("transaction", views.TransactionViewSet, basename="transaction")

urlpatterns = [
    path("", include(router.urls)),
]
