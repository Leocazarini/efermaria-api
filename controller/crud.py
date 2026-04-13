import logging
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from django.utils import timezone
from datetime import datetime
from django.db.models import Count, Q
from collections import defaultdict
from appointments.models import StudentAppointment, EmployeeAppointment, VisitorAppointment

logger = logging.getLogger('controller.crud')

########### Generic CRUD functions ###########

def create_objects(model, data_list):
    """
    Creates objects in the specified model using the provided data list.
    Args:
        model (Model): The Django model in which objects will be created.
        data_list (list): A list of dictionaries containing the data for each object to be created.
    Returns:
        JsonResponse: A JSON response containing the status of the operation and the created objects or error message.
    Raises:
        ValidationError: If there is a validation error while creating the objects.
        Exception: For any other exceptions that occur during the creation process.
    Logs:
        Info: Logs the start of the function and general information.
        Debug: Logs the model and data received, and each created object.
        Error: Logs validation errors and any other exceptions.
    """
    logger.info("Iniciando create_objects")
    try:
        logger.debug(f"Creating objects in model: {model}")
        logger.debug(f"Data received: {data_list}")
        objects = []
        for data in data_list:
            obj = model.objects.create(**data)
            obj.save()
            objects.append(model_to_dict(obj))
            logger.debug(f"Created object: {obj}")
        logger.info("Dados enviados para a interface do usuário.")
        return JsonResponse({'status': 'success', 'data': objects}, status=201)
    except ValidationError as e:
        logger.error(f"Validation Error: {e.message_dict}")
        logger.info("Dados enviados para a interface do usuário.")
        return JsonResponse({'status': 'error', 'message': e.message_dict}, status=400)
    except Exception as e:
        logger.error(f"Exception: {e}")
        logger.info("Dados enviados para a interface do usuário.")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def get_object(model, name=None, registry=None, email=None, related_fields=None):
    """
    Retrieve an object or a list of objects from the database based on the provided filters.
    Args:
        model (Model): The Django model class to query.
        name (str, optional): The name to filter objects by (case-insensitive, partial match).
        registry (str, optional): The registry identifier to filter objects by.
        email (str, optional): The email to filter objects by.
        related_fields (list or str, optional): The related fields to select in the query.
    Returns:
        list: A list containing the found object(s) if any, or None if no object is found by email.
    Raises:
        Http404: If no objects are found with the provided name or registry, or if neither name nor registry is provided.
    Logs:
        - Info: Logs the start of the function, and successful retrieval of objects.
        - Debug: Logs the details of the query filters applied.
        - Warning: Logs when no records are found for the provided email or name.
        - Error: Logs when neither name nor registry is provided.
    """
    logger.info("Iniciando get_object")
    logger.info(f"Starting get_object function for model: {model.__name__}.")
    query = model.objects.all()
    
    if related_fields:
        if isinstance(related_fields, list):
            logger.debug(f"Selecting related fields: {related_fields}.")
            query = query.select_related(*related_fields)
        else:
            logger.debug(f"Selecting related field: {related_fields}.")
            query = query.select_related(related_fields)
    
    if email:
        logger.debug(f"Filtering object with email: {email}.")
        try:
            obj = query.get(email=email)
            logger.info(f"Object found with email: {email}.")
            logger.info("Dados enviados para a interface do usuário.")
            return [obj]
        except model.DoesNotExist:
            logger.warning(f"No records found with email: {email}")
            return None

    if name:
        logger.debug(f"Filtering objects with name containing: {name}.")
        objs = query.filter(name__icontains=name)
        if not objs.exists():
            logger.warning("No records found with the provided name.")
            raise Http404('No records found.')
        logger.info(f"{len(objs)} objects found with the name containing: {name}.")
        logger.info("Dados enviados para a interface do usuário.")
        return list(objs)  
    elif registry:
        logger.debug(f"Filtering object with registry: {registry}.")
        obj = get_object_or_404(query, registry=registry)
        logger.info(f"Object found with registry: {registry}.")
        logger.info("Dados enviados para a interface do usuário.")
        return [obj]  
    else:
        logger.error("Neither name nor registry was provided. Raising Http404.")
        raise Http404('Name or registry must be provided.')

