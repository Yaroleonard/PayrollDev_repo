"""
PayOS — Payroll System Backend
Flask REST API with SQLite database
Run: python app.py
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

# ─── App Setup ────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="static")
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), "payroll.db")

# ─── Deduction rates ──────────────────────────────────────────────────────────
TAX_RATE     = 0.20
SS_RATE      = 0.065
HEALTH_RATE  = 0.03
PENSION_RATE = 0.05


# ─── DB Helpers ───────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS employees (
        id          TEXT PRIMARY KEY,
        name        TEXT NOT NULL,
        department  TEXT NOT NULL,
        type        TEXT NOT NULL CHECK(type IN ('Full-Time','Part-Time','Contract')),
        gross       REAL NOT NULL CHECK(gross > 0),
        status      TEXT NOT NULL DEFAULT 'Pending'
                        CHECK(status IN ('Paid','Pending','On Hold')),
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS payroll_runs (
        run_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        period      TEXT NOT NULL,
        run_at      TEXT NOT NULL DEFAULT (datetime('now')),
        total_gross REAL NOT NULL,
        total_net   REAL NOT NULL,
        emp_count   INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS payslips (
        slip_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id      INTEGER NOT NULL REFERENCES payroll_runs(run_id),
        emp_id      TEXT NOT NULL REFERENCES employees(id),
        gross       REAL NOT NULL,
        tax         REAL NOT NULL,
        ss          REAL NOT NULL,
        health      REAL NOT NULL,
        pension     REAL NOT NULL,
        net         REAL NOT NULL,
        generated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """)

    # Seed sample data if table is empty
    if cur.execute("SELECT COUNT(*) FROM employees").fetchone()[0] == 0:
        seed = [
            ("EMP-001","Alice Johnson",  "Engineering","Full-Time", 7800, "Paid"),
            ("EMP-002","Marcus Chen",    "Marketing",  "Full-Time", 6200, "Pending"),
            ("EMP-003","Priya Sharma",   "Finance",    "Full-Time", 8500, "Paid"),
            ("EMP-004","James Osei",     "HR",         "Part-Time", 3200, "Paid"),
            ("EMP-005","Sofia Torres",   "Design",     "Contract",  5500, "On Hold"),
            ("EMP-006","Liam Patel",     "Engineering","Full-Time", 9200, "Pending"),
            ("EMP-007","Nana Ama",       "Operations", "Full-Time", 5900, "Paid"),
            ("EMP-008","David Kim",      "Finance",    "Contract",  7100, "Paid"),
        ]
        cur.executemany(
            "INSERT INTO employees (id,name,department,type,gross,status) VALUES (?,?,?,?,?,?)",
            seed
        )

    conn.commit()
    conn.close()


def calc_deductions(gross: float) -> dict:
    tax     = round(gross * TAX_RATE, 2)
    ss      = round(gross * SS_RATE, 2)
    health  = round(gross * HEALTH_RATE, 2)
    pension = round(gross * PENSION_RATE, 2)
    total   = round(tax + ss + health + pension, 2)
    net     = round(gross - total, 2)
    return {"tax": tax, "ss": ss, "health": health,
            "pension": pension, "total": total, "net": net}


def row_to_emp(row) -> dict:
    d = calc_deductions(row["gross"])
    return {
        "id":         row["id"],
        "name":       row["name"],
        "department": row["department"],
        "type":       row["type"],
        "gross":      row["gross"],
        "status":     row["status"],
        "created_at": row["created_at"],
        "deductions": d,
    }


