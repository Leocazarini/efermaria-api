from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('controller.urls')),
    path('accounts/', include('allauth.urls')),
    path('appointments/', include('appointments.urls')),
    path('patients/', include('patients.urls')),
    path('reports/', include('reports.urls')),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)