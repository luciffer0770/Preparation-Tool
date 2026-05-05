import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "ps_etw.db"


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db():
    """Create all tables and seed config lists. Safe to call multiple times."""
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS projects (
        id               TEXT PRIMARY KEY,
        code             TEXT NOT NULL,
        name             TEXT NOT NULL DEFAULT '',
        customer         TEXT DEFAULT '',
        engine_type      TEXT DEFAULT '',
        serial           TEXT DEFAULT '',
        trolley_code     TEXT DEFAULT '',
        trolley_location TEXT DEFAULT '',
        pm_name          TEXT DEFAULT '',
        start_date       TEXT DEFAULT '',
        target_finish    TEXT DEFAULT '',
        forecast_finish  TEXT DEFAULT '',
        contract_ref     TEXT DEFAULT '',
        working_hrs_day  INTEGER DEFAULT 9,
        warn_threshold   INTEGER DEFAULT 3,
        crit_threshold   INTEGER DEFAULT 1,
        status           TEXT DEFAULT 'Not Started',
        archived         INTEGER DEFAULT 0,
        created_at       TEXT DEFAULT (datetime('now')),
        updated_at       TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS team_members (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id   TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
        name         TEXT NOT NULL,
        role         TEXT DEFAULT '',
        dept         TEXT DEFAULT '',
        email        TEXT DEFAULT '',
        phone        TEXT DEFAULT '',
        access_level TEXT DEFAULT 'Technician',
        notes        TEXT DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS activities (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id     TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
        seq_num        INTEGER NOT NULL,
        major_phase    TEXT NOT NULL,
        phase          TEXT NOT NULL,
        activity_name  TEXT NOT NULL,
        sub_activity   TEXT DEFAULT '',
        technician     TEXT DEFAULT '',
        dept           TEXT DEFAULT 'Mech',
        priority       TEXT DEFAULT 'Medium',
        plan_start     TEXT DEFAULT '',
        plan_finish    TEXT DEFAULT '',
        duration_d     INTEGER DEFAULT 1,
        float_d        INTEGER DEFAULT 0,
        pct_complete   INTEGER DEFAULT 0,
        status         TEXT DEFAULT 'Not Started',
        est_hours      REAL DEFAULT 9,
        actual_hours   REAL DEFAULT 0,
        actual_start   TEXT DEFAULT '',
        actual_finish  TEXT DEFAULT '',
        hrs_spent      REAL DEFAULT 0,
        delay_d        INTEGER DEFAULT 0,
        alert_level    TEXT DEFAULT 'OK',
        predecessor_id INTEGER DEFAULT NULL,
        notes          TEXT DEFAULT '',
        created_at     TEXT DEFAULT (datetime('now')),
        updated_at     TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS materials (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id        TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
        part_number       TEXT DEFAULT '',
        description       TEXT NOT NULL,
        linked_activity_id INTEGER DEFAULT NULL,
        quantity          INTEGER DEFAULT 1,
        ownership         TEXT DEFAULT 'Bosch',
        criticality       TEXT DEFAULT 'Medium',
        need_by_date      TEXT DEFAULT '',
        status            TEXT DEFAULT 'Not Ordered',
        supplier          TEXT DEFAULT '',
        tracking_ref      TEXT DEFAULT '—',
        promised_date     TEXT DEFAULT '—',
        received_date     TEXT DEFAULT '—',
        risk_flag         TEXT DEFAULT 'OK',
        lead_time_d       INTEGER DEFAULT 0,
        value_eur         REAL DEFAULT 0,
        notes             TEXT DEFAULT '',
        latest_order_date TEXT DEFAULT '—',
        order_alert       TEXT DEFAULT '—',
        created_at        TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS delays_actions (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id      TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
        activity_id     INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
        action_required TEXT DEFAULT '',
        root_cause      TEXT DEFAULT 'Other',
        action_owner    TEXT DEFAULT '',
        target_date     TEXT DEFAULT '',
        resolution      TEXT DEFAULT '',
        delay_status    TEXT DEFAULT 'Open',
        total_delay_hrs REAL DEFAULT 0,
        created_at      TEXT DEFAULT (datetime('now')),
        updated_at      TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS documents (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
        doc_type   TEXT DEFAULT 'PDF',
        title      TEXT NOT NULL,
        category   TEXT DEFAULT '',
        revision   TEXT DEFAULT '—',
        date_added TEXT DEFAULT (date('now')),
        added_by   TEXT DEFAULT '',
        doc_status TEXT DEFAULT 'Active',
        file_path  TEXT DEFAULT '',
        notes      TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS config_lists (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        list_name  TEXT NOT NULL,
        list_value TEXT NOT NULL,
        sort_order INTEGER DEFAULT 0,
        UNIQUE(list_name, list_value)
    );

    CREATE INDEX IF NOT EXISTS idx_act_proj ON activities(project_id);
    CREATE INDEX IF NOT EXISTS idx_mat_proj ON materials(project_id);
    CREATE INDEX IF NOT EXISTS idx_del_proj ON delays_actions(project_id);
    CREATE INDEX IF NOT EXISTS idx_doc_proj ON documents(project_id);
    """)

    defaults = {
        "status":       ["Not Started", "In Progress", "Complete", "Blocked", "Delayed", "On Hold"],
        "priority":     ["Critical", "High", "Medium", "Low"],
        "department":   ["Mech", "Inst", "ENG", "QA", "LOG", "PROC", "HSE", "IT"],
        "ownership":    ["Bosch", "Customer", "Supplier", "Third Party"],
        "mat_status":   ["Not Ordered", "Ordered", "In Transit", "Arrived", "Available"],
        "root_cause":   ["Supplier Delay", "Material Shortage", "Client Dependency", "Quality Issue",
                         "Tooling Unavailable", "Resource Shortage", "Design Change",
                         "Weather/External", "Planning Error", "Other"],
        "action_status":["Open", "Mitigating", "Closed"],
        "criticality":  ["Critical", "High", "Medium", "Low"],
        "doc_type":     ["PDF", "Word", "Excel", "Drawing", "Web", "Other"],
        "doc_category": ["Engine Specification", "Test Plan", "Maintenance Manual", "Inspection Report",
                         "Drawing & CAD", "Customer Document", "Safety/HSE",
                         "Calibration Certificate", "Other"],
        "doc_status":   ["Active", "Superseded", "Archived", "Under Review"],
    }
    for list_name, values in defaults.items():
        for i, v in enumerate(values):
            conn.execute(
                "INSERT OR IGNORE INTO config_lists(list_name,list_value,sort_order) VALUES(?,?,?)",
                (list_name, v, i))

    from backend.models import MECH_PHASES, ELEC_PHASES
    for i, v in enumerate(MECH_PHASES):
        conn.execute(
            "INSERT OR IGNORE INTO config_lists(list_name,list_value,sort_order) VALUES(?,?,?)",
            ("phases_mech", v, i))
    for i, v in enumerate(ELEC_PHASES):
        conn.execute(
            "INSERT OR IGNORE INTO config_lists(list_name,list_value,sort_order) VALUES(?,?,?)",
            ("phases_elec", v, i))

    conn.commit()
    conn.close()


def db_fetchall(sql: str, params=()) -> list[dict]:
    conn = get_conn()
    rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    conn.close()
    return rows


def db_fetchone(sql: str, params=()) -> dict | None:
    conn = get_conn()
    row = conn.execute(sql, params).fetchone()
    conn.close()
    return dict(row) if row else None


def db_execute(sql: str, params=()) -> int:
    conn = get_conn()
    cur = conn.execute(sql, params)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


def get_config() -> dict[str, list[str]]:
    rows = db_fetchall("SELECT list_name, list_value FROM config_lists ORDER BY list_name, sort_order")
    result: dict[str, list] = {}
    for r in rows:
        result.setdefault(r["list_name"], []).append(r["list_value"])
    return result


def get_projects(include_archived: bool = True) -> list[dict]:
    if include_archived:
        projects = db_fetchall("SELECT * FROM projects ORDER BY created_at DESC")
    else:
        projects = db_fetchall(
            "SELECT * FROM projects WHERE archived=0 ORDER BY created_at DESC")
    for p in projects:
        acts = db_fetchall("SELECT status FROM activities WHERE project_id=?", (p["id"],))
        total = len(acts)
        done = sum(1 for a in acts if a["status"] == "Complete")
        delayed = sum(1 for a in acts if a["status"] == "Delayed")
        blocked = sum(1 for a in acts if a["status"] == "Blocked")
        p["total_acts"] = total
        p["done_acts"] = done
        p["pct"] = round(done / total * 100) if total > 0 else 0
        p["delayed_count"] = delayed
        p["blocked_count"] = blocked
        if delayed > 0 or blocked > 0:
            p["health"] = "overdue"
        else:
            p["health"] = "ok"
    return projects


def get_activities(project_id: str) -> list[dict]:
    return db_fetchall(
        "SELECT * FROM activities WHERE project_id=? ORDER BY seq_num", (project_id,))


def get_materials(project_id: str) -> list[dict]:
    return db_fetchall(
        "SELECT * FROM materials WHERE project_id=? ORDER BY id", (project_id,))


def get_delays(project_id: str) -> list[dict]:
    return db_fetchall("""
        SELECT d.*, a.activity_name, a.phase, a.seq_num, a.technician,
               a.plan_start, a.plan_finish, a.float_d, a.pct_complete, a.status as act_status
        FROM delays_actions d
        JOIN activities a ON a.id = d.activity_id
        WHERE d.project_id=? ORDER BY d.id
    """, (project_id,))


def get_documents(project_id: str) -> list[dict]:
    return db_fetchall(
        "SELECT * FROM documents WHERE project_id=? ORDER BY id", (project_id,))


def recompute_material_alerts(project_id: str):
    """Update risk_flag and order_alert from need_by_date and status."""
    from datetime import date
    from backend.scheduler import parse_date

    mats = db_fetchall("SELECT * FROM materials WHERE project_id=?", (project_id,))
    today = date.today()
    for m in mats:
        need = parse_date(m.get("need_by_date") or "")
        status = m.get("status") or "Not Ordered"
        risk = "OK"
        alert = "—"
        if status in ("Not Ordered", "Ordered") and need and need < today:
            alert = "ORDER NOW — past need-by"
            risk = "AT RISK"
        elif status == "In Transit" and need and (need - today).days <= 3:
            risk = "WARN"
        db_execute(
            """UPDATE materials SET risk_flag=?, order_alert=? WHERE id=?""",
            (risk, alert, m["id"]))


def sync_delays(project_id: str):
    acts = db_fetchall(
        "SELECT id FROM activities WHERE project_id=? AND status IN ('Blocked','Delayed')",
        (project_id,))
    existing = {r["activity_id"] for r in db_fetchall(
        "SELECT activity_id FROM delays_actions WHERE project_id=?", (project_id,))}
    for a in acts:
        if a["id"] not in existing:
            db_execute("""INSERT INTO delays_actions
                (project_id, activity_id, action_required, root_cause, delay_status)
                VALUES (?,?,?,?,?)""",
                (project_id, a["id"], "", "Other", "Open"))
