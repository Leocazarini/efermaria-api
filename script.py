import os
import django

# Configurando o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')  
django.setup()

from patients.models import (Student, ClassGroup, StudentInfo, Employee, 
                             Department, EmployeeInfo, Visitor)
from patients.views import (create_students, create_student_info, create_class_group, 
                            create_employees, create_employee_info, create_department, 
                            )
from controller.crud import create_objects, update_info

def create_student_info_direct(data):
    """
    Função auxiliar para criar ou atualizar StudentInfo diretamente usando um dicionário de dados.
    """
    try:
        print("Creating or updating student info directly")
        print(f"Request data: {data}")

        if not isinstance(data, dict):
            print("Invalid data format, expected a dictionary")
            return {'status': 'error', 'message': 'Invalid data format, expected a dictionary'}
        
        student_id = data.get('student_id')
        allergies = data.get('allergies')
        patient_notes = data.get('patient_notes')

        if not student_id:
            print("Missing required field: student_id")
            return {'status': 'error', 'message': 'Missing required field: student_id'}

        print(f"Calling update_info for student_id: {student_id}")
        updated_info = update_info(StudentInfo, student_id, 'student_id', allergies, patient_notes)
        print(f"Student info updated successfully for student_id: {student_id}")

        return {'status': 'success', 'message': 'Student info updated successfully', 'data': updated_info.id}

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def create_employee_info_direct(data):
    """
    Função auxiliar para criar ou atualizar EmployeeInfo diretamente usando um dicionário de dados.
    """
    try:
        print("Creating or updating employee info directly")
        print(f"Request data: {data}")

        if not isinstance(data, dict):
            print("Invalid data format, expected a dictionary")
            return {'status': 'error', 'message': 'Invalid data format, expected a dictionary'}
        
        employee_id = data.get('employee_id')
        allergies = data.get('allergies')
        patient_notes = data.get('patient_notes')

        if not employee_id:
            print("Missing required field: employee_id")
            return {'status': 'error', 'message': 'Missing required field: employee_id'}

        print(f"Calling update_info for employee_id: {employee_id}")
        updated_info = update_info(EmployeeInfo, employee_id, 'employee_id', allergies, patient_notes)
        print(f"Employee info updated successfully for employee_id: {employee_id}")

        return {'status': 'success', 'message': 'Employee info updated successfully', 'data': updated_info.id}

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def create_visitors_direct(data_list):
    """
    Função auxiliar para criar visitantes diretamente usando uma lista de dicionários.
    """
    print("Creating visitors directly")
    if isinstance(data_list, list):
        for data in data_list:
            if not isinstance(data, dict):
                print("Invalid data format, expected a dictionary")
                return {'status': 'error', 'message': 'Invalid data format, expected a dictionary'}
            
            name = data.get('name')
            age = data.get('age')
            gender = data.get('gender')
            relationship = data.get('relationship')
            email = data.get('email')  
            allergies = data.get('allergies', '')
            patient_notes = data.get('patient_notes', '')

            if not name or not age or not gender or not relationship or not email:
                print("Missing required fields in visitor data")
                return {'status': 'error', 'message': 'Missing required fields'}

            visitor = Visitor.objects.create(
                name=name,
                age=age,
                gender=gender,
                relationship=relationship,
                email=email,  
                allergies=allergies,
                patient_notes=patient_notes
            )
            print(f"Visitor {visitor.name} created successfully with email {visitor.email}")
        return {'status': 'success', 'message': 'Visitors created successfully'}
    else:
        print("Invalid data format, expected a list of dictionaries")
        return {'status': 'error', 'message': 'Invalid data format, expected a list of dictionaries'}

