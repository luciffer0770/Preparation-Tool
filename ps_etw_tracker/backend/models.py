# ps_etw_tracker/backend/models.py — Master activity template (PS-ETW build-up)
from __future__ import annotations

# Phase keys must match MECH_PHASES / ELEC_PHASES below.
# Hours are est_hours used by auto_schedule (working-day bin-pack).

ACT_TEMPLATES = {
    "Engine Receipt": [
        ("Engine unloading & safe handling", "Mech", 2),
        ("Visual inspection & damage check", "Mech", 1),
        ("Engine serial & configuration verification", "Mech", 1),
        ("Spare parts accountability & tagging", "Mech", 1),
    ],
    "Trolley Prep": [
        ("Trolley cleaning & preparation", "Mech", 2),
    ],
    "Mounting": [
        ("Review engine mounting drawings", "Mech", 2),
        ("Mounting bracket design", "Mech", 3),
        ("Mounting bracket fabrication", "Mech", 6),
        ("Side mounting bracket fabrication", "Mech", 4),
        ("Damper section verification", "Mech", 1),
    ],
    "Alignment": [
        ("Screw jack & damper section installation", "Mech", 2),
        ("Engine mounting on trolley", "Mech", 3),
        ("Engine-dyno alignment", "Mech", 3),
    ],
    "Drive System": [
        ("Drive plate drawing review", "Mech", 1),
        ("Drive plate machining", "Mech", 4),
        ("Shaft fitment & verification", "Mech", 2),
    ],
    "Starter": [
        ("Starter motor fitment", "Mech", 2),
    ],
    "Crank Pulley": [
        ("Crank pulley modification", "Mech", 3),
    ],
    "Encoder": [
        ("Encoder flange design", "Mech", 2),
        ("Encoder flange machining", "Mech", 3),
        ("Encoder pulley machining", "Mech", 2),
        ("Angle encoder mounting", "Mech", 2),
    ],
    "Measurement": [
        ("Measurement layout finalization", "Mech", 2),
        ("Combustion sensor boss machining", "Mech", 4),
    ],
    "Air Circuit": [
        ("Air filter installation", "Mech", 1),
        ("Air filter to compressor hose routing", "Mech", 2),
        ("Compressor to intercooler routing", "Mech", 2),
        ("TVA / PFM / HFM / Dump valve fitment", "Mech", 2),
        ("Intercooler to intake routing", "Mech", 2),
        ("Turbo to intercooler support fabrication", "Mech", 2),
        ("Intercooler routing supports", "Mech", 2),
    ],
    "CCV System": [
        ("CCV assembly with NRV", "Mech", 2),
    ],
    "EGR System": [
        ("EGR valve assembly", "Mech", 2),
        ("EGR cooler assembly", "Mech", 2),
        ("EGR cooler to intake pipe", "Mech", 2),
        ("Exhaust to EGR cooler pipe", "Mech", 2),
    ],
    "Exhaust Circuit": [
        ("Exhaust manifold installation", "Mech", 2),
        ("Catcon installation", "Mech", 2),
        ("TC exit flange adaptation", "Mech", 2),
    ],
    "Turbo System": [
        ("Turbocharger installation", "Mech", 3),
        ("TC oil inlet bolt & drain gasket", "Mech", 1),
    ],
    "Lubrication": [
        ("Lube oil filling & sump verification", "Mech", 1),
        ("Oil filter installation", "Mech", 1),
    ],
    "Cooling": [
        ("Thermostat gasket fitment", "Mech", 1),
        ("Water inlet/outlet adaptation", "Mech", 3),
    ],
    "Fuel System": [
        ("CNG regulator, hoses & filters", "Mech", 3),
    ],
    "Belt Drive": [
        ("Drive belt installation", "Mech", 1),
    ],
    "Gaskets": [
        ("Intake, exhaust, EGR, TC gasket install", "Mech", 2),
    ],
    "Readiness for Mech": [
        ("Mechanical readiness declaration", "Mech", 1),
    ],
    "Wiring Harness": [
        ("Check as per terminal diagram", "Inst", 2),
        ("W/H to BOB to ECU routing", "Inst", 2),
        ("BOB tapping connections", "Inst", 2),
    ],
    "ECU": [
        ("ECU mounting", "Inst", 2),
        ("ECU power cable installation", "Inst", 1),
        ("ECU power validation", "Inst", 1),
    ],
    "Communication": [
        ("CAN setup", "Inst", 1),
    ],
    "Power": [
        ("DC function box", "Inst", 2),
        ("AC function box", "Inst", 2),
        ("Terminal box + fuse", "Inst", 1),
    ],
    "Pressure Sensors": [
        ("Liquid media sensor install", "Inst", 2),
        ("Air media sensor install", "Inst", 2),
        ("10 bar calibration", "Inst", 1),
        ("6 bar calibration", "Inst", 2),
        ("Power cable routing", "Inst", 2),
    ],
    "Pressure Lines": [
        ("Medium temp pipe", "Inst", 2),
        ("High temp braided pipe", "Inst", 2),
        ("Pipe caps", "Inst", 1),
    ],
    "Temperature Sensors": [
        ("RTD install", "Inst", 2),
        ("RTD cable routing", "Inst", 1),
        ("Thermocouple install", "Inst", 2),
        ("TC cable + cold junction", "Inst", 1),
    ],
    "Encoder Elec": [
        ("Angle encoder install", "Inst", 2),
        ("Signal validation", "Inst", 1),
    ],
    "EGT": [
        ("EGT sensor install", "Inst", 3),
        ("DOC/DPF/SCR instrumentation", "Inst", 2),
    ],
    "Lambda": [
        ("Lambda sensor integration", "Inst", 2),
    ],
    "Combustion": [
        ("Combustion sensor install", "Inst", 3),
        ("Clamp meter verification", "Inst", 1),
    ],
    "Drive by Wire": [
        ("Accelerator pedal install", "Inst", 2),
        ("Calibration", "Inst", 2),
    ],
    "Fuel Control": [
        ("EKP circuit install", "Inst", 2),
        ("EKP power routing", "Inst", 1),
    ],
    "Measurement Elec": [
        ("Measurement box install", "Inst", 1),
    ],
    "Routing": [
        ("Cable tray install", "Inst", 2),
        ("Channel wiring", "Inst", 2),
        ("Cable labeling", "Inst", 1),
    ],
    "ETAS": [
        ("ES592 install", "Inst", 2),
        ("Power cable", "Inst", 1),
        ("CAN setup", "Inst", 1),
        ("Clamp mounting", "Inst", 1),
    ],
    "Validation": [
        ("Electrical pre-check", "Inst", 2),
    ],
}