def get_by_id(model, pk, related_fields=None):
    """
    Retrieve an object by its primary key (pk) from the specified model, optionally including related fields.
    Args:
        model (Model): The Django model class from which to retrieve the object.
        pk (int): The primary key of the object to retrieve.
        related_fields (list or str, optional): A list or a single string of related fields to include in the query using select_related.
    Returns:
        Model instance: The retrieved model instance.
    Raises:
        Http404: If the object does not exist.
    """
    logger.info("Iniciando get_by_id")
    query = model.objects.all()
    
    if related_fields:
        if isinstance(related_fields, list):
            query = query.select_related(*related_fields)
        else:
            query = query.select_related(related_fields)
    
    result = get_object_or_404(query, pk=pk)
    logger.info("Dados enviados para a interface do usuário.")
    return result

def update_object(model, registry, data):
    """
    Updates an object of the given model with the provided data.
    Args:
        model (Model): The Django model class of the object to be updated.
        registry (str): The registry identifier of the object to be updated.
        data (dict): A dictionary containing the fields and values to update the object with.
    Returns:
        JsonResponse: A JSON response indicating the status of the update operation.
                      - If successful, returns a JSON response with status 'success' and the updated object data.
                      - If the object is not found, returns a JSON response with status 'error' and a 404 status code.
                      - If there is a validation error, returns a JSON response with status 'error' and a 400 status code.
    Logs:
        - Logs the start of the update operation.
        - Logs if the object is found and is being updated.
        - Logs if the object is successfully updated.
        - Logs a warning if the object is not found.
        - Logs an error if there is a validation error during the update.
    """
    logger.info("Iniciando update_object")
    logger.info(f"Starting update_object function for model: {model.__name__}, registry: {registry}.")
    
    try:
        obj = get_object_or_404(model, registry=registry)
        logger.debug(f"Object found with registry: {registry}. Updating with data: {data}.")
        
        for key, value in data.items():
            setattr(obj, key, value)
        
        obj.save()
        logger.info(f"Object with registry {registry} updated successfully.")
        logger.info("Dados enviados para a interface do usuário.")
        return JsonResponse({'status': 'success', 'data': model_to_dict(obj)})
    
    except Http404:
        logger.warning(f"Object with registry {registry} not found.")
        logger.info("Dados enviados para a interface do usuário.")
        return JsonResponse({'status': 'error', 'message': 'Object not found'}, status=404)
    
    except ValidationError as e:
        logger.error(f"Validation error while updating object with registry {registry}: {e.message_dict}")
        logger.info("Dados enviados para a interface do usuário.")
        return JsonResponse({'status': 'error', 'message': e.message_dict}, status=400)

def delete_object(model, registry):
    """
    Deletes an object from the database based on the provided model and registry.
    Args:
        model (Model): The Django model class from which the object should be deleted.
        registry (str): The registry identifier of the object to be deleted.
    Returns:
        JsonResponse: A JSON response indicating the result of the delete operation.
            - If successful, returns a JSON response with status 'success' and a message 'Deleted successfully'.
            - If the object is not found, returns a JSON response with status 'error' and a message 'Object not found', with a 404 status code.
            - If any other exception occurs, returns a JSON response with status 'error' and the exception message, with a 400 status code.
    Logs:
        - Logs the start of the delete operation with the model name and registry.
        - Logs if the object is found and is being deleted.
        - Logs if the object is successfully deleted.
        - Logs a warning if the object is not found.
        - Logs an error if any other exception occurs during the delete operation.
    """
    logger.info("Iniciando delete_object")
    logger.info(f"Starting delete_object function for model: {model.__name__}, registry: {registry}.")
    
    try:
        obj = get_object_or_404(model, registry=registry)
        logger.debug(f"Object found with registry: {registry}. Deleting object.")
        
        obj.delete()
        logger.info(f"Object with registry {registry} deleted successfully.")
        logger.info("Dados enviados para a interface do usuário.")
        return JsonResponse({'status': 'success', 'message': 'Deleted successfully'})    
    
    except Http404:
        logger.warning(f"Object with registry {registry} not found.")
        logger.info("Dados enviados para a interface do usuário.")
        return JsonResponse({'status': 'error', 'message': 'Object not found'}, status=404)
    
    except Exception as e:
        logger.error(f"Error occurred while deleting object with registry {registry}: {str(e)}")
        logger.info("Dados enviados para a interface do usuário.")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