def run_data_insertion():
    print("Starting data insertion script")

    # Dados para inserir no banco
    class_groups_data = [
        {'name': 'Turma A', 'segment': 'Primário', 'director': 'Carlos Silva'},
        {'name': 'Turma B', 'segment': 'Secundário', 'director': 'Maria Oliveira'}
    ]

    # Nomes realistas para estudantes
    student_names = [
        "Pedro Silva", "Ana Maria", "Carla Oliveira", "Lucas Fernandes", "Mariana Souza", 
        "João da Silva", "Luísa Costa", "Gabriel Rocha", "Beatriz Santos", "Felipe Araújo",
        "Sofia Lima", "Rafael Almeida", "Fernanda Duarte", "Mateus Mendes", "Isabela Reis", 
        "Thiago Cardoso", "Juliana Nogueira", "Leonardo Gonçalves", "Larissa Martins", 
        "Gustavo Barros", "Camila Fonseca", "Eduardo Carvalho", "Renata Borges", 
        "Vinícius Almeida", "Patrícia Teixeira", "Rodrigo Cavalcante", "Letícia Pinto", 
        "César Monteiro", "Bárbara Figueiredo", "Marcelo Ferreira"
    ]
    
    parent_names = [
        ("Carlos", "Ana"), ("Paulo", "Maria"), ("Roberto", "Clara"), ("Fernando", "Juliana"), 
        ("José", "Fernanda"), ("Bruno", "Patrícia"), ("Ricardo", "Renata"), ("Gustavo", "Helena"), 
        ("André", "Beatriz"), ("Sérgio", "Lúcia"), ("Fábio", "Cristina"), ("Miguel", "Bianca"), 
        ("Henrique", "Marina"), ("Alexandre", "Natália"), ("Danilo", "Carolina")
    ]

    students_data = [
        {'name': student_names[i], 'age': 10 + i % 10, 'gender': 'Masculino' if i % 2 == 0 else 'Feminino', 
         'registry': f'STU{100+i:03}', 'class_group_id': (i % 2) + 1, 'birth_date': f'201{i % 10}-01-01', 
         'father_name': parent_names[i % len(parent_names)][0], 
         'father_phone': '123456789', 'mother_name': parent_names[i % len(parent_names)][1], 
         'mother_phone': '987654321', 'email': f'{student_names[i].lower().replace(" ", ".")}@example.com'} 
         for i in range(30)  
    ]

    # Adicionando homônimos
    students_data[2]['name'] = 'Ana Maria Oliveira'  
    students_data[3]['name'] = 'Ana Maria Pereira'   
    students_data[4]['name'] = 'Ana Maria Costa'     
    
    # Dois alunos com o mesmo nome completo
    students_data[10]['name'] = 'João da Silva'
    students_data[11]['name'] = 'João da Silva'  
    
    student_info_data = [
        {'student_id': i+1, 'allergies': 'Amendoim' if i % 3 == 0 else '', 
         'patient_notes': 'Alergia leve' if i % 3 == 0 else ''} for i in range(30)
    ]

    department_names = ["Recursos Humanos", "TI", "Administração", "Educação", "Saúde"]

    departments_data = [{'name': department_names[i % len(department_names)], 'director': f"Diretor {i}"} for i in range(5)]

    employee_names = [
        "Carlos Eduardo", "Paula Mendes", "Rodrigo Silva", "Mariana Costa", "Tiago Ferreira", 
        "Fernanda Almeida", "José Santos", "Ana Paula", "Bruno Lima", "Claudia Rocha", 
        "Marcelo Teixeira", "Patricia Souza", "Rafael Lopes", "Juliana Araujo", "Pedro Martins", 
        "Larissa Rodrigues", "Diego Pires", "Gabriela Monteiro", "Vinicius Souza", "Monica Dias",
        "Fernando Meirelles", "Camila Borges", "Thiago Cardoso", "Renata Braga", "André Silva", 
        "Juliana Lima", "Lucas Moreira", "Isabel Farias", "Rafael Carvalho", "Sandra Freitas"
    ]

    employees_data = [
        {'name': employee_names[i], 'age': 25 + i % 10, 'gender': 'Masculino' if i % 2 == 0 else 'Feminino', 
         'registry': f'EMP{100+i:03}', 'department_id': (i % len(departments_data)) + 1, 'position': f'Cargo {i}', 
         'birth_date': f'198{i % 10}-01-01', 'email': f'{employee_names[i].lower().replace(" ", ".")}@example.com'} 
         for i in range(30)  
    ]

    employee_info_data = [
        {'employee_id': i+1, 'allergies': 'Poeira' if i % 3 == 0 else '', 
         'patient_notes': 'Evitar locais empoeirados' if i % 3 == 0 else ''} for i in range(30)
    ]

    visitor_names = [
        "Cláudio Alves", "Maria Eduarda", "Antônio Nunes", "Fernanda Oliveira", "Ricardo Gomes", 
        "Laura Campos", "João Lucas", "Beatriz Ramos", "Paulo Henrique", "Cecília Duarte", 
        "Marcos Aurélio", "Lívia Almeida", "Felipe Bastos", "Vanessa Carvalho", "Caio Augusto", 
        "Juliana Pereira", "Daniel Gonçalves", "Amanda Souza", "Bruno Machado", "Natalia Santos",
        "Rafael Costa", "Ana Cláudia", "Renato Silva", "Bianca Fernandes", "Leonardo Cunha", 
        "Raquel Monteiro", "Lucas Santos", "Marta Ribeiro", "Guilherme Boulos", "Tatiane Vieira"
    ]

    visitors_data = [
        {'name': visitor_names[i], 'age': 30 + i % 20, 'gender': 'Masculino' if i % 2 == 0 else 'Feminino', 
         'relationship': 'Parente', 
         'email': f'{visitor_names[i].lower().replace(" ", ".")}@example.com'} for i in range(30)  
    ]

    # Inserir dados usando as funções de criação
    create_class_group(class_groups_data)
    create_students(students_data)

    # Criar informações adicionais para os estudantes usando a função auxiliar
    for info in student_info_data:
        create_student_info_direct(info)

    create_department(departments_data)
    create_employees(employees_data)

    # Criar informações adicionais para os funcionários usando a função auxiliar
    for info in employee_info_data:
        create_employee_info_direct(info)

    # Usar a nova função para criar visitantes diretamente
    create_visitors_direct(visitors_data)

    print("Data insertion completed successfully")

# Executar o script
if __name__ == "__main__":
    run_data_insertion()