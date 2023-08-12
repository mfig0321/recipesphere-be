
"""application URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from health import views as health_views
from users import views as user_views


# Setup the URLs and include login URLs for the browsable API.
urlpatterns = [
    path('admin/', admin.site.urls),

    # Applications Urls
    path('health/', health_views.HealthCheckEndpoint.as_view(), name='health'),

    # API
    path(
        'api/createuser/',
        user_views.CreateUserView.as_view(),
        name='createuser'),
    path('', include('recipe.urls')),
    path('', include('tags.urls')),
    path('', include('users.urls')),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='api-schema'),
        name='api-docs'),
    path('api/me/', user_views.ManageUserView.as_view(), name='me'),
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/login/', user_views.CreateTokenView.as_view(), name='login'),
    path('api/verify/', user_views.VerifyEmailView.as_view(), name='verify'),
]