########### Info tables ###########

def get_info_by_patient(info_model, foreign_key_value, foreign_key_field):
    """
    Retrieves information from the specified model based on a foreign key field and its value.
    Args:
        info_model (Model): The Django model class to query.
        foreign_key_value (Any): The value of the foreign key field to filter by.
        foreign_key_field (str): The name of the foreign key field to filter by.
    Returns:
        Model instance or None: The instance of the model if found, otherwise None.
    Raises:
        info_model.DoesNotExist: If no instance is found matching the foreign key field and value.
    """
    logger.info("Iniciando get_info_by_patient")
    logger.info(f"Starting get_info_by_patient function for model: {info_model.__name__}.")
    logger.debug(f"Looking up {info_model.__name__} with {foreign_key_field} = {foreign_key_value}.")
    
    try:
        result = info_model.objects.get(**{foreign_key_field: foreign_key_value})
        logger.info(f"Information found for {foreign_key_field} = {foreign_key_value}.")
        logger.info("Dados enviados para a interface do usuário.")
        return result
        
    except info_model.DoesNotExist:
        logger.warning(f"No information found for {foreign_key_field} = {foreign_key_value}.")
        return None

def update_info(info_model, foreign_key_value, foreign_key_field, allergies=None, patient_notes=None):
    """
    Updates or creates information for a given model based on a foreign key value.
    Args:
        info_model (Model): The model class to update or create information for.
        foreign_key_value (Any): The value of the foreign key to identify the record.
        foreign_key_field (str): The name of the foreign key field.
        allergies (str, optional): The allergies information to update. Defaults to None.
        patient_notes (str, optional): The patient notes to update. Defaults to None.
    Returns:
        Model: The updated or newly created model instance.
    """
    logger.info("Iniciando update_info")
    logger.info(f"Starting update_info function for model: {info_model.__name__}.")
    logger.debug(f"Updating information for {foreign_key_field} = {foreign_key_value}. Allergies: {allergies}, Notes: {patient_notes}")
    
    info = get_info_by_patient(info_model, foreign_key_value, foreign_key_field)
    
    if info:
        logger.info(f"Information found for {foreign_key_field} = {foreign_key_value}. Updating record.")
        info.allergies = allergies
        info.patient_notes = patient_notes
        info.save()
        logger.info(f"Information updated for {foreign_key_field} = {foreign_key_value}.")
        logger.info("Dados enviados para a interface do usuário.")
        return info
    else:
        logger.warning(f"No information found for {foreign_key_field} = {foreign_key_value}. Creating new record.")
        return create_info(info_model, foreign_key_value, foreign_key_field, allergies, patient_notes)

def create_info(info_model, foreign_key_value, foreign_key_field, allergies=None, patient_notes=None):
    """
    Creates a new information entry in the database for the given model.
    Args:
        info_model (Model): The Django model class to create an entry for.
        foreign_key_value (Any): The value of the foreign key to associate with the new entry.
        foreign_key_field (str): The name of the foreign key field in the model.
        allergies (str, optional): Information about patient allergies. Defaults to None.
        patient_notes (str, optional): Additional notes about the patient. Defaults to None.
    Returns:
        Model: The created model instance.
    Logs:
        Logs the start and successful completion of the information creation process.
    """
    logger.info("Iniciando create_info")
    logger.info(f"Starting create_info function for model: {info_model.__name__}.")
    logger.debug(f"Creating information for {foreign_key_field} = {foreign_key_value}. Allergies: {allergies}, Notes: {patient_notes}")
    
    info = info_model.objects.create(**{
        foreign_key_field: foreign_key_value,
        'allergies': allergies,
        'patient_notes': patient_notes
    })
    
    logger.info(f"Information created successfully for {foreign_key_field} = {foreign_key_value}.")
    logger.info("Dados enviados para a interface do usuário.")
    return info

########### Visitor update info ###########

def update_visitor_info(visitor_model, visitor_email, allergies=None, patient_notes=None):
    """
    Updates the information of a visitor in the database.
    Args:
        visitor_model (Model): The Django model representing the visitor.
        visitor_email (str): The email of the visitor to be updated.
        allergies (str, optional): The updated allergies information. Defaults to None.
        patient_notes (str, optional): The updated patient notes. Defaults to None.
    Returns:
        JsonResponse: A JSON response indicating the status of the update operation.
                      If successful, returns the updated visitor data.
                      If the visitor is not found, returns an error message with a 404 status.
    """
    logger.info("Iniciando update_visitor_info")
    # Obter o objeto real do visitante
    visitor = get_object(visitor_model, email=visitor_email)

    if visitor and len(visitor) > 0:
        # Acessar o primeiro visitante da lista
        visitor_obj = visitor[0]
        logger.debug(f"Updating visitor: allergies={allergies}, patient_notes={patient_notes}")

        # Atualizar os campos diretamente no objeto
        visitor_obj.allergies = allergies
        visitor_obj.patient_notes = patient_notes

        # Salvar as alterações no banco de dados
        visitor_obj.save()

        logger.info(f"Information updated for visitor with email: {visitor_email}.")
        logger.info("Dados enviados para a interface do usuário.")
        return JsonResponse({'status': 'success', 'data': model_to_dict(visitor_obj)})
    
    else:
        logger.warning(f"No visitor found with email: {visitor_email}.")
        logger.info("Dados enviados para a interface do usuário.")
        return JsonResponse({'status': 'error', 'message': 'Visitor not found'}, status=404)
    
########### Appointment search ###########

def get_appointment(model, identifier_field, patient_id=None, appointment_date=None):
    """
    Retrieve appointments based on dynamic filters for patient ID and appointment date.
    Args:
        model (Django Model): The Django model to query.
        identifier_field (str): The field name used to identify the patient (e.g., 'student_id' or 'employee_id').
        patient_id (int, optional): The ID of the patient to filter by. Defaults to None.
        appointment_date (datetime.date, optional): The date of the appointment to filter by. Defaults to None.
    Returns:
        list: A list of dictionaries representing the filtered appointment records. 
              Returns an empty list if no records match the criteria.
    Logs:
        Logs various stages of the function execution, including:
        - Start of the function.
        - Warnings if no search parameters are provided or if no results are found.
        - Debug information for applied filters.
        - Info on the number of records found.
    """
    logger.info("Iniciando get_appointment")
    logger.info(f"Starting get_appointment function for model: {model.__name__}.")

    if patient_id is None and appointment_date is None:
        logger.warning("No search parameters provided.")
        return []

    # Inicia a query base
    query = model.objects.all()

    # Filtro dinâmico por patient_id (student_id ou employee_id)
    if patient_id:
        filter_kwargs = {identifier_field: patient_id}  # Usamos o identificador dinâmico
        query = query.filter(**filter_kwargs)
        logger.debug(f"Filtering appointments by {identifier_field} = {patient_id}.")

    # Filtro por appointment_date
    if appointment_date:
        query = query.filter(appointment_date=appointment_date)
        logger.debug(f"Filtering appointments by appointment_date = {appointment_date}.")

    # Verifica se há resultados
    if not query.exists():
        logger.warning(f"No appointments found for the given criteria: {identifier_field} = {patient_id}, appointment_date = {appointment_date}.")
        return []

    # Converte os resultados em dicionários
    results = list(query.values())
    logger.info(f"Appointments found: {len(results)} record(s) found.")
    logger.info("Dados enviados para a interface do usuário.")
    return results

########### Index Module ###########

