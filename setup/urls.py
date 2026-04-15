from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/auth/', include('authentication.urls')),

    # REST API v1
    path('api/v1/patients/', include('patients.urls')),
    path('api/v1/appointments/', include('appointments.urls')),
    path('api/v1/reports/', include('reports.urls')),
    path('api/v1/imports/', include('imports.urls')),

    # OpenAPI schema + Swagger / ReDoc
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
