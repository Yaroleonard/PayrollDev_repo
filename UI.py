HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PayOS — Payroll Management System</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=IBM+Plex+Mono:wght@400;500&family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0d0f14;
    --surface: #13161e;
    --surface2: #1a1f2c;
    --border: #252b3b;
    --accent: #4fffb0;
    --accent2: #ff6b6b;
    --accent3: #ffd93d;
    --text: #e8eaf0;
    --muted: #6b7494;
    --card: #161b28;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Outfit', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    display: flex;
    overflow-x: hidden;
  }

  /* SIDEBAR */
  .sidebar {
    width: 240px;
    min-height: 100vh;
    background: var(--surface);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    position: fixed;
    left: 0; top: 0; bottom: 0;
    z-index: 100;
    animation: slideInLeft 0.5s ease;
  }

  @keyframes slideInLeft {
    from { transform: translateX(-100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }

  .logo {
    padding: 28px 24px 24px;
    border-bottom: 1px solid var(--border);
  }

  .logo-mark {
    font-family: 'DM Serif Display', serif;
    font-size: 26px;
    color: var(--accent);
    letter-spacing: -0.5px;
  }

  .logo-sub {
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 2px;
    font-family: 'IBM Plex Mono', monospace;
  }

  .nav {
    padding: 20px 12px;
    flex: 1;
  }

  .nav-section {
    margin-bottom: 24px;
  }

  .nav-label {
    font-size: 9px;
    letter-spacing: 2.5px;
    color: var(--muted);
    text-transform: uppercase;
    padding: 0 12px;
    margin-bottom: 8px;
    font-family: 'IBM Plex Mono', monospace;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    cursor: pointer;
    color: var(--muted);
    font-size: 14px;
    font-weight: 400;
    transition: all 0.2s;
    margin-bottom: 2px;
  }

  .nav-item:hover { background: var(--surface2); color: var(--text); }
  .nav-item.active { background: rgba(79,255,176,0.1); color: var(--accent); }

  .nav-icon {
    width: 18px; height: 18px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px;
  }

  .sidebar-footer {
    padding: 16px;
    border-top: 1px solid var(--border);
  }

  .user-chip {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    background: var(--surface2);
  }

  .avatar {
    width: 32px; height: 32px; border-radius: 50%;
    background: linear-gradient(135deg, var(--accent), #00c87a);
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 600; color: #0d0f14;
  }

  .user-info { flex: 1; }
  .user-name { font-size: 13px; font-weight: 500; }
  .user-role { font-size: 10px; color: var(--muted); font-family: 'IBM Plex Mono', monospace; }

  /* MAIN */
  .main {
    margin-left: 240px;
    flex: 1;
    padding: 0;
    animation: fadeIn 0.6s ease 0.2s both;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .topbar {
    padding: 20px 36px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--surface);
    position: sticky; top: 0; z-index: 50;
  }

  .page-title {
    font-family: 'DM Serif Display', serif;
    font-size: 22px;
    color: var(--text);
  }

  .topbar-actions { display: flex; gap: 10px; }

  .btn {
    padding: 9px 18px;
    border-radius: 8px;
    font-family: 'Outfit', sans-serif;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    border: none;
    transition: all 0.2s;
  }

  .btn-ghost {
    background: transparent;
    color: var(--muted);
    border: 1px solid var(--border);
  }
  .btn-ghost:hover { border-color: var(--accent); color: var(--accent); }

  .btn-primary {
    background: var(--accent);
    color: #0d0f14;
    font-weight: 600;
  }
  .btn-primary:hover { background: #3ae89a; transform: translateY(-1px); box-shadow: 0 4px 20px rgba(79,255,176,0.3); }

  .btn-danger {
    background: rgba(255,107,107,0.1);
    color: var(--accent2);
    border: 1px solid rgba(255,107,107,0.2);
  }
  .btn-danger:hover { background: rgba(255,107,107,0.2); }

  /* CONTENT */
  .content { padding: 32px 36px; }

  /* KPI CARDS */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 32px;
  }

  .kpi-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
    animation: cardIn 0.5s ease both;
  }

  .kpi-card:nth-child(1) { animation-delay: 0.1s; }
  .kpi-card:nth-child(2) { animation-delay: 0.2s; }
  .kpi-card:nth-child(3) { animation-delay: 0.3s; }
  .kpi-card:nth-child(4) { animation-delay: 0.4s; }

  @keyframes cardIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,0,0,0.3); }

  .kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
  }

  .kpi-card.green::before { background: var(--accent); }
  .kpi-card.red::before { background: var(--accent2); }
  .kpi-card.yellow::before { background: var(--accent3); }
  .kpi-card.blue::before { background: #60b4ff; }

  .kpi-label {
    font-size: 11px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 12px;
  }

  .kpi-value {
    font-family: 'DM Serif Display', serif;
    font-size: 32px;
    color: var(--text);
    line-height: 1;
    margin-bottom: 8px;
  }

  .kpi-change {
    font-size: 12px;
    display: flex; align-items: center; gap: 4px;
  }

  .kpi-change.up { color: var(--accent); }
  .kpi-change.down { color: var(--accent2); }

  /* LAYOUT GRID */
  .layout-grid {
    display: grid;
    grid-template-columns: 1fr 340px;
    gap: 20px;
    margin-bottom: 28px;
  }

  /* TABLE */
  .panel {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
  }

  .panel-header {
    padding: 18px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .panel-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text);
  }

  .panel-meta {
    font-size: 11px;
    color: var(--muted);
    font-family: 'IBM Plex Mono', monospace;
  }

  .search-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0 12px;
    width: 220px;
  }

  .search-bar input {
    background: transparent;
    border: none;
    outline: none;
    color: var(--text);
    font-family: 'Outfit', sans-serif;
    font-size: 13px;
    padding: 8px 0;
    width: 100%;
  }

  .search-bar input::placeholder { color: var(--muted); }

  table { width: 100%; border-collapse: collapse; }

  thead th {
    padding: 12px 16px;
    text-align: left;
    font-size: 10px;
    font-weight: 500;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-family: 'IBM Plex Mono', monospace;
    border-bottom: 1px solid var(--border);
    background: var(--surface2);
  }

  tbody tr {
    border-bottom: 1px solid rgba(37,43,59,0.5);
    transition: background 0.15s;
  }
  tbody tr:last-child { border-bottom: none; }
  tbody tr:hover { background: var(--surface2); }

  td {
    padding: 14px 16px;
    font-size: 13px;
  }

  .emp-cell { display: flex; align-items: center; gap: 10px; }

  .mini-avatar {
    width: 30px; height: 30px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 600; color: #0d0f14;
    flex-shrink: 0;
  }

  .emp-name { font-weight: 500; font-size: 13px; }
  .emp-id { font-size: 10px; color: var(--muted); font-family: 'IBM Plex Mono', monospace; }

  .badge {
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 500;
    display: inline-block;
  }

  .badge-green { background: rgba(79,255,176,0.1); color: var(--accent); }
  .badge-yellow { background: rgba(255,217,61,0.1); color: var(--accent3); }
  .badge-red { background: rgba(255,107,107,0.1); color: var(--accent2); }
  .badge-blue { background: rgba(96,180,255,0.1); color: #60b4ff; }

  .amount { font-family: 'IBM Plex Mono', monospace; font-size: 13px; font-weight: 500; }

  .action-btns { display: flex; gap: 6px; }
  .icon-btn {
    width: 28px; height: 28px; border-radius: 6px;
    border: 1px solid var(--border);
    background: transparent;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px;
    transition: all 0.2s;
    color: var(--muted);
  }
  .icon-btn:hover { border-color: var(--accent); color: var(--accent); background: rgba(79,255,176,0.05); }

  /* PAYROLL SUMMARY SIDE PANEL */
  .summary-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
  }

  .summary-header {
    padding: 18px 20px;
    border-bottom: 1px solid var(--border);
    background: linear-gradient(135deg, rgba(79,255,176,0.05), rgba(79,255,176,0));
  }

  .period-badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: var(--accent);
    background: rgba(79,255,176,0.1);
    padding: 3px 8px;
    border-radius: 4px;
    margin-bottom: 8px;
    display: inline-block;
    letter-spacing: 1px;
  }

  .summary-body { padding: 20px; }

  .summary-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid rgba(37,43,59,0.5);
    font-size: 13px;
  }

  .summary-row:last-child { border-bottom: none; }
  .summary-row .label { color: var(--muted); }
  .summary-row .val { font-family: 'IBM Plex Mono', monospace; font-weight: 500; }

  .summary-total {
    margin-top: 16px;
    padding: 14px 16px;
    background: rgba(79,255,176,0.05);
    border: 1px solid rgba(79,255,176,0.15);
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .summary-total .label { font-weight: 600; font-size: 14px; }
  .summary-total .val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 18px;
    font-weight: 600;
    color: var(--accent);
  }

  .run-btn {
    width: 100%;
    margin-top: 16px;
    padding: 13px;
    background: var(--accent);
    color: #0d0f14;
    border: none;
    border-radius: 8px;
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
    letter-spacing: 0.5px;
  }

  .run-btn:hover { background: #3ae89a; box-shadow: 0 4px 24px rgba(79,255,176,0.35); transform: translateY(-1px); }

  /* DEDUCTIONS TABLE */
  .deduction-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px dashed rgba(37,43,59,0.8);
    font-size: 12px;
  }

  .deduction-item:last-child { border-bottom: none; }
  .deduction-name { color: var(--muted); }
  .deduction-pct {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: var(--accent2);
    background: rgba(255,107,107,0.08);
    padding: 2px 6px;
    border-radius: 4px;
  }
  .deduction-amt { font-family: 'IBM Plex Mono', monospace; color: var(--accent2); }

  /* MODAL */
  .modal-overlay {
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.7);
    backdrop-filter: blur(4px);
    z-index: 200;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.25s;
  }

  .modal-overlay.open {
    opacity: 1;
    pointer-events: all;
  }

  .modal {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    width: 520px;
    max-height: 85vh;
    overflow-y: auto;
    transform: scale(0.9);
    transition: transform 0.25s;
  }

  .modal-overlay.open .modal { transform: scale(1); }

  .modal-header {
    padding: 24px 28px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .modal-title {
    font-family: 'DM Serif Display', serif;
    font-size: 20px;
  }

  .close-btn {
    width: 32px; height: 32px; border-radius: 8px;
    border: 1px solid var(--border);
    background: transparent;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    color: var(--muted);
    font-size: 16px;
    transition: all 0.2s;
  }

  .close-btn:hover { border-color: var(--accent2); color: var(--accent2); }

  .modal-body { padding: 24px 28px; }

  .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

  .form-group { display: flex; flex-direction: column; gap: 6px; }
  .form-group.full { grid-column: span 2; }

  .form-label {
    font-size: 11px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'IBM Plex Mono', monospace;
  }

  .form-input, .form-select {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    color: var(--text);
    font-family: 'Outfit', sans-serif;
    font-size: 13px;
    outline: none;
    transition: border-color 0.2s;
  }

  .form-input:focus, .form-select:focus { border-color: var(--accent); }
  .form-select option { background: var(--surface2); }

  .modal-footer {
    padding: 16px 28px 24px;
    display: flex;
    gap: 10px;
    justify-content: flex-end;
  }

  /* PAYSLIP */
  .payslip-modal {
    width: 580px;
  }

  .payslip-header {
    background: linear-gradient(135deg, #0a1f14, #0d2a1a);
    border-bottom: 2px solid var(--accent);
    padding: 28px;
  }

  .payslip-company {
    font-family: 'DM Serif Display', serif;
    font-size: 22px;
    color: var(--accent);
  }

  .payslip-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: var(--muted);
    margin-top: 4px;
  }

  .payslip-emp-info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    padding: 20px 28px;
    border-bottom: 1px solid var(--border);
  }

  .info-item .info-label {
    font-size: 10px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 3px;
  }

  .info-item .info-val {
    font-size: 13px;
    font-weight: 500;
  }

  .payslip-table { padding: 20px 28px; }

  .payslip-section-title {
    font-size: 10px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 2px;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border);
  }

  .payslip-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    font-size: 13px;
  }

  .payslip-row .p-label { color: var(--muted); }
  .payslip-row .p-val { font-family: 'IBM Plex Mono', monospace; }

  .payslip-net {
    margin: 16px 28px 28px;
    background: var(--accent);
    border-radius: 10px;
    padding: 16px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .payslip-net .net-label {
    font-weight: 700;
    color: #0d0f14;
    font-size: 15px;
  }

  .payslip-net .net-val {
    font-family: 'DM Serif Display', serif;
    font-size: 26px;
    color: #0d0f14;
  }

  /* NOTIFICATION TOAST */
  .toast {
    position: fixed;
    bottom: 28px; right: 28px;
    background: var(--surface);
    border: 1px solid var(--accent);
    border-radius: 10px;
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 13px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    transform: translateY(100px);
    opacity: 0;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    z-index: 300;
  }

  .toast.show { transform: translateY(0); opacity: 1; }
  .toast-icon { font-size: 18px; }

  /* TABS */
  .tabs { display: flex; gap: 4px; margin-bottom: 20px; }

  .tab {
    padding: 8px 16px;
    border-radius: 8px;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--muted);
    font-family: 'Outfit', sans-serif;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .tab.active { background: rgba(79,255,176,0.1); border-color: rgba(79,255,176,0.3); color: var(--accent); }
  .tab:hover:not(.active) { border-color: var(--muted); color: var(--text); }

  /* SCROLLBAR */
  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>
</head>
<body>

<!-- SIDEBAR -->
<aside class="sidebar">
  <div class="logo">
    <div class="logo-mark">PayOS</div>
    <div class="logo-sub">Payroll System</div>
  </div>
  <nav class="nav">
    <div class="nav-section">
      <div class="nav-label">Main</div>
      <div class="nav-item active" onclick="setNav(this, 'dashboard')">
        <span class="nav-icon">⊞</span> Dashboard
      </div>
      <div class="nav-item" onclick="setNav(this, 'payroll')">
        <span class="nav-icon">💰</span> Payroll
      </div>
      <div class="nav-item" onclick="setNav(this, 'employees')">
        <span class="nav-icon">👥</span> Employees
      </div>
    </div>
    <div class="nav-section">
      <div class="nav-label">Reports</div>
      <div class="nav-item" onclick="setNav(this, 'reports')">
        <span class="nav-icon">📊</span> Reports
      </div>
      <div class="nav-item" onclick="setNav(this, 'tax')">
        <span class="nav-icon">🗂</span> Tax & Compliance
      </div>
      <div class="nav-item" onclick="setNav(this, 'history')">
        <span class="nav-icon">🕓</span> Pay History
      </div>
    </div>
    <div class="nav-section">
      <div class="nav-label">Config</div>
      <div class="nav-item" onclick="setNav(this, 'deductions')">
        <span class="nav-icon">⚙</span> Deductions
      </div>
      <div class="nav-item" onclick="setNav(this, 'settings')">
        <span class="nav-icon">◎</span> Settings
      </div>
    </div>
  </nav>
  <div class="sidebar-footer">
    <div class="user-chip">
      <div class="avatar">AD</div>
      <div class="user-info">
        <div class="user-name">Admin</div>
        <div class="user-role">HR MANAGER</div>
      </div>
    </div>
  </div>
</aside>

<!-- MAIN CONTENT -->
<main class="main">
  <div class="topbar">
    <div class="page-title">Dashboard Overview</div>
    <div class="topbar-actions">
      <button class="btn btn-ghost" onclick="exportPayroll()">⬇ Export</button>
      <button class="btn btn-primary" onclick="openModal('addEmployeeModal')">+ Add Employee</button>
    </div>
  </div>

  <div class="content">

    <!-- TABS -->
    <div class="tabs">
      <button class="tab active" onclick="setTab(this,'all')">All Employees</button>
      <button class="tab" onclick="setTab(this,'full')">Full-Time</button>
      <button class="tab" onclick="setTab(this,'part')">Part-Time</button>
      <button class="tab" onclick="setTab(this,'contract')">Contract</button>
    </div>

    <!-- KPI CARDS -->
    <div class="kpi-grid">
      <div class="kpi-card green">
        <div class="kpi-label">Total Employees</div>
        <div class="kpi-value" id="totalEmp">8</div>
        <div class="kpi-change up">↑ 2 this month</div>
      </div>
      <div class="kpi-card blue">
        <div class="kpi-label">Monthly Payroll</div>
        <div class="kpi-value" id="totalPayroll">$0</div>
        <div class="kpi-change up">↑ 3.2% vs last</div>
      </div>
      <div class="kpi-card yellow">
        <div class="kpi-label">Total Deductions</div>
        <div class="kpi-value" id="totalDeductions">$0</div>
        <div class="kpi-change down">↓ Tax + Benefits</div>
      </div>
      <div class="kpi-card red">
        <div class="kpi-label">Net Disbursement</div>
        <div class="kpi-value" id="netDisbursement">$0</div>
        <div class="kpi-change up">↑ Ready to process</div>
      </div>
    </div>

    <!-- MAIN LAYOUT -->
    <div class="layout-grid">
      <!-- EMPLOYEE TABLE -->
      <div class="panel">
        <div class="panel-header">
          <div>
            <div class="panel-title">Employee Payroll</div>
            <div class="panel-meta" id="periodLabel">Period: May 2025</div>
          </div>
          <div class="search-bar">
            <span style="color:var(--muted);font-size:14px">⌕</span>
            <input type="text" placeholder="Search employees..." id="searchInput" oninput="filterTable()">
          </div>
        </div>
        <table id="empTable">
          <thead>
            <tr>
              <th>Employee</th>
              <th>Department</th>
              <th>Type</th>
              <th>Gross Pay</th>
              <th>Deductions</th>
              <th>Net Pay</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody id="empTableBody"></tbody>
        </table>
      </div>

      <!-- SUMMARY PANEL -->
      <div class="summary-card">
        <div class="summary-header">
          <div class="period-badge">MAY 2025 · CYCLE 1</div>
          <div class="panel-title">Payroll Summary</div>
        </div>
        <div class="summary-body">
          <div class="summary-row">
            <span class="label">Gross Salaries</span>
            <span class="val" id="sumGross">$0.00</span>
          </div>
          <div class="summary-row">
            <span class="label">Income Tax</span>
            <span class="val" style="color:var(--accent2)" id="sumTax">-$0.00</span>
          </div>
          <div class="summary-row">
            <span class="label">Social Security</span>
            <span class="val" style="color:var(--accent2)" id="sumSS">-$0.00</span>
          </div>
          <div class="summary-row">
            <span class="label">Health Insurance</span>
            <span class="val" style="color:var(--accent2)" id="sumHealth">-$0.00</span>
          </div>
          <div class="summary-row">
            <span class="label">Pension (5%)</span>
            <span class="val" style="color:var(--accent2)" id="sumPension">-$0.00</span>
          </div>
          <div class="summary-row">
            <span class="label">Employees Paid</span>
            <span class="val" id="sumCount">0</span>
          </div>
          <div class="summary-total">
            <span class="label">Net Total</span>
            <span class="val" id="sumNet">$0.00</span>
          </div>
          <button class="run-btn" onclick="runPayroll()">⚡ Run Payroll</button>
        </div>
      </div>
    </div>

  </div>
</main>

<!-- ADD EMPLOYEE MODAL -->
<div class="modal-overlay" id="addEmployeeModal">
  <div class="modal">
    <div class="modal-header">
      <div class="modal-title">Add New Employee</div>
      <button class="close-btn" onclick="closeModal('addEmployeeModal')">✕</button>
    </div>
    <div class="modal-body">
      <div class="form-grid">
        <div class="form-group">
          <label class="form-label">First Name</label>
          <input class="form-input" id="fName" placeholder="John">
        </div>
        <div class="form-group">
          <label class="form-label">Last Name</label>
          <input class="form-input" id="lName" placeholder="Doe">
        </div>
        <div class="form-group">
          <label class="form-label">Employee ID</label>
          <input class="form-input" id="empId" placeholder="EMP-009">
        </div>
        <div class="form-group">
          <label class="form-label">Department</label>
          <select class="form-select" id="dept">
            <option>Engineering</option>
            <option>Marketing</option>
            <option>Finance</option>
            <option>HR</option>
            <option>Operations</option>
            <option>Design</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Employment Type</label>
          <select class="form-select" id="empType">
            <option>Full-Time</option>
            <option>Part-Time</option>
            <option>Contract</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Gross Salary ($)</label>
          <input class="form-input" id="salary" type="number" placeholder="5000">
        </div>
        <div class="form-group full">
          <label class="form-label">Pay Status</label>
          <select class="form-select" id="payStatus">
            <option>Pending</option>
            <option>Paid</option>
            <option>On Hold</option>
          </select>
        </div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-ghost" onclick="closeModal('addEmployeeModal')">Cancel</button>
      <button class="btn btn-primary" onclick="addEmployee()">Save Employee</button>
    </div>
  </div>
</div>

<!-- PAYSLIP MODAL -->
<div class="modal-overlay" id="payslipModal">
  <div class="modal payslip-modal">
    <div class="payslip-header">
      <div style="display:flex;justify-content:space-between;align-items:start">
        <div>
          <div class="payslip-company">PayOS Corp.</div>
          <div class="payslip-meta">PAYSLIP · MAY 2025 · CYCLE 1</div>
        </div>
        <button class="close-btn" onclick="closeModal('payslipModal')">✕</button>
      </div>
    </div>
    <div class="payslip-emp-info" id="payslipInfo"></div>
    <div class="payslip-table">
      <div class="payslip-section-title">Earnings</div>
      <div id="payslipEarnings"></div>
      <div class="payslip-section-title" style="margin-top:16px">Deductions</div>
      <div id="payslipDeductions"></div>
    </div>
    <div class="payslip-net">
      <div class="net-label">NET PAY</div>
      <div class="net-val" id="payslipNet"></div>
    </div>
  </div>
</div>

<!-- TOAST -->
<div class="toast" id="toast">
  <span class="toast-icon" id="toastIcon">✓</span>
  <span id="toastMsg">Action completed</span>
</div>

<script>
// DATA
const colors = ['#4fffb0','#60b4ff','#ffd93d','#ff6b6b','#c084fc','#fb923c','#34d399','#f472b6'];

let employees = [
  { id:'EMP-001', name:'Alice Johnson', dept:'Engineering', type:'Full-Time', gross:7800, status:'Paid' },
  { id:'EMP-002', name:'Marcus Chen',   dept:'Marketing',   type:'Full-Time', gross:6200, status:'Pending' },
  { id:'EMP-003', name:'Priya Sharma',  dept:'Finance',     type:'Full-Time', gross:8500, status:'Paid' },
  { id:'EMP-004', name:'James Osei',    dept:'HR',          type:'Part-Time', gross:3200, status:'Paid' },
  { id:'EMP-005', name:'Sofia Torres',  dept:'Design',      type:'Contract',  gross:5500, status:'On Hold' },
  { id:'EMP-006', name:'Liam Patel',    dept:'Engineering', type:'Full-Time', gross:9200, status:'Pending' },
  { id:'EMP-007', name:'Nana Ama',      dept:'Operations',  type:'Full-Time', gross:5900, status:'Paid' },
  { id:'EMP-008', name:'David Kim',     dept:'Finance',     type:'Contract',  gross:7100, status:'Paid' },
];

// DEDUCTION RATES
const TAX_RATE    = 0.20;
const SS_RATE     = 0.065;
const HEALTH_RATE = 0.03;
const PENSION_RATE= 0.05;

function calcDeductions(gross) {
  const tax     = gross * TAX_RATE;
  const ss      = gross * SS_RATE;
  const health  = gross * HEALTH_RATE;
  const pension = gross * PENSION_RATE;
  const total   = tax + ss + health + pension;
  return { tax, ss, health, pension, total, net: gross - total };
}

function fmt(n) { return '$' + n.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g,','); }