def next_emp_id(cur) -> str:
    row = cur.execute(
        "SELECT id FROM employees ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if not row:
        return "EMP-001"
    try:
        num = int(row["id"].split("-")[1]) + 1
        return f"EMP-{num:03d}"
    except (IndexError, ValueError):
        return "EMP-001"


# ─── Routes ───────────────────────────────────────────────────────────────────

# Serve the frontend
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ── Employees ──────────────────────────────────────────────────────────────────
@app.route("/api/employees", methods=["GET"])
def list_employees():
    dept    = request.args.get("dept")
    emp_type= request.args.get("type")
    status  = request.args.get("status")
    q       = request.args.get("q", "").lower()

    conn = get_db()
    rows = conn.execute("SELECT * FROM employees ORDER BY created_at DESC").fetchall()
    conn.close()

    emps = [row_to_emp(r) for r in rows]

    if dept:
        emps = [e for e in emps if e["department"] == dept]
    if emp_type:
        emps = [e for e in emps if e["type"] == emp_type]
    if status:
        emps = [e for e in emps if e["status"] == status]
    if q:
        emps = [e for e in emps
                if q in e["name"].lower() or q in e["id"].lower()
                or q in e["department"].lower()]

    return jsonify({"employees": emps, "count": len(emps)})


@app.route("/api/employees", methods=["POST"])
def create_employee():
    data = request.get_json(force=True)
    required = ("name", "department", "type", "gross")
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    valid_types   = ("Full-Time", "Part-Time", "Contract")
    valid_statuses = ("Paid", "Pending", "On Hold")

    if data["type"] not in valid_types:
        return jsonify({"error": f"type must be one of {valid_types}"}), 400

    status = data.get("status", "Pending")
    if status not in valid_statuses:
        return jsonify({"error": f"status must be one of {valid_statuses}"}), 400

    try:
        gross = float(data["gross"])
        if gross <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "gross must be a positive number"}), 400

    conn = get_db()
    cur  = conn.cursor()
    emp_id = data.get("id") or next_emp_id(cur)

    if cur.execute("SELECT 1 FROM employees WHERE id=?", (emp_id,)).fetchone():
        conn.close()
        return jsonify({"error": f"Employee ID {emp_id} already exists"}), 409

    cur.execute(
        "INSERT INTO employees (id,name,department,type,gross,status) VALUES (?,?,?,?,?,?)",
        (emp_id, data["name"].strip(), data["department"], data["type"], gross, status)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM employees WHERE id=?", (emp_id,)).fetchone()
    conn.close()
    return jsonify(row_to_emp(row)), 201


@app.route("/api/employees/<emp_id>", methods=["GET"])
def get_employee(emp_id):
    conn = get_db()
    row  = conn.execute("SELECT * FROM employees WHERE id=?", (emp_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify(row_to_emp(row))


@app.route("/api/employees/<emp_id>", methods=["PUT"])
def update_employee(emp_id):
    conn = get_db()
    row  = conn.execute("SELECT * FROM employees WHERE id=?", (emp_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Employee not found"}), 404

    data = request.get_json(force=True)
    fields, values = [], []

    if "name" in data:
        fields.append("name=?"); values.append(data["name"].strip())
    if "department" in data:
        fields.append("department=?"); values.append(data["department"])
    if "type" in data:
        if data["type"] not in ("Full-Time","Part-Time","Contract"):
            conn.close()
            return jsonify({"error": "Invalid type"}), 400
        fields.append("type=?"); values.append(data["type"])
    if "gross" in data:
        try:
            g = float(data["gross"])
            if g <= 0: raise ValueError
        except (TypeError, ValueError):
            conn.close()
            return jsonify({"error": "gross must be a positive number"}), 400
        fields.append("gross=?"); values.append(g)
    if "status" in data:
        if data["status"] not in ("Paid","Pending","On Hold"):
            conn.close()
            return jsonify({"error": "Invalid status"}), 400
        fields.append("status=?"); values.append(data["status"])

    if not fields:
        conn.close()
        return jsonify({"error": "No valid fields to update"}), 400

    values.append(emp_id)
    conn.execute(f"UPDATE employees SET {', '.join(fields)} WHERE id=?", values)
    conn.commit()
    row = conn.execute("SELECT * FROM employees WHERE id=?", (emp_id,)).fetchone()
    conn.close()
    return jsonify(row_to_emp(row))


@app.route("/api/employees/<emp_id>", methods=["DELETE"])
def delete_employee(emp_id):
    conn = get_db()
    row  = conn.execute("SELECT * FROM employees WHERE id=?", (emp_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Employee not found"}), 404
    conn.execute("DELETE FROM employees WHERE id=?", (emp_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Employee {emp_id} deleted"})


# ── Payroll Summary ─────────────────────────────────────────────────────────────
@app.route("/api/payroll/summary", methods=["GET"])
def payroll_summary():
    conn = get_db()
    rows = conn.execute("SELECT * FROM employees").fetchall()
    conn.close()

    gross_total = sum(r["gross"] for r in rows)
    tax_total   = sum(r["gross"] * TAX_RATE     for r in rows)
    ss_total    = sum(r["gross"] * SS_RATE      for r in rows)
    health_total= sum(r["gross"] * HEALTH_RATE  for r in rows)
    pension_total=sum(r["gross"] * PENSION_RATE for r in rows)
    deduct_total= tax_total + ss_total + health_total + pension_total
    net_total   = gross_total - deduct_total

    return jsonify({
        "period":         "May 2025",
        "employee_count": len(rows),
        "gross":          round(gross_total, 2),
        "tax":            round(tax_total, 2),
        "social_security":round(ss_total, 2),
        "health":         round(health_total, 2),
        "pension":        round(pension_total, 2),
        "total_deductions": round(deduct_total, 2),
        "net":            round(net_total, 2),
    })


# ── Run Payroll ─────────────────────────────────────────────────────────────────
@app.route("/api/payroll/run", methods=["POST"])
def run_payroll():
    period = request.get_json(force=True).get("period", "May 2025")

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM employees WHERE status='Pending'"
    ).fetchall()

    if not rows:
        conn.close()
        return jsonify({"message": "No pending employees to process", "processed": 0})

    gross_total = sum(r["gross"] for r in rows)
    deduct_total= sum(calc_deductions(r["gross"])["total"] for r in rows)
    net_total   = gross_total - deduct_total

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO payroll_runs (period, total_gross, total_net, emp_count) VALUES (?,?,?,?)",
        (period, round(gross_total,2), round(net_total,2), len(rows))
    )
    run_id = cur.lastrowid

    for r in rows:
        d = calc_deductions(r["gross"])
        cur.execute(
            "INSERT INTO payslips (run_id,emp_id,gross,tax,ss,health,pension,net) VALUES (?,?,?,?,?,?,?,?)",
            (run_id, r["id"], r["gross"], d["tax"], d["ss"], d["health"], d["pension"], d["net"])
        )

    cur.execute("UPDATE employees SET status='Paid' WHERE status='Pending'")
    conn.commit()
    conn.close()

    return jsonify({
        "message":     f"Payroll processed for {len(rows)} employees",
        "run_id":      run_id,
        "period":      period,
        "processed":   len(rows),
        "total_gross": round(gross_total, 2),
        "total_net":   round(net_total, 2),
    })


# ── Payslip ─────────────────────────────────────────────────────────────────────
@app.route("/api/employees/<emp_id>/payslip", methods=["GET"])
def get_payslip(emp_id):
    conn = get_db()
    row  = conn.execute("SELECT * FROM employees WHERE id=?", (emp_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Employee not found"}), 404

    d = calc_deductions(row["gross"])
    return jsonify({
        "employee": row_to_emp(row),
        "period":   "May 2025",
        "earnings": {
            "basic_salary": row["gross"],
            "overtime":     0,
            "allowances":   0,
            "total":        row["gross"],
        },
        "deductions": {
            "income_tax":      d["tax"],
            "social_security": d["ss"],
            "health_insurance":d["health"],
            "pension":         d["pension"],
            "total":           d["total"],
        },
        "net_pay": d["net"],
    })


# ── Payroll History ─────────────────────────────────────────────────────────────
@app.route("/api/payroll/history", methods=["GET"])
def payroll_history():
    conn = get_db()
    runs = conn.execute(
        "SELECT * FROM payroll_runs ORDER BY run_at DESC LIMIT 20"
    ).fetchall()
    conn.close()
    return jsonify({
        "history": [dict(r) for r in runs]
    })


# ── Departments ─────────────────────────────────────────────────────────────────
@app.route("/api/departments", methods=["GET"])
def departments():
    conn = get_db()
    rows = conn.execute(
        "SELECT department, COUNT(*) as count, SUM(gross) as total_gross "
        "FROM employees GROUP BY department ORDER BY total_gross DESC"
    ).fetchall()
    conn.close()
    return jsonify({"departments": [dict(r) for r in rows]})


# ── Health Check ────────────────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})


# ─── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("\n  PayOS Backend running at http://localhost:5000")
    print("  API docs:\n")
    print("  GET    /api/employees          — list all employees")
    print("  POST   /api/employees          — create employee")
    print("  GET    /api/employees/<id>     — get one employee")
    print("  PUT    /api/employees/<id>     — update employee")
    print("  DELETE /api/employees/<id>     — delete employee")
    print("  GET    /api/employees/<id>/payslip  — generate payslip")
    print("  GET    /api/payroll/summary    — payroll totals")
    print("  POST   /api/payroll/run        — process payroll")
    print("  GET    /api/payroll/history    — past payroll runs")
    print("  GET    /api/departments        — dept breakdown")
    print("  GET    /api/health             — health check\n")
    app.run(debug=True, port=5000)
