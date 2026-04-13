import logging
import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import *
from patients.views import (search_student, search_employee, 
                            search_visitor, manage_visitor_data)

from controller.crud import (create_objects, create_info, 
                             get_info_by_patient, update_info )




logger = logging.getLogger('appointments.views')




"""
The following four functions render pages on the user interface:

1. home(request):
    Renders the home page of the application.

2. student_identify(request):
    Renders the page for identifying students.

3. employee_identify(request):
    Renders the page for identifying employees.

4. visitor_identify(request):
    Renders the page for identifying visitors.
"""


@login_required
def home(request):
    logger.info('Iniciando home')
    if request.method == 'GET':
        logger.info('Requisição GET recebida')
        logger.info('Dados enviados para a interface do usuário: index.html')
        return render(request, 'index.html')
    

@login_required
def student_identify(request):
    logger.info('Iniciando student_identify')
    if request.method == 'GET':
        logger.info('Requisição GET recebida')
        logger.info('Dados enviados para a interface do usuário: search_student.html')
        return render(request, 'search_student.html')
    

@login_required
def employee_identify(request):
    logger.info('Iniciando employee_identify')
    if request.method == 'GET':
        logger.info('Requisição GET recebida')
        logger.info('Dados enviados para a interface do usuário: search_employee.html')
        return render(request, 'search_employee.html')
    

@login_required
def visitor_identify(request):
    logger.info('Iniciando visitor_identify')
    if request.method == 'GET':
        logger.info('Requisição GET recebida')
        logger.info('Dados enviados para a interface do usuário: search_visitor.html')
        return render(request, 'search_visitor.html')



        

# Appointments views

@login_required
def student_appointment(request):
    """
    Handles the student appointment request.
    This view function processes GET requests to search for a student based on the provided
    name or registry. If neither name nor registry is provided, it returns an error response.
    If the student is not found, it renders a template with an error message. If the student
    is found, it renders a template with the student's information.
    Args:
        request (HttpRequest): The HTTP request object containing GET parameters.
    Returns:
        JsonResponse: If neither name nor registry is provided, returns a JSON response with
                    an error message and status code 400.
        HttpResponse: If the student is not found, returns an HTTP response rendering the
                    'search_student.html' template with an error message.
                    If the student is found, returns an HTTP response rendering the
                    'ap_student.html' template with the student's information.
    """
    logger.info('Iniciando student_appointment')
    if request.method == 'GET':
        logger.info('Requisição GET recebida')
        name = request.GET.get('name', None)
        registry = request.GET.get('registry', None)
        if not name and not registry:
            logger.error('No name or registry provided')
            return JsonResponse({'status': 'error', 'message': 'Missing required fields: name or registry'}, status=400)
        student = search_student(name, registry)

        if student is None:
            logger.error('Student not found')
            logger.info('Dados enviados para a interface do usuário: search_student.html com mensagem de erro')
            return render(request, 'search_student.html', {'error_message': 'Estudante não encontrado.'})

        logger.info('Dados enviados para a interface do usuário: ap_student.html')
        return render(request, 'ap_student.html', {'student': student})


@login_required
def employee_appointment(request):
    """
    Handles the employee appointment view.
    This view processes GET requests to search for an employee based on the provided
    'name' and 'registry' parameters. If the employee is found, it renders the 
    'ap_employee.html' template with the employee's information. If the employee is 
    not found, it logs an error and renders the 'search_employee.html' template with 
    an error message.
    Args:
        request (HttpRequest): The HTTP request object containing metadata about the 
                               request.
    Returns:
        HttpResponse: The rendered HTML response based on the search results.
    """
    logger.info('Iniciando employee_appointment')
    if request.method == 'GET':
        logger.info('Requisição GET recebida')
        name = request.GET.get('name', None)
        registry = request.GET.get('registry', None)
        employee = search_employee(name, registry)

        if employee is None:
            logger.error('Employee not found')
            logger.info('Dados enviados para a interface do usuário: search_employee.html com mensagem de erro')
            return render(request, 'search_employee.html', {'error_message': 'Colaborador não encontrado.'})

        logger.info('Dados enviados para a interface do usuário: ap_employee.html')
        return render(request, 'ap_employee.html', {'employee': employee})


