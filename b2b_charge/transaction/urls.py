from django.urls import include, path
from rest_framework import routers

from transaction import views

router = routers.DefaultRouter()
router.register("transaction", views.TransactionViewSet, basename="transaction")
router.register("creadit_request", views.CreditRequestViewSet, basename="creadit_request")

urlpatterns = [
    path("", include(router.urls)),
]
