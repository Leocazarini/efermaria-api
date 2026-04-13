# CLAUDE.md — Sistema de Enfermaria Escolar

Este arquivo descreve o projeto, a arquitetura atual, o estado de refatoração e as convenções que devem ser seguidas em todo o trabalho neste repositório.

---

## Visão Geral do Projeto

**School Infirmary System** é uma aplicação web para gestão de atendimentos de uma enfermaria escolar. Desenvolvida originalmente como sistema interno, está sendo refatorada em um case de portfólio de engenharia de software de alto nível.

- **Backend:** Python 3 + Django 5.0.7 + Django REST Framework
- **Banco de dados:** PostgreSQL 15 (via Docker)
- **Autenticação:** JWT nativo via `djangorestframework-simplejwt` (Google SSO foi removido)
- **Infraestrutura:** Docker + docker-compose
- **Testes:** pytest + pytest-django
- **Documentação de API (planejada):** drf-yasg (Swagger)

---

## Estrutura de Apps Django

```
enfermaria-dev/
├── setup/           # Configurações do projeto (settings, urls, wsgi, asgi)
├── authentication/  # Auth JWT — já totalmente modernizado com DRF
├── patients/        # Models de pacientes (Student, Employee, Visitor)
├── appointments/    # Models de atendimentos (StudentAppointment, etc.)
├── controller/      # LEGADO — lógica de negócio misturada com CRUD genérico
├── reports/         # Geração de relatórios
├── templates/       # HTML Django Templates — serão substituídos pelo frontend React
└── logs/            # Logs por app e módulo (FileHandler separado por contexto)
```

---

## Modelos Principais

### `patients/models.py`
| Model | Descrição |
|---|---|
| `ClassGroup` | Turma escolar com segmento e diretor |
| `Student` | Aluno com FK para ClassGroup e OneToOne para StudentInfo |
| `StudentInfo` | Alergias e notas clínicas do aluno |
| `Department` | Departamento com diretor |
| `Employee` | Funcionário com FK para Department e OneToOne para EmployeeInfo |
| `EmployeeInfo` | Alergias e notas clínicas do funcionário |
| `Visitor` | Visitante externo (sem FK — entidade autossuficiente) |

### `appointments/models.py`
| Model | Descrição |
|---|---|
| `StudentAppointment` | Atendimento de aluno — FK para Student |
| `EmployeeAppointment` | Atendimento de funcionário — FK para Employee |
| `VisitorAppointment` | Atendimento de visitante — FK para Visitor |

Todos os atendimentos têm: `infirmary`, `nurse`, `date`, `reason`, `treatment`, `notes`, `revaluation`, `created_at`, `updated_at`.

---

## Autenticação (já modernizado)

O app `authentication/` está completamente refatorado com DRF e JWT.

