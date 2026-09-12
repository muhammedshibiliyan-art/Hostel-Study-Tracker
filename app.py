import streamlit as st
import json
import os
from datetime import date

DATA_FILE = "hostel_students.json"
LOG_FILE = "daily_study_logs.json"
DIVISIONS_FILE = "hostel_divisions.json"

DEFAULT_DIVISIONS = {
    "Plus One": ["Plus One N1", "Plus One N2", "Plus One J1"],
    "Plus Two": ["Plus Two N1", "Plus Two J1"]
}

SUBJECTS = {
    "NEET": ["Physics", "Chemistry", "Zoology", "Botany", "English"],
    "JEE": ["Physics", "Chemistry", "Maths", "English"]
}

EFFORT_LEVELS = [
    "⭐ High Focus (Distraction-free)", 
    "⚡ Moderate Focus", 
    "⚠️ Low Focus / Distracted"
]

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

divisions = load_data(DIVISIONS_FILE, DEFAULT_DIVISIONS)
students = load_data(DATA_FILE, [])
logs = load_data(LOG_FILE, [])

st.set_page_config(page_title="Hostel Study Tracker", page_icon="📖", layout="centered")
st.title("📚 Hostel Study Tracker")

# --- 1. STUDENT & DIVISION MANAGEMENT ---
with st.expander("➕ Register Students / Manage Divisions"):
    st.subheader("Add Student")
    new_name = st.text_input("Student Name")
    new_grade = st.selectbox("Grade", ["Plus One", "Plus Two"], key="reg_grade")
    
    current_div_options = divisions.get(new_grade, []) + ["➕ Add New Division..."]
    selected_div_choice = st.selectbox("Division", current_div_options, key="reg_div")
    
    custom_div = ""
    if selected_div_choice == "➕ Add New Division...":
        custom_div = st.text_input("Enter New Division Name (e.g. Plus One J2 or N3)", key="custom_div_input").strip()
    
    if st.button("Save Student"):
        chosen_div = custom_div if selected_div_choice == "➕ Add New Division..." else selected_div_choice
        
        if not new_name.strip():
            st.error("Please enter a valid student name.")
        elif selected_div_choice == "➕ Add New Division..." and not custom_div:
            st.error("Please enter the custom division name.")
        else:
            final_name = new_name.strip()
            # If a new division was created, save it permanently
            if selected_div_choice == "➕ Add New Division..." and custom_div not in divisions[new_grade]:
                divisions[new_grade].append(custom_div)
                save_data(DIVISIONS_FILE, divisions)

            students.append({"name": final_name, "grade": new_grade, "division": chosen_div})
            save_data(DATA_FILE, students)
            st.toast(f"✅ Saved! {final_name} ({chosen_div}) registered.", icon="🎉")
            st.success(f"Student '{final_name}' successfully added to {chosen_div}!")
            st.rerun()

    if students:
        st.write("---")
        st.caption(f"Total Registered Students: {len(students)}")
        del_target = st.selectbox("Remove a student", ["-- Select to Remove --"] + [f"{s['name']} ({s['division']})" for s in students])
        if st.button("Delete Student") and del_target != "-- Select to Remove --":
            students = [s for s in students if f"{s['name']} ({s['division']})" != del_target]
            save_data(DATA_FILE, students)
            st.toast(f"🗑️ Removed {del_target}", icon="⚠️")
            st.rerun()

if not students:
    st.info("⚠️ Register at least one student above to start logging sessions.")
    st.stop()

# --- 2. LOG / EDIT DAILY STUDY SESSION ---
st.header("📝 Log / Edit Session")

selected_date = st.date_input("Target Date", value=date.today())
selected_date_str = str(selected_date)

student_names = [f"{s['name']} ({s['division']})" for s in students]
selected_display = st.selectbox("Select Student", student_names)
selected_student = students[student_names.index(selected_display)]

track = "JEE" if "J" in selected_student["division"] else "NEET"
available_subjects = SUBJECTS[track]

existing_entry = next(
    (l for l in logs if l.get("name") == selected_student["name"] and l.get("date") == selected_date_str), 
    None
)

if existing_entry:
    st.info(f"✏️ Editing entry for **{selected_student['name']}** on **{selected_date_str}**")
