"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from apps.patients.views import patients_page

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.authentication.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
    path("api/patients/", include("apps.patients.urls")),
    path("patients/", patients_page, name="patients_page"),
    path("api/etl/", include("apps.etl.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/ml/", include("apps.ml.urls")),
    path("api/reports/", include("apps.reports.urls")),
    # Alias legacy para compatibilidad con rutas anteriores
    path("auth/", include("apps.authentication.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("", RedirectView.as_view(url="/dashboard/", permanent=False)),
]
