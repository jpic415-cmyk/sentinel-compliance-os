cat << 'EOF' > standalone_dashboard.py
"""
Sentinel Compliance OS — Gemini Cloud-Accelerated Edition
Purpose: Single-tenant compliance platform utilizing Gemini API for high-speed 
statutory safety nets, governing authority RAG audits, and live web accessibility.
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

client = genai.Client()

def query_gemini_ai(prompt_text):
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_text,
            config={
                'temperature': 0.1,
                'system_instruction': (
                    "You are an expert Connecticut POST-C accreditation and legal compliance auditor. "
                    "You must evaluate agency operational records and policies strictly against the provided "
                    "Governing Authority Source of Truth and state mandatory minimum floors."
                )
            }
        )
        return response.text
    except Exception as e:
        return f"⚠️ [GEMINI API ERROR]: Could not reach Gemini. Details: {str(e)}"

def log_audit(conn, action_type, details, performed_by="Command Staff"):
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
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS governing_documents (
        doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
        authority_level TEXT NOT NULL,
        issuing_body TEXT NOT NULL,
        doc_code TEXT NOT NULL,
        doc_title TEXT NOT NULL,
        effective_date TEXT NOT NULL,
        full_text TEXT NOT NULL,
        statutory_verdict TEXT DEFAULT 'Pending Gemini Audit'
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accreditation_standards (
        standard_code TEXT PRIMARY KEY,
        framework_type TEXT NOT NULL,
        chapter_title TEXT NOT NULL,
        standard_description TEXT NOT NULL,
        target_table TEXT NOT NULL,
        governing_doc_id INTEGER,
        FOREIGN KEY(governing_doc_id) REFERENCES governing_documents(doc_id)
    );
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS audit_trail (log_id INTEGER PRIMARY KEY AUTOINCREMENT, action_type TEXT NOT NULL, details TEXT NOT NULL, performed_by TEXT NOT NULL, timestamp TEXT NOT NULL);")

    cursor.execute("SELECT config_value FROM agency_profile WHERE config_key = 'accreditation_framework';")
    if not cursor.fetchone():
        cursor.execute("INSERT OR REPLACE INTO agency_profile VALUES ('agency_name', 'Cheshire Police Department');")
        cursor.execute("INSERT OR REPLACE INTO agency_profile VALUES ('accreditation_framework', 'CT_POST_ALL_TIERS');")
        log_audit(conn, "SYSTEM_INIT", "Initialized Gemini Cloud Proof of Concept profile.", "System")

    cursor.execute("SELECT COUNT(*) FROM governing_documents;")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO governing_documents (authority_level, issuing_body, doc_code, doc_title, effective_date, full_text, statutory_verdict) VALUES (?, ?, ?, ?, ?, ?, ?);", [
            ("Municipal", "Town Council", "ORD-2024-02", "Fleet Management Ordinance", "2024-01-15", "All municipal cruisers must undergo monthly mileage and safety checks.", "PASSED: Meets State Tier I Minimums"),
            ("Agency", "Chief of Police", "GO-201", "Use of Force Directive", "2026-01-01", "Officers shall use objectively reasonable force. Annual review required.", "PASSED: Meets CT POST-C Tier I Mandates")
        ])
        log_audit(conn, "DATABASE_SEED", "Seeded mock data for POC.", "System")

    conn.commit()
    conn.close()

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sentinel Compliance OS — Gemini Cloud POC</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .header { background: #1e293b; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 5px solid #3b82f6; display: flex; justify-content: space-between; align-items: center; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .card { background: #1e293b; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        h1, h2 { margin-top: 0; color: #60a5fa; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #334155; font-size: 14px; }
        th { color: #94a3b8; }
        .badge-green { background: #22c55e; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .badge-red { background: #ef4444; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
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
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Sentinel Compliance OS</h1>
            <p style="margin: 0; color: #94a3b8;">Powered by Gemini Cloud API — Proof of Concept</p>
        </div>
        <div>
            <button class="btn-blue" style="width:auto; margin:0; padding:8px 12px;" onclick="openModal('doc-modal')">📜 + Ingest Policy & Run Gemini Audit</button>
        </div>
    </div>
    <div class="grid">
        <div class="card" style="grid-column: 1 / -1; border-left: 5px solid #0284c7;">
            <h2>🏛 Governing Authority Repository & Gemini Safety Net</h2>
            <table id="doc-repo-table">
                <thead>
                    <tr>
                        <th>Code & Title</th>
                        <th>Issuing Body</th>
                        <th>Gemini Statutory Safety Verdict</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>
    <div class="grid">
        <div class="card" style="grid-column: 1 / -1; border-left: 5px solid #a855f7;">
            <h2>🧠 Gemini RAG Audit & Compliance Inspector</h2>
            <button onclick="runGeminiAudit()">Run Live Gemini Compliance Audit</button>
            <div id="ai-output-box" class="ai-console">Click above to query Gemini against your governing documents...</div>
        </div>
    </div>
    <div id="doc-modal" class="modal">
        <div class="modal-content">
            <h2>📜 Ingest Policy & Run Gemini Check</h2>
            <label style="font-size:12px; color:#94a3b8;">Authority Level:</label>
            <select id="doc-level">
                <option value="Agency">Agency General Order / SOP</option>
                <option value="Municipal">Municipal Ordinance</option>
            </select>
            <label style="font-size:12px; color:#94a3b8;">Issuing Body:</label>
            <input type="text" id="doc-issuer" placeholder="e.g. Chief of Police">
            <label style="font-size:12px; color:#94a3b8;">Document Code:</label>
            <input type="text" id="doc-code" placeholder="e.g. GO-305">
            <label style="font-size:12px; color:#94a3b8;">Document Title:</label>
            <input type="text" id="doc-title" placeholder="e.g. Body-Worn Camera Policy">
            <label style="font-size:12px; color:#94a3b8;">Policy Text:</label>
            <textarea id="doc-text" rows="4" placeholder="Paste policy text here..."></textarea>
            <button class="btn-green" onclick="submitGoverningDoc()">Save & Run Gemini Audit</button>
            <button style="background:#64748b;" onclick="closeModal('doc-modal')">Cancel</button>
        </div>
    </div>
    <script>
        function loadData() {
            fetch('/api/dashboard-data').then(res => res.json()).then(data => {
                let docHtml = '';
                data.governing_docs.forEach(doc => {
                    let verdictBadge = doc.statutory_verdict.startsWith('PASSED') ? 
                        `<span class="badge-green">${doc.statutory_verdict}</span>` : 
                        `<span class="badge-red">${doc.statutory_verdict}</span>`;
                    docHtml += `<tr><td><b>${doc.doc_code}</b>: ${doc.doc_title}</td><td>${doc.issuing_body}</td><td>${verdictBadge}</td></tr>`;
                });
                document.querySelector('#doc-repo-table tbody').innerHTML = docHtml;
            });
        }
        function openModal(id) { document.getElementById(id).style.display = 'flex'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }
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
            }).then(res => res.json()).then(r => {
                closeModal('doc-modal');
                loadData();
                alert("Gemini Statutory Safety Net Verdict:\\n\\n" + r.verdict);
            });
        }
        function runGeminiAudit() {
            const consoleBox = document.getElementById('ai-output-box');
            consoleBox.style.display = 'block';
            consoleBox.innerText = "Querying Gemini cloud API with governing authority context...";
            fetch('/api/ai-audit', { method: 'POST' }).then(res => res.json()).then(response => { consoleBox.innerText = response.result; });
        }
        loadData();
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
            governing_docs = [dict(row) for row in conn.execute("SELECT * FROM governing_documents;").fetchall()]
            conn.close()
            self.wfile.write(json.dumps({"governing_docs": governing_docs}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        req = json.loads(self.rfile.read(content_length).decode('utf-8')) if content_length > 0 else {}
        if self.path == '/api/add-governing-doc':
            doc_code = req.get('doc_code')
            doc_title = req.get('doc_title')
            full_text = req.get('full_text')
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
            ai_prompt = (
                "Analyze the following newly ingested agency policy text against mandatory state accreditation floors (Connecticut POST-C Tiers I, II, III). "
                "Determine if the policy meets state minimums or if there is a statutory deficiency or conflict. "
                "If it meets or exceeds requirements, start your response with 'PASSED:' followed by a brief summary. "
                "If it falls below state minimums, start your response with 'FAILED/DEFICIENCY:' followed by the exact liability risk.\n\n"
                f"Policy Code & Title: {doc_code} - {doc_title}\nPolicy Content:\n{full_text}"
            )
            ai_verdict = query_gemini_ai(ai_prompt).strip()
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO governing_documents (authority_level, issuing_body, doc_code, doc_title, effective_date, full_text, statutory_verdict) VALUES (?, ?, ?, ?, ?, ?, ?);",
                         (req['authority_level'], req['issuing_body'], doc_code, doc_title, timestamp, full_text, ai_verdict))
            log_audit(conn, "GEMINI_SAFETY_NET_CHECK", f"Ingested {doc_code} with Gemini verdict: {ai_verdict[:50]}...", "Command Staff")
            conn.commit()
            conn.close()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "verdict": ai_verdict}).encode())
        elif self.path == '/api/ai-audit':
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            gov_docs = [dict(row) for row in conn.execute("SELECT * FROM governing_documents;").fetchall()]
            conn.close()
            prompt = f"Perform an executive compliance audit of our department based on these governing documents: {json.dumps(gov_docs)}. Highlight any potential statutory risks or strengths."
            ai_response = query_gemini_ai(prompt)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"result": ai_response}).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    init_and_seed_db()
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"Server running on port {PORT}")
        httpd.serve_forever()
EOF