else:
    st.caption(f"Track: **{track}** | Division: **{selected_student['division']}**")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Session 1\n**6:00 PM – 7:30 PM**")
    default_s1_pres = existing_entry.get("s1_present", True) if existing_entry else True
    s1_present = st.checkbox("Present in Session 1", value=default_s1_pres, key="s1_pres")
    
    s1_start_val = st.time_input("Actual Start Time", value=None, key="s1_time", disabled=not s1_present)
    
    sub1_index = 0
    if existing_entry and existing_entry.get("s1_sub") in available_subjects:
        sub1_index = available_subjects.index(existing_entry["s1_sub"]) + 1
    s1_sub = st.selectbox("Subject", ["None"] + available_subjects, index=sub1_index, key="s1_sub", disabled=not s1_present)
    
    default_s1_topic = existing_entry.get("s1_topic", "") if existing_entry and existing_entry.get("s1_topic") != "N/A" else ""
    s1_topic = st.text_input("Topic Studied", value=default_s1_topic, key="s1_top", disabled=not s1_present)
    
    target_opts = ["Completed", "Partial", "Incomplete"]
    target1_idx = target_opts.index(existing_entry["s1_target"]) if (existing_entry and existing_entry.get("s1_target") in target_opts) else 0
    s1_target = st.radio("Target Achieved?", target_opts, index=target1_idx, key="s1_target", horizontal=True, disabled=not s1_present)
    
    default_s1_quiz = existing_entry.get("s1_quiz", "") if existing_entry else ""
    s1_quiz = st.text_input("MCQ / Quiz Result", value=default_s1_quiz, placeholder="e.g. 4/5 or Good concept", key="s1_quiz", disabled=not s1_present)

with col2:
    st.markdown("### Session 2\n**8:30 PM – 11:30 PM**")
    default_s2_pres = existing_entry.get("s2_present", True) if existing_entry else True
    s2_present = st.checkbox("Present in Session 2", value=default_s2_pres, key="s2_pres")
    
    s2_start_val = st.time_input("Actual Start Time", value=None, key="s2_time", disabled=not s2_present)
    
    sub2_index = 0
    if existing_entry and existing_entry.get("s2_sub") in available_subjects:
        sub2_index = available_subjects.index(existing_entry["s2_sub"]) + 1
    s2_sub = st.selectbox("Subject", ["None"] + available_subjects, index=sub2_index, key="s2_sub", disabled=not s2_present)
    
    default_s2_topic = existing_entry.get("s2_topic", "") if existing_entry and existing_entry.get("s2_topic") != "N/A" else ""
    s2_topic = st.text_input("Topic Studied", value=default_s2_topic, key="s2_top", disabled=not s2_present)
    
    target2_idx = target_opts.index(existing_entry["s2_target"]) if (existing_entry and existing_entry.get("s2_target") in target_opts) else 0
    s2_target = st.radio("Target Achieved?", target_opts, index=target2_idx, key="s2_target", horizontal=True, disabled=not s2_present)
    
    default_s2_quiz = existing_entry.get("s2_quiz", "") if existing_entry else ""
    s2_quiz = st.text_input("MCQ / Quiz Result", value=default_s2_quiz, placeholder="e.g. 3/5 or Needs revision", key="s2_quiz", disabled=not s2_present)

focus_idx = EFFORT_LEVELS.index(existing_entry["focus"]) if (existing_entry and existing_entry.get("focus") in EFFORT_LEVELS) else 0
focus_eval = st.select_slider("Study Discipline & Focus", options=EFFORT_LEVELS, value=EFFORT_LEVELS[focus_idx])

default_rem = existing_entry.get("remarks", "") if existing_entry else ""
remarks = st.text_input("Remarks / Notes", value=default_rem, placeholder="e.g. 10m late returning from break, attentive throughout")

btn_label = "Update Entry" if existing_entry else "Submit Entry"
if st.button(btn_label, type="primary"):
    if s1_start_val:
        s1_time_str = s1_start_val.strftime("%I:%M %p")
    elif existing_entry and existing_entry.get("s1_start"):
        s1_time_str = existing_entry["s1_start"]
    else:
        s1_time_str = "Absent" if not s1_present else "Not logged"

    if s2_start_val:
        s2_time_str = s2_start_val.strftime("%I:%M %p")
    elif existing_entry and existing_entry.get("s2_start"):
        s2_time_str = existing_entry["s2_start"]
    else:
        s2_time_str = "Absent" if not s2_present else "Not logged"

    entry = {
        "date": selected_date_str,
        "name": selected_student["name"],
        "grade": selected_student["grade"],
        "division": selected_student["division"],
        "s1_present": s1_present,
        "s1_start": s1_time_str,
        "s1_sub": s1_sub if s1_present else "N/A",
        "s1_topic": s1_topic.strip() if (s1_present and s1_topic) else "N/A",
        "s1_target": s1_target if s1_present else "N/A",
        "s1_quiz": s1_quiz.strip() if (s1_present and s1_quiz) else "",
        "s2_present": s2_present,
        "s2_start": s2_time_str,
        "s2_sub": s2_sub if s2_present else "N/A",
        "s2_topic": s2_topic.strip() if (s2_present and s2_topic) else "N/A",
        "s2_target": s2_target if s2_present else "N/A",
        "s2_quiz": s2_quiz.strip() if (s2_present and s2_quiz) else "",
        "focus": focus_eval,
        "remarks": remarks.strip()
    }

    logs = [l for l in logs if not (l["name"] == entry["name"] and l["date"] == entry["date"])]
    logs.append(entry)
    save_data(LOG_FILE, logs)
    
    st.toast(f"✅ Entry saved for {selected_student['name']}!", icon="💾")
    st.success(f"Saved! Record updated for {selected_student['name']} ({selected_date_str}).")
    st.rerun()

# --- 3. REPORT GENERATOR ---
st.header("📋 Generate WhatsApp Report")
target_grade = st.radio("Select Class Group", ["Plus One", "Plus Two"], horizontal=True)
report_date = st.date_input("Report Date", value=selected_date)
report_date_str = str(report_date)

if st.button("Generate Formatted Report"):
    formatted_date_display = report_date.strftime("%d-%m-%Y")
    grade_logs = [l for l in logs if l.get("grade") == target_grade and l.get("date") == report_date_str]

    if not grade_logs:
        st.warning(f"No records logged for {target_grade} on {formatted_date_display}.")
    else:
        report_lines = [
            "📖 *HOSTEL DAILY STUDY REPORT* 📖",
            f"*Class:* {target_grade.upper()}",
            f"🗓️ *Date:* {formatted_date_display}",
            "⏰ *Study Hours:*",
            "• Session 1: 06:00 PM – 07:30 PM",
            "• Session 2: 08:30 PM – 11:30 PM",
            "━━━━━━━━━━━━━━━━━━━━"
        ]

        for log in grade_logs:
            student_block = [f"👤 *{log['name']}* ({log['division']})"]
            
            # Session 1 Block
            if log.get("s1_present", True):
                student_block.append(f"▪️ *Session 1:* Started: `{log['s1_start']}`")
                student_block.append(f"   ▫️ *Subject:* {log['s1_sub']}")
                student_block.append(f"   ▫️ *Topic:* {log['s1_topic']} ({log['s1_target']})")
                if log.get("s1_quiz"):
                    student_block.append(f"   ▫️ *Topic Check (MCQ):* {log['s1_quiz']}")
            else:
                student_block.append("▪️ *Session 1:* Absent")

            # Session 2 Block
            if log.get("s2_present", True):
                student_block.append(f"▪️ *Session 2:* Started: `{log['s2_start']}`")
                student_block.append(f"   ▫️ *Subject:* {log['s2_sub']}")
                student_block.append(f"   ▫️ *Topic:* {log['s2_topic']} ({log['s2_target']})")
                if log.get("s2_quiz"):
                    student_block.append(f"   ▫️ *Topic Check (MCQ):* {log['s2_quiz']}")
            else:
                student_block.append("▪️ *Session 2:* Absent")

            student_block.append(f"▪️ *Focus:* {log['focus']}")
            
            if log.get('remarks'):
                student_block.append(f"⚠️ *Note:* {log['remarks']}")
                
            student_block.append("────────────────────")
            report_lines.extend(student_block)

        report_lines.append("━━━━━━━━━━━━━━━━━━━━")
        report_lines.append("📌 *Reported by Hostel Mentor*")

        final_text = "\n".join(report_lines)
        st.text_area("Copy and paste to WhatsApp:", final_text, height=350)