### Endpoints disponíveis (`/api/auth/`)
| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/auth/register/` | Criação de usuário |
| POST | `/api/auth/login/` | Login — retorna `access` + `refresh` tokens |
| POST | `/api/auth/token/refresh/` | Renova o access token |
| GET | `/api/auth/me/` | Perfil do usuário autenticado |
| POST | `/api/auth/change-password/` | Troca de senha autenticada |

### Configuração JWT (`setup/settings.py`)
- `ACCESS_TOKEN_LIFETIME`: 8 horas
- `REFRESH_TOKEN_LIFETIME`: 7 dias
- `ROTATE_REFRESH_TOKENS`: True
- Header: `Authorization: Bearer <token>`

---

## Estado Atual da Refatoração

O projeto está em transição arquitetural entre dois padrões:

### Padrão Legado (a ser eliminado)
```
patients/views.py  →  controller/crud.py  →  DB
```
- `controller/crud.py` é um módulo genérico com funções como `create_objects`, `get_object`, `get_by_id`, `update_object`, etc.
- As views atuais de `patients`, `appointments` e `reports` delegam tudo para esse módulo.
- As rotas ainda servem Django Templates HTML.
- **Este padrão deve ser destruído ao longo das Fases 2 e 3.**

### Padrão Alvo (a ser construído)
```
api_views.py  →  serializers.py  →  services.py  →  models.py  →  DB
```
Cada app terá sua própria camada estrita com responsabilidade única.

---

## Arquitetura Alvo por App

Ao refatorar `patients`, `appointments` e `reports`, cada um deve ter:

```
<app>/
├── models.py       # Apenas classes ORM — sem lógica de negócio
├── services.py     # NOVO — Lógica de negócio pura. Sem Request, sem Response HTTP.
├── serializers.py  # NOVO — Traduz Models para JSON e valida formato de dados.
├── api_views.py    # NOVO — Apenas trata HTTP: pega Request, chama Service, retorna Response.
└── urls.py         # Roteamento dos endpoints /api/v1/<app>/
```

### Regras de responsabilidade:
- **`models.py`**: Somente definição de campos e relações. Sem lógica.
- **`services.py`**: Regras de negócio (ex: não pode criar atendimento em data passada, verificar se aluno existe). Recebe dados Python, retorna dados Python. Nunca importa `Request` nem `Response`.
- **`serializers.py`**: Valida formato/tipo dos dados de entrada (DRF Serializer). Faz a ponte entre JSON e objetos Python/Django.
- **`api_views.py`**: Orquestra o fluxo HTTP — recebe Request → chama Serializer → passa para Service → retorna HTTP Response com status code correto.

---

## Roadmap de Implementação

### Fase 1 — Higienização e Setup (CONCLUÍDA)
- [x] Credenciais movidas para `.env` com `python-dotenv`
- [x] `ALLOWED_HOSTS` via variável de ambiente
- [x] IPs internos removidos
- [x] Google OAuth removido, substituído por JWT nativo
- [x] `Dockerfile` e `docker-compose.yml` criados
- [x] `pytest` e `pytest-django` configurados
- [x] `djangorestframework` e `djangorestframework-simplejwt` instalados
- [ ] `README.md` atualizado para portfólio

### Fase 2 — TDD e Camada de Serviços (PRÓXIMA)
- [ ] Escrever testes vermelhos em `patients/tests/test_services.py`
- [ ] Criar `patients/services.py` migrando lógica de `controller/crud.py`
- [ ] Fazer testes passarem (verde)
- [ ] Repetir para `appointments/` e `reports/`
- [ ] Deletar `controller/crud.py` quando se tornar obsoleto

### Fase 3 — REST API
- [ ] Criar `serializers.py` para todos os models
- [ ] Criar `api_views.py` para todos os apps (substituir `views.py`)
- [ ] Criar rotas `/api/v1/<app>/` em `urls.py`
- [ ] Testar com Swagger (drf-yasg) e testes de request

### Fase 4 — Frontend Mobile-First (React)
- [ ] Novo container Node com React (Vite)
- [ ] Integração JWT entre frontend e API
- [ ] Design mobile-first responsivo
- [ ] Container `frontend` no `docker-compose.yml` já reservado (porta 3000)

---

## Configuração de Ambiente

### Variáveis de Ambiente (`.env` baseado em `.env.example`)
```env
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=ENFERMARIA_DB
DB_USER=postgres
DB_PASSWORD=...
DB_HOST=127.0.0.1
DB_PORT=5432
```

### Subir o ambiente com Docker
```bash
docker-compose up --build
```

Serviços:
- `db`: PostgreSQL 15 na porta `5432`
- `api`: Django na porta `8000`
- `frontend`: Node 20 na porta `3000` (reservado para Fase 4)

### Rodar sem Docker (desenvolvimento local)
```bash
pip install -r requirements.txt
cp .env.example .env   # preencher os valores
python manage.py migrate
python manage.py runserver
```

---

## Testes

### Configuração (`pytest.ini`)
```ini
[pytest]
DJANGO_SETTINGS_MODULE = setup.settings
python_files = tests.py test_*.py *_tests.py
addopts = --nomigrations --reuse-db
```

### Rodar testes
```bash
pytest
```

### Convenção de localização dos testes
```
<app>/tests/
├── __init__.py
└── unit_tests/
    ├── __init__.py
    ├── tests_models.py
    └── test_services.py   # criar aqui na Fase 2
```

### Importante sobre testes
- `--nomigrations`: usa `syncdb` ao invés de rodar migrations — testes são mais rápidos.
- `--reuse-db`: reutiliza o banco de teste entre runs se o schema não mudou.
- Testes de `services.py` **não devem simular request HTTP** — testam lógica pura.

---

## Logging

Cada app tem seus próprios FileHandlers configurados em `setup/settings.py`. Os arquivos ficam em `logs/<app>/<module>.log`. O formato é:

```
%(asctime)s [%(levelname)s] %(name)s: %(message)s
```

Loggers disponíveis: `patients.views`, `appointments.views`, `controller.crud`, `controller.views`, `reports.views`.

Para usar em um novo módulo:
```python
import logging
logger = logging.getLogger('<app>.<module>')
```

---

## Convenções de Código

- Idioma do código: **Inglês** (nomes de variáveis, funções, classes, comentários técnicos).
- Idioma dos logs e mensagens de usuário: **Português**.
- Nenhuma lógica de negócio nos `views` / `api_views` — apenas orquestração HTTP.
- Nenhuma lógica de negócio nos `models` — apenas campos e relações ORM.
- `services.py` nunca importa `django.http`, `rest_framework.request`, nem `rest_framework.response`.
- Todos os endpoints REST devem usar prefixo `/api/v1/`.
- Todas as views REST herdam de `APIView` (DRF) — não usar `@csrf_exempt` nas novas views.

---

## Dependências Principais

| Pacote | Versão | Uso |
|---|---|---|
| Django | 5.0.7 | Framework web |
| djangorestframework | 3.15.2 | REST API |
| djangorestframework-simplejwt | 5.3.1 | Autenticação JWT |
| drf-yasg | 1.21.7 | Swagger (documentação) |
| psycopg2 | 2.9.10 | Driver PostgreSQL |
| python-dotenv | 1.0.1 | Variáveis de ambiente |
| gunicorn | 23.0.0 | Servidor WSGI produção |
| pytest | 8.3.2 | Framework de testes |
| pytest-django | 4.8.0 | Integração Django + pytest |
