import logging

from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from user.filters import UserFilter
from user.models import User
from user.permissions import IsAdmin, is_admin
from user.serializers import (
    UserInfoSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from utils.views import BaseModelViewSet

logger = logging.getLogger(__name__)


class UserViewSet(BaseModelViewSet):
    """
    View to list all users in the system
    """

    filterset_class = UserFilter
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    search_fields = [
        "^username",
        "phone_number",
        "^first_name",
        "^last_name",
        "^employee_id",
    ]

    def get_queryset(self):
        queryset = (
            User.objects.filter(is_active=True)
            .prefetch_related("groups")
            .order_by("full_name")
        )

        return queryset

    @swagger_auto_schema(
        method="get",
        operation_description="Get the details of the currently logged-in user.",
        responses={200: UserSerializer()},
    )
    @action(detail=False, methods=["GET"])
    def current_user(self, request):
        serializer = UserSerializer(request.user, context={"request": request}).data
        return Response(serializer)

    @swagger_auto_schema(
        method="get",
        operation_description="Log out the current user. If logged in via SSO, redirects to the logout URL.",
        responses={
            200: openapi.Response("Successfully logged out."),
            302: "Redirects to the SSO logout URL if logged in via SSO.",
        },
    )
    @action(detail=False, methods=["GET"])
    def logout(self, request):
        try:
            token = Token.objects.filter(user=request.user).first()
            if token:
                token.delete()
        except Exception as e:
            logger.error(
                f"ERROR IN USER LOGOUT: while processing token logout for user {request.user}: {e}"
            )

        try:
            auth.logout(request)
        except Exception as e:
            logger.error(
                f"ERROR IN USER LOGOUT: while logging out user {request.user}: {e}"
            )

        return Response({"message": "done"})

    @swagger_auto_schema(
        method="post",
        operation_description="Register a new user with the provided details.",
        request_body=UserRegistrationSerializer,
        responses={
            201: UserSerializer(),
            400: "Invalid input data.",
            500: "Internal server error.",
        },
    )
    @action(detail=False, methods=["post"], permission_classes=[])
    def register(self, request):
        """
        Handles user registration.
        """
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            # try:
            user = serializer.save(
                password=make_password(serializer.validated_data["password"])
            )
            logger.info(
                f"USER REGISTER: New user registered: {user.username} (ID: {user.id})"
            )
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED,
            )
            # except Exception as e:
            #     logger.error(f"USER REGISTER: Error during registration: {str(e)}")
            #     return Response(
            #         {"error": "Internal server error."},
            #         status=status.HTTP_400_BAD_REQUEST,
            #     )

        logger.warning(
            f"USER REGISTER: Invalid registration attempt: {serializer.errors}"
        )
        return Response(
            {
                "error": "Invalid input. Please check your data.",
                "details": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
