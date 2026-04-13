import logging
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator 
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, time
from patients.views import search_student, search_employee
from appointments.models import *
from controller.crud import get_appointment, get_all_appointments

logger = logging.getLogger('reports.views')

def student_search(request):
    """
    Handles the student search functionality.

    This view function processes GET requests to render the student search
    record page. It logs the initiation of the search, the receipt of the GET
    request, and the data sent to the user interface.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered student search record page.
    """
    logger.info('Iniciando student_search')
    if request.method == 'GET':
        logger.info('Requisição GET recebida')
        logger.info('Dados enviados para a interface do usuário.')
        return render(request, 'student_search_record.html')

def student_record(request):
    """
    Handles the student record retrieval and rendering based on the request method and parameters.
    Args:
        request (HttpRequest): The HTTP request object containing method and parameters.
    Returns:
        JsonResponse: If the request method is GET and required parameters are missing, returns a JSON response with an error message and status 400.
        HttpResponse: If the student is not found, returns an HTTP response rendering the 'student_search_record.html' template with an error message.
        HttpResponse: If the student is found, returns an HTTP response rendering the 'student_record.html' template with student and appointment data.
    """
    logger.info('Iniciando student_record')
    if request.method == 'GET':
        logger.info('Requisição GET recebida')
        name = request.GET.get('name', None)
        registry = request.GET.get('registry', None)
        
        if not name and not registry:
            logger.error('No name or registry provided')
            logger.info('Dados enviados para a interface do usuário.')
            return JsonResponse({'status': 'error', 'message': 'Missing required fields: name or registry'}, status=400)
        
        # Busca o estudante
        student = search_student(name, registry)
    
        if student is None:
            logger.error('Student not found')
            logger.info('Dados enviados para a interface do usuário.')
            return render(request, 'student_search_record.html', {'error_message': 'Estudante não encontrado.'}) 

        # Identifica o campo correto do ID
        identifier_field = 'student_id' 

        # Obtém os dados dos atendimentos do paciente
        appointment = get_appointment(StudentAppointment, identifier_field, patient_id=student['id'])

        logger.debug(f'Appointments found: {appointment}')

        list_appointments = list(appointment)
        list_appointments.sort(key=lambda x: x['date'], reverse=True)

        logger.info('Dados enviados para a interface do usuário.')
        return render(request, 'student_record.html', {'student': student, 'appointment': list_appointments})

def employee_search(request):
    """
    Handles the employee search functionality.

    This view function processes GET requests to render the employee search record page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered employee search record page.
    """
    logger.info('Iniciando employee_search')
    if request.method == 'GET':
        logger.info('Requisição GET recebida')
        logger.info('Dados enviados para a interface do usuário.')
        return render(request, 'employee_search_record.html')

def employee_record(request):
    """
    Handles the employee record retrieval based on GET request parameters.
    Logs the start of the process and checks if the request method is GET. 
    Retrieves 'name' and 'registry' from the request parameters. If neither 
    is provided, logs an error and returns a JSON response with an error message.
    Searches for the employee using the provided 'name' or 'registry'. If the 
    employee is not found, logs an error and renders an error message on the 
    'employee_search_record.html' template.
    If the employee is found, retrieves the employee's appointments, sorts them 
    by date in descending order, and renders the 'employee_record.html' template 
    with the employee and appointment data.
    Args:
        request (HttpRequest): The HTTP request object containing method and parameters.
    Returns:
        HttpResponse: Renders the appropriate template with context data or returns 
                      a JSON response with an error message.
    """
    logger.info('Iniciando employee_record')
    if request.method == 'GET':
        logger.info('Requisição GET recebida')
        name = request.GET.get('name', None)
        registry = request.GET.get('registry', None)
        
        if not name and not registry:
            logger.error('No name or registry provided')
            logger.info('Dados enviados para a interface do usuário.')
            return JsonResponse({'status': 'error', 'message': 'Missing required fields: name or registry'}, status=400)
        
        # Busca o funcionário
        employee = search_employee(name, registry)
    
        if employee is None:
            logger.error('Employee not found')
            logger.info('Dados enviados para a interface do usuário.')
            return render(request, 'employee_search_record.html', {'error_message': 'Colaborador não encontrado.'}) 

        # Identifica o campo correto do ID
        identifier_field = 'employee_id' 

        # Obtém os dados dos atendimentos do paciente
        appointment = get_appointment(EmployeeAppointment, identifier_field, patient_id=employee['id'])

        logger.debug(f'Appointments found: {appointment}')

        list_appointments = list(appointment)
        list_appointments.sort(key=lambda x: x['date'], reverse=True)

        logger.info('Dados enviados para a interface do usuário.')
        return render(request, 'employee_record.html', {'employee': employee, 'appointment': list_appointments})

