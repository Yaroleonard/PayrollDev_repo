-- ============================================================
--  RMU PAYROLL MANAGEMENT SYSTEM - DATABASE SCHEMA
--  Regional Maritime University (RMU), Accra, Ghana
--  Created: 2026
-- ============================================================

-- Drop existing tables if re-running
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS payslips CASCADE;
DROP TABLE IF EXISTS payroll_runs CASCADE;
DROP TABLE IF EXISTS deductions CASCADE;
DROP TABLE IF EXISTS allowances CASCADE;
DROP TABLE IF EXISTS tax_brackets CASCADE;
DROP TABLE IF EXISTS leave_records CASCADE;
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS bank_details CASCADE;
DROP TABLE IF EXISTS employee_qualifications CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS departments CASCADE;
DROP TABLE IF EXISTS job_grades CASCADE;
DROP TABLE IF EXISTS job_titles CASCADE;
DROP TABLE IF EXISTS deduction_types CASCADE;
DROP TABLE IF EXISTS allowance_types CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================================
-- 1. USERS (System Access)
-- ============================================================
CREATE TABLE users (
    user_id       SERIAL PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(30)  NOT NULL CHECK (role IN ('admin','hr_manager','payroll_officer','auditor','employee')),
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    last_login    TIMESTAMP,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 2. DEPARTMENTS
-- ============================================================
CREATE TABLE departments (
    dept_id       SERIAL PRIMARY KEY,
    dept_code     VARCHAR(10)  NOT NULL UNIQUE,
    dept_name     VARCHAR(100) NOT NULL,
    hod_emp_id    INT,                          -- FK added after employees table
    budget        NUMERIC(14,2) DEFAULT 0,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 3. JOB GRADES (Salary Bands)
-- ============================================================
CREATE TABLE job_grades (
    grade_id      SERIAL PRIMARY KEY,
    grade_code    VARCHAR(10)  NOT NULL UNIQUE,  -- e.g. GR-1, GR-2 … GR-12
    grade_name    VARCHAR(50)  NOT NULL,
    min_salary    NUMERIC(12,2) NOT NULL,
    max_salary    NUMERIC(12,2) NOT NULL,
    currency      CHAR(3)       NOT NULL DEFAULT 'GHS',
    created_at    TIMESTAMP     NOT NULL DEFAULT NOW(),
    CHECK (max_salary >= min_salary)
);

-- ============================================================
-- 4. JOB TITLES
-- ============================================================
CREATE TABLE job_titles (
    title_id      SERIAL PRIMARY KEY,
    title_code    VARCHAR(20)  NOT NULL UNIQUE,
    title_name    VARCHAR(100) NOT NULL,
    grade_id      INT          NOT NULL REFERENCES job_grades(grade_id),
    category      VARCHAR(30)  CHECK (category IN ('academic','administrative','technical','support')),
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 5. EMPLOYEES
-- ============================================================
CREATE TABLE employees (
    emp_id          SERIAL PRIMARY KEY,
    staff_id        VARCHAR(20)  NOT NULL UNIQUE,   -- e.g. RMU-2024-001
    first_name      VARCHAR(60)  NOT NULL,
    middle_name     VARCHAR(60),
    last_name       VARCHAR(60)  NOT NULL,
    gender          CHAR(1)      NOT NULL CHECK (gender IN ('M','F','O')),
    date_of_birth   DATE         NOT NULL,
    national_id     VARCHAR(30)  NOT NULL UNIQUE,   -- Ghana Card / Passport
    ssnit_number    VARCHAR(25)  UNIQUE,            -- Ghana Social Security
    tin             VARCHAR(20)  UNIQUE,            -- Tax Identification Number
    email           VARCHAR(120) NOT NULL UNIQUE,
    phone           VARCHAR(20),
    address         TEXT,

    -- Employment details
    dept_id         INT          NOT NULL REFERENCES departments(dept_id),
    title_id        INT          NOT NULL REFERENCES job_titles(title_id),
    grade_id        INT          NOT NULL REFERENCES job_grades(grade_id),
    employment_type VARCHAR(20)  NOT NULL CHECK (employment_type IN ('permanent','contract','part-time','intern')),
    hire_date       DATE         NOT NULL,
    termination_date DATE,
    status          VARCHAR(20)  NOT NULL DEFAULT 'active'
                      CHECK (status IN ('active','inactive','suspended','terminated','retired')),

    -- Salary
    basic_salary    NUMERIC(12,2) NOT NULL,
    currency        CHAR(3)       NOT NULL DEFAULT 'GHS',

    supervisor_id   INT           REFERENCES employees(emp_id),
    user_id         INT           REFERENCES users(user_id),
    created_at      TIMESTAMP     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP     NOT NULL DEFAULT NOW()
);

-- Add HOD FK now that employees table exists
ALTER TABLE departments
  ADD CONSTRAINT fk_hod FOREIGN KEY (hod_emp_id) REFERENCES employees(emp_id);

-- ============================================================
-- 6. EMPLOYEE QUALIFICATIONS
-- ============================================================
CREATE TABLE employee_qualifications (
    qual_id         SERIAL PRIMARY KEY,
    emp_id          INT          NOT NULL REFERENCES employees(emp_id) ON DELETE CASCADE,
    degree          VARCHAR(100) NOT NULL,    -- e.g. MSc Naval Architecture
    institution     VARCHAR(150) NOT NULL,
    year_obtained   SMALLINT     NOT NULL,
    is_professional BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 7. BANK DETAILS
-- ============================================================
CREATE TABLE bank_details (
    bank_id         SERIAL PRIMARY KEY,
    emp_id          INT          NOT NULL REFERENCES employees(emp_id) ON DELETE CASCADE,
    bank_name       VARCHAR(100) NOT NULL,
    branch          VARCHAR(100),
    account_number  VARCHAR(30)  NOT NULL,
    account_name    VARCHAR(150) NOT NULL,
    account_type    VARCHAR(20)  DEFAULT 'savings' CHECK (account_type IN ('savings','current','salary')),
    is_primary      BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
    UNIQUE (emp_id, account_number)
);

-- ============================================================
-- 8. ALLOWANCE TYPES (Configurable)
-- ============================================================
CREATE TABLE allowance_types (
    allow_type_id   SERIAL PRIMARY KEY,
    code            VARCHAR(20)  NOT NULL UNIQUE,   -- e.g. HOUSING, TRANSPORT
    name            VARCHAR(100) NOT NULL,
    is_taxable      BOOLEAN      NOT NULL DEFAULT FALSE,
    is_percentage   BOOLEAN      NOT NULL DEFAULT FALSE,  -- % of basic or flat amount
    default_value   NUMERIC(10,2) NOT NULL DEFAULT 0,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 9. ALLOWANCES (Per Employee)
-- ============================================================
CREATE TABLE allowances (
    allowance_id    SERIAL PRIMARY KEY,
    emp_id          INT          NOT NULL REFERENCES employees(emp_id) ON DELETE CASCADE,
    allow_type_id   INT          NOT NULL REFERENCES allowance_types(allow_type_id),
    amount          NUMERIC(10,2) NOT NULL,
    effective_date  DATE         NOT NULL,
    end_date        DATE,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 10. DEDUCTION TYPES (Configurable)
-- ============================================================
CREATE TABLE deduction_types (
    ded_type_id     SERIAL PRIMARY KEY,
    code            VARCHAR(20)  NOT NULL UNIQUE,   -- e.g. SSNIT, PAYE, UNION
    name            VARCHAR(100) NOT NULL,
    is_mandatory    BOOLEAN      NOT NULL DEFAULT FALSE,
    is_percentage   BOOLEAN      NOT NULL DEFAULT FALSE,
    default_rate    NUMERIC(7,4) NOT NULL DEFAULT 0,   -- % rate or flat amount
    beneficiary     VARCHAR(100),                       -- e.g. Ghana Revenue Authority
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 11. TAX BRACKETS (Ghana PAYE)
-- ============================================================
CREATE TABLE tax_brackets (
    bracket_id      SERIAL PRIMARY KEY,
    effective_year  SMALLINT     NOT NULL,
    lower_bound     NUMERIC(12,2) NOT NULL DEFAULT 0,
    upper_bound     NUMERIC(12,2),                     -- NULL = no upper limit
    rate            NUMERIC(5,4)  NOT NULL,             -- e.g. 0.1750 = 17.5%
    created_at      TIMESTAMP     NOT NULL DEFAULT NOW()
);

-- Ghana PAYE 2024 seed data
INSERT INTO tax_brackets (effective_year, lower_bound, upper_bound, rate) VALUES
  (2024,     0.00,    402.00, 0.0000),
  (2024,   402.00,    510.00, 0.0500),
  (2024,   510.00,    840.00, 0.1000),
  (2024,   840.00,   1260.00, 0.1750),
  (2024,  1260.00,   5000.00, 0.2500),
  (2024,  5000.00,  10000.00, 0.3000),
  (2024, 10000.00,       NULL, 0.3500);

-- ============================================================
-- 12. DEDUCTIONS (Per Employee)
-- ============================================================
CREATE TABLE deductions (
    deduction_id    SERIAL PRIMARY KEY,
    emp_id          INT          NOT NULL REFERENCES employees(emp_id) ON DELETE CASCADE,
    ded_type_id     INT          NOT NULL REFERENCES deduction_types(ded_type_id),
    amount          NUMERIC(10,2),                      -- override flat amount
    rate            NUMERIC(7,4),                       -- override percentage
    effective_date  DATE         NOT NULL,
    end_date        DATE,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    notes           TEXT,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 13. LEAVE RECORDS
-- ============================================================
CREATE TABLE leave_records (
    leave_id        SERIAL PRIMARY KEY,
    emp_id          INT          NOT NULL REFERENCES employees(emp_id) ON DELETE CASCADE,
    leave_type      VARCHAR(30)  NOT NULL CHECK (leave_type IN ('annual','sick','maternity','paternity','study','unpaid','compassionate')),
    start_date      DATE         NOT NULL,
    end_date        DATE         NOT NULL,
    days_taken      SMALLINT     NOT NULL,
    is_paid         BOOLEAN      NOT NULL DEFAULT TRUE,
    approved_by     INT          REFERENCES employees(emp_id),
    status          VARCHAR(20)  NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','approved','rejected','cancelled')),
    notes           TEXT,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
    CHECK (end_date >= start_date)
);

-- ============================================================
-- 14. ATTENDANCE
-- ============================================================
CREATE TABLE attendance (
    att_id          SERIAL PRIMARY KEY,
    emp_id          INT          NOT NULL REFERENCES employees(emp_id) ON DELETE CASCADE,
    att_date        DATE         NOT NULL,
    check_in        TIME,
    check_out       TIME,
    status          VARCHAR(20)  NOT NULL DEFAULT 'present'
                      CHECK (status IN ('present','absent','late','half_day','on_leave')),
    remarks         VARCHAR(200),
    UNIQUE (emp_id, att_date)
);

-- ============================================================
-- 15. PAYROLL RUNS (Monthly Payroll Batches)
-- ============================================================
CREATE TABLE payroll_runs (
    run_id          SERIAL PRIMARY KEY,
    run_name        VARCHAR(100) NOT NULL,              -- e.g. "May 2026 Payroll"
    pay_period_start DATE        NOT NULL,
    pay_period_end   DATE        NOT NULL,
    pay_date         DATE        NOT NULL,
    status          VARCHAR(20)  NOT NULL DEFAULT 'draft'
                      CHECK (status IN ('draft','processing','approved','paid','cancelled')),
    total_gross     NUMERIC(16,2) DEFAULT 0,
    total_deductions NUMERIC(16,2) DEFAULT 0,
    total_net       NUMERIC(16,2) DEFAULT 0,
    employee_count  INT          DEFAULT 0,
    prepared_by     INT          REFERENCES users(user_id),
    approved_by     INT          REFERENCES users(user_id),
    approved_at     TIMESTAMP,
    notes           TEXT,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
    CHECK (pay_period_end >= pay_period_start)
);

-- ============================================================
-- 16. PAYSLIPS (One per Employee per Payroll Run)
-- ============================================================
CREATE TABLE payslips (
    payslip_id          SERIAL PRIMARY KEY,
    run_id              INT           NOT NULL REFERENCES payroll_runs(run_id) ON DELETE CASCADE,
    emp_id              INT           NOT NULL REFERENCES employees(emp_id),
    staff_id            VARCHAR(20)   NOT NULL,
    full_name           VARCHAR(200)  NOT NULL,
    department          VARCHAR(100)  NOT NULL,
    job_title           VARCHAR(100)  NOT NULL,
    pay_period_start    DATE          NOT NULL,
    pay_period_end      DATE          NOT NULL,
    pay_date            DATE          NOT NULL,

    -- Earnings
    basic_salary        NUMERIC(12,2) NOT NULL DEFAULT 0,
    housing_allowance   NUMERIC(10,2) NOT NULL DEFAULT 0,
    transport_allowance NUMERIC(10,2) NOT NULL DEFAULT 0,
    research_allowance  NUMERIC(10,2) NOT NULL DEFAULT 0,
    medical_allowance   NUMERIC(10,2) NOT NULL DEFAULT 0,
    other_allowances    NUMERIC(10,2) NOT NULL DEFAULT 0,
    overtime_pay        NUMERIC(10,2) NOT NULL DEFAULT 0,
    gross_pay           NUMERIC(12,2) NOT NULL DEFAULT 0,

    -- Deductions
    ssnit_employee      NUMERIC(10,2) NOT NULL DEFAULT 0,  -- 5.5% employee
    ssnit_employer      NUMERIC(10,2) NOT NULL DEFAULT 0,  -- 13% employer (info only)
    paye_tax            NUMERIC(10,2) NOT NULL DEFAULT 0,
    union_dues          NUMERIC(10,2) NOT NULL DEFAULT 0,
    loan_repayment      NUMERIC(10,2) NOT NULL DEFAULT 0,
    other_deductions    NUMERIC(10,2) NOT NULL DEFAULT 0,
    total_deductions    NUMERIC(12,2) NOT NULL DEFAULT 0,

    net_pay             NUMERIC(12,2) NOT NULL DEFAULT 0,
    currency            CHAR(3)       NOT NULL DEFAULT 'GHS',

    bank_name           VARCHAR(100),
    account_number      VARCHAR(30),
    payment_status      VARCHAR(20)   NOT NULL DEFAULT 'pending'
                          CHECK (payment_status IN ('pending','paid','failed','on_hold')),
    paid_at             TIMESTAMP,
    notes               TEXT,
    created_at          TIMESTAMP     NOT NULL DEFAULT NOW(),
    UNIQUE (run_id, emp_id)
);

-- ============================================================
-- 17. AUDIT LOGS
-- ============================================================
CREATE TABLE audit_logs (
    log_id          SERIAL PRIMARY KEY,
    user_id         INT          REFERENCES users(user_id),
    action          VARCHAR(50)  NOT NULL,   -- e.g. INSERT, UPDATE, DELETE, LOGIN
    table_name      VARCHAR(60),
    record_id       INT,
    old_values      JSONB,
    new_values      JSONB,
    ip_address      INET,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX idx_employees_dept     ON employees(dept_id);
CREATE INDEX idx_employees_status   ON employees(status);
CREATE INDEX idx_employees_hire     ON employees(hire_date);
CREATE INDEX idx_payslips_run       ON payslips(run_id);
CREATE INDEX idx_payslips_emp       ON payslips(emp_id);
CREATE INDEX idx_payslips_paydate   ON payslips(pay_date);
CREATE INDEX idx_attendance_emp     ON attendance(emp_id, att_date);
CREATE INDEX idx_leave_emp          ON leave_records(emp_id, status);
CREATE INDEX idx_audit_table        ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_created      ON audit_logs(created_at);

-- ============================================================
-- VIEWS
-- ============================================================

-- Employee full profile view
CREATE VIEW v_employee_profile AS
SELECT
    e.emp_id,
    e.staff_id,
    e.first_name || ' ' || COALESCE(e.middle_name || ' ', '') || e.last_name AS full_name,
    e.gender,
    e.date_of_birth,
    EXTRACT(YEAR FROM AGE(e.date_of_birth))::INT AS age,
    e.national_id,
    e.ssnit_number,
    e.tin,
    e.email,
    e.phone,
    d.dept_name,
    jt.title_name AS job_title,
    jg.grade_code,
    e.employment_type,
    e.hire_date,
    EXTRACT(YEAR FROM AGE(e.hire_date))::INT AS years_of_service,
    e.basic_salary,
    e.currency,
    e.status
FROM employees e
JOIN departments  d  ON e.dept_id  = d.dept_id
JOIN job_titles   jt ON e.title_id = jt.title_id
JOIN job_grades   jg ON e.grade_id = jg.grade_id;

-- Monthly payroll summary view
CREATE VIEW v_payroll_summary AS
SELECT
    pr.run_id,
    pr.run_name,
    pr.pay_period_start,
    pr.pay_period_end,
    pr.pay_date,
    pr.status,
    pr.employee_count,
    pr.total_gross,
    pr.total_deductions,
    pr.total_net,
    COUNT(ps.payslip_id) FILTER (WHERE ps.payment_status = 'paid')   AS paid_count,
    COUNT(ps.payslip_id) FILTER (WHERE ps.payment_status = 'pending') AS pending_count
FROM payroll_runs pr
LEFT JOIN payslips ps ON pr.run_id = ps.run_id
GROUP BY pr.run_id;

-- Department payroll cost view
CREATE VIEW v_dept_payroll_cost AS
SELECT
    d.dept_name,
    COUNT(e.emp_id)          AS headcount,
    SUM(e.basic_salary)      AS total_basic,
    AVG(e.basic_salary)      AS avg_basic,
    MIN(e.basic_salary)      AS min_basic,
    MAX(e.basic_salary)      AS max_basic
FROM employees e
JOIN departments d ON e.dept_id = d.dept_id
WHERE e.status = 'active'
GROUP BY d.dept_name
ORDER BY total_basic DESC;

-- ============================================================
-- STORED PROCEDURES & FUNCTIONS
-- ============================================================

-- Function: Calculate Ghana PAYE tax for a given monthly income
CREATE OR REPLACE FUNCTION calculate_paye(monthly_income NUMERIC, tax_year SMALLINT DEFAULT 2024)
RETURNS NUMERIC AS $$
DECLARE
    tax        NUMERIC := 0;
    rec        RECORD;
    prev_upper NUMERIC := 0;
    taxable    NUMERIC;
BEGIN
    FOR rec IN
        SELECT lower_bound, upper_bound, rate
        FROM tax_brackets
        WHERE effective_year = tax_year
        ORDER BY lower_bound
    LOOP
        IF monthly_income <= rec.lower_bound THEN
            EXIT;
        END IF;
        taxable := LEAST(monthly_income, COALESCE(rec.upper_bound, monthly_income)) - rec.lower_bound;
        tax     := tax + (taxable * rec.rate);
    END LOOP;
    RETURN ROUND(tax, 2);
END;
$$ LANGUAGE plpgsql;

-- Function: Compute net pay for a single employee
CREATE OR REPLACE FUNCTION compute_net_pay(p_emp_id INT)
RETURNS TABLE (
    gross_pay        NUMERIC,
    total_allowances NUMERIC,
    ssnit_employee   NUMERIC,
    paye_tax         NUMERIC,
    other_deductions NUMERIC,
    total_deductions NUMERIC,
    net_pay          NUMERIC
) AS $$
DECLARE
    v_basic    NUMERIC;
    v_allow    NUMERIC;
    v_gross    NUMERIC;
    v_ssnit    NUMERIC;
    v_paye     NUMERIC;
    v_other    NUMERIC;
    v_total_d  NUMERIC;
BEGIN
    SELECT basic_salary INTO v_basic FROM employees WHERE emp_id = p_emp_id;

    -- Total active allowances
    SELECT COALESCE(SUM(a.amount),0) INTO v_allow
    FROM allowances a
    WHERE a.emp_id = p_emp_id AND a.is_active = TRUE
      AND (a.end_date IS NULL OR a.end_date >= CURRENT_DATE);

    v_gross  := v_basic + v_allow;
    v_ssnit  := ROUND(v_basic * 0.055, 2);       -- 5.5% of basic
    v_paye   := calculate_paye(v_gross - v_ssnit);

    SELECT COALESCE(SUM(
        CASE WHEN d.is_percentage THEN v_basic * dt.default_rate
             ELSE COALESCE(d.amount, dt.default_rate) END
    ), 0) INTO v_other
    FROM deductions d
    JOIN deduction_types dt ON d.ded_type_id = dt.ded_type_id
    WHERE d.emp_id = p_emp_id AND d.is_active = TRUE
      AND dt.code NOT IN ('SSNIT','PAYE')
      AND (d.end_date IS NULL OR d.end_date >= CURRENT_DATE);

    v_total_d := v_ssnit + v_paye + v_other;

    RETURN QUERY SELECT
        v_gross,
        v_allow,
        v_ssnit,
        v_paye,
        v_other,
        v_total_d,
        ROUND(v_gross - v_total_d, 2);
END;
$$ LANGUAGE plpgsql;

-- Procedure: Generate payslips for a payroll run
CREATE OR REPLACE PROCEDURE generate_payroll_run(p_run_id INT)
LANGUAGE plpgsql AS $$
DECLARE
    emp RECORD;
    np  RECORD;
    bd  RECORD;
BEGIN
    FOR emp IN
        SELECT emp_id, staff_id,
               first_name || ' ' || last_name AS full_name
        FROM employees WHERE status = 'active'
    LOOP
        SELECT * INTO np FROM compute_net_pay(emp.emp_id);

        SELECT b.bank_name, b.account_number INTO bd
        FROM bank_details b
        WHERE b.emp_id = emp.emp_id AND b.is_primary = TRUE LIMIT 1;

        INSERT INTO payslips (
            run_id, emp_id, staff_id, full_name,
            department, job_title,
            pay_period_start, pay_period_end, pay_date,
            basic_salary, other_allowances, gross_pay,
            ssnit_employee, paye_tax, other_deductions,
            total_deductions, net_pay,
            bank_name, account_number
        )
        SELECT
            p_run_id,
            emp.emp_id,
            emp.staff_id,
            emp.full_name,
            d.dept_name,
            jt.title_name,
            pr.pay_period_start,
            pr.pay_period_end,
            pr.pay_date,
            (SELECT basic_salary FROM employees WHERE emp_id = emp.emp_id),
            np.total_allowances,
            np.gross_pay,
            np.ssnit_employee,
            np.paye_tax,
            np.other_deductions,
            np.total_deductions,
            np.net_pay,
            bd.bank_name,
            bd.account_number
        FROM payroll_runs pr
        JOIN employees   e  ON e.emp_id  = emp.emp_id
        JOIN departments d  ON d.dept_id = e.dept_id
        JOIN job_titles  jt ON jt.title_id = e.title_id
        WHERE pr.run_id = p_run_id
        ON CONFLICT (run_id, emp_id) DO UPDATE
            SET gross_pay        = EXCLUDED.gross_pay,
                total_deductions = EXCLUDED.total_deductions,
                net_pay          = EXCLUDED.net_pay,
                updated_at       = NOW() -- note: payslips doesn't have updated_at; harmless
        ;
    END LOOP;

    -- Update run totals
    UPDATE payroll_runs pr SET
        total_gross      = (SELECT COALESCE(SUM(gross_pay),0)        FROM payslips WHERE run_id = p_run_id),
        total_deductions = (SELECT COALESCE(SUM(total_deductions),0)  FROM payslips WHERE run_id = p_run_id),
        total_net        = (SELECT COALESCE(SUM(net_pay),0)           FROM payslips WHERE run_id = p_run_id),
        employee_count   = (SELECT COUNT(*)                           FROM payslips WHERE run_id = p_run_id),
        updated_at       = NOW()
    WHERE run_id = p_run_id;
END;
$$;

-- ============================================================
-- TRIGGERS
-- ============================================================

-- Auto-update updated_at on employees
CREATE OR REPLACE FUNCTION trg_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_employees_updated
    BEFORE UPDATE ON employees
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();

CREATE TRIGGER trg_payroll_runs_updated
    BEFORE UPDATE ON payroll_runs
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();

-- Audit trigger function
CREATE OR REPLACE FUNCTION trg_audit_log()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs(action, table_name, record_id, old_values, new_values)
    VALUES (
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.emp_id, OLD.emp_id, NEW.payslip_id, OLD.payslip_id),
        CASE WHEN TG_OP != 'INSERT' THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP != 'DELETE' THEN to_jsonb(NEW) ELSE NULL END
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_employees
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH ROW EXECUTE FUNCTION trg_audit_log();

CREATE TRIGGER trg_audit_payslips
    AFTER INSERT OR UPDATE OR DELETE ON payslips
    FOR EACH ROW EXECUTE FUNCTION trg_audit_log();

-- ============================================================
-- SEED DATA
-- ============================================================

-- Allowance types (RMU-specific)
INSERT INTO allowance_types (code, name, is_taxable, is_percentage, default_value) VALUES
  ('HOUSING',    'Housing Allowance',         TRUE,  TRUE,  0.20),
  ('TRANSPORT',  'Transport Allowance',       FALSE, FALSE, 500.00),
  ('RESEARCH',   'Research Allowance',        FALSE, FALSE, 800.00),
  ('MEDICAL',    'Medical Allowance',         FALSE, FALSE, 300.00),
  ('MARITIME',   'Maritime Risk Allowance',   FALSE, TRUE,  0.10),
  ('ACADEMIC',   'Academic Excellence',       FALSE, FALSE, 600.00),
  ('UTILITIES',  'Utilities Allowance',       FALSE, FALSE, 200.00);

-- Deduction types
INSERT INTO deduction_types (code, name, is_mandatory, is_percentage, default_rate, beneficiary) VALUES
  ('SSNIT',      'SSNIT Contribution (Employee)', TRUE,  TRUE,  0.0550, 'Social Security & National Insurance Trust'),
  ('PAYE',       'Income Tax (PAYE)',              TRUE,  FALSE, 0.0000, 'Ghana Revenue Authority'),
  ('UNION',      'Staff Union Dues',               FALSE, FALSE, 50.00,  'RMU Staff Union'),
  ('LOAN',       'Staff Loan Repayment',           FALSE, FALSE, 0.00,   'RMU Finance'),
  ('INSURANCE',  'Group Life Insurance',           FALSE, TRUE,  0.0100, 'Enterprise Insurance'),
  ('FUEL',       'Fuel Advance Recovery',          FALSE, FALSE, 0.00,   'RMU Finance');

-- Job grades
INSERT INTO job_grades (grade_code, grade_name, min_salary, max_salary) VALUES
  ('GR-1',  'Support Staff I',       1200, 2000),
  ('GR-2',  'Support Staff II',      2000, 3000),
  ('GR-3',  'Technical Staff I',     3000, 4500),
  ('GR-4',  'Technical Staff II',    4500, 6000),
  ('GR-5',  'Senior Technical',      6000, 8000),
  ('GR-6',  'Professional I',        8000, 11000),
  ('GR-7',  'Professional II',      11000, 15000),
  ('GR-8',  'Senior Professional',  15000, 20000),
  ('GR-9',  'Principal Officer',    20000, 27000),
  ('GR-10', 'Lecturer',              8000, 14000),
  ('GR-11', 'Senior Lecturer',      14000, 22000),
  ('GR-12', 'Professor / Director', 22000, 40000);

-- Departments
INSERT INTO departments (dept_code, dept_name, budget) VALUES
  ('RECT',   'Office of the Rector',              2000000),
  ('NAVAL',  'Dept of Naval Architecture',        1500000),
  ('MARINE', 'Dept of Marine Engineering',        1500000),
  ('LOGIST', 'Dept of Logistics & Supply Chain',  1200000),
  ('MPORT',  'Dept of Maritime & Port Management', 1200000),
  ('ICT',    'ICT Department',                     800000),
  ('FINANCE','Finance & Accounts',                 900000),
  ('HR',     'Human Resource Management',          600000),
  ('LIBR',   'Library Services',                   300000),
  ('SECUR',  'Security & Safety',                  350000);

-- Job titles
INSERT INTO job_titles (title_code, title_name, grade_id, category) VALUES
  ('RECTOR',     'Rector',                       12, 'academic'),
  ('PROF',       'Professor',                    12, 'academic'),
  ('ASSOC_PROF', 'Associate Professor',          11, 'academic'),
  ('SR_LECT',    'Senior Lecturer',              11, 'academic'),
  ('LECT',       'Lecturer',                     10, 'academic'),
  ('ASST_LECT',  'Assistant Lecturer',            7, 'academic'),
  ('REG',        'Registrar',                    12, 'administrative'),
  ('DIR',        'Director',                     11, 'administrative'),
  ('SR_ADMIN',   'Senior Administrative Officer', 8, 'administrative'),
  ('ADMIN',      'Administrative Officer',        7, 'administrative'),
  ('ICT_MGR',    'ICT Manager',                   9, 'technical'),
  ('SR_ICT',     'Senior ICT Officer',             7, 'technical'),
  ('ICT_OFF',    'ICT Officer',                    6, 'technical'),
  ('ACCT',       'Accountant',                    7, 'administrative'),
  ('SR_ACCT',    'Senior Accountant',              8, 'administrative'),
  ('TECH',       'Technician',                    4, 'technical'),
  ('LIBR_OFF',   'Library Officer',               6, 'support'),
  ('CLEANER',    'Cleaner',                       1, 'support'),
  ('GUARD',      'Security Guard',               2, 'support');

-- ============================================================
-- END OF SCHEMA
-- ============================================================