def get_nurse_appointments_current_year():
    """
    Retrieves the count of appointments for each nurse for the current year.
    This function filters appointments from three different models (StudentAppointment, 
    EmployeeAppointment, and VisitorAppointment) based on the current year. It then 
    combines these appointments into a single list and counts the number of appointments 
    for each nurse. The result is returned as a list of dictionaries, where each 
    dictionary contains a nurse and their corresponding appointment count.
    Returns:
        list: A list of dictionaries, each containing a 'nurse' and their 'count' of 
              appointments for the current year.
    """
    logger.info("Iniciando get_nurse_appointments_current_year")
    # Get the current year
    current_year = timezone.now().year

    # Filter appointments for the current year for each model
    student_appointments = StudentAppointment.objects.filter(date__year=current_year)
    employee_appointments = EmployeeAppointment.objects.filter(date__year=current_year)
    visitor_appointments = VisitorAppointment.objects.filter(date__year=current_year)

    # Combine the querysets into a list
    all_appointments = list(student_appointments) + list(employee_appointments) + list(visitor_appointments)

    # Dictionary to store the count per nurse
    nurse_counts = defaultdict(int)

    # Iterate over all appointments and count per nurse
    for appointment in all_appointments:
        nurse = appointment.nurse
        nurse_counts[nurse] += 1

    # Convert the dictionary into a list of dictionaries for the template
    nurse_appointments = [{'nurse': nurse, 'count': count} for nurse, count in nurse_counts.items()]

    logger.info("Dados enviados para a interface do usuário.")
    return nurse_appointments

def get_total_appointments_current_year():
    """
    Calculate the total number of appointments for students, employees, and visitors for the current year.
    This function retrieves the current year using the timezone module and then queries the database
    to count the number of appointments for students, employees, and visitors that occurred within
    the current year. It sums these counts to get the total number of appointments.
    Returns:
        int: The total number of appointments for the current year.
    """
    logger.info("Iniciando get_total_appointments_current_year")
    current_year = timezone.now().year

    total_students = StudentAppointment.objects.filter(date__year=current_year).count()
    total_employees = EmployeeAppointment.objects.filter(date__year=current_year).count()
    total_visitors = VisitorAppointment.objects.filter(date__year=current_year).count()

    total_appointments = total_students + total_employees + total_visitors

    logger.info("Dados enviados para a interface do usuário.")
    return total_appointments

def get_total_appointments_today():
    """
    Retrieves the total number of appointments for students, employees, and visitors scheduled for today.
    This function queries the StudentAppointment, EmployeeAppointment, and VisitorAppointment models
    to count the number of appointments for the current date and returns the sum of these counts.
    Returns:
        int: The total number of appointments for today.
    """
    logger.info("Iniciando get_total_appointments_today")
    today = timezone.now().date()

    total_students = StudentAppointment.objects.filter(date__date=today).count()
    total_employees = EmployeeAppointment.objects.filter(date__date=today).count()
    total_visitors = VisitorAppointment.objects.filter(date__date=today).count()

    total_appointments = total_students + total_employees + total_visitors

    logger.info("Dados enviados para a interface do usuário.")
    return total_appointments

def get_total_appointments_infirmary_current_year(infirmary):
    """
    Calculate the total number of appointments in a given infirmary for the current year.
    This function sums up the number of student, employee, and visitor appointments
    for the specified infirmary in the current year. If the infirmary is None or empty,
    it returns 0 and logs a warning.
    Args:
        infirmary (str): The name of the infirmary to calculate appointments for.
    Returns:
        int: The total number of appointments in the specified infirmary for the current year.
    """
    logger.info("Iniciando get_total_appointments_infirmary_current_year")
    if not infirmary:
        logger.warning("Infirmary is None or empty.")
        return 0  # Retornar 0 se infirmary é None ou vazio

    current_year = timezone.now().year
    infirmary_normalized = infirmary.strip()

    total_students = StudentAppointment.objects.filter(
        date__year=current_year,
        infirmary__iexact=infirmary_normalized
    ).count()
    total_employees = EmployeeAppointment.objects.filter(
        date__year=current_year,
        infirmary__iexact=infirmary_normalized
    ).count()
    total_visitors = VisitorAppointment.objects.filter(
        date__year=current_year,
        infirmary__iexact=infirmary_normalized
    ).count()

    total_appointments = total_students + total_employees + total_visitors

    logger.debug(f"Total appointments for infirmary '{infirmary}': {total_appointments}")
    logger.info("Dados enviados para a interface do usuário.")
    return total_appointments

