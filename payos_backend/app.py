"""
PayOS Backend — Flask REST API
Matches every endpoint consumed by the PayOS frontend (index.html)

Endpoints:
  GET  /api/health
  GET  /api/payroll/summary
  GET  /api/employees          ?type=Full-Time|Part-Time|Contract  &q=search
  POST /api/employees
  PUT  /api/employees/<id>
  DELETE /api/employees/<id>
  GET  /api/employees/<id>/payslip
  POST /api/payroll/run
"""

from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from datetime import datetime, timezone
import uuid, math

def utcnow():
    return datetime.now(timezone.utc).isoformat()

app = Flask(__name__)
CORS(app)  # Allow the frontend to call from any origin

# ─────────────────────────────────────────────────────────────────────────────
# In-memory store — replace with a real DB (SQLite / MySQL / Postgres) later
# ─────────────────────────────────────────────────────────────────────────────
employees = {}

def _next_id():
    return "EMP" + str(100 + len(employees) + 1).zfill(3)

def _calc_deductions(gross: float) -> dict:
    """
    Standard deduction rates used by the frontend payslip view:
      Income Tax     20%
      Social Security 6.5%
      Health Ins      3%
      Pension         5%
    """
    tax    = round(gross * 0.20, 2)
    ss     = round(gross * 0.065, 2)
    health = round(gross * 0.03, 2)
    pension= round(gross * 0.05, 2)
    total  = round(tax + ss + health + pension, 2)
    net    = round(gross - total, 2)
    return {
        "income_tax":      tax,
        "social_security": ss,
        "health_insurance":health,
        "pension":         pension,
        "total":           total,
        "net":             net,
        # Short keys used by the employee list table
        "tax":   tax,
        "ss":    ss,
    }

def _employee_dict(emp: dict) -> dict:
    """Return the shape the frontend table expects."""
    d = _calc_deductions(emp["gross"])
    return {
        "id":         emp["id"],
        "name":       emp["name"],
        "department": emp["department"],
        "type":       emp["type"],
        "gross":      emp["gross"],
        "status":     emp["status"],
        "deductions": d,
    }

def _seed():
    """Pre-load some realistic demo employees."""
    seeds = [
        ("Kofi Mensah",      "Engineering",  "Full-Time",  8500, "Paid"),
        ("Ama Owusu",        "Marketing",    "Full-Time",  6200, "Paid"),
        ("Kwame Boateng",    "Finance",      "Full-Time",  7800, "Pending"),
        ("Abena Asante",     "HR",           "Part-Time",  3200, "Pending"),
        ("Yaw Darko",        "Engineering",  "Contract",   5500, "Paid"),
        ("Efua Addo",        "Design",       "Full-Time",  6900, "Paid"),
        ("Nana Agyei",       "Operations",   "Full-Time",  5100, "On Hold"),
        ("Akosua Frimpong",  "Engineering",  "Contract",   4800, "Pending"),
    ]
    for name, dept, typ, gross, status in seeds:
        eid = "EMP" + str(101 + len(employees)).zfill(3)
        employees[eid] = {
            "id": eid, "name": name, "department": dept,
            "type": typ, "gross": float(gross), "status": status,
            "created_at": utcnow(),
        }

_seed()

# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "timestamp": utcnow(),
        "employee_count": len(employees),
        "version": "1.0.0",
    })


@app.route("/api/payroll/summary")
def payroll_summary():
    gross = sum(e["gross"] for e in employees.values())
    deds  = [_calc_deductions(e["gross"]) for e in employees.values()]
    tax    = round(sum(d["income_tax"]       for d in deds), 2)
    ss     = round(sum(d["social_security"]  for d in deds), 2)
    health = round(sum(d["health_insurance"] for d in deds), 2)
    pension= round(sum(d["pension"]          for d in deds), 2)
    total_deductions = round(tax + ss + health + pension, 2)
    net = round(gross - total_deductions, 2)

    return jsonify({
        "employee_count":  len(employees),
        "gross":           round(gross, 2),
        "tax":             tax,
        "social_security": ss,
        "health":          health,
        "pension":         pension,
        "total_deductions":total_deductions,
        "net":             net,
        "period":          "May 2025",
        "run_at":          None,
    })


