<div align="center">
  <h1>Sistema de Enfermaria Escolar</h1>
  <p><b>Sistema de gestão de enfermarias escolares — do legado à arquitetura moderna</b></p>

  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python" alt="Python Badge" />
  <img src="https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django" alt="Django Badge" />
  <img src="https://img.shields.io/badge/React-Vite-61DAFB?style=for-the-badge&logo=react" alt="React Badge" />
  <img src="https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker" alt="Docker Badge" />
  <img src="https://img.shields.io/badge/PostgreSQL-15-316192?style=for-the-badge&logo=postgresql" alt="Postgres Badge" />
</div>

<br>

## Sobre o Projeto

Este sistema foi criado originalmente para suprir uma demanda real de uma empresa em que trabalhei há dois anos. Na época, quatro enfermarias escolares controlavam atendimentos manualmente, em planilhas e registros em papel — um processo lento, disperso e propenso a erros. O sistema nasceu como uma solução interna em Django monolítico com templates HTML, e resolveu o problema de forma funcional desde o primeiro dia de uso.

Com o tempo, o código envelheceu. Ele funcionava, mas carregava o peso de uma arquitetura sem camadas definidas, lógica espalhada nos `views`, credenciais hardcoded e ausência total de testes. A decisão foi refatorar do zero: manter o propósito original — gerenciar enfermarias escolares — mas reconstruir a base com as práticas e ferramentas que o projeto merecia.

O resultado é este repositório: uma aplicação moderna, com API REST documentada, frontend React mobile-first, autenticação JWT, testes automatizados e infraestrutura containerizada.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12 + Django 5.0.7 + Django REST Framework |
| Autenticação | JWT via `djangorestframework-simplejwt` |
| Frontend | React 18 + Vite + TailwindCSS |
| Banco de Dados | PostgreSQL 15 |
| Infraestrutura | Docker + Docker Compose |
| Testes | pytest + pytest-django |
| Documentação de API | drf-spectacular (Swagger UI + ReDoc) |

---

## Funcionalidades

### Gestão de Pacientes

O sistema suporta três tipos de pacientes:

- **Alunos** — com matrícula, turma e ficha clínica (alergias e observações médicas)
- **Funcionários** — com matrícula, departamento e ficha clínica
- **Visitantes** — cadastrados diretamente no momento do atendimento, sem vínculo institucional

A busca de pacientes é feita por nome (com resultado paginado) ou diretamente por matrícula. A criação de alunos e funcionários ocorre exclusivamente via importação de arquivo CSV/XLSX, refletindo o fluxo real de sistemas institucionais.

### Registro de Atendimentos

Cada atendimento registra: enfermaria, enfermeira responsável, data, motivo da visita, tratamento realizado e observações. O sistema suporta o campo de **reavaliação** — quando um paciente precisa de acompanhamento posterior, o atendimento é marcado com uma data de retorno e permanece em aberto até ser resolvido.

A tela de **Reavaliações Pendentes** consolida todos os casos em aberto em uma única visualização, independente do tipo de paciente.

### Histórico do Paciente

O histórico completo de atendimentos de qualquer paciente é acessível a partir do seu perfil, incluindo data, motivo, tratamento e status de reavaliação de cada visita.

### Relatórios e Estatísticas

- **Relatório por período:** lista todos os atendimentos em um intervalo de datas, com filtros por enfermaria e busca por nome de paciente
- **Estatísticas gerais:** total de atendimentos no ano e no dia atual, ranking de atendimentos por enfermeira
- **Estatísticas por enfermaria:** visão isolada de uma unidade específica

### Importação de Dados

Administradores podem importar listas de alunos e funcionários via arquivos `.csv` ou `.xlsx`. O sistema detecta automaticamente o tipo de entidade pelo conteúdo do arquivo e processa registros em lote, criando ou atualizando conforme necessário.

### Gestão de Usuários (Administradores)

O fluxo de usuários é controlado: novos cadastros ficam pendentes de aprovação por um administrador antes de acessar o sistema. A tela de gestão permite aprovar, desativar, reativar e remover usuários, além de conceder ou revogar permissões de staff.

---

## Arquitetura

O código segue uma arquitetura de camadas estrita, sem lógica de negócio fora do lugar:

```
api_views.py  →  serializers.py  →  services.py  →  models.py  →  DB
```

- **`models.py`** — apenas definição de campos e relações ORM
- **`services.py`** — toda a lógica de negócio; nunca importa `Request` nem `Response`
- **`serializers.py`** — validação e tradução entre JSON e objetos Python
- **`api_views.py`** — orquestração HTTP pura: recebe, valida, chama service, responde

---

## Como Rodar

### Com Docker (recomendado)

```bash
git clone https://github.com/Leocazarini/efermaria-api.git
cd efermaria-api/enfermaria-dev
cp .env.example .env   # preencher os valores
docker-compose up --build
```

Serviços disponíveis:
- API Django: `http://localhost:8000`
- Frontend React: `http://localhost:3000`
- Swagger UI: `http://localhost:8000/api/docs/`

### Sem Docker (desenvolvimento local)

```bash
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

### Variáveis de Ambiente

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

---

## Testes

```bash
pytest
```

Os testes cobrem serviços (unitários) e endpoints (integração), organizados por app em `<app>/tests/unit_tests/` e `<app>/tests/integration_tests/`.

---

## Documentação da API

| URL | Descrição |
|---|---|
| `/api/docs/` | Swagger UI interativo |
| `/api/redoc/` | ReDoc |
| `/api/schema/` | Schema OpenAPI (JSON/YAML) |