def get_total_appointments_infirmary_today(infirmary):
    """
    Calculate the total number of appointments in a given infirmary for today.
    This function retrieves the total number of student, employee, and visitor appointments
    scheduled for the current day in the specified infirmary. If the infirmary is None or empty,
    it returns 0 and logs a warning.
    Args:
        infirmary (str): The name of the infirmary to check for appointments.
    Returns:
        int: The total number of appointments for the given infirmary today.
    Raises:
        None
    Example:
        total_appointments = get_total_appointments_infirmary_today("Main Infirmary")
        print(total_appointments)
    """
    logger.info("Iniciando get_total_appointments_infirmary_today")
    if not infirmary:
        logger.warning("Infirmary is None or empty.")
        return 0  # Retornar 0 se infirmary é None ou vazio

    today = timezone.now().date()
    infirmary_normalized = infirmary.strip()

    total_students = StudentAppointment.objects.filter(
        date__date=today,
        infirmary__iexact=infirmary_normalized
    ).count()
    total_employees = EmployeeAppointment.objects.filter(
        date__date=today,
        infirmary__iexact=infirmary_normalized
    ).count()
    total_visitors = VisitorAppointment.objects.filter(
        date__date=today,
        infirmary__iexact=infirmary_normalized
    ).count()

    total_appointments = total_students + total_employees + total_visitors

    logger.debug(f"Total appointments for infirmary '{infirmary}': {total_appointments}")
    logger.info("Dados enviados para a interface do usuário.")
    return total_appointments

########### Reports Module ###########

def get_student_appointments(date_begin, date_end, infirmaries, search_term):
    """
    Retrieves student appointments within a specified date range and infirmaries, optionally filtered by a search term.
    Args:
        date_begin (datetime.date): The start date of the range to filter appointments.
        date_end (datetime.date): The end date of the range to filter appointments.
        infirmaries (list): A list of infirmary identifiers to filter appointments.
        search_term (str): An optional search term to filter appointments by student details, reason, treatment, notes, infirmary, nurse, or date.
    Returns:
        QuerySet: A Django QuerySet of StudentAppointment objects that match the specified filters.
    """
    logger.info("Iniciando get_student_appointments")
    logger.info(f"Obtendo atendimentos de estudantes de {date_begin} a {date_end} nas enfermarias: {infirmaries} com termo de busca: {search_term}")

    # Filtros básicos
    filters = Q(
        date__range=[date_begin, date_end],
        infirmary__in=infirmaries,
    )

    if search_term:
        search_filters = Q(
            student__name__icontains=search_term) | \
            Q(current_class__icontains=search_term) | \
            Q(student__class_group__name__icontains=search_term) | \
            Q(student__age__icontains=search_term) | \
            Q(student__gender__icontains=search_term) | \
            Q(reason__icontains=search_term) | \
            Q(treatment__icontains=search_term) | \
            Q(notes__icontains=search_term) | \
            Q(revaluation__icontains=search_term) | \
            Q(contact_parents__icontains=search_term) | \
            Q(infirmary__icontains=search_term) | \
            Q(nurse__icontains=search_term)
        
        # Tentar buscar por data se o termo corresponder a uma data
        try:
            search_date = datetime.strptime(search_term, '%d/%m/%Y').date()
            search_filters |= Q(date__date=search_date)
        except ValueError:
            pass  # Não é uma data, ignorar

        filters &= search_filters

    result = StudentAppointment.objects.filter(filters).select_related('student__class_group')
    logger.info("Dados enviados para a interface do usuário.")
    return result

def get_employee_appointments(date_begin, date_end, infirmaries, search_term):
    """
    Retrieves employee appointments within a specified date range, infirmaries, and optional search term.
    Args:
        date_begin (datetime.date): The start date for the range of appointments.
        date_end (datetime.date): The end date for the range of appointments.
        infirmaries (list): A list of infirmary identifiers to filter the appointments.
        search_term (str): An optional search term to filter the appointments by employee details, reason, treatment, notes, or date.
    Returns:
        QuerySet: A Django QuerySet containing the filtered employee appointments with related employee department data.
    """
    logger.info("Iniciando get_employee_appointments")
    logger.info(f"Obtendo atendimentos de funcionários de {date_begin} a {date_end} nas enfermarias: {infirmaries} com termo de busca: {search_term}")

    filters = Q(
        date__range=[date_begin, date_end],
        infirmary__in=infirmaries,
    )

    if search_term:
        search_filters = Q(
            employee__name__icontains=search_term) | \
            Q(employee__department__name__icontains=search_term) | \
            Q(employee__age__icontains=search_term) | \
            Q(employee__gender__icontains=search_term) | \
            Q(reason__icontains=search_term) | \
            Q(treatment__icontains=search_term) | \
            Q(notes__icontains=search_term) | \
            Q(revaluation__icontains=search_term) | \
            Q(infirmary__icontains=search_term) | \
            Q(nurse__icontains=search_term)
        
        try:
            search_date = datetime.strptime(search_term, '%d/%m/%Y').date()
            search_filters |= Q(date__date=search_date)
        except ValueError:
            pass

        filters &= search_filters

    result = EmployeeAppointment.objects.filter(filters).select_related('employee__department')
    logger.info("Dados enviados para a interface do usuário.")
    return result

