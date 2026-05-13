# PayOS — Backend + Frontend

A lightweight Flask REST API backend for the **PayOS** payroll management frontend.

---

## 📁 Files

```
payos_backend/
├── app.py            ← Flask backend (all API routes)
├── index.html        ← PayOS frontend (pre-integrated, no changes needed)
├── requirements.txt  ← Python dependencies
└── README.md
```

---

## 🚀 Run in 3 steps

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the backend
```bash
python app.py
```
> API running at **http://localhost:5000**

### 3. Open the frontend
Open `index.html` in your browser (double-click it, or use Live Server in VS Code).

The green **"API Connected"** indicator in the top bar confirms the frontend is talking to the backend.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check — frontend polls this every 10s |
| GET | `/api/payroll/summary` | KPI totals (gross, tax, SS, health, pension, net) |
| GET | `/api/employees` | List employees (`?type=Full-Time` `&q=search`) |
| POST | `/api/employees` | Add a new employee |
| PUT | `/api/employees/<id>` | Update employee |
| DELETE | `/api/employees/<id>` | Remove employee |
| GET | `/api/employees/<id>/payslip` | Full payslip breakdown |
| POST | `/api/payroll/run` | Process payroll (marks Pending → Paid) |

---

## 💡 Deduction rates

These match the labels shown in the frontend:

| Deduction | Rate |
|-----------|------|
| Income Tax | 20% of gross |
| Social Security | 6.5% of gross |
| Health Insurance | 3% of gross |
| Pension | 5% of gross |

---

## 🗄️ Upgrading to a real database

The backend uses an in-memory Python dict (data resets on restart). To persist data:

1. Add `flask-sqlalchemy` and `mysqlclient` to `requirements.txt`
2. Replace the `employees` dict with SQLAlchemy models
3. Point `SQLALCHEMY_DATABASE_URI` at your MySQL instance

The route logic stays identical — only the storage layer changes.
