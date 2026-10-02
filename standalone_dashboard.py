import sqlite3
import json
import datetime
import os
import base64
import streamlit as st
from google import genai

st.set_page_config(
    page_title="Sentinel Compliance OS — Governing Authority Master",
    page_icon="🛡️",
    layout="wide"
)

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

@st.cache_resource
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

init_and_seed_db()

# Main Streamlit UI Layout
st.title("🛡️ Sentinel Compliance OS — Governing Authority Master")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
profile = {row['config_key']: row['config_value'] for row in conn.execute("SELECT * FROM agency_profile;").fetchall()}
current_fw = profile.get('accreditation_framework', 'CT_POST_ALL_TIERS')

# Sidebar Controls
st.sidebar.title("⚙️ Command Controls")
selected_fw = st.sidebar.selectbox("Framework", ["CT_POST_ALL_TIERS", "CALEA"], index=0 if current_fw == "CT_POST_ALL_TIERS" else 1)
if selected_fw != current_fw:
    conn.execute("INSERT OR REPLACE INTO agency_profile VALUES ('accreditation_framework', ?);", (selected_fw,))
    conn.commit()
    st.rerun()

rbac_tier = st.sidebar.selectbox("RBAC Tier", ["command", "supervisor", "patrol"])

# Metrics calculation
officers = [dict(row) for row in conn.execute("SELECT * FROM officers;").fetchall()]
fleet = [dict(row) for row in conn.execute("SELECT * FROM fleet_cruisers;").fetchall()]
facilities = [dict(row) for row in conn.execute("SELECT * FROM facility_inspections;").fetchall()]
policies = [dict(row) for row in conn.execute("SELECT * FROM policy_acknowledgments;").fetchall()]
standards = [dict(row) for row in conn.execute("SELECT * FROM accreditation_standards WHERE framework_type = ?;", (selected_fw,)).fetchall()]
governing_docs = [dict(row) for row in conn.execute("SELECT * FROM governing_documents;").fetchall()]
audit_trail = [dict(row) for row in conn.execute("SELECT * FROM audit_trail ORDER BY log_id DESC LIMIT 20;").fetchall()]
conn.close()

total_policies = len(policies) or 1
ack_policies = sum(1 for p in policies if p['is_acknowledged'])
total_fleet = len(fleet) or 1
grounded_fleet = sum(1 for f in fleet if f['is_grounded'])
health_score = round(((ack_policies / total_policies) * 50) + (((total_fleet - grounded_fleet) / total_fleet) * 50), 1)

# Health Score Banner
st.metric("🛡️ Executive Compliance Health Score", f"{health_score}%", delta="Audit Ready" if health_score >= 90 else "Review Required")

if rbac_tier in ["command", "supervisor"]:
    st.markdown("### 🏛️ Governing Authority Document Repository")
    st.dataframe(governing_docs, use_container_width=True)

    st.markdown("### 📋 Active Accreditation Standards & Live Proof Matrix")
    st.dataframe(standards, use_container_width=True)

if rbac_tier == "command":
    st.markdown("### 🧠 Gemini Cloud AI Intelligence Command Center")
    ai_module = st.selectbox("Select Intelligence Query", ["statutory_gap", "predictive_drift", "rag_inspector", "grant_matching"])
    if st.button("Execute AI Analysis"):
        with st.spinner("Synthesizing with Gemini..."):
            persona = f"You are an expert governing authority and compliance legal advisor for {profile.get('agency_name')}."
            if ai_module == 'statutory_gap':
                prompt = f"{persona} Review governing documents ({json.dumps(governing_docs)}) and policy statuses ({json.dumps(policies)}). Draft a concise compliance risk memo."
            elif ai_module == 'predictive_drift':
                prompt = f"{persona} Analyze active sworn roster ({json.dumps(officers)}) for Tier II recertification drift risks."
            elif ai_module == 'rag_inspector':
                prompt = f"Audit agency records. Governing docs: {json.dumps(governing_docs)}. Fleet: {json.dumps(fleet)}. Safety logs: {json.dumps(facilities)}."
            else:
                prompt = f"{persona} Draft an executive justification for a State Equipment Grant based on fleet status: {json.dumps(fleet)}."
            
            st.markdown(query_gemini_llm(prompt))

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Sworn Roster")
    st.dataframe(officers, use_container_width=True)
with col2:
    st.markdown("### Patrol Fleet Status")
    st.dataframe(fleet, use_container_width=True)

if rbac_tier in ["command", "supervisor"]:
    st.markdown("### Facility Life-Safety Logs")
    st.dataframe(facilities, use_container_width=True)

if rbac_tier == "command":
    st.markdown("### 📜 Immutable Chain-of-Custody Audit Trail")
    st.dataframe(audit_trail, use_container_width=True)
