from django.urls import path

from .api_views import ExternalSyncView, FileImportView

urlpatterns = [
    path('file/', FileImportView.as_view(), name='import-file'),
    path('sync/', ExternalSyncView.as_view(), name='import-sync'),
]