@app.route("/api/employees", methods=["GET"])
def list_employees():
    emp_type = request.args.get("type", "").strip()
    query    = request.args.get("q", "").strip().lower()

    result = list(employees.values())

    if emp_type and emp_type.lower() != "all":
        result = [e for e in result if e["type"] == emp_type]
    if query:
        result = [e for e in result
                  if query in e["name"].lower()
                  or query in e["department"].lower()
                  or query in e["id"].lower()]

    return jsonify({"employees": [_employee_dict(e) for e in result]})


@app.route("/api/employees", methods=["POST"])
def add_employee():
    body = request.get_json(force=True) or {}
    name  = body.get("name", "").strip()
    dept  = body.get("department", "").strip()
    typ   = body.get("type", "Full-Time").strip()
    gross = body.get("gross")
    status= body.get("status", "Pending").strip()

    if not name or not dept:
        return jsonify({"error": "name and department are required"}), 400
    try:
        gross = float(gross)
        if gross <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "gross must be a positive number"}), 400

    eid = _next_id()
    employees[eid] = {
        "id": eid, "name": name, "department": dept,
        "type": typ, "gross": gross, "status": status,
        "created_at": utcnow(),
    }
    return jsonify({"employee": _employee_dict(employees[eid])}), 201


@app.route("/api/employees/<eid>", methods=["PUT"])
def update_employee(eid):
    emp = employees.get(eid)
    if not emp:
        return jsonify({"error": "Employee not found"}), 404

    body = request.get_json(force=True) or {}
    if "name"       in body: emp["name"]       = body["name"].strip()
    if "department" in body: emp["department"] = body["department"].strip()
    if "type"       in body: emp["type"]       = body["type"].strip()
    if "status"     in body: emp["status"]     = body["status"].strip()
    if "gross"      in body:
        try:
            emp["gross"] = float(body["gross"])
        except (TypeError, ValueError):
            return jsonify({"error": "gross must be a number"}), 400

    return jsonify({"employee": _employee_dict(emp)})


@app.route("/api/employees/<eid>", methods=["DELETE"])
def delete_employee(eid):
    if eid not in employees:
        return jsonify({"error": "Employee not found"}), 404
    del employees[eid]
    return jsonify({"deleted": eid})


@app.route("/api/employees/<eid>/payslip")
def get_payslip(eid):
    emp = employees.get(eid)
    if not emp:
        return jsonify({"error": "Employee not found"}), 404

    gross = emp["gross"]
    d = _calc_deductions(gross)

    return jsonify({
        "employee": {
            "id":         emp["id"],
            "name":       emp["name"],
            "department": emp["department"],
            "type":       emp["type"],
            "status":     emp["status"],
        },
        "earnings": {
            "basic_salary": gross,
            "overtime":     0,
            "total":        gross,
        },
        "deductions": {
            "income_tax":       d["income_tax"],
            "social_security":  d["social_security"],
            "health_insurance": d["health_insurance"],
            "pension":          d["pension"],
            "total":            d["total"],
        },
        "net_pay":  d["net"],
        "period":   "May 2025",
        "issued_at": utcnow(),
    })


@app.route("/api/payroll/run", methods=["POST"])
def run_payroll():
    body   = request.get_json(force=True) or {}
    period = body.get("period", "May 2025")

    count = 0
    for emp in employees.values():
        if emp["status"] == "Pending":
            emp["status"] = "Paid"
            count += 1

    return jsonify({
        "message": f"Payroll processed for {period} — {count} employee(s) marked as Paid.",
        "period":  period,
        "processed": count,
        "run_at":  utcnow(),
    })


# ─────────────────────────────────────────────────────────────────────────────
# Error handlers
# ─────────────────────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    print("=" * 50)
    print("  PayOS Backend running on http://localhost:5000")
    print("  Frontend must set:  const API = 'http://localhost:5000/api'")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