MECH_PHASES = [
    "Engine Receipt", "Trolley Prep", "Mounting", "Alignment", "Drive System",
    "Starter", "Crank Pulley", "Encoder", "Measurement", "Air Circuit",
    "CCV System", "EGR System", "Exhaust Circuit", "Turbo System", "Lubrication",
    "Cooling", "Fuel System", "Belt Drive", "Gaskets", "Readiness for Mech",
]
ELEC_PHASES = [
    "Wiring Harness", "ECU", "Communication", "Power", "Pressure Sensors",
    "Pressure Lines", "Temperature Sensors", "Encoder Elec", "EGT", "Lambda",
    "Combustion", "Drive by Wire", "Fuel Control", "Measurement Elec",
    "Routing", "ETAS", "Validation",
]

TECH_MECH = ["R. Sharma", "A. Kumar", "S. Patel", "M. Reddy", "K. Iyer"]
TECH_ELEC = ["P. Nair", "D. Singh", "V. Rao", "N. Gupta", "T. Joshi"]


def template_activity_count() -> int:
    return sum(len(ACT_TEMPLATES.get(p, [])) for p in MECH_PHASES + ELEC_PHASES)


def build_seed_activities(project_id: str) -> list[dict]:
    acts = []
    seq = 1
    for phase in MECH_PHASES + ELEC_PHASES:
        major = "MECHANICAL PREP" if phase in MECH_PHASES else "ELECTRICAL PREP"
        techs = TECH_MECH if major == "MECHANICAL PREP" else TECH_ELEC
        for (name, dept, hrs) in ACT_TEMPLATES.get(phase, []):
            acts.append({
                "project_id":    project_id,
                "seq_num":       seq,
                "major_phase":   major,
                "phase":         phase,
                "activity_name": name,
                "sub_activity":  "",
                "technician":    techs[seq % len(techs)],
                "dept":          dept,
                "priority":      "Critical" if seq <= 5 else "High" if seq <= 20 else "Medium",
                "plan_start":    "",
                "plan_finish":   "",
                "duration_d":    1,
                "float_d":       0,
                "pct_complete":  0,
                "status":        "Not Started",
                "est_hours":     hrs,
                "actual_hours":  0,
                "actual_start":  "",
                "actual_finish": "",
                "hrs_spent":     0,
                "delay_d":       0,
                "alert_level":   "OK",
                "predecessor_id": seq - 1 if seq > 1 else None,
                "notes":         "",
            })
            seq += 1
    return acts


def create_project_with_activities(data: dict) -> str:
    from backend.database import get_conn
    from backend.scheduler import auto_schedule, compute_derived

    proj_id = data["code"]
    conn = get_conn()
    conn.execute("""
        INSERT INTO projects (id,code,name,customer,engine_type,serial,
            trolley_code,trolley_location,pm_name,start_date,target_finish,
            contract_ref,working_hrs_day,warn_threshold,crit_threshold,status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (proj_id, data.get("code"), data.get("name", ""),
          data.get("customer", ""), data.get("engine_type", ""),
          data.get("serial", ""), data.get("trolley_code", ""),
          data.get("trolley_location", ""), data.get("pm_name", ""),
          data.get("start_date", ""), data.get("target_finish", ""),
          data.get("contract_ref", ""), int(data.get("working_hrs", 9)),
          int(data.get("warn", 3)), int(data.get("crit", 1)), "Not Started"))

    acts = build_seed_activities(proj_id)
    if data.get("start_date"):
        acts = auto_schedule(acts, data["start_date"], int(data.get("working_hrs", 9)))
        acts = compute_derived(
            acts,
            data.get("target_finish") or data.get("forecast_finish") or "",
            int(data.get("warn", 3)),
            int(data.get("crit", 1)))

    for a in acts:
        conn.execute("""INSERT INTO activities
            (project_id,seq_num,major_phase,phase,activity_name,sub_activity,
             technician,dept,priority,plan_start,plan_finish,duration_d,float_d,
             pct_complete,status,est_hours,actual_hours,actual_start,actual_finish,
             hrs_spent,delay_d,alert_level,predecessor_id,notes)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (a["project_id"], a["seq_num"], a["major_phase"], a["phase"],
             a["activity_name"], a["sub_activity"], a["technician"], a["dept"],
             a["priority"], a["plan_start"], a["plan_finish"], a["duration_d"],
             a["float_d"], a["pct_complete"], a["status"], a["est_hours"],
             a["actual_hours"], a["actual_start"], a["actual_finish"],
             a["hrs_spent"], a["delay_d"], a["alert_level"],
             a["predecessor_id"], a["notes"]))
    conn.commit()
    conn.close()
    return proj_id
