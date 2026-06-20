# 🏥 Rehab Backend - Advanced Healthcare Management System

> **Enterprise-Grade Rehabilitation Center Management Platform**
> 
> A powerful, scalable backend solution for modern healthcare facilities with real-time analytics and comprehensive patient management capabilities.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**Rehab Backend** is a sophisticated Django-based management system designed for rehabilitation centers, healthcare facilities, and wellness clinics. It streamlines patient care coordination, payment processing, and financial analytics with an intuitive, role-based architecture.

**Perfect for:**
- Rehabilitation centers & therapy clinics
- Healthcare facility management
- Patient data administration
- Financial reporting & billing systems
- Medical practice optimization

---

## ✨ Key Features

### 🔐 Advanced Authentication & Authorization
- **Multi-tier access control** with customizable roles (Admin, Staff, Clinician, Receptionist)
- **Secure JWT/session-based authentication** with password hashing
- **Granular permission management** for different user roles
- **Activity logging** for compliance and audit trails

### 👥 Comprehensive Patient Management
- **Full CRUD operations** for patient records
- **Detailed patient profiles** including medical history, contact information, and treatment notes
- **Treatment plan tracking** with progress monitoring
- **Appointment scheduling** and management
- **Medical document storage** and retrieval

### 💳 Sophisticated Payment & Billing System
- **Flexible payment tracking** (weekly, monthly, quarterly, custom periods)
- **Multiple payment method support** (cash, card, online transfer, insurance)
- **Automated invoice generation**
- **Payment status management** (pending, completed, overdue)
- **Refund processing** and transaction history
- **Tax calculation** and compliance reporting

### 📊 Advanced Financial Analytics & Visualization
- **Interactive charts** powered by Chart.js
- **Real-time revenue dashboards** with key performance indicators
- **Payment distribution analysis** (by type, method, and time period)
- **Monthly income trends** with comparative analysis
- **Expense tracking** and profit margin calculations
- **Custom report generation** with exportable formats (PDF, Excel)
- **Predictive analytics** for financial forecasting

### 📱 RESTful API Architecture
- **Clean, well-documented REST endpoints**
- **JSON request/response format**
- **Pagination and filtering** support
- **Rate limiting** and DDoS protection
- **API versioning** for backward compatibility

### 🗄️ Robust Database Management
- **PostgreSQL** for reliable data persistence
- **ORM-based data models** with Django ORM
- **Automatic migrations** and schema management
- **Data validation** and integrity checks
- **Backup & recovery** procedures

---

## 🛠️ Technology Stack

| Category | Technologies |
|----------|--------------|
| **Backend Framework** | Django 3.x/4.x (Python) |
| **Database** | PostgreSQL 12+ |
| **Frontend Layer** | HTML5, CSS3, JavaScript (ES6+) |
| **Data Visualization** | Chart.js, Matplotlib |
| **Authentication** | JWT / Django Session Auth |
| **API Documentation** | Django REST Framework |
| **Testing** | Pytest, Django Test Suite |
| **Deployment** | Docker, Gunicorn, Nginx |

**Languages Distribution:**
- Python: 41.2% (Backend Logic)
- HTML: 39.3% (Frontend Templates)
- JavaScript: 10.3% (Interactive Features)
- CSS: 9.2% (Styling & UX)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip & virtualenv
- Git

### Installation Steps

**1️⃣ Clone the Repository**
```bash
git clone https://github.com/Davoadeivai/rehab_backend.git
cd rehab_backend
```

**2️⃣ Create & Activate Virtual Environment**
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

**3️⃣ Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**4️⃣ Configure Environment Variables**
```bash
# Create .env file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Required Environment Variables:**
```
DEBUG=False
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/rehab_db
ALLOWED_HOSTS=localhost,127.0.0.1
```

**5️⃣ Database Setup**
```bash
# Run migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json
```

**6️⃣ Run Development Server**
```bash
python manage.py runserver

# Server will be available at http://127.0.0.1:8000
# Admin panel: http://127.0.0.1:8000/admin
```

---

## Project Structure

```
rehab_backend/
├── manage.py                 # Django management script
├── requirements.txt          # Project dependencies
├── .env.example             # Environment variables template
├── README.md                # This file
├── config/                  # Django settings & configuration
│   ├── settings.py         # Main settings
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI configuration
├── apps/                    # Django applications
│   ├── patients/           # Patient management
│   ├── payments/           # Payment tracking
│   ├── users/              # User authentication
│   ├── reports/            # Financial reports
│   └── api/                # REST API endpoints
├── static/                 # Static files (CSS, JS, images)
├── templates/              # HTML templates
├── media/                  # User-uploaded files
└── tests/                  # Unit & integration tests
```

---

## 📡 API Documentation

### Core Endpoints

**Authentication**
```http
POST   /api/auth/login          - User login
POST   /api/auth/logout         - User logout
POST   /api/auth/refresh        - Refresh token
POST   /api/auth/register       - Register new user
```

**Patients**
```http
GET    /api/patients/           - List all patients
POST   /api/patients/           - Create new patient
GET    /api/patients/<id>/      - Get patient details
PUT    /api/patients/<id>/      - Update patient
DELETE /api/patients/<id>/      - Delete patient
```

**Payments**
```http
GET    /api/payments/           - List payments
POST   /api/payments/           - Record payment
GET    /api/payments/<id>/      - Get payment details
PUT    /api/payments/<id>/      - Update payment
GET    /api/payments/report/    - Generate payment report
```

**Financial Reports**
```http
GET    /api/reports/dashboard/  - Financial dashboard
GET    /api/reports/income/     - Monthly income report
GET    /api/reports/distribution/ - Payment distribution
GET    /api/reports/export/     - Export reports (PDF/Excel)
```

---

## ⚙️ Configuration

### Database Configuration
Update `config/settings.py` with your PostgreSQL credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rehab_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Email Configuration (for notifications)
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
```

---

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.patients

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

---

## 📦 Deployment

### Production Deployment with Docker
```bash
# Build Docker image
docker build -t rehab_backend:latest .

# Run container
docker run -p 8000:8000 --env-file .env rehab_backend:latest
```

### Nginx Configuration
Refer to `nginx.conf` in the repository for production server setup.

---

## 🤝 Contributing

We welcome contributions! Here's how to get involved:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Coding Standards
- Follow PEP 8 style guide
- Add docstrings to all functions
- Write unit tests for new features
- Update documentation as needed

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for complete details.

---

## 🆘 Support & Contact

- **Issues & Bug Reports:** [GitHub Issues](https://github.com/Davoadeivai/rehab_backend/issues)
- **Documentation:** Check the [Wiki](https://github.com/Davoadeivai/rehab_backend/wiki)
- **Email Support:** [contact@yourmail.com]

---

## 🌟 Acknowledgments

- Django community for the excellent framework
- PostgreSQL for reliable database management
- Chart.js for beautiful data visualization
- All contributors and supporters

---

**Made with ❤️ for healthcare professionals**

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Django](https://img.shields.io/badge/Django-4.0+-green?logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-lightblue?logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
