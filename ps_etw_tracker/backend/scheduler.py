import math
from datetime import date, timedelta

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def parse_date(s) -> date | None:
    if not s or str(s).strip() in ("", "—", "null", "None"):
        return None
    if isinstance(s, date):
        return s
    s = str(s).strip()
    try:
        # ISO YYYY-MM-DD
        if len(s) >= 10 and s[4] == "-" and s[7] == "-":
            y, mo, da = int(s[:4]), int(s[5:7]), int(s[8:10])
            return date(y, mo, da)
        parts = s.split("-")
        if len(parts) == 3:
            d = int(parts[0])
            m_str = parts[1].capitalize()
            if m_str in MONTHS:
                m = MONTHS.index(m_str) + 1
                y_str = parts[2]
                y = 2000 + int(y_str) if len(y_str) == 2 else int(y_str)
                return date(y, m, d)
    except Exception:
        pass
    return None


def fmt_date(d: date | None) -> str:
    if not d:
        return ""
    return f"{d.day:02d}-{MONTHS[d.month - 1]}-{str(d.year)[2:]}"


def is_weekend(d: date) -> bool:
    return d.weekday() >= 5


def next_wd(d: date) -> date:
    nd = d + timedelta(days=1)
    while is_weekend(nd):
        nd += timedelta(days=1)
    return nd


def add_wd(d: date, n: int) -> date:
    x = d
    for _ in range(n):
        x += timedelta(days=1)
        while is_weekend(x):
            x += timedelta(days=1)
    return x


def count_wd(start: date, end: date) -> int:
    if not start or not end or end < start:
        return 0
    count, d = 0, start
    while d <= end:
        if not is_weekend(d):
            count += 1
        d += timedelta(days=1)
    return count


def auto_schedule(activities: list[dict], start_date_str: str, hrs_per_day: int = 9) -> list[dict]:
    start = parse_date(start_date_str)
    if not start:
        return activities
    cur = start
    while is_weekend(cur):
        cur = next_wd(cur)
    hours_today = 0.0
    for act in activities:
        est = float(act.get("est_hours") or hrs_per_day)
        if est <= 0:
            est = float(hrs_per_day)
        if hours_today > 0 and hours_today + est > hrs_per_day:
            cur = next_wd(cur)
            hours_today = 0.0
        act["plan_start"] = fmt_date(cur)
        days_needed = max(1, math.ceil(est / hrs_per_day))
        fin = add_wd(cur, days_needed - 1)
        act["plan_finish"] = fmt_date(fin)
        act["duration_d"] = count_wd(cur, fin)
        hours_today += est
        if hours_today >= hrs_per_day:
            cur = next_wd(fin)
            hours_today = 0.0
    return activities


def compute_derived(activities: list[dict], target_finish_str: str,
                    warn: int = 3, crit: int = 1) -> list[dict]:
    target = parse_date(target_finish_str)
    today = date.today()
    for act in activities:
        pf = parse_date(act.get("plan_finish"))
        af = parse_date(act.get("actual_finish"))
        status = act.get("status", "Not Started")
        if pf and target:
            act["float_d"] = max(0, count_wd(pf, target) - 1)
        else:
            # No target date: do not treat as zero float (avoids false WARN on all rows)
            act["float_d"] = 999
        if pf and af and af > pf:
            act["delay_d"] = count_wd(pf, af) - 1
        elif status in ("Delayed", "Blocked") and pf and today > pf:
            act["delay_d"] = count_wd(pf, today) - 1
        else:
            act["delay_d"] = act.get("delay_d") or 0
        f = act.get("float_d") or 0
        if status in ("Blocked", "Delayed") or f < 0:
            act["alert_level"] = "CRIT"
        elif target and status not in ("Complete",) and f <= warn:
            act["alert_level"] = "WARN"
        else:
            act["alert_level"] = "OK"
    return activities


def ensure_schedule_populated(project_id: str):
    """Run auto-schedule if project has start_date but activities lack plan dates."""
    from backend.database import db_fetchone, get_activities

    proj = db_fetchone("SELECT * FROM projects WHERE id=?", (project_id,))
    if not proj or not str(proj.get("start_date") or "").strip():
        return
    acts = get_activities(project_id)
    if not acts:
        return
    if any(not str(a.get("plan_start") or "").strip() for a in acts):
        run_schedule_and_save(project_id)


def run_schedule_and_save(project_id: str):
    from backend.database import db_fetchone, get_activities, db_execute, sync_delays, get_conn

    proj = db_fetchone("SELECT * FROM projects WHERE id=?", (project_id,))
    if not proj or not str(proj.get("start_date") or "").strip():
        return
    acts = get_activities(project_id)
    acts = auto_schedule(acts, proj["start_date"], int(proj.get("working_hrs_day") or 9))
    tf = proj.get("target_finish") or proj.get("forecast_finish") or ""
    acts = compute_derived(
        acts, tf,
        int(proj.get("warn_threshold") or 3),
        int(proj.get("crit_threshold") or 1))
    conn = get_conn()
    for a in acts:
        conn.execute("""UPDATE activities
            SET plan_start=?, plan_finish=?, duration_d=?, float_d=?,
                delay_d=?, alert_level=?, updated_at=datetime('now')
            WHERE id=?""",
            (a["plan_start"], a["plan_finish"], a["duration_d"],
             a["float_d"], a["delay_d"], a["alert_level"], a["id"]))
    conn.commit()
    conn.close()
    sync_delays(project_id)
