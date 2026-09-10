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
            return json.load(f)
    return default

def save_data(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

students = load_data(DATA_FILE, [])
logs = load_data(LOG_FILE, [])

st.set_page_config(page_title="Hostel Study Tracker", layout="centered")

# --- STUDENT MANAGEMENT ---
with st.expander("➕ Register / Manage Students"):
    new_name = st.text_input("Student Name")
    new_grade = st.selectbox("Grade", ["Plus One", "Plus Two"])
    new_div = st.selectbox("Division", DIVISIONS[new_grade])
    
    if st.button("Save Student"):
        if new_name.strip():
            students.append({"name": new_name.strip(), "grade": new_grade, "division": new_div})
            save_data(DATA_FILE, students)
            st.success(f"Added {new_name.strip()} ({new_div})")
            st.rerun()

if not students:
    st.info("Please register students above to begin logging sessions.")
    st.stop()

# --- LOG STUDY SESSION ---
st.header("📝 Log Daily Session")

student_names = [f"{s['name']} ({s['division']})" for s in students]
selected_display = st.selectbox("Select Student", student_names)
selected_student = students[student_names.index(selected_display)]

track = "JEE" if "J" in selected_student["division"] else "NEET"
available_subjects = SUBJECTS[track]

col1, col2 = st.columns(2)
with col1:
    session_1_start = st.time_input("Session 1 Start (Sched: 6:00 PM)", value=None)
    session_1_sub = st.selectbox("Session 1 Subject", ["None"] + available_subjects, key="s1_sub")
    session_1_topic = st.text_input("Session 1 Topic", key="s1_top")

with col2:
    session_2_start = st.time_input("Session 2 Start (Sched: 8:30 PM)", value=None)
    session_2_sub = st.selectbox("Session 2 Subject", ["None"] + available_subjects, key="s2_sub")
    session_2_topic = st.text_input("Session 2 Topic", key="s2_top")

remarks = st.text_input("Remarks / Punctuality Notes (e.g., Started 45m late)")

if st.button("Submit Entry"):
    entry = {
        "date": str(date.today()),
        "name": selected_student["name"],
        "grade": selected_student["grade"],
        "division": selected_student["division"],
        "s1_start": session_1_start.strftime("%I:%M %p") if session_1_start else "Absent/Late",
        "s1_sub": session_1_sub,
        "s1_topic": session_1_topic,
        "s2_start": session_2_start.strftime("%I:%M %p") if session_2_start else "Absent/Late",
        "s2_sub": session_2_sub,
        "s2_topic": session_2_topic,
        "remarks": remarks
    }
    # Update if already exists for today, else append
    logs = [l for l in logs if not (l["name"] == entry["name"] and l["date"] == entry["date"])]
    logs.append(entry)
    save_data(LOG_FILE, logs)
    st.success(f"Entry saved for {selected_student['name']}!")

# --- REPORT GENERATOR ---
st.header("📋 Generate WhatsApp Report")
target_grade = st.radio("Select Class Report", ["Plus One", "Plus Two"], horizontal=True)

if st.button("Generate Formatted Report"):
    today_str = str(date.today())
    grade_logs = [l for l in logs if l.get("grade") == target_grade and l.get("date") == today_str]

    if not grade_logs:
        st.warning(f"No records found for {target_grade} today.")
    else:
        report_lines = [
            f"*{target_grade.upper()} - DAILY HOSTEL STUDY REPORT*",
            f"📅 *Date:* {today_str}\n",
            "━━━━━━━━━━━━━━━━━━━━"
        ]

        for log in grade_logs:
            student_block = [
                f"👤 *{log['name']}* ({log['division']})",
                f"▪️ *Session 1:* Started: `{log['s1_start']}` | {log['s1_sub']} ({log['s1_topic'] or 'N/A'})",
                f"▪️ *Session 2:* Started: `{log['s2_start']}` | {log['s2_sub']} ({log['s2_topic'] or 'N/A'})"
            ]
            if log['remarks']:
                student_block.append(f"⚠️ *Note:* {log['remarks']}")
            student_block.append("────────────────────")
            report_lines.extend(student_block)

        final_text = "\n".join(report_lines)
        st.text_area("Copy and paste to WhatsApp:", final_text, height=250)

