# 🏦 Payroll Management System — Django Backend

A production-ready REST API for managing employee payroll, built with **Django + MySQL + JWT Auth**.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- MySQL 8.0+

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your MySQL credentials
```

### 4. Create MySQL Database
```sql
CREATE DATABASE payroll_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 7. Start Server
```bash
python manage.py runserver
```

API available at: `http://localhost:8000/api/`
Admin panel: `http://localhost:8000/admin/`

---

## 📦 Project Structure

```
payroll_system/          ← Django project config & settings
authentication/          ← Custom User model, JWT auth, roles
employees/               ← Employee profiles, departments, salary grades
payroll/                 ← Payroll periods, payslips, tax calculator
leaves/                  ← Leave types, requests, balances
```

---

## 🔐 Authentication & Roles

| Role             | Permissions                                      |
|------------------|--------------------------------------------------|
| `admin`          | Full access                                      |
| `hr_manager`     | Employee mgmt, leave approval, payroll approval  |
| `payroll_officer`| Generate payroll, manage deductions              |
| `employee`       | View own profile, payslips, submit leave         |

### Login
```http
POST /api/auth/login/
Content-Type: application/json

{ "email": "user@example.com", "password": "secret" }
```
Returns `access` + `refresh` JWT tokens.

All subsequent requests require:
```
Authorization: Bearer <access_token>
```

---

## 📡 API Endpoints

### 🔑 Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Login, get JWT tokens |
| POST | `/api/auth/logout/` | Logout (blacklist refresh token) |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET/PUT | `/api/auth/profile/` | View/update own profile |
| PUT | `/api/auth/change-password/` | Change password |
| GET/POST | `/api/auth/users/` | List/create users (admin only) |

### 👥 Employees
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/employees/` | List/create employees |
| GET | `/api/employees/me/` | My profile |
| GET | `/api/employees/stats/` | Headcount stats |
| GET/PUT/PATCH | `/api/employees/<id>/` | Employee detail |
| GET/PUT | `/api/employees/<id>/salary/` | Salary grade |
| GET/POST | `/api/employees/departments/` | Departments |
| GET/POST | `/api/employees/job-titles/` | Job titles |

### 💰 Payroll
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/payroll/periods/` | Payroll periods |
| POST | `/api/payroll/periods/<id>/generate/` | Generate payslips for all employees |
| POST | `/api/payroll/periods/<id>/approve/` | Approve payroll |
| POST | `/api/payroll/periods/<id>/mark-paid/` | Mark as paid |
| GET | `/api/payroll/periods/<id>/summary/` | Payroll summary |
| GET | `/api/payroll/payslips/` | List payslips (filtered by role) |
| GET | `/api/payroll/my-payslips/` | My payslips |
| GET/POST | `/api/payroll/deductions/` | Deduction types |
| GET/POST | `/api/payroll/employees/<id>/deductions/` | Employee deductions |

### 🏖️ Leaves
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/leaves/types/` | Leave types |
| GET/POST | `/api/leaves/requests/` | Submit/list leave requests |
| DELETE | `/api/leaves/requests/<id>/` | Cancel leave request |
| POST | `/api/leaves/requests/<id>/review/` | Approve/reject leave |
| GET | `/api/leaves/balances/` | Leave balances (HR sees all) |
| GET | `/api/leaves/my-balances/` | My leave balances |

---

## 🧮 Tax Calculation (Ghana PAYE)

Payslips are automatically calculated using **Ghana Revenue Authority (GRA)** tax bands:

| Annual Income (GHS) | Tax Rate |
|---------------------|----------|
| 0 – 4,380           | 0%       |
| 4,381 – 5,940       | 5%       |
| 5,941 – 18,000      | 10%      |
| 18,001 – 42,000     | 17.5%    |
| 42,001 – 144,000    | 25%      |
| Above 144,000       | 30%      |

**SSNIT:** 5.5% employee / 13% employer (on basic salary)

---

## 🔄 Payroll Workflow

```
1. Create Payroll Period (draft)
2. POST /periods/<id>/generate/   → Calculates all payslips
3. Review payslips
4. POST /periods/<id>/approve/    → HR Manager approves
5. POST /periods/<id>/mark-paid/  → Mark as disbursed
```

---

## ⚙️ Production Deployment

```bash
# Set environment variables
export DEBUG=False
export SECRET_KEY=<strong-random-key>
export DB_PASSWORD=<secure-password>

# Collect static files
python manage.py collectstatic

# Use Gunicorn
gunicorn payroll_system.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 🗄️ Database Schema (Key Tables)

- `auth_users` — Custom user accounts with roles
- `departments` — Company departments
- `employees` — Employee profiles & employment details
- `salary_grades` — Per-employee salary structure
- `payroll_periods` — Monthly payroll runs
- `payslips` — Individual payslip records
- `deductions` — Configurable deduction types (SSNIT, loans, etc.)
- `leave_types` — Annual leave, sick leave, etc.
- `leave_requests` — Employee leave applications
- `leave_balances` — Days used/remaining per employee per year