def get_visitor_appointments(date_begin, date_end, infirmaries, search_term):
    """
    Retrieve visitor appointments within a specified date range and infirmaries, optionally filtered by a search term.
    Args:
        date_begin (datetime.date): The start date of the range to filter appointments.
        date_end (datetime.date): The end date of the range to filter appointments.
        infirmaries (list): A list of infirmary identifiers to filter appointments.
        search_term (str): An optional search term to filter appointments by visitor details, reason, treatment, notes, infirmary, nurse, or date.
    Returns:
        QuerySet: A Django QuerySet of VisitorAppointment objects that match the specified filters.
    """
    logger.info("Iniciando get_visitor_appointments")
    logger.info(f"Obtendo atendimentos de visitantes de {date_begin} a {date_end} nas enfermarias: {infirmaries} com termo de busca: {search_term}")

    filters = Q(
        date__range=[date_begin, date_end],
        infirmary__in=infirmaries,
    )

    if search_term:
        search_filters = Q(
            visitor__name__icontains=search_term) | \
            Q(visitor__relationship__icontains=search_term) | \
            Q(visitor__age__icontains=search_term) | \
            Q(visitor__gender__icontains=search_term) | \
            Q(reason__icontains=search_term) | \
            Q(treatment__icontains=search_term) | \
            Q(notes__icontains=search_term) | \
            Q(revaluation__icontains=search_term) | \
            Q(infirmary__icontains=search_term) | \
            Q(nurse__icontains=search_term)
        
        try:
            search_date = datetime.strptime(search_term, '%d/%m/%Y').date()
            search_filters |= Q(date__date=search_date)
        except ValueError:
            pass

        filters &= search_filters

    result = VisitorAppointment.objects.filter(filters).select_related('visitor')
    logger.info("Dados enviados para a interface do usuário.")
    return result

