from django.urls import path

from .api_views import AppointmentsReportView, InfirmaryStatsView, StatsView

urlpatterns = [
    path('appointments/', AppointmentsReportView.as_view(), name='report-appointments'),
    path('stats/', StatsView.as_view(), name='report-stats'),
    path('stats/infirmary/<str:infirmary_name>/', InfirmaryStatsView.as_view(), name='report-stats-infirmary'),
]
