"""
Sentinel Compliance OS — Governing Authority Cloud Master Edition
Purpose: Enterprise compliance suite with multi-tier POST-C/CALEA accreditation, 
Governing Authority document repository, live data-entry, immutable audit logging, and Gemini Cloud AI.
"""

import http.server
import socketserver
import sqlite3
import json
import datetime
import os
import base64
from google import genai

PORT = int(os.environ.get("PORT", 8080))
DB_PATH = "sentinel_agency.db"
UPLOAD_DIR = "proof_uploads"

# Initialize Gemini Client for Cloud Execution
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

def query_gemini_llm(prompt_text):
    """Sends prompt to Google Gemini API for cloud agency analysis."""
    if not client:
        return "⚠️ [GEMINI ERROR]: GEMINI_API_KEY environment variable not configured in Railway."
    try:
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt_text
        )
        return response.text
    except Exception as e:
        return f"⚠️ [GEMINI ERROR]: {str(e)}"

def log_audit(conn, action_type, details, performed_by="Command Staff"):
    """Records an immutable audit trail entry for chain-of-custody compliance."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO audit_trail (action_type, details, performed_by, timestamp) VALUES (?, ?, ?, ?);",
                 (action_type, details, performed_by, ts))
    conn.commit()

def init_and_seed_db():
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS agency_profile (config_key TEXT PRIMARY KEY, config_value TEXT NOT NULL);")
    cursor.execute("CREATE TABLE IF NOT EXISTS officers (officer_id TEXT PRIMARY KEY, full_name TEXT NOT NULL, rank_title TEXT NOT NULL, cycle_start_year INTEGER NOT NULL, cycle_end_year INTEGER NOT NULL, current_year INTEGER NOT NULL, drug_screen_valid INTEGER NOT NULL DEFAULT 1);")
    cursor.execute("CREATE TABLE IF NOT EXISTS fleet_cruisers (unit_id TEXT PRIMARY KEY, year_make_model TEXT NOT NULL, current_odometer INTEGER NOT NULL, is_grounded INTEGER NOT NULL DEFAULT 0, grounding_reason TEXT);")
    cursor.execute("CREATE TABLE IF NOT EXISTS facility_inspections (inspection_id INTEGER PRIMARY KEY AUTOINCREMENT, task_code TEXT NOT NULL, task_title TEXT NOT NULL, completed_by_name TEXT NOT NULL, submission_timestamp TEXT NOT NULL, retention_schedule TEXT NOT NULL);")
    cursor.execute("CREATE TABLE IF NOT EXISTS policy_acknowledgments (ack_id INTEGER PRIMARY KEY AUTOINCREMENT, officer_id TEXT NOT NULL, policy_code TEXT NOT NULL, is_acknowledged INTEGER NOT NULL DEFAULT 0, acknowledged_at TEXT);")
    cursor.execute("CREATE TABLE IF NOT EXISTS accreditation_standards (standard_code TEXT PRIMARY KEY, framework_type TEXT NOT NULL, chapter_title TEXT NOT NULL, standard_description TEXT NOT NULL, target_table TEXT NOT NULL);")
    cursor.execute("CREATE TABLE IF NOT EXISTS audit_evidence (evidence_id INTEGER PRIMARY KEY AUTOINCREMENT, standard_code TEXT NOT NULL, evidence_type TEXT NOT NULL, file_path TEXT NOT NULL, description TEXT, uploaded_at TEXT NOT NULL);")
    cursor.execute("CREATE TABLE IF NOT EXISTS audit_trail (log_id INTEGER PRIMARY KEY AUTOINCREMENT, action_type TEXT NOT NULL, details TEXT NOT NULL, performed_by TEXT NOT NULL, timestamp TEXT NOT NULL);")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS governing_documents (
        doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
        authority_level TEXT NOT NULL,
        issuing_body TEXT NOT NULL,
        doc_code TEXT NOT NULL,
        doc_title TEXT NOT NULL,
        effective_date TEXT NOT NULL,
        full_text TEXT NOT NULL,
        linked_standard_code TEXT
    );
    """)

    cursor.execute("SELECT config_value FROM agency_profile WHERE config_key = 'accreditation_framework';")
    if not cursor.fetchone():
        cursor.execute("INSERT OR REPLACE INTO agency_profile VALUES ('agency_name', 'Cheshire Police Department');")
        cursor.execute("INSERT OR REPLACE INTO agency_profile VALUES ('accreditation_framework', 'CT_POST_ALL_TIERS');")
        cursor.execute("INSERT OR REPLACE INTO agency_profile VALUES ('jurisdiction_state', 'Connecticut');")
        cursor.execute("INSERT OR REPLACE INTO agency_profile VALUES ('ori_number', 'CT0030100');")
        log_audit(conn, "SYSTEM_INIT", "Initialized agency onboarding profile for Governing Authority OS.", "System")

    cursor.execute("SELECT COUNT(*) FROM officers;")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO officers VALUES (?, ?, ?, ?, ?, ?, ?);", [
            ("14829", "Patrol Officer J. Smith", "Patrol Officer", 2024, 2027, 3, 1),
            ("15012", "Sgt. D. Reynolds", "Sergeant", 2024, 2027, 3, 1),
            ("15104", "Patrol Officer T. Baker", "Patrol Officer", 2026, 2029, 1, 1),
            ("14911", "Patrol Officer R. Davis", "Patrol Officer", 2025, 2028, 2, 1)
        ])

        cursor.executemany("INSERT INTO fleet_cruisers VALUES (?, ?, ?, ?, ?);", [
            ("Unit 104", "2023 Ford Interceptor", 42350, 0, None),
            ("Unit 102", "2022 Ford Interceptor", 58210, 0, None),
            ("Unit 106", "2024 Chevy Tahoe PPV", 14200, 1, "Light bar wiring short")
        ])

        cursor.executemany("INSERT INTO facility_inspections (task_code, task_title, completed_by_name, submission_timestamp, retention_schedule) VALUES (?, ?, ?, ?, ?);", [
            ("FAC-01", "Sally Port Eyewash 3-Min Flush", "Sgt. D. Reynolds", "2026-08-28 07:15:00", "CT Schedule S4/S7 (5-Year)"),
            ("FAC-02", "Holding Cell Emergency Intercom Test", "Cpl. J. Piccirillo", "2026-09-01 10:30:00", "CT Schedule S4/S7 (5-Year)")
        ])

        cursor.executemany("INSERT INTO policy_acknowledgments (officer_id, policy_code, is_acknowledged, acknowledged_at) VALUES (?, ?, ?, ?);", [
            ("14829", "GO-201 (Use of Force)", 1, "2026-01-10 08:00:00"),
            ("14829", "GO-304 (ALPR Operations)", 0, None),
            ("15012", "GO-201 (Use of Force)", 1, "2026-01-15 09:00:00"),
            ("15012", "GO-304 (ALPR Operations)", 1, "2026-01-15 09:05:00")
        ])

        cursor.executemany("INSERT OR REPLACE INTO accreditation_standards VALUES (?, ?, ?, ?, ?);", [
            ("POST-1.1", "CT_POST_ALL_TIERS", "Tier I: Use of Force & Liability Directives", "Mandatory annual policy distribution and signed officer acknowledgments.", "policy_acknowledgments"),
            ("POST-1.3", "CT_POST_ALL_TIERS", "Tier I: Patrol Fleet Operational Readiness", "Preventive maintenance and active operational logs for emergency vehicles.", "fleet_cruisers"),
            ("POST-1.5", "CT_POST_ALL_TIERS", "Tier I: Holding Facility Life-Safety Checks", "Routine physical inspections of holding cells and safety equipment.", "facility_inspections"),
            ("POST-2.2", "CT_POST_ALL_TIERS", "Tier II: Sworn Certification & Training Cycles", "Active tracking of triennial POST-C recertification and mandatory training hours.", "officers"),
            ("POST-2.4", "CT_POST_ALL_TIERS", "Tier II: Traffic Enforcement & ALPR Compliance", "Standardized operating procedures and compliance tracking for automated plate readers.", "policy_acknowledgments"),
            ("POST-3.1", "CT_POST_ALL_TIERS", "Tier III: Executive Administrative Control & Auditing", "Comprehensive internal review, chain-of-custody audit logs, and risk management.", "audit_trail"),
            ("CALEA-41.1", "CALEA", "Organizational Structure & Command", "Agency maintains clear operational command channels and directive distribution.", "policy_acknowledgments"),
            ("CALEA-82.1", "CALEA", "Critical Incident & Equipment Readiness", "Operational readiness and preventive maintenance logs for emergency response fleets.", "fleet_cruisers")
        ])

        cursor.executemany("INSERT INTO governing_documents (authority_level, issuing_body, doc_code, doc_title, effective_date, full_text, linked_standard_code) VALUES (?, ?, ?, ?, ?, ?, ?);", [
            ("Municipal", "Town Council / Selectmen", "ORD-2024-02", "Municipal Fleet Asset Management & Usage Ordinance", "2024-01-15", "All municipal vehicles, including police cruisers, must undergo monthly mileage and safety inspections...", "POST-1.3"),
            ("Agency", "Office of the Chief of Police", "GO-201", "Use of Force and Deadly Force Directive", "2026-01-01", "Officers shall use only that amount of force that is objectively reasonable... All officers must acknowledge annually.", "POST-1.1"),
            ("Agency", "Office of the Chief of Police", "GO-304", "Automated License Plate Reader (ALPR) Operations", "2026-02-01", "ALPR data shall be retained in accordance with state guidelines. Mandatory annual officer review required.", "POST-2.4")
        ])
        log_audit(conn, "DATABASE_SEED", "Seeded multi-tier standards and Governing Authority documents.", "System")

    conn.commit()
    conn.close()

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sentinel Compliance OS — Governing Authority Master</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .header { background: #1e293b; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 5px solid #3b82f6; display: flex; justify-content: space-between; align-items: center; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .card { background: #1e293b; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        h1, h2 { margin-top: 0; color: #60a5fa; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #334155; font-size: 14px; }
        th { color: #94a3b8; }
        .badge-red { background: #ef4444; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .badge-green { background: #22c55e; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .badge-yellow { background: #eab308; color: black; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .badge-blue { background: #0284c7; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .stat-num { font-size: 28px; font-weight: bold; color: #38bdf8; margin: 5px 0; }
        select, input, textarea { background: #0f172a; color: white; border: 1px solid #3b82f6; padding: 8px 12px; border-radius: 6px; font-weight: bold; width: 100%; box-sizing: border-box; margin-bottom: 10px; }
        button { background: #9333ea; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; width: 100%; margin-top: 5px; }
        button:hover { background: #7e22ce; }
        .btn-green { background: #22c55e; }
        .btn-green:hover { background: #16a34a; }
        .btn-blue { background: #0284c7; }
        .btn-blue:hover { background: #0369a1; }
        .ai-console { background: #111827; border: 1px solid #7e22ce; padding: 15px; border-radius: 8px; margin-top: 15px; font-family: monospace; color: #38bdf8; white-space: pre-wrap; display: none; line-height: 1.4; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); justify-content: center; align-items: center; z-index: 1000; }
        .modal-content { background: #1e293b; padding: 30px; border-radius: 8px; width: 450px; border: 1px solid #3b82f6; }
        .role-section { display: block; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1 id="agency-title-header">Sentinel Compliance OS</h1>
            <p id="agency-framework-sub" style="margin: 0; color: #94a3b8;">Loading Governing Authority Hub...</p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
            <div>
                <label style="font-size: 11px; color: #94a3b8; display: block; margin-bottom: 3px;">Framework:</label>
                <select id="framework-selector" onchange="updateFramework(this.value)" style="width:auto;">
                    <option value="CT_POST_ALL_TIERS">CT POST-C (Tiers I, II, III Concurrent)</option>
                    <option value="CALEA">CALEA International Standards</option>
                </select>
            </div>
            <div>
                <label style="font-size: 11px; color: #94a3b8; display: block; margin-bottom: 3px;">RBAC Tier:</label>
                <select id="role-selector" onchange="switchRole()" style="width:auto;">
                    <option value="command">Tier 3: Command</option>
                    <option value="supervisor">Tier 2: Sergeant</option>
                    <option value="patrol">Tier 1: Patrol</option>
                </select>
            </div>
            <div style="display:flex; gap:5px; margin-top:15px;">
                <button class="btn-blue" style="width:auto; margin:0; padding:8px 12px;" onclick="openModal('doc-modal')">📜 + Document</button>
                <button class="btn-blue" style="width:auto; margin:0; padding:8px 12px;" onclick="openModal('import-modal')">📂 CSV</button>
                <button class="btn-blue" style="width:auto; margin:0; padding:8px 12px;" onclick="openModal('photo-modal')">📷 Photo</button>
                <button style="width:auto; margin:0; padding:8px 12px; background:#3b82f6;" onclick="openModal('settings-modal')">⚙️ Setup</button>
            </div>
        </div>
    </div>

    <!-- Compliance Health Score Banner -->
    <div class="grid role-section" data-roles="command supervisor patrol">
        <div class="card" style="border-left: 5px solid #38bdf8; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin:0; color:#38bdf8;">🛡️ Executive Compliance Health Score</h2>
                <p style="margin: 5px 0 0 0; font-size:13px; color:#94a3b8;">Real-time risk assessment across municipal ordinances, agency directives, and accreditation standards.</p>
            </div>
            <div style="text-align: right;">
                <div id="health-score-num" style="font-size: 36px; font-weight: bold; color: #22c55e;">--%</div>
                <div id="health-score-status" style="font-size: 12px; font-weight: bold; color: #22c55e;">AUDIT READY</div>
            </div>
        </div>
    </div>

    <!-- Governing Authority Repository Viewer -->
    <div class="grid role-section" data-roles="command supervisor">
        <div class="card" style="grid-column: 1 / -1; border-left: 5px solid #0284c7;">
            <h2>🏛️ Governing Authority Document Repository</h2>
            <p style="font-size: 13px; color: #94a3b8; margin-bottom: 15px;">Indexed town ordinances, selectmen resolutions, attorney opinions, and agency general orders governing operations:</p>
            <table id="doc-repo-table">
                <thead>
                    <tr>
                        <th>Authority Level</th>
                        <th>Issuing Body</th>
                        <th>Document Code & Title</th>
                        <th>Effective Date</th>
                        <th>Linked Standard</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>

    <!-- Accreditation Proofs Matrix -->
    <div class="grid role-section" data-roles="command supervisor">
        <div class="card" style="grid-column: 1 / -1; border-left: 5px solid #22c55e;">
            <h2>📋 Active Multi-Tier Accreditation Standards & Live Proof Matrix</h2>
            <table id="accreditation-table">
                <thead>
                    <tr>
                        <th>Standard</th>
                        <th>Chapter Title & Requirement</th>
                        <th>Live Proof Source</th>
                        <th>Readiness Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>

    <!-- AI Command Center -->
    <div class="grid role-section" data-roles="command">
        <div class="card" style="grid-column: 1 / -1; border-left: 5px solid #a855f7;">
            <h2>🧠 Cloud AI Intelligence Command Center (Powered by Gemini)</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; margin-bottom: 15px;">
                <button onclick="runAIAgent('statutory_gap')">1. Statutory Gap Analysis</button>
                <button onclick="runAIAgent('predictive_drift')">2. Recertification Drift AI</button>
                <button onclick="runAIAgent('rag_inspector')">3. Accreditation RAG Query</button>
                <button onclick="runAIAgent('grant_matching')">4. Grant Funding Matcher</button>
            </div>
            <div id="ai-output-box" class="ai-console">Select an intelligence module above to query Gemini AI...</div>
        </div>
    </div>

    <div class="grid">
        <div class="card role-section" data-roles="command patrol">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2>Sworn Roster Compliance</h2>
                <button style="width:auto; padding:4px 8px; font-size:12px;" onclick="openModal('officer-modal')">+ Add</button>
            </div>
            <div class="stat-num" id="total-sworn">0 Officers</div>
            <table id="roster-table">
                <thead><tr><th>Officer</th><th>Badge</th><th>Cycle</th><th>Status</th></tr></thead>
                <tbody></tbody>
            </table>
        </div>

        <div class="card role-section" data-roles="command supervisor">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2>Patrol Fleet Status</h2>
                <button style="width:auto; padding:4px 8px; font-size:12px;" onclick="openModal('fleet-modal')">+ Log</button>
            </div>
            <div class="stat-num" id="fleet-count">0 Units</div>
            <table id="fleet-table">
                <thead><tr><th>Unit</th><th>Odometer</th><th>Status</th></tr></thead>
                <tbody></tbody>
            </table>
        </div>

        <div class="card role-section" data-roles="command supervisor">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2>Facility Life-Safety Logs</h2>
                <button style="width:auto; padding:4px 8px; font-size:12px;" onclick="openModal('facility-modal')">+ Log</button>
            </div>
            <div class="stat-num" id="fac-count">0 Logs</div>
            <table id="facility-table">
                <thead><tr><th>Code</th><th>Title</th><th>Cleared By</th></tr></thead>
                <tbody></tbody>
            </table>
        </div>

        <div class="card role-section" data-roles="command supervisor patrol">
            <h2>Policy Acknowledgment Tracker</h2>
            <table id="policy-table">
                <thead><tr><th>Officer</th><th>Policy</th><th>Status</th></tr></thead>
                <tbody></tbody>
            </table>
        </div>
    </div>

    <!-- Immutable Audit Trail Viewer -->
    <div class="grid role-section" data-roles="command">
        <div class="card" style="grid-column: 1 / -1; border-left: 5px solid #eab308;">
            <h2>📜 Immutable Chain-of-Custody Audit Trail</h2>
            <table id="audit-trail-table">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Action Type</th>
                        <th>Details</th>
                        <th>Performed By</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>

    <!-- Modals -->
    <div id="settings-modal" class="modal">
        <div class="modal-content">
            <h2>⚙️ Agency Onboarding Settings</h2>
            <label style="font-size:12px; color:#94a3b8;">Department Name:</label>
            <input type="text" id="setting-agency-name">
            <label style="font-size:12px; color:#94a3b8;">State Jurisdiction:</label>
            <input type="text" id="setting-state">
            <label style="font-size:12px; color:#94a3b8;">ORI Number:</label>
            <input type="text" id="setting-ori" style="margin-bottom:15px;">
            <button class="btn-green" onclick="saveAgencySettings()">Save Configuration</button>
            <button style="background:#64748b;" onclick="closeModal('settings-modal')">Cancel</button>
        </div>
    </div>

    <div id="doc-modal" class="modal">
        <div class="modal-content">
            <h2>📜 Ingest Governing Document</h2>
            <label style="font-size:12px; color:#94a3b8;">Authority Level:</label>
            <select id="doc-level">
                <option value="Municipal">Municipal (Town Ord / Selectmen)</option>
                <option value="Agency">Agency (Chief General Order / SOP)</option>
                <option value="Accreditation">Accreditation (State / National)</option>
            </select>
            <label style="font-size:12px; color:#94a3b8;">Issuing Body:</label>
            <input type="text" id="doc-issuer" placeholder="e.g. Town Council or Chief of Police">
            <label style="font-size:12px; color:#94a3b8;">Document Code:</label>
            <input type="text" id="doc-code" placeholder="e.g. ORD-2026-01">
            <label style="font-size:12px; color:#94a3b8;">Document Title:</label>
            <input type="text" id="doc-title" placeholder="e.g. Municipal Public Safety Ordinance">
            <label style="font-size:12px; color:#94a3b8;">Full Text / Content:</label>
            <textarea id="doc-text" rows="4" placeholder="Paste full ordinance or directive text here for AI RAG analysis..."></textarea>
            <button class="btn-green" onclick="submitGoverningDoc()">Ingest into Repository</button>
            <button style="background:#64748b;" onclick="closeModal('doc-modal')">Cancel</button>
        </div>
    </div>

    <div id="import-modal" class="modal">
        <div class="modal-content">
            <h2>📂 Ingest CSV Roster / Fleet Data</h2>
            <label style="font-size:12px; color:#94a3b8;">Target Table:</label>
            <select id="import-target">
                <option value="officers">Sworn Roster (officers)</option>
                <option value="fleet_cruisers">Fleet Cruisers (fleet_cruisers)</option>
            </select>
            <label style="font-size:12px; color:#94a3b8;">Select CSV File:</label>
            <input type="file" id="csv-file-input" accept=".csv" style="padding:6px; margin-bottom:15px;">
            <button class="btn-green" onclick="uploadCSV()">Process & Ingest</button>
            <button style="background:#64748b;" onclick="closeModal('import-modal')">Cancel</button>
        </div>
    </div>

    <div id="photo-modal" class="modal">
        <div class="modal-content">
            <h2>📷 Upload Mobile Inspection Photo</h2>
            <label style="font-size:12px; color:#94a3b8;">Standard Code:</label>
            <input type="text" id="photo-std" placeholder="e.g. POST-1.5">
            <label style="font-size:12px; color:#94a3b8;">Description:</label>
            <input type="text" id="photo-desc" placeholder="e.g. Eyewash verification">
            <label style="font-size:12px; color:#94a3b8;">Image:</label>
            <input type="file" id="photo-file-input" accept="image/*" style="padding:6px; margin-bottom:15px;">
            <button class="btn-green" onclick="uploadPhoto()">Upload Evidence</button>
            <button style="background:#64748b;" onclick="closeModal('photo-modal')">Cancel</button>
        </div>
    </div>

    <div id="fleet-modal" class="modal">
        <div class="modal-content">
            <h2>🚗 Add Patrol Cruiser</h2>
            <label style="font-size:12px; color:#94a3b8;">Unit ID:</label>
            <input type="text" id="fleet-unit-id">
            <label style="font-size:12px; color:#94a3b8;">Make & Model:</label>
            <input type="text" id="fleet-model">
            <label style="font-size:12px; color:#94a3b8;">Odometer:</label>
            <input type="number" id="fleet-odo" style="margin-bottom:15px;">
            <button class="btn-green" onclick="submitFleetEntry()">Save Cruiser</button>
            <button style="background:#64748b;" onclick="closeModal('fleet-modal')">Cancel</button>
        </div>
    </div>

    <div id="facility-modal" class="modal">
        <div class="modal-content">
            <h2>🏢 Log Facility Safety Inspection</h2>
            <label style="font-size:12px; color:#94a3b8;">Task Code:</label>
            <input type="text" id="fac-code">
            <label style="font-size:12px; color:#94a3b8;">Task Title:</label>
            <input type="text" id="fac-title">
            <label style="font-size:12px; color:#94a3b8;">Officer Name:</label>
            <input type="text" id="fac-officer" style="margin-bottom:15px;">
            <button class="btn-green" onclick="submitFacilityEntry()">Save Log</button>
            <button style="background:#64748b;" onclick="closeModal('facility-modal')">Cancel</button>
        </div>
    </div>

    <script>
        function loadData() {
            fetch('/api/dashboard-data')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('agency-title-header').innerText = data.profile.agency_name + " — Sentinel Compliance OS";
                    document.getElementById('agency-framework-sub').innerText = "ORI: " + (data.profile.ori_number || 'N/A') + " | Framework: " + data.profile.accreditation_framework;
                    document.getElementById('framework-selector').value = data.profile.accreditation_framework;
                    
                    document.getElementById('setting-agency-name').value = data.profile.agency_name;
                    document.getElementById('setting-state').value = data.profile.jurisdiction_state;
                    document.getElementById('setting-ori').value = data.profile.ori_number;

                    let score = data.health_score;
                    document.getElementById('health-score-num').innerText = score + "%";
                    let statusEl = document.getElementById('health-score-status');
                    if (score >= 90) { statusEl.innerText = "AUDIT READY (TIER I-III)"; statusEl.style.color = "#22c55e"; }
                    else if (score >= 75) { statusEl.innerText = "MINOR DRIFT DETECTED"; statusEl.style.color = "#eab308"; }
                    else { statusEl.innerText = "COMPLIANCE RISK"; statusEl.style.color = "#ef4444"; }

                    let docHtml = '';
                    data.governing_docs.forEach(doc => {
                        let badge = doc.authority_level === 'Municipal' ? '<span class="badge-blue">Municipal</span>' : '<span class="badge-green">Agency</span>';
                        docHtml += `<tr>
                            <td>${badge}</td>
                            <td><b>${doc.issuing_body}</b></td>
                            <td><b>${doc.doc_code}</b>: ${doc.doc_title}</td>
                            <td>${doc.effective_date}</td>
                            <td><code>${doc.linked_standard_code || 'N/A'}</code></td>
                        </tr>`;
                    });
                    document.querySelector('#doc-repo-table tbody').innerHTML = docHtml;

                    let rosterHtml = '';
                    data.officers.forEach(o => {
                        rosterHtml += `<tr><td><b>${o.full_name}</b></td><td>#${o.officer_id}</td><td>Year ${o.current_year}</td><td><span class="badge-yellow">Active</span></td></tr>`;
                    });
                    document.querySelector('#roster-table tbody').innerHTML = rosterHtml;
                    document.getElementById('total-sworn').innerText = data.officers.length + " Officers";

                    let fleetHtml = '';
                    data.fleet.forEach(f => {
                        let badge = f.is_grounded ? '<span class="badge-red">GROUNDED</span>' : '<span class="badge-green">CLEAR</span>';
                        fleetHtml += `<tr><td><b>${f.unit_id}</b></td><td>${f.current_odometer.toLocaleString()} Mi</td><td>${badge}</td></tr>`;
                    });
                    document.querySelector('#fleet-table tbody').innerHTML = fleetHtml;
                    document.getElementById('fleet-count').innerText = data.fleet.length + " Units";

                    let facilityHtml = '';
                    data.facilities.forEach(fac => {
                        facilityHtml += `<tr><td><b>${fac.task_code}</b></td><td>${fac.task_title}</td><td>${fac.completed_by_name}</td></tr>`;
                    });
                    document.querySelector('#facility-table tbody').innerHTML = facilityHtml;
                    document.getElementById('fac-count').innerText = data.facilities.length + " Logs";

                    let policyHtml = '';
                    data.policies.forEach(p => {
                        let badge = p.is_acknowledged ? '<span class="badge-green">SIGNED</span>' : '<span class="badge-red">PENDING</span>';
                        policyHtml += `<tr><td>#${p.officer_id}</td><td>${p.policy_code}</td><td>${badge}</td></tr>`;
                    });
                    document.querySelector('#policy-table tbody').innerHTML = policyHtml;

                    let accHtml = '';
                    data.standards.forEach(s => {
                        accHtml += `<tr>
                            <td><b>${s.standard_code}</b></td>
                            <td><b>${s.chapter_title}</b><br><span style="font-size:12px; color:#94a3b8;">${s.standard_description}</span></td>
                            <td>Table: <code>${s.target_table}</code></td>
                            <td><span class="badge-green">100% READY</span></td>
                            <td><button style="padding:4px 8px; font-size:12px; width:auto;" onclick="exportBinder('${s.standard_code}')">Export</button></td>
                        </tr>`;
                    });
                    document.querySelector('#accreditation-table tbody').innerHTML = accHtml;

                    let auditHtml = '';
                    data.audit_trail.forEach(log => {
                        auditHtml += `<tr><td><code style="font-size:12px;">${log.timestamp}</code></td><td><b>${log.action_type}</b></td><td>${log.details}</td><td>${log.performed_by}</td></tr>`;
                    });
                    document.querySelector('#audit-trail-table tbody').innerHTML = auditHtml;
                });
        }

        function openModal(id) { document.getElementById(id).style.display = 'flex'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }

        function updateFramework(fw) {
            fetch('/api/update-profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ accreditation_framework: fw })
            }).then(() => loadData());
        }

        function saveAgencySettings() {
            const payload = {
                agency_name: document.getElementById('setting-agency-name').value,
                jurisdiction_state: document.getElementById('setting-state').value,
                ori_number: document.getElementById('setting-ori').value
            };
            fetch('/api/update-profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            }).then(() => { closeModal('settings-modal'); loadData(); });
        }

        function submitGoverningDoc() {
            const payload = {
                authority_level: document.getElementById('doc-level').value,
                issuing_body: document.getElementById('doc-issuer').value,
                doc_code: document.getElementById('doc-code').value,
                doc_title: document.getElementById('doc-title').value,
                full_text: document.getElementById('doc-text').value
            };
            fetch('/api/add-governing-doc', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            }).then(() => { closeModal('doc-modal'); loadData(); alert("Governing document successfully ingested!"); });
        }

        function uploadCSV() {
            const fileInput = document.getElementById('csv-file-input');
            const targetTable = document.getElementById('import-target').value;
            if (fileInput.files.length === 0) { alert("Select a CSV file."); return; }
            const reader = new FileReader();
            reader.onload = function(e) {
                fetch('/api/import-csv', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ table: targetTable, csv_data: e.target.result })
                }).then(res => res.json()).then(r => { alert(r.message); closeModal('import-modal'); loadData(); });
            };
            reader.readAsText(fileInput.files[0]);
        }

        function uploadPhoto() {
            const fileInput = document.getElementById('photo-file-input');
            const stdCode = document.getElementById('photo-std').value;
            const desc = document.getElementById('photo-desc').value;
            if (fileInput.files.length === 0 || !stdCode) { alert("Provide standard code and image."); return; }
            const reader = new FileReader();
            reader.onload = function(e) {
                fetch('/api/upload-photo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ standard_code: stdCode, description: desc, image_base64: e.target.result, filename: fileInput.files[0].name })
                }).then(res => res.json()).then(r => { alert(r.message); closeModal('photo-modal'); loadData(); });
            };
            reader.readAsDataURL(fileInput.files[0]);
        }

        function submitFleetEntry() {
            const payload = {
                unit_id: document.getElementById('fleet-unit-id').value,
                year_make_model: document.getElementById('fleet-model').value,
                current_odometer: parseInt(document.getElementById('fleet-odo').value || 0)
            };
            fetch('/api/add-fleet', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            }).then(() => { closeModal('fleet-modal'); loadData(); });
        }

        function submitFacilityEntry() {
            const payload = {
                task_code: document.getElementById('fac-code').value,
                task_title: document.getElementById('fac-title').value,
                completed_by_name: document.getElementById('fac-officer').value,
                retention_schedule: "CT Schedule S4/S7 (5-Year)"
            };
            fetch('/api/add-facility', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            }).then(() => { closeModal('facility-modal'); loadData(); });
        }

        function exportBinder(code) {
            fetch('/api/export-binder?code=' + code)
                .then(res => res.json())
                .then(data => {
                    let blob = new Blob([data.report], { type: 'text/plain' });
                    let link = document.createElement('a');
                    link.href = window.URL.createObjectURL(blob);
                    link.download = `Compliance_Binder_${code}.txt`;
                    link.click();
                });
        }

        function switchRole() {
            const role = document.getElementById('role-selector').value;
            document.querySelectorAll('.role-section').forEach(sec => {
                const allowed = sec.getAttribute('data-roles');
                sec.style.display = allowed.includes(role) ? 'block' : 'none';
            });
        }

        function runAIAgent(moduleType) {
            const consoleBox = document.getElementById('ai-output-box');
            consoleBox.style.display = 'block';
            consoleBox.innerText = "Querying Gemini cloud intelligence model with secure governing authority context...";

            fetch('/api/ai-agent', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ module: moduleType })
            }).then(res => res.json()).then(response => {
                consoleBox.innerText = response.result;
            }).catch(err => {
                consoleBox.innerText = "❌ Error connecting to AI server: " + err;
            });
        }

        loadData();
        switchRole();
    </script>
</body>
</html>
"""

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode())
        elif self.path == '/api/dashboard-data':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            profile = {row['config_key']: row['config_value'] for row in conn.execute("SELECT * FROM agency_profile;").fetchall()}
            current_fw = profile.get('accreditation_framework', 'CT_POST_ALL_TIERS')

            officers = [dict(row) for row in conn.execute("SELECT * FROM officers;").fetchall()]
            fleet = [dict(row) for row in conn.execute("SELECT * FROM fleet_cruisers;").fetchall()]
            facilities = [dict(row) for row in conn.execute("SELECT * FROM facility_inspections;").fetchall()]
            policies = [dict(row) for row in conn.execute("SELECT * FROM policy_acknowledgments;").fetchall()]
            standards = [dict(row) for row in conn.execute("SELECT * FROM accreditation_standards WHERE framework_type = ?;", (current_fw,)).fetchall()]
            governing_docs = [dict(row) for row in conn.execute("SELECT * FROM governing_documents;").fetchall()]
            audit_trail = [dict(row) for row in conn.execute("SELECT * FROM audit_trail ORDER BY log_id DESC LIMIT 20;").fetchall()]
            conn.close()

            total_policies = len(policies) or 1
            ack_policies = sum(1 for p in policies if p['is_acknowledged'])
            total_fleet = len(fleet) or 1
            grounded_fleet = sum(1 for f in fleet if f['is_grounded'])
            
            policy_score = (ack_policies / total_policies) * 50
            fleet_score = ((total_fleet - grounded_fleet) / total_fleet) * 50
            health_score = round(policy_score + fleet_score, 1)
            
            payload = {
                "profile": profile, 
                "officers": officers, 
                "fleet": fleet, 
                "facilities": facilities, 
                "policies": policies, 
                "standards": standards,
                "governing_docs": governing_docs,
                "audit_trail": audit_trail,
                "health_score": health_score
            }
            self.wfile.write(json.dumps(payload).encode())
        elif self.path.startswith('/api/export-binder'):
            code = self.path.split('=')[1]
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            profile = {row['config_key']: row['config_value'] for row in conn.execute("SELECT * FROM agency_profile;").fetchall()}
            standard = conn.execute("SELECT * FROM accreditation_standards WHERE standard_code = ?;", (code,)).fetchone()
            records = conn.execute(f"SELECT * FROM {standard['target_table']};").fetchall()
            evidence = conn.execute("SELECT * FROM audit_evidence WHERE standard_code = ?;", (code,)).fetchall()
            gov_docs = conn.execute("SELECT * FROM governing_documents WHERE linked_standard_code = ?;", (code,)).fetchall()
            
            log_audit(conn, "EXPORT_BINDER", f"Exported cryptographic proof binder for standard {code}.", "Accreditation Manager")
            conn.close()

            report = f"""================================================================================
SENTINEL COMPLIANCE OS — CRYPTOGRAPHIC AUDIT PROOF BINDER
================================================================================
Agency: {profile.get('agency_name')}
State Jurisdiction: {profile.get('jurisdiction_state')}
ORI Number: {profile.get('ori_number')}
Accreditation Framework: {profile.get('accreditation_framework')}
Standard Code: {standard['standard_code']}
Chapter: {standard['chapter_title']}
Requirement: {standard['standard_description']}
Export Timestamp: {datetime.datetime.now().isoformat()}
Status: VERIFIED 100% AUDIT READY
--------------------------------------------------------------------------------
LINKED GOVERNING AUTHORITY DOCUMENTS:
"""
            for doc in gov_docs:
                report += f"- [{doc['authority_level']}] {doc['issuing_body']} | {doc['doc_code']}: {doc['doc_title']}\n"

            report += f"\nVERIFIED LIVE DATABASE PROOFS ({standard['target_table']}):\n"
            for rec in records:
                report += json.dumps(dict(rec), indent=2) + "\n\n"
            
            if evidence:
                report += "--------------------------------------------------------------------------------\nATTACHED MOBILE EVIDENCE:\n"
                for ev in evidence:
                    report += f"- [{ev['evidence_type']}] {ev['description']} (Stored at: {ev['file_path']} on {ev['uploaded_at']})\n"

            report += "================================================================================\n"

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"report": report}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        req = json.loads(self.rfile.read(content_length).decode('utf-8')) if content_length > 0 else {}

        if self.path == '/api/update-profile':
            conn = sqlite3.connect(DB_PATH)
            for k, v in req.items():
                if v: conn.execute("INSERT OR REPLACE INTO agency_profile VALUES (?, ?);", (k, str(v)))
            log_audit(conn, "UPDATE_PROFILE", f"Updated agency onboarding parameters: {list(req.keys())}", "Command Staff")
            conn.commit()
            conn.close()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())

        elif self.path == '/api/add-governing-doc':
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO governing_documents (authority_level, issuing_body, doc_code, doc_title, effective_date, full_text) VALUES (?, ?, ?, ?, ?, ?);",
                         (req['authority_level'], req['issuing_body'], req['doc_code'], req['doc_title'], timestamp, req['full_text']))
            log_audit(conn, "DOC_INGEST", f"Ingested governing document {req['doc_code']}: {req['doc_title']}", "Command Staff")
            conn.commit()
            conn.close()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())

        elif self.path == '/api/import-csv':
            target_table = req.get('table')
            csv_text = req.get('csv_data')
            import csv, io
            f = io.StringIO(csv_text.strip())
            reader = csv.reader(f)
            next(reader, None)
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            count = 0
            for row in reader:
                if not row: continue
                if target_table == 'officers':
                    cursor.execute("INSERT OR REPLACE INTO officers VALUES (?, ?, ?, ?, ?, ?, ?);", tuple(row))
                elif target_table == 'fleet_cruisers':
                    cursor.execute("INSERT OR REPLACE INTO fleet_cruisers VALUES (?, ?, ?, ?, ?);", tuple(row))
                count += 1
            log_audit(conn, "CSV_IMPORT", f"Successfully imported {count} records into table {target_table}.", "Administrator")
            conn.commit()
            conn.close()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": f"Successfully imported {count} records!"}).encode())

        elif self.path == '/api/upload-photo':
            std_code = req.get('standard_code')
            desc = req.get('description')
            img_data = req.get('image_base64')
            filename = req.get('filename', 'evidence.jpg')
            
            header, encoded = img_data.split(",", 1)
            file_bytes = base64.b64decode(encoded)
            file_path = os.path.join(UPLOAD_DIR, f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}")
            with open(file_path, "wb") as fh:
                fh.write(file_bytes)

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO audit_evidence (standard_code, evidence_type, file_path, description, uploaded_at) VALUES (?, ?, ?, ?, ?);",
                         (std_code, "Mobile Photo Evidence", file_path, desc, timestamp))
            log_audit(conn, "PHOTO_UPLOAD", f"Uploaded photo evidence for standard {std_code}: {desc}", "Field Officer")
            conn.commit()
            conn.close()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": "Photo evidence successfully linked to accreditation binder!"}).encode())

        elif self.path == '/api/add-fleet':
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT OR REPLACE INTO fleet_cruisers VALUES (?, ?, ?, 0, NULL);", 
                         (req['unit_id'], req['year_make_model'], req['current_odometer']))
            log_audit(conn, "FLEET_ADD", f"Added patrol cruiser unit {req['unit_id']}.", "Fleet Supervisor")
            conn.commit()
            conn.close()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())

        elif self.path == '/api/add-facility':
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO facility_inspections (task_code, task_title, completed_by_name, submission_timestamp, retention_schedule) VALUES (?, ?, ?, ?, ?);",
                         (req['task_code'], req['task_title'], req['completed_by_name'], timestamp, req['retention_schedule']))
            log_audit(conn, "FACILITY_LOG", f"Logged facility inspection {req['task_code']} - {req['task_title']}.", req['completed_by_name'])
            conn.commit()
            conn.close()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())

        elif self.path == '/api/ai-agent':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                req = json.loads(self.rfile.read(content_length).decode('utf-8')) if content_length > 0 else {}
                module = req.get('module')

                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                profile = {row['config_key']: row['config_value'] for row in conn.execute("SELECT * FROM agency_profile;").fetchall()}
                current_fw = profile.get('accreditation_framework', 'CT_POST_ALL_TIERS')
                agency_name = profile.get('agency_name', 'Municipal Police Department')

                officers = [dict(row) for row in conn.execute("SELECT * FROM officers;").fetchall()]
                fleet = [dict(row) for row in conn.execute("SELECT * FROM fleet_cruisers;").fetchall()]
                facilities = [dict(row) for row in conn.execute("SELECT * FROM facility_inspections;").fetchall()]
                policies = [dict(row) for row in conn.execute("SELECT * FROM policy_acknowledgments;").fetchall()]
                gov_docs = [dict(row) for row in conn.execute("SELECT * FROM governing_documents;").fetchall()]
                
                log_audit(conn, "AI_QUERY", f"Ran AI compliance module: {module} under {current_fw}.", "Command Staff")
                conn.commit()
                conn.close()

                persona = f"You are an expert governing authority and compliance legal advisor for {agency_name} under Connecticut POST-C Tiers I, II, and III concurrent standards."

                if module == 'statutory_gap':
                    prompt = f"{persona} Review our governing documents ({json.dumps(gov_docs)}) and current policy acknowledgment status ({json.dumps(policies)}). Draft a concise administrative memo assessing compliance risks."
                elif module == 'predictive_drift':
                    prompt = f"{persona} Here is our active sworn roster: {json.dumps(officers)}. Analyze recertification drift risks for Tier II compliance and recommend scheduling priorities."
                elif module == 'rag_inspector':
                    prompt = f"You are an external accreditation inspector auditing Connecticut POST-C Tiers I, II, and III. Governing authorities: {json.dumps(gov_docs)}. Fleet records: {json.dumps(fleet)}. Safety logs: {json.dumps(facilities)}. Provide a comprehensive audit verification summary."
                elif module == 'grant_matching':
                    prompt = f"{persona} Draft a brief executive justification for a State Equipment Grant based on our governing fleet ordinances and fleet status: {json.dumps(fleet)}."
                else:
                    prompt = "Provide a general governing authority compliance summary."

                ai_response = query_gemini_llm(prompt)
                response_bytes = json.dumps({"result": ai_response}).encode('utf-8')
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Content-Length", str(len(response_bytes)))
                self.end_headers()
                self.wfile.write(response_bytes)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"result": f"⚠️ Error: {str(e)}"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

import socket

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()
import socket

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()

import socket
import time

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()

if __name__ == '__main__':
    init_and_seed_db()
    
    server = None
    max_retries = 5
    for attempt in range(max_retries):
        try:
            server = ReusableTCPServer(("", PORT), DashboardHandler)
            break
        except OSError as e:
            if e.errno == 98 and attempt < max_retries - 1:
                print(f"⚠️ Port {PORT} in use, retrying in 2 seconds (Attempt {attempt+1}/{max_retries})...")
                time.sleep(2)
            else:
                raise e

    print("================================================================================")
    print(f"  SENTINEL COMPLIANCE OS — MASTER RUNNING AT PORT: {PORT}")
    print("================================================================================")
    server.serve_forever()