@login_required
def visitor_appointment(request):
    """
    Handle visitor appointment requests.
    This view function processes GET requests to search for a visitor by name and email.
    If both name and email are not provided, it renders the 'ap_visitor.html' template.
    If a visitor is found, it renders the 'ap_visitor.html' template with the visitor's details.
    If a visitor is not found, it logs an error and renders the 'search_visitor.html' template with an error message.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: The rendered template response.
    """

    logger.info('Iniciando visitor_appointment')
    if request.method == 'GET':
        logger.info('Requisição GET recebida')
        name = request.GET.get('name', None)
        email = request.GET.get('email', None)

        if not name and not email:
            logger.info('Dados enviados para a interface do usuário: ap_visitor.html')
            return render(request, 'ap_visitor.html')

        visitor = search_visitor(name, email)

        if visitor is None:
            logger.error('Visitor not found')
            logger.info('Dados enviados para a interface do usuário: search_visitor.html com mensagem de erro')
            return render(request, 'search_visitor.html', {'error_message': 'Visitante não encontrado.'})

        logger.info('Dados enviados para a interface do usuário: ap_visitor.html')
        return render(request, 'ap_visitor.html', {'visitor': visitor}) 
              

@csrf_exempt
def student_record(request):
    """
    Handles the student record creation and update process based on the incoming POST request.
    Args:
        request (HttpRequest): The HTTP request object containing the student record data in JSON format.
    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.
    Raises:
        json.JSONDecodeError: If the JSON data in the request body cannot be decoded.
        Exception: For any other exceptions that occur during the process.
    The function performs the following steps:
    1. Reads and parses the JSON data from the request body.
    2. Extracts relevant fields from the JSON data.
    3. Checks if student information exists and updates it if necessary.
    4. Creates new student information if it does not exist.
    5. Constructs a dictionary for the student appointment data.
    6. Creates a new student appointment record.
    7. Returns a JSON response indicating the result of the operation.
    If the request method is not POST, it returns a JSON response with a 405 status code indicating that the method is not allowed.
    """
    logger.info('Iniciando student_record')
    if request.method == 'POST':
        logger.info('Requisição POST recebida')
        try:
            data = json.loads(request.body)
            logger.debug('Dados recebidos: %s', data)

            student_id = data.get('student_id')
            allergies = data.get('allergies')
            patient_notes = data.get('patient_notes')
            infirmary = data.get('infirmary')
            nurse = data.get('nurse')
            current_class = data.get('current_class')
            date = timezone.now()
            reason = data.get('reason')
            treatment = data.get('treatment')
            notes = data.get('notes')
            revaluation = data.get('revaluation')
            contact_parents = data.get('contact_parents')

            data_info_list = [
                student_id,
                allergies,
                patient_notes
            ]

            info = get_info_by_patient(StudentInfo, student_id, 'student')
            logger.debug('Info: %s', info)
            if info:
                if allergies != info.allergies or patient_notes != info.patient_notes:
                    update_info(StudentInfo, student_id, 'student', allergies, patient_notes)
                    logger.info('Dados do aluno atualizados com sucesso')
                else:
                    logger.info('Nenhuma atualização necessária para as informações do aluno')
            else:
                create_info(StudentInfo, student_id, 'student', allergies, patient_notes)
                logger.info('Novas informações do aluno criadas')

            data_dict = {
                'student_id': student_id,
                'infirmary': infirmary,
                'nurse': nurse,
                'current_class': current_class,
                'date': date,
                'reason': reason,
                'treatment': treatment,
                'notes': notes,
                'revaluation': revaluation,
                'contact_parents': contact_parents
            }

            data_list = [data_dict]

            response = create_objects(StudentAppointment, data_list)
            logger.info('Registro de atendimento do aluno criado com sucesso')

            return response

        except json.JSONDecodeError:
            logger.error('Failed to decode JSON', exc_info=True)
            return JsonResponse({'error': 'Falha ao decodificar JSON'}, status=400)
        except Exception as e:
            logger.error('An error occurred: %s', e, exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)

    logger.error('Method not allowed')
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@csrf_exempt
def employee_record(request):
    """
    Handles the employee record creation and update based on the incoming POST request.
    This function processes a POST request containing employee information in JSON format.
    It extracts the relevant fields from the JSON, checks if the employee information needs
    to be updated or created, and then creates a record in the EmployeeAppointment table.
    Args:
        request (HttpRequest): The HTTP request object containing the JSON payload.
    Returns:
        JsonResponse: A JSON response indicating success or failure of the operation.
    Raises:
        json.JSONDecodeError: If the JSON payload cannot be decoded.
        Exception: For any other exceptions that occur during processing.
    """
    logger.info('Iniciando employee_record')
    if request.method == 'POST':
        logger.info('Requisição POST recebida')
        try:
            data = json.loads(request.body)
            logger.debug('Dados recebidos: %s', data)

            employee_id = data.get('employee_id')
            allergies = data.get('allergies')
            patient_notes = data.get('patient_notes')
            infirmary = data.get('infirmary')
            nurse = data.get('nurse')
            date = timezone.now()
            reason = data.get('reason')
            treatment = data.get('treatment')
            notes = data.get('notes')
            revaluation = data.get('revaluation')

            data_info_list = [
                employee_id,
                allergies,
                patient_notes
            ]

            info = get_info_by_patient(EmployeeInfo, employee_id, 'employee')
            logger.debug('Info: %s', info)
            if info:
                if allergies != info.allergies or patient_notes != info.patient_notes:
                    update_info(EmployeeInfo, employee_id, 'employee', allergies, patient_notes)
                    logger.info('Dados do colaborador atualizados com sucesso')
                else:
                    logger.info('Nenhuma atualização necessária para as informações do colaborador')
            else:
                create_info(EmployeeInfo, employee_id, 'employee', allergies, patient_notes)
                logger.info('Novas informações do colaborador criadas')

            data_dict = {
                'employee_id': employee_id,
                'infirmary': infirmary,
                'nurse': nurse,
                'date': date,
                'reason': reason,
                'treatment': treatment,
                'notes': notes,
                'revaluation': revaluation,
            }

            data_list = [data_dict]

            response = create_objects(EmployeeAppointment, data_list)
            logger.info('Registro de atendimento do colaborador criado com sucesso')

            return response

        except json.JSONDecodeError:
            logger.error('Failed to decode JSON', exc_info=True)
            return JsonResponse({'error': 'Falha ao decodificar JSON'}, status=400)
        except Exception as e:
            logger.error('An error occurred: %s', e, exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)

    logger.error('Method not allowed')
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@csrf_exempt
def register_visitor_appointment(visitor, appointment_data):
    """
    Registers a visitor appointment by adding the visitor object to the appointment data
    and creating a new appointment record.
    Args:
        visitor (object): The visitor instance to be added to the appointment.
        appointment_data (dict): A dictionary containing the appointment details.
    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.
                    - On success: {'status': 'success', 'message': 'Atendimento salvo com sucesso!'}, status=201
                    - On failure: {'status': 'error', 'message': 'Erro ao criar o atendimento'}, status=500
                    - On exception: {'status': 'error', 'message': str(e)}, status=500
    Raises:
        Exception: If an error occurs during the appointment registration process.
    """
   
    logger.info('Iniciando register_visitor_appointment')
    try:
        appointment_data['visitor'] = visitor

        appointment_response = create_objects(VisitorAppointment, [appointment_data])

        if appointment_response.status_code != 201:
            logger.error(f"Error creating appointment: {appointment_response.content}")
            return JsonResponse({'status': 'error', 'message': 'Erro ao criar o atendimento'}, status=500)

        logger.info('Atendimento do visitante criado com sucesso')
        return JsonResponse({'status': 'success', 'message': 'Atendimento salvo com sucesso!'}, status=201)

    except Exception as e:
        logger.error(f'Error registering appointment: {e}', exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



@csrf_exempt
def visitor_record(request):
    """
    Handles the visitor record creation process.
    This view function processes a POST request containing visitor and appointment data in JSON format.
    It extracts the visitor information, manages the visitor data, and registers the visitor's appointment.
    Args:
        request (HttpRequest): The HTTP request object containing the visitor and appointment data in JSON format.
    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.
            - On success: Returns a JSON response with the registered appointment data.
            - On failure: Returns a JSON response with an error message and appropriate HTTP status code.
    Raises:
        json.JSONDecodeError: If the JSON data in the request body cannot be decoded.
        Exception: For any other exceptions that occur during the process.
    """
    logger.info('Iniciando visitor_record')
    if request.method == 'POST':
        logger.info('Requisição POST recebida')
        try:
            data = json.loads(request.body)
            logger.debug('Dados recebidos: %s', data)

            visitor_data = {
                'name': data.get('visitor_name'),
                'age': data.get('visitor_age'),
                'email': data.get('visitor_email'),
                'gender': data.get('visitor_gender'),
                'allergies': data.get('allergies'),
                'relationship': data.get('visitor_relationship'),
                'patient_notes': data.get('patient_notes'),
            }

            logger.debug('Visitor Data Extracted: %s', visitor_data)

            visitor = manage_visitor_data(visitor_data)
            if not visitor:
                logger.error('Erro ao gerenciar os dados do visitante')
                return JsonResponse({'status': 'error', 'message': 'Erro ao gerenciar os dados do visitante'}, status=500)

            appointment_data = {
                'infirmary': data.get('infirmary'),
                'nurse': data.get('nurse'),
                'reason': data.get('reason'),
                'treatment': data.get('treatment'),
                'notes': data.get('notes'),
                'revaluation': data.get('revaluation'),
                'date': timezone.now(),
            }

            logger.info('Iniciando registro do atendimento do visitante')
            return register_visitor_appointment(visitor, appointment_data)

        except json.JSONDecodeError:
            logger.error('Failed to decode JSON', exc_info=True)
            return JsonResponse({'error': 'Falha ao decodificar JSON'}, status=400)
        except Exception as e:
            logger.error(f'An error occurred: {e}', exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)

    logger.error('Method not allowed')
    return JsonResponse({'error': 'Método não permitido'}, status=405)