function initials(name) { return name.split(' ').map(w=>w[0]).join('').toUpperCase(); }

function statusBadge(s) {
  if(s==='Paid') return 'badge-green';
  if(s==='Pending') return 'badge-yellow';
  if(s==='On Hold') return 'badge-red';
  return 'badge-blue';
}

let activeFilter = 'all';

function renderTable(list) {
  const body = document.getElementById('empTableBody');
  body.innerHTML = '';
  list.forEach((e, i) => {
    const d = calcDeductions(e.gross);
    const col = colors[i % colors.length];
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>
        <div class="emp-cell">
          <div class="mini-avatar" style="background:${col}">${initials(e.name)}</div>
          <div>
            <div class="emp-name">${e.name}</div>
            <div class="emp-id">${e.id}</div>
          </div>
        </div>
      </td>
      <td>${e.dept}</td>
      <td><span class="badge ${e.type==='Full-Time'?'badge-green':e.type==='Part-Time'?'badge-yellow':'badge-blue'}">${e.type}</span></td>
      <td><span class="amount">${fmt(e.gross)}</span></td>
      <td><span class="amount" style="color:var(--accent2)">${fmt(d.total)}</span></td>
      <td><span class="amount" style="color:var(--accent)">${fmt(d.net)}</span></td>
      <td><span class="badge ${statusBadge(e.status)}">${e.status}</span></td>
      <td>
        <div class="action-btns">
          <button class="icon-btn" title="View Payslip" onclick="viewPayslip(${i})">🧾</button>
          <button class="icon-btn" title="Edit" onclick="editEmp(${i})">✏</button>
          <button class="icon-btn" title="Delete" onclick="deleteEmp(${i})">✕</button>
        </div>
      </td>
    `;
    body.appendChild(tr);
  });
  updateKPIs();
}

function getFiltered() {
  let list = employees;
  if(activeFilter==='full') list = list.filter(e=>e.type==='Full-Time');
  if(activeFilter==='part') list = list.filter(e=>e.type==='Part-Time');
  if(activeFilter==='contract') list = list.filter(e=>e.type==='Contract');
  const q = document.getElementById('searchInput').value.toLowerCase();
  if(q) list = list.filter(e=>e.name.toLowerCase().includes(q)||e.dept.toLowerCase().includes(q)||e.id.toLowerCase().includes(q));
  return list;
}

function updateKPIs() {
  const grossTotal = employees.reduce((s,e)=>s+e.gross,0);
  const deductTotal = employees.reduce((s,e)=>s+calcDeductions(e.gross).total,0);
  const netTotal = grossTotal - deductTotal;

  document.getElementById('totalEmp').textContent = employees.length;
  document.getElementById('totalPayroll').textContent = fmt(grossTotal);
  document.getElementById('totalDeductions').textContent = fmt(deductTotal);
  document.getElementById('netDisbursement').textContent = fmt(netTotal);

  document.getElementById('sumGross').textContent = fmt(grossTotal);
  const taxSum = employees.reduce((s,e)=>s+calcDeductions(e.gross).tax,0);
  const ssSum  = employees.reduce((s,e)=>s+calcDeductions(e.gross).ss,0);
  const hlSum  = employees.reduce((s,e)=>s+calcDeductions(e.gross).health,0);
  const penSum = employees.reduce((s,e)=>s+calcDeductions(e.gross).pension,0);

  document.getElementById('sumTax').textContent = '-'+fmt(taxSum);
  document.getElementById('sumSS').textContent  = '-'+fmt(ssSum);
  document.getElementById('sumHealth').textContent = '-'+fmt(hlSum);
  document.getElementById('sumPension').textContent = '-'+fmt(penSum);
  document.getElementById('sumCount').textContent = employees.length;
  document.getElementById('sumNet').textContent = fmt(netTotal);
}

function filterTable() { renderTable(getFiltered()); }

function setTab(el, filter) {
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  el.classList.add('active');
  activeFilter = filter;
  filterTable();
}

function setNav(el) {
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  el.classList.add('active');
  showToast('⚙', 'Section: ' + el.textContent.trim());
}

function openModal(id) { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }

function addEmployee() {
  const fn = document.getElementById('fName').value.trim();
  const ln = document.getElementById('lName').value.trim();
  const id = document.getElementById('empId').value.trim();
  const dept = document.getElementById('dept').value;
  const type = document.getElementById('empType').value;
  const gross = parseFloat(document.getElementById('salary').value);
  const status = document.getElementById('payStatus').value;

  if(!fn || !ln || !id || isNaN(gross) || gross <= 0) {
    showToast('⚠', 'Please fill all fields correctly'); return;
  }

  employees.push({ id, name: fn + ' ' + ln, dept, type, gross, status });
  closeModal('addEmployeeModal');
  ['fName','lName','empId','salary'].forEach(f => document.getElementById(f).value = '');
  renderTable(getFiltered());
  showToast('✓', `${fn} ${ln} added successfully`);
}

function deleteEmp(i) {
  const filtered = getFiltered();
  const emp = filtered[i];
  const realIdx = employees.indexOf(emp);
  if(realIdx > -1) {
    const name = employees[realIdx].name;
    employees.splice(realIdx, 1);
    renderTable(getFiltered());
    showToast('🗑', name + ' removed');
  }
}

function editEmp(i) {
  const filtered = getFiltered();
  const emp = filtered[i];
  const newSalary = prompt(`Update gross salary for ${emp.name}:`, emp.gross);
  if(newSalary !== null && !isNaN(parseFloat(newSalary)) && parseFloat(newSalary) > 0) {
    const realIdx = employees.indexOf(emp);
    employees[realIdx].gross = parseFloat(newSalary);
    renderTable(getFiltered());
    showToast('✓', 'Salary updated for ' + emp.name);
  }
}

function viewPayslip(i) {
  const filtered = getFiltered();
  const emp = filtered[i];
  const d = calcDeductions(emp.gross);
  const col = colors[i % colors.length];

  document.getElementById('payslipInfo').innerHTML = `
    <div class="info-item">
      <div class="info-label">Employee Name</div>
      <div class="info-val">${emp.name}</div>
    </div>
    <div class="info-item">
      <div class="info-label">Employee ID</div>
      <div class="info-val" style="font-family:var(--mono)">${emp.id}</div>
    </div>
    <div class="info-item">
      <div class="info-label">Department</div>
      <div class="info-val">${emp.dept}</div>
    </div>
    <div class="info-item">
      <div class="info-label">Employment Type</div>
      <div class="info-val">${emp.type}</div>
    </div>
    <div class="info-item">
      <div class="info-label">Pay Period</div>
      <div class="info-val">May 1–31, 2025</div>
    </div>
    <div class="info-item">
      <div class="info-label">Pay Status</div>
      <div class="info-val"><span class="badge ${statusBadge(emp.status)}">${emp.status}</span></div>
    </div>
  `;

  document.getElementById('payslipEarnings').innerHTML = `
    <div class="payslip-row"><span class="p-label">Basic Salary</span><span class="p-val">${fmt(emp.gross)}</span></div>
    <div class="payslip-row"><span class="p-label">Overtime</span><span class="p-val" style="color:var(--accent)">$0.00</span></div>
    <div class="payslip-row"><span class="p-label">Allowances</span><span class="p-val" style="color:var(--accent)">$0.00</span></div>
    <div class="payslip-row" style="border-top:1px solid var(--border);margin-top:6px;padding-top:10px;font-weight:600"><span class="p-label" style="color:var(--text)">Total Earnings</span><span class="p-val">${fmt(emp.gross)}</span></div>
  `;

  document.getElementById('payslipDeductions').innerHTML = `
    <div class="payslip-row"><span class="p-label">Income Tax (20%)</span><span class="p-val" style="color:var(--accent2)">-${fmt(d.tax)}</span></div>
    <div class="payslip-row"><span class="p-label">Social Security (6.5%)</span><span class="p-val" style="color:var(--accent2)">-${fmt(d.ss)}</span></div>
    <div class="payslip-row"><span class="p-label">Health Insurance (3%)</span><span class="p-val" style="color:var(--accent2)">-${fmt(d.health)}</span></div>
    <div class="payslip-row"><span class="p-label">Pension (5%)</span><span class="p-val" style="color:var(--accent2)">-${fmt(d.pension)}</span></div>
    <div class="payslip-row" style="border-top:1px solid var(--border);margin-top:6px;padding-top:10px;font-weight:600"><span class="p-label" style="color:var(--text)">Total Deductions</span><span class="p-val" style="color:var(--accent2)">-${fmt(d.total)}</span></div>
  `;

  document.getElementById('payslipNet').textContent = fmt(d.net);
  openModal('payslipModal');
}

function runPayroll() {
  employees.forEach(e => {
    if(e.status === 'Pending') e.status = 'Paid';
  });
  renderTable(getFiltered());
  showToast('⚡', 'Payroll processed successfully!');
}

function exportPayroll() {
  let csv = 'ID,Name,Department,Type,Gross,Deductions,Net,Status\n';
  employees.forEach(e => {
    const d = calcDeductions(e.gross);
    csv += `${e.id},"${e.name}",${e.dept},${e.type},${e.gross.toFixed(2)},${d.total.toFixed(2)},${d.net.toFixed(2)},${e.status}\n`;
  });
  const blob = new Blob([csv], {type:'text/csv'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'payroll_may2025.csv';
  a.click();
  showToast('⬇', 'Payroll exported as CSV');
}

function showToast(icon, msg) {
  const t = document.getElementById('toast');
  document.getElementById('toastIcon').textContent = icon;
  document.getElementById('toastMsg').textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

// Close modal on overlay click
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', e => {
    if(e.target === overlay) overlay.classList.remove('open');
  });
});

// INIT
renderTable(employees);
</script>
</body>
</html>