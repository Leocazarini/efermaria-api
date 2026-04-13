<div align="center">
  <h1>🏥 School Infirmary System</h1>
  <p><b>An advanced portfolio study on Modernization, Refactoring, and Architecture</b></p>

  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python" alt="Python Badge" />
  <img src="https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django" alt="Django Badge" />
  <img src="https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker" alt="Docker Badge" />
  <img src="https://img.shields.io/badge/PostgreSQL-Ready-316192?style=for-the-badge&logo=postgresql" alt="Postgres Badge" />
</div>

<br>

## 📖 About The Project

This project was initially developed as a bespoke, customized management solution for a specific institution. Originally built as a standard, monolithic Django application with HTML templates, it served its purpose by replacing spreadsheets and manual paper trails for four distinct school infirmaries. 

**However, the goal has evolved.** This repository now serves as a **Case Study in Software Engineering**. The primary objective is to take a functional legacy monolithic system and refactor it into an industry-standard, scalable, and modern application.

### The Transformation Journey:
- **Generalization:** Stripped out all hardcoded institutional data, private IP bindings, and confidential secrets, transforming the codebase into an open-source template.
- **Architectural Shift:** Moving away from classic "Fat Controllers" (views) into a **Domain-Driven Service Layer** (`services.py`).
- **Headless API:** The server-rendered HTML UI is being completely dismantled and replaced by a pure RESTful API utilizing Django Rest Framework (DRF) and Swagger for documentation.
- **Modern UI:** Introduction of a separate, Mobile-First frontend built with React/Next.js to consume the API securely.
- **DevOps:** Fully containerized using Docker and Docker Compose (Postgres, Django API, Frontend).
- **Test-Driven:** Introducing `pytest` for rigorous unit testing on the new service layers.

---

## ✨ Core Features

- **Patient Management:** Comprehensive CRUD operations for student and staff health records.
- **Appointment Tracking:** Logging daily infirmary visits, symptom descriptions, and treatments provided.
- **Medical Records:** Centralized view of a patient's complete history, including allergies, chronic conditions, and clinical observations.
- **Analytics & Reporting:** Dynamic report generation across multiple infirmaries.

---

## 🛠️ Stack Overview

### 🔹 Infrastructure & DevOps
- Docker & Docker Compose
- PostgreSQL 15

### 🔹 Backend API (Refactoring Phase)
- Python 3.12
- Django 5
- Django Rest Framework (DRF)
- drf-yasg (Swagger)
- Pytest (TDD)

### 🔹 Frontend (Upcoming Phase)
- Node.js (React / Next.js)
- JWT Authentication
- TailwindCSS (Mobile-First approach)

---

## 🚀 Getting Started (Local Development)

Thanks to Docker, getting the project up and running is frictionless.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Leocazarini/efermaria-api.git
   cd enfermaria-api/enfermaria-dev
   ```

2. **Environment Variables:**
   Create a `.env` file based on the example structure. Be sure to fill out the blank keys:
   ```bash
   cp .env.example .env
   ```

3. **Spin up the containers:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - The API server will be accessible natively at `http://localhost:8000/`

---
> *Status: Development is ongoing. Currently executing Phase 1 & 2 (Dockerization, TDD, and Domain Services).*
