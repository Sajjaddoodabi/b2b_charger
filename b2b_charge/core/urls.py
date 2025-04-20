"""
URL configuration for b2b_charger project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.authtoken.views import obtain_auth_token

from core.settings import LOCAL_APPS

schema_view = get_schema_view(
    openapi.Info(
        title="B2b Charger API",
        default_version="v1",
        description="B2B Charger API Documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Authentication URLs
auth_urlpatterns = [
    path("auth/", obtain_auth_token, name="obtain_auth_token"),
]

local_apps_urlpatterns = [path(f"{app}/", include(f"{app}.urls")) for app in LOCAL_APPS]

# API URLs
api_urlpatterns = []

# Main URL patterns
urlpatterns = [
    # Swagger and Redoc Documentation
    path("swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger.yaml", schema_view.without_ui(cache_timeout=0), name="schema-yaml"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # APIs
    path("api/", include(api_urlpatterns)),
    # Admin
    path("admin/", admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
