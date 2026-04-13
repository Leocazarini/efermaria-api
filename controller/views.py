import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from urllib.parse import unquote
from appointments.models import StudentAppointment, EmployeeAppointment, VisitorAppointment
from .crud import (get_nurse_appointments_current_year, get_total_appointments_current_year, 
                   get_total_appointments_today, get_total_appointments_infirmary_current_year, 
                   get_total_appointments_infirmary_today)

logger = logging.getLogger('controller.views')

@login_required
def index(request):
    logger.info('Iniciando index')
    if request.method == 'GET':
        logger.info('Requisição GET recebida')
        selected_infirmary = request.COOKIES.get('infirmary')
        if selected_infirmary:
            selected_infirmary = unquote(selected_infirmary)
            selected_infirmary = selected_infirmary.strip()
            logger.debug(f"Selected infirmary after decoding: '{selected_infirmary}'")
        else:
            selected_infirmary = None  # Ou defina um valor padrão, se necessário
            logger.debug("No infirmary selected, setting to None")

        nurse_appointments = get_nurse_appointments_current_year()
        total_appointments_year = get_total_appointments_current_year()
        total_appointments_today = get_total_appointments_today()
        total_appointments_infirmary_year = get_total_appointments_infirmary_current_year(selected_infirmary)
        total_appointments_infirmary_today = get_total_appointments_infirmary_today(selected_infirmary)

        full_name = request.user.first_name
        context = {
            'first_name': full_name,
            'nurse_appointments': nurse_appointments,
            'total_appointments_year': total_appointments_year,
            'total_appointments_today': total_appointments_today,
            'total_appointments_infirmary_year': total_appointments_infirmary_year,
            'total_appointments_infirmary_today': total_appointments_infirmary_today,
            'selected_infirmary': selected_infirmary,
        }
        logger.info('Dados enviados para a interface do usuário.')
        return render(request, 'index.html', context)
    

def logout(request):
    logger.info('Iniciando logout')
    if request.method == 'GET':
        logger.info('Requisição GET recebida')
        logger.info('Dados enviados para a interface do usuário.')
        return render(request, 'user/account/logout.html')


def get_user_info(request):
    logger.info('Iniciando get_user_info')
    if request.user.is_authenticated:
        logger.info('Usuário autenticado')
        full_name = request.user.first_name
        logger.info('Dados enviados para a interface do usuário.')
        return JsonResponse({'first_name': full_name})
    else:
        logger.error('Usuário não autenticado')
        logger.info('Dados enviados para a interface do usuário.')
        return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
    

def get_chart_data(request):
    logger.info('Iniciando get_chart_data')
    # Agregar as contagens por enfermaria
    labels = ["Infantil", "Fundamental", "Ensino Médio", "Atendimento Externo"]
    infirmary_counts = {label: 0 for label in labels}
    logger.debug(f"Labels defined: {labels}")
    logger.debug("Initialized infirmary_counts dictionary.")

    # Agregar contagens do StudentAppointment
    student_counts = StudentAppointment.objects.values('infirmary').annotate(count=Count('id'))
    logger.debug(f"Student counts retrieved: {list(student_counts)}")
    for item in student_counts:
        infirmary = item['infirmary']
        if infirmary in infirmary_counts:
            infirmary_counts[infirmary] += item['count']
    logger.debug(f"Infirmary counts after StudentAppointment: {infirmary_counts}")

    # Agregar contagens do EmployeeAppointment
    employee_counts = EmployeeAppointment.objects.values('infirmary').annotate(count=Count('id'))
    logger.debug(f"Employee counts retrieved: {list(employee_counts)}")
    for item in employee_counts:
        infirmary = item['infirmary']
        if infirmary in infirmary_counts:
            infirmary_counts[infirmary] += item['count']
    logger.debug(f"Infirmary counts after EmployeeAppointment: {infirmary_counts}")

    # Agregar contagens do VisitorAppointment
    visitor_counts = VisitorAppointment.objects.values('infirmary').annotate(count=Count('id'))
    logger.debug(f"Visitor counts retrieved: {list(visitor_counts)}")
    for item in visitor_counts:
        infirmary = item['infirmary']
        if infirmary in infirmary_counts:
            infirmary_counts[infirmary] += item['count']
    logger.debug(f"Final infirmary counts: {infirmary_counts}")

    # Preparar os dados para o gráfico
    data = [infirmary_counts[label] for label in labels]
    logger.debug(f"Data prepared for chart: {data}")

    logger.info('Dados enviados para a interface do usuário.')
    # Retornar os dados em formato JSON com ensure_ascii=False
    return JsonResponse(
        {'labels': labels, 'data': data},
        json_dumps_params={'ensure_ascii': False}
    )
