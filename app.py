import streamlit as st
import json
import os
from datetime import date

DATA_FILE = "hostel_students.json"
LOG_FILE = "daily_study_logs.json"

DIVISIONS = {
    "Plus One": ["Plus One N1", "Plus One N2", "Plus One J1"],
    "Plus Two": ["Plus Two J1", "Plus Two N1", "Plus Two N2"]
}

SUBJECTS = {
    "NEET": ["Physics", "Chemistry", "Zoology", "Botany", "English"],
    "JEE": ["Physics", "Chemistry", "Maths", "English"]
}

def load_data(filepath, default):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            try:
                return json.load(f)
            except Exception:
                return default
    return default

def save_data(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

students = load_data(DATA_FILE, [])
logs = load_data(LOG_FILE, [])

st.set_page_config(page_title="Hostel Study Tracker", page_icon="📖", layout="centered")

st.title("📚 Hostel Study Tracker")

# --- 1. STUDENT REGISTRATION ---
with st.expander("➕ Register / Manage Students"):
    new_name = st.text_input("Student Name")
    new_grade = st.selectbox("Grade", ["Plus One", "Plus Two"], key="reg_grade")
    new_div = st.selectbox("Division", DIVISIONS[new_grade], key="reg_div")
    
    if st.button("Save Student"):
        if new_name.strip():
            students.append({"name": new_name.strip(), "grade": new_grade, "division": new_div})
            save_data(DATA_FILE, students)
            st.success(f"Added {new_name.strip()} ({new_div})")
            st.rerun()

    if students:
        st.write("---")
        st.caption(f"Total Registered Students: {len(students)}")
        del_target = st.selectbox("Remove a student", ["-- Select to Remove --"] + [f"{s['name']} ({s['division']})" for s in students])
        if st.button("Delete Student") and del_target != "-- Select to Remove --":
            students = [s for s in students if f"{s['name']} ({s['division']})" != del_target]
            save_data(DATA_FILE, students)
            st.warning(f"Removed {del_target}")
            st.rerun()

if not students:
    st.info("⚠️ Please register at least one student above to start logging sessions.")
    st.stop()

# --- 2. LOG DAILY STUDY SESSION ---
st.header("📝 Log Daily Session")

student_names = [f"{s['name']} ({s['division']})" for s in students]
selected_display = st.selectbox("Select Student", student_names)
selected_student = students[student_names.index(selected_display)]

track = "JEE" if "J" in selected_student["division"] else "NEET"
available_subjects = SUBJECTS[track]

st.caption(f"Track: **{track}** | Division: **{selected_student['division']}**")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Session 1 (6:00 PM)")
    session_1_present = st.checkbox("Present in Session 1", value=True)
    session_1_start = st.time_input("Start Time", value=None, key="s1_time", disabled=not session_1_present)
    session_1_sub = st.selectbox("Subject", ["None"] + available_subjects, key="s1_sub", disabled=not session_1_present)
    session_1_topic = st.text_input("Topic Studied", key="s1_top", disabled=not session_1_present)

with col2:
    st.subheader("Session 2 (8:30 PM)")
    session_2_present = st.checkbox("Present in Session 2", value=True)
    session_2_start = st.time_input("Start Time", value=None, key="s2_time", disabled=not session_2_present)
    session_2_sub = st.selectbox("Subject", ["None"] + available_subjects, key="s2_sub", disabled=not session_2_present)
    session_2_topic = st.text_input("Topic Studied", key="s2_top", disabled=not session_2_present)

remarks = st.text_input("Remarks / Punctuality Notes (e.g. Late by 20 mins, indisposed)")

if st.button("Submit Entry", type="primary"):
    today_str = str(date.today())
    
    s1_time_str = session_1_start.strftime("%I:%M %p") if (session_1_present and session_1_start) else ("Absent" if not session_1_present else "Not specified")
    s2_time_str = session_2_start.strftime("%I:%M %p") if (session_2_present and session_2_start) else ("Absent" if not session_2_present else "Not specified")

    entry = {
        "date": today_str,
        "name": selected_student["name"],
        "grade": selected_student["grade"],
        "division": selected_student["division"],
        "s1_present": session_1_present,
        "s1_start": s1_time_str,
        "s1_sub": session_1_sub if session_1_present else "N/A",
        "s1_topic": session_1_topic if session_1_present else "N/A",
        "s2_present": session_2_present,
        "s2_start": s2_time_str,
        "s2_sub": session_2_sub if session_2_present else "N/A",
        "s2_topic": session_2_topic if session_2_present else "N/A",
        "remarks": remarks.strip()
    }

    # Replace entry if already entered for this student today
    logs = [l for l in logs if not (l["name"] == entry["name"] and l["date"] == entry["date"])]
    logs.append(entry)
    save_data(LOG_FILE, logs)
    st.success(f"Log saved for {selected_student['name']}!")

# --- 3. REPORT GENERATOR ---
st.header("📋 Generate WhatsApp Report")
target_grade = st.radio("Select Class Group", ["Plus One", "Plus Two"], horizontal=True)

if st.button("Generate Formatted Report"):
    today_str = str(date.today())
    grade_logs = [l for l in logs if l.get("grade") == target_grade and l.get("date") == today_str]

    if not grade_logs:
        st.warning(f"No records found for {target_grade} today ({today_str}).")
    else:
        report_lines = [
            f"*{target_grade.upper()} - DAILY HOSTEL STUDY REPORT*",
            f"📅 *Date:* {today_str}",
            "━━━━━━━━━━━━━━━━━━━━"
        ]

        for log in grade_logs:
            s1_detail = f"Started: `{log['s1_start']}` | {log['s1_sub']} ({log['s1_topic'] or 'N/A'})" if log.get('s1_present', True) else "Absent"
            s2_detail = f"Started: `{log['s2_start']}` | {log['s2_sub']} ({log['s2_topic'] or 'N/A'})" if log.get('s2_present', True) else "Absent"

            student_block = [
                f"👤 *{log['name']}* ({log['division']})",
                f"▪️ *Session 1 (6:00 PM):* {s1_detail}",
                f"▪️ *Session 2 (8:30 PM):* {s2_detail}"
            ]
            if log['remarks']:
                student_block.append(f"⚠️ *Note:* {log['remarks']}")
            student_block.append("────────────────────")
            report_lines.extend(student_block)

        final_text = "\n".join(report_lines)
        st.text_area("Copy and paste to WhatsApp:", final_text, height=300)
            