def get_all_appointments(date_begin, date_end, infirmaries, search_term):
    """
    Retrieve all appointments within a specified date range, infirmaries, and search term.
    This function consolidates appointments for students, employees, and visitors into a single list,
    each with relevant details, and sorts them by date in descending order.
    Args:
        date_begin (datetime): The start date for filtering appointments.
        date_end (datetime): The end date for filtering appointments.
        infirmaries (list): A list of infirmaries to filter the appointments.
        search_term (str): A search term to filter the appointments.
    Returns:
        list: A list of dictionaries, each representing an appointment with the following keys:
            - type (str): The type of the person (Estudante, Funcionário, Visitante).
            - name (str): The name of the person.
            - additional_info_label (str): The label for additional information (e.g., Turma, Departamento, Relacionamento).
            - additional_info (str): The additional information (e.g., class group, department, relationship).
            - age (int): The age of the person.
            - gender (str): The gender of the person.
            - date (datetime): The date of the appointment.
            - reason (str): The reason for the appointment.
            - treatment (str): The treatment provided during the appointment.
            - notes (str): Additional notes about the appointment.
            - infirmary (str): The infirmary where the appointment took place.
            - nurse (str): The nurse who attended the appointment.
            - current_class (str): The current class of the student (empty for employees and visitors).
    """
    logger.info("Iniciando get_all_appointments")
    student_appointments = get_student_appointments(date_begin, date_end, infirmaries, search_term)
    employee_appointments = get_employee_appointments(date_begin, date_end, infirmaries, search_term)
    visitor_appointments = get_visitor_appointments(date_begin, date_end, infirmaries, search_term)

    # Unificar os atendimentos em uma lista única
    all_appointments = []

    for appointment in student_appointments:
        all_appointments.append({
            'type': 'Estudante',
            'name': appointment.student.name,
            'additional_info_label': 'Turma',
            'additional_info': appointment.student.class_group.name if appointment.student.class_group else '',
            'age': appointment.student.age,
            'gender': appointment.student.gender,
            'date': appointment.date,
            'reason': appointment.reason,
            'treatment': appointment.treatment,
            'notes': appointment.notes,
            'infirmary': appointment.infirmary,
            'nurse': appointment.nurse,
            'current_class': appointment.current_class,
            'revaluation': appointment.revaluation, 
            'contact_parents' : appointment.contact_parents,
        })

    for appointment in employee_appointments:
        all_appointments.append({
            'type': 'Funcionário',
            'name': appointment.employee.name,
            'additional_info_label': 'Departamento',
            'additional_info': appointment.employee.department.name if appointment.employee.department else '',
            'age': appointment.employee.age,
            'gender': appointment.employee.gender,
            'date': appointment.date,
            'reason': appointment.reason,
            'treatment': appointment.treatment,
            'notes': appointment.notes,
            'infirmary': appointment.infirmary,
            'nurse': appointment.nurse,
            'current_class': '', 
            'revaluation': appointment.revaluation, 
            'contact_parents' : '', 
        })

    for appointment in visitor_appointments:
        all_appointments.append({
            'type': 'Visitante',
            'name': appointment.visitor.name,
            'additional_info_label': 'Relacionamento',
            'additional_info': appointment.visitor.relationship,
            'age': appointment.visitor.age,
            'gender': appointment.visitor.gender,
            'date': appointment.date,
            'reason': appointment.reason,
            'treatment': appointment.treatment,
            'notes': appointment.notes,
            'infirmary': appointment.infirmary,
            'nurse': appointment.nurse,
            'current_class': '', 
            'revaluation': appointment.revaluation, 
            'contact_parents' : '',
        })

    all_appointments.sort(key=lambda x: x['date'], reverse=True)
    logger.debug(f"All appointments: {all_appointments}")
    logger.info("Dados enviados para a interface do usuário.")
    return all_appointments

########### Charts Module ###########

def get_chart_data(request):
    """
    Aggregates appointment counts by infirmary and prepares data for a chart.
    This function aggregates the counts of appointments from three different models:
    StudentAppointment, EmployeeAppointment, and VisitorAppointment. It then prepares
    the data for a chart by categorizing the counts into predefined infirmary labels.
    Args:
        request: The HTTP request object.
    Returns:
        JsonResponse: A JSON response containing the labels and aggregated data for the chart.
    """
    logger.info("Iniciando get_chart_data")
    # Agregar as contagens por enfermaria
    labels = ["Infantil", "Fundamental", "Ensino Médio", "Externo"]
    infirmary_counts = {label: 0 for label in labels}

    # Agregar contagens do StudentAppointment
    student_counts = StudentAppointment.objects.values('infirmary').annotate(count=Count('id'))
    for item in student_counts:
        infirmary = item['infirmary']
        if infirmary in infirmary_counts:
            infirmary_counts[infirmary] += item['count']

    # Agregar contagens do EmployeeAppointment
    employee_counts = EmployeeAppointment.objects.values('infirmary').annotate(count=Count('id'))
    for item in employee_counts:
        infirmary = item['infirmary']
        if infirmary in infirmary_counts:
            infirmary_counts[infirmary] += item['count']

    # Agregar contagens do VisitorAppointment
    visitor_counts = VisitorAppointment.objects.values('infirmary').annotate(count=Count('id'))
    for item in visitor_counts:
        infirmary = item['infirmary']
        if infirmary in infirmary_counts:
            infirmary_counts[infirmary] += item['count']

    # Preparar os dados para o gráfico
    data = [infirmary_counts[label] for label in labels]

    logger.info("Dados enviados para a interface do usuário.")
    # Retornar os dados em formato JSON
    return JsonResponse({'labels': labels, 'data': data})
