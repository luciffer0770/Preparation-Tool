# ps_etw_tracker/backend/models.py — 91-activity master template
from __future__ import annotations

ACT_TEMPLATES = {
    "Engine Receipt": [
        ("Engine unloading & safe handling", "Mech", 9),
        ("Visual inspection & damage check", "Mech", 4),
        ("Engine serial & configuration verification", "Mech", 3),
        ("Spare parts accountability & tagging", "Mech", 4),
    ],
    "Trolley Prep": [("Trolley cleaning & preparation", "Mech", 6)],
    "Mounting": [
        ("Review engine mounting drawings", "Mech", 4),
        ("Mounting bracket design", "Mech", 6),
        ("Mounting bracket fabrication", "Mech", 9),
        ("Side mounting bracket fabrication", "Mech", 6),
        ("Damper section verification", "Mech", 4),
    ],
    "Alignment": [
        ("Screw jack & damper section installation", "Mech", 5),
        ("Engine mounting on trolley", "Mech", 9),
        ("Engine-dyno alignment", "Mech", 6),
    ],
    "Drive System": [
        ("Drive plate drawing review", "Mech", 3),
        ("Drive plate machining", "Mech", 9),
        ("Shaft fitment & verification", "Mech", 6),
    ],
    "Starter": [
        ("Starter motor inspection", "Mech", 3),
        ("Starter motor fitment", "Mech", 5),
    ],
    "Crank Pulley": [
        ("Crank pulley modification", "Mech", 4),
        ("Crank pulley torque verification", "Mech", 3),
    ],
    "Encoder": [
        ("Encoder flange design", "Mech", 4),
        ("Encoder flange machining", "Mech", 9),
        ("Encoder pulley machining", "Mech", 6),
        ("Angle encoder mounting", "Mech", 4),
    ],
    "Measurement": [
        ("Measurement layout finalization", "Mech", 4),
        ("Combustion sensor boss machining", "Mech", 9),
    ],
    "Air Circuit": [
        ("Air filter installation", "Mech", 3),
        ("Air filter to compressor inlet hose routing", "Mech", 6),
        ("Compressor outlet to intercooler hose", "Mech", 6),
        ("Intercooler to intake manifold hose", "Mech", 6),
    ],
    "CCV System": [
        ("CCV assembly & circuit with NRV", "Mech", 5),
    ],
    "EGR System": [
        ("EGR valve assembly", "Mech", 5),
        ("EGR cooler assembly", "Mech", 5),
        ("EGR cooler to intake manifold pipe", "Mech", 5),
    ],
    "Exhaust Circuit": [
        ("Exhaust manifold installation", "Mech", 5),
        ("Catcon installation", "Mech", 5),
        ("TC exit flange adaptation", "Mech", 6),
    ],
    "Turbo System": [
        ("Turbocharger installation", "Mech", 5),
        ("TC oil inlet banjo & drain gasket", "Mech", 4),
        ("Turbo wastegate setup", "Mech", 4),
    ],
    "Lubrication": [
        ("Lube oil filling & sump verification", "Mech", 3),
        ("Oil lines install & leak test", "Mech", 5),
    ],
    "Cooling": [
        ("Thermostat gasket fitment", "Mech", 3),
        ("Water inlet/outlet adaptation", "Mech", 6),
        ("Coolant fill & bleed", "Mech", 4),
    ],
    "Fuel System": [
        ("CNG regulator, hoses & filters installation", "Mech", 7),
        ("Fuel rail inspection", "Mech", 3),
        ("Pressure test fuel system", "Mech", 5),
    ],
    "Belt Drive": [
        ("Drive belt installation", "Mech", 3),
        ("Belt tension setup & check", "Mech", 4),
    ],
    "Gaskets": [
        ("Intake, exhaust, EGR, TC gasket installation", "Mech", 5),
        ("Gasket torque verification", "Mech", 3),
    ],
    "Readiness for Mech": [
        ("Mechanical readiness declaration", "Mech", 4),
    ],
    "Wiring Harness": [
        ("Check according to terminal diagram", "Inst", 3),
        ("W/H to BOB to ECU routing", "Inst", 7),
        ("BOB tapping connections", "Inst", 5),
    ],
    "ECU": [
        ("ECU mounting & fixation", "Inst", 4),
        ("ECU power cable installation", "Inst", 3),
        ("ECU power circuit validation", "Inst", 3),
    ],
    "Communication": [
        ("CAN communication setup", "Inst", 5),
        ("CAN termination check", "Inst", 3),
    ],
    "Power": [
        ("DC function box installation", "Inst", 4),
        ("AC function box installation", "Inst", 4),
        ("Terminal box with 7.5A fuse installation", "Inst", 3),
    ],
    "Pressure Sensors": [
        ("Liquid media pressure sensor installation", "Inst", 4),
        ("Air media pressure sensor installation", "Inst", 4),
        ("Low pressure transmitter 10 bar cal", "Inst", 4),
        ("Pressure transmitter power cable routing", "Inst", 3),
    ],
    "Pressure Lines": [
        ("Medium temperature pressure pipe", "Inst", 4),
        ("High temperature braided pipe", "Inst", 4),
        ("Pressure pipe caps installation", "Inst", 3),
    ],
    "Temperature Sensors": [
        ("RTD installation", "Inst", 4),
        ("RTD extension cable routing", "Inst", 3),
        ("Thermocouple installation", "Inst", 4),
    ],
    "Encoder Elec": [
        ("Angle encoder installation", "Inst", 4),
    ],
    "EGT": [
        ("EGT sensor installation", "Inst", 5),
        ("DOC/DPF/SCR/Brick instrumentation", "Inst", 5),
    ],
    "Lambda": [
        ("Lambda sensor external integration", "Inst", 4),
    ],
    "Combustion": [
        ("Combustion pressure sensor installation", "Inst", 6),
    ],
    "Drive by Wire": [
        ("Accelerator pedal installation", "Inst", 4),
    ],
    "Fuel Control": [
        ("EKP circuit installation", "Inst", 5),
    ],
    "Measurement Elec": [
        ("Measurement box installation", "Inst", 4),
    ],
    "Routing": [
        ("Cable tray installation", "Inst", 4),
        ("Centre channel wiring arrangement", "Inst", 4),
    ],
    "ETAS": [
        ("ETAS ES592 installation", "Inst", 3),
        ("ETAS power cable connection", "Inst", 3),
        ("ETAS CAN cable setup", "Inst", 4),
    ],
    "Validation": [
        ("Pre-power continuity check", "Inst", 4),
        ("Power-on smoke test", "Inst", 4),
        ("ECU communication validation", "Inst", 5),
        ("Final electrical sign-off", "Inst", 4),
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