@login_required
def reports(request):
    """
    Handles the reports view for GET and POST requests.
    For GET requests:
    - Logs the initiation and receipt of the GET request.
    - Renders the 'reports.html' template.
    For POST requests:
    - Logs the receipt of the POST request.
    - Retrieves and logs form data from the request.
    - Validates the form data and logs any errors.
    - If there are validation errors, returns a JSON response with errors for AJAX requests,
      or renders the 'reports.html' template with error messages for non-AJAX requests.
    - Converts date strings to datetime objects and handles any parsing errors.
    - Retrieves all appointments based on the form data.
    - Implements pagination for the retrieved appointments.
    - Renders the appropriate template based on whether the request is an AJAX request or not.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: The rendered template or JSON response based on the request type.
    """
    logger.info('Iniciando reports')
    if request.method == 'GET':
        logger.info('Requisição GET recebida')
        logger.info('Dados enviados para a interface do usuário.')
        return render(request, 'reports.html')

    elif request.method == 'POST':
        logger.info('Requisição POST recebida')
        logger.debug('POST request received')

        date_begin = request.POST.get('date_begin')
        date_end = request.POST.get('date_end')
        infirmaries = request.POST.getlist('infirmaries')
        search_term = request.POST.get('search_term', '').strip()

        logger.debug(f'info: {date_begin}, {date_end}, {infirmaries}, {search_term}')

        # Validações
        errors = []
        if not date_begin:
            errors.append("Por favor, preencha a data de início.")
        if not date_end:
            errors.append("Por favor, preencha a data de fim.")
        if not infirmaries:
            errors.append("Por favor, selecione pelo menos uma enfermaria.")

        if errors:
            logger.error(f'Errors in form submission: {errors}')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                logger.info('Dados enviados para a interface do usuário.')
                return JsonResponse({'errors': errors}, status=400)
            else:
                for error in errors:
                    messages.error(request, error)
                logger.info('Dados enviados para a interface do usuário.')
                return render(request, 'reports.html')

        # Conversão das datas
        try:
            date_begin = datetime.strptime(date_begin, '%Y-%m-%d')
            date_end = datetime.strptime(date_end, '%Y-%m-%d')
            date_end = datetime.combine(date_end.date(), time.max)  # Define a hora para 23:59:59.999999
        except ValueError as e:
            logger.error(f'Date parsing error: {e}', exc_info=True)
            logger.info('Dados enviados para a interface do usuário.')
            return JsonResponse({'errors': ['Data inválida.']}, status=400)

        # Número de resultados por página
        RESULTS_PER_PAGE = 100 

        # Obtenção dos atendimentos
        all_appointments = get_all_appointments(date_begin, date_end, infirmaries, search_term)
        logger.debug(f'All appointments retrieved: {all_appointments}')

        # Implementação da paginação
        paginator = Paginator(all_appointments, RESULTS_PER_PAGE)

        # Obtenha o número da página atual
        page_number = request.POST.get('page') or 1

        # Obtenha a página desejada
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'date_begin': date_begin,
            'date_end': date_end,
            'paginator': paginator,
            'search_term': search_term,
        }

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Renderiza o template parcial e retorna como HTML
            html = render_to_string('report_results_partial.html', context, request=request)
            logger.info('Dados enviados para a interface do usuário.')
            return HttpResponse(html)
        else:
            logger.info('Dados enviados para a interface do usuário.')
            return render(request, 'report_results.html', context)
    else:
        logger.error(f'Request method {request.method} not allowed')
        logger.info('Dados enviados para a interface do usuário.')
        return render(request, 'reports.html')
