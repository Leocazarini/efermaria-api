import logging
from datetime import datetime, time

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AppointmentQuerySerializer
from .services import (
    get_all_appointments,
    get_nurse_appointments_current_year,
    get_total_appointments_current_year,
    get_total_appointments_infirmary_current_year,
    get_total_appointments_infirmary_today,
    get_total_appointments_today,
)

logger = logging.getLogger('reports.api_views')


class AppointmentsReportView(APIView):
    def get(self, request):
        serializer = AppointmentQuerySerializer(data={
            **request.query_params.dict(),
            'infirmaries': request.query_params.getlist('infirmaries'),
        })
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        date_begin = timezone.make_aware(
            datetime.combine(data['date_begin'], time.min)
        )
        date_end = timezone.make_aware(
            datetime.combine(data['date_end'], time.max)
        )

        appointments = get_all_appointments(
            date_begin,
            date_end,
            data['infirmaries'],
            data['search'],
        )
        return Response(appointments)


class StatsView(APIView):
    def get(self, request):
        return Response({
            'total_current_year': get_total_appointments_current_year(),
            'total_today': get_total_appointments_today(),
            'nurses': get_nurse_appointments_current_year(),
        })


class InfirmaryStatsView(APIView):
    def get(self, request, infirmary_name):
        return Response({
            'infirmary': infirmary_name,
            'total_current_year': get_total_appointments_infirmary_current_year(infirmary_name),
            'total_today': get_total_appointments_infirmary_today(infirmary_name),
        })
