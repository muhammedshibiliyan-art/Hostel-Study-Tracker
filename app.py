import streamlit as st
import json
import os
import urllib.parse
from datetime import date

DATA_FILE = "hostel_students.json"
LOG_FILE = "daily_study_logs.json"
DIVISIONS_FILE = "hostel_divisions.json"
TOPICS_FILE = "subject_topics_cache.json"

DEFAULT_DIVISIONS = {
    "Plus One": ["Plus One N1", "Plus One N2", "Plus One J1", "Plus One J2"],
    "Plus Two": ["Plus Two N1", "Plus Two N2", "Plus Two J1"]
}

SUBJECTS = {
    "NEET": ["Physics", "Chemistry", "Zoology", "Botany", "English", "Maths"],
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
topic_cache = load_data(TOPICS_FILE, {})

st.set_page_config(page_title="Hostel Study Tracker", page_icon="📖", layout="centered")
st.title("📚 Hostel Study Tracker")

tab_log, tab_report, tab_manage_logs, tab_settings = st.tabs([
    "📝 Log Session", 
    "📋 WhatsApp Report", 
    "🗑️ Manage / Delete Logs",
    "⚙️ Manage Roster"
])

# ==========================================
# TAB 1: LOG DAILY STUDY SESSION
# ==========================================
with tab_log:
    if not students:
        st.info("⚠️ Go to the '⚙️ Manage Roster' tab to register students first.")
    else:
        selected_date = st.date_input("Date", value=date.today(), key="log_date")
        selected_date_str = str(selected_date)

        logged_names = {l["name"] for l in logs if l.get("date") == selected_date_str}
        total_students = len(students)
        logged_count = len([s for s in students if s["name"] in logged_names])
        progress_val = logged_count / total_students if total_students > 0 else 0

        st.progress(progress_val, text=f"Logged: {logged_count} / {total_students} Students ({int(progress_val * 100)}%)")

        student_display_options = []
        for s in students:
            status_icon = "🟢" if s["name"] in logged_names else "⚪"
            student_display_options.append(f"{status_icon} {s['name']} ({s['division']})")

        selected_display = st.selectbox("Select Student", student_display_options)
        selected_index = student_display_options.index(selected_display)
        selected_student = students[selected_index]

        track = "JEE" if "J" in selected_student["division"] else "NEET"
        available_subjects = SUBJECTS[track]

        existing_entry = next(
            (l for l in logs if l.get("name") == selected_student["name"] and l.get("date") == selected_date_str), 
            None
        )

        if existing_entry:
            st.info(f"✏️ Editing entry for **{selected_student['name']}**")

        st.write("---")
        session_tabs = st.tabs(["Session 1 (6:00 PM – 7:30 PM)", "Session 2 (8:30 PM – 11:30 PM)"])

        # --- SESSION 1 ---
        with session_tabs[0]:
            default_s1_pres = existing_entry.get("s1_present", True) if existing_entry else True
            s1_present = st.checkbox("Present in Session 1", value=default_s1_pres, key="s1_pres")

            if s1_present:
                st.caption("Quick Start Time:")
                s1_preset = st.radio(
                    "S1 Quick Time",
                    ["On Time (06:00 PM)", "+5m (06:05 PM)", "+10m (06:10 PM)", "+15m (06:15 PM)", "+30m (06:30 PM)", "Custom"],
                    horizontal=True,
                    key="s1_quick"
                )

                if s1_preset == "Custom":
                    s1_start_val = st.time_input("Custom Start Time", value=None, key="s1_custom_time")
                    s1_time_str = s1_start_val.strftime("%I:%M %p") if s1_start_val else "Not logged"
                else:
                    s1_time_str = s1_preset.split("(")[-1].replace(")", "")

                sub1_index = 0
                if existing_entry and existing_entry.get("s1_sub") in available_subjects:
                    sub1_index = available_subjects.index(existing_entry["s1_sub"])
                s1_sub = st.selectbox("Subject", available_subjects, index=sub1_index, key="s1_sub")

                known_topics_s1 = topic_cache.get(s1_sub, [])
                default_s1_topic = existing_entry.get("s1_topic", "") if existing_entry else ""
                
                if known_topics_s1:
                    topic_choice_s1 = st.selectbox("Previous Topics (or type below)", ["-- New Topic --"] + known_topics_s1, key="s1_cache_picker")
                    if topic_choice_s1 != "-- New Topic --":
                        default_s1_topic = topic_choice_s1

                s1_topic = st.text_input("Topic Studied", value=default_s1_topic, key="s1_topic_input")

                target_opts = ["Completed", "Partial", "Incomplete"]
                target1_idx = target_opts.index(existing_entry["s1_target"]) if (existing_entry and existing_entry.get("s1_target") in target_opts) else 0
                s1_target = st.radio("Target Status", target_opts, index=target1_idx, horizontal=True, key="s1_target")

                default_s1_quiz = existing_entry.get("s1_quiz", "") if existing_entry else ""
                s1_quiz = st.text_input("MCQ / Quiz Score", value=default_s1_quiz, placeholder="e.g. 4/5 or Good concept", key="s1_quiz")
            else:
                s1_time_str = "Absent"
                s1_sub = "N/A"
                s1_topic = "N/A"
                s1_target = "N/A"
                s1_quiz = ""

        # --- SESSION 2 ---
        with session_tabs[1]:
            default_s2_pres = existing_entry.get("s2_present", True) if existing_entry else True
            s2_present = st.checkbox("Present in Session 2", value=default_s2_pres, key="s2_pres")

            if s2_present:
                st.caption("Quick Start Time:")
                s2_preset = st.radio(
                    "S2 Quick Time",
                    ["On Time (08:30 PM)", "+5m (08:35 PM)", "+10m (08:40 PM)", "+15m (08:45 PM)", "+30m (09:00 PM)", "Custom"],
                    horizontal=True,
                    key="s2_quick"
                )

                if s2_preset == "Custom":
                    s2_start_val = st.time_input("Custom Start Time", value=None, key="s2_custom_time")
                    s2_time_str = s2_start_val.strftime("%I:%M %p") if s2_start_val else "Not logged"
                else:
                    s2_time_str = s2_preset.split("(")[-1].replace(")", "")

                sub2_index = 0
                if existing_entry and existing_entry.get("s2_sub") in available_subjects:
                    sub2_index = available_subjects.index(existing_entry["s2_sub"])
                s2_sub = st.selectbox("Subject", available_subjects, index=sub2_index, key="s2_sub")

                known_topics_s2 = topic_cache.get(s2_sub, [])
                default_s2_topic = existing_entry.get("s2_topic", "") if existing_entry else ""

                if known_topics_s2:
                    topic_choice_s2 = st.selectbox("Previous Topics (or type below)", ["-- New Topic --"] + known_topics_s2, key="s2_cache_picker")
                    if topic_choice_s2 != "-- New Topic --":
                        default_s2_topic = topic_choice_s2

                s2_topic = st.text_input("Topic Studied", value=default_s2_topic, key="s2_topic_input")

                target2_idx = target_opts.index(existing_entry["s2_target"]) if (existing_entry and existing_entry.get("s2_target") in target_opts) else 0
                s2_target = st.radio("Target Status", target_opts, index=target2_idx, horizontal=True, key="s2_target")

                default_s2_quiz = existing_entry.get("s2_quiz", "") if existing_entry else ""
                s2_quiz = st.text_input("MCQ / Quiz Score", value=default_s2_quiz, placeholder="e.g. 3/5 or Needs revision", key="s2_quiz")
            else:
                s2_time_str = "Absent"
                s2_sub = "N/A"
                s2_topic = "N/A"
                s2_target = "N/A"
                s2_quiz = ""

        st.write("---")
        focus_idx = EFFORT_LEVELS.index(existing_entry["focus"]) if (existing_entry and existing_entry.get("focus") in EFFORT_LEVELS) else 0
        focus_eval = st.select_slider("Study Discipline & Focus", options=EFFORT_LEVELS, value=EFFORT_LEVELS[focus_idx])

        remarks = st.text_input("Remarks / Notes (Optional)", value="", placeholder="e.g. 10m late returning from break, attentive throughout", key=f"rem_{selected_student['name']}")

        btn_label = "Update Entry" if existing_entry else "Save Entry"
        if st.button(btn_label, type="primary", use_container_width=True):
            if s1_present and s1_topic.strip() and s1_topic.strip() != "N/A":
                topic_cache.setdefault(s1_sub, [])
                if s1_topic.strip() not in topic_cache[s1_sub]:
                    topic_cache[s1_sub].append(s1_topic.strip())

            if s2_present and s2_topic.strip() and s2_topic.strip() != "N/A":
                topic_cache.setdefault(s2_sub, [])
                if s2_topic.strip() not in topic_cache[s2_sub]:
                    topic_cache[s2_sub].append(s2_topic.strip())

            save_data(TOPICS_FILE, topic_cache)

            entry = {
                "date": selected_date_str,
                "name": selected_student["name"],
                "grade": selected_student["grade"],
                "division": selected_student["division"],
                "s1_present": s1_present,
                "s1_start": s1_time_str,
                "s1_sub": s1_sub,
                "s1_topic": s1_topic.strip() if s1_present else "N/A",
                "s1_target": s1_target,
                "s1_quiz": s1_quiz.strip(),
                "s2_present": s2_present,
                "s2_start": s2_time_str,
                "s2_sub": s2_sub,
                "s2_topic": s2_topic.strip() if s2_present else "N/A",
                "s2_target": s2_target,
                "s2_quiz": s2_quiz.strip(),
                "focus": focus_eval,
                "remarks": remarks.strip()
            }

            logs = [l for l in logs if not (l["name"] == entry["name"] and l["date"] == entry["date"])]
            logs.append(entry)
            save_data(LOG_FILE, logs)
            
            st.toast(f"✅ Saved for {selected_student['name']}!", icon="💾")
            st.success(f"Record saved for {selected_student['name']}.")
            st.rerun()

# ==========================================
# TAB 2: WHATSAPP REPORT GENERATOR
# ==========================================
with tab_report:
    st.subheader("Generate Daily Report")
    target_grade = st.radio("Select Class Group", ["Plus One", "Plus Two"], horizontal=True, key="rep_grade")
    report_date = st.date_input("Report Date", value=date.today(), key="rep_date")
    report_date_str = str(report_date)

    if st.button("Build Formatted Report", type="primary", use_container_width=True):
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
                
                if log.get("s1_present", True):
                    student_block.append(f"▪️ *Session 1:* Started: `{log['s1_start']}`")
                    student_block.append(f"   ▫️ *Subject:* {log['s1_sub']}")
                    student_block.append(f"   ▫️ *Topic:* {log['s1_topic']} ({log['s1_target']})")
                    if log.get("s1_quiz"):
                        student_block.append(f"   ▫️ *Topic Check (MCQ):* {log['s1_quiz']}")
                else:
                    student_block.append("▪️ *Session 1:* Absent")

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
            st.session_state["generated_report"] = final_text

    if "generated_report" in st.session_state:
        final_text = st.session_state["generated_report"]
        st.text_area("WhatsApp Text Format:", final_text, height=350)
        
        encoded_text = urllib.parse.quote(final_text)
        col_wa1, col_wa2 = st.columns(2)
        with col_wa1:
            st.link_button("📲 Regular WhatsApp", f"whatsapp://send?text={encoded_text}", use_container_width=True)
        with col_wa2:
            st.link_button("🌐 WhatsApp Web / Fallback", f"https://api.whatsapp.com/send?text={encoded_text}", use_container_width=True)

# ==========================================
# TAB 3: MANAGE / DELETE LOGS
# ==========================================
with tab_manage_logs:
    st.subheader("🗑️ Delete a Specific Entry")
    del_log_date = st.date_input("Select Date of Entry", value=date.today(), key="del_log_date_pick")
    del_log_date_str = str(del_log_date)

    matching_logs = [l for l in logs if l.get("date") == del_log_date_str]

    if not matching_logs:
        st.info(f"No study records found for {del_log_date.strftime('%d-%m-%Y')}.")
    else:
        log_options = ["-- Select Entry to Delete --"] + [
            f"{l['name']} ({l['division']}) - S1: {l.get('s1_sub', 'N/A')}, S2: {l.get('s2_sub', 'N/A')}"
            for l in matching_logs
        ]
        
        selected_log_to_delete = st.selectbox("Select Student Entry to Delete", log_options)

        if st.button("🗑️ Delete Selected Entry Completely", type="primary", use_container_width=True):
            if selected_log_to_delete == "-- Select Entry to Delete --":
                st.warning("Please choose an entry from the list first.")
            else:
                target_student_name = selected_log_to_delete.split(" (")[0]
                logs = [l for l in logs if not (l["name"] == target_student_name and l["date"] == del_log_date_str)]
                save_data(LOG_FILE, logs)
                st.toast(f"✅ Deleted record for {target_student_name} on {del_log_date_str}!", icon="🗑️")
                st.success(f"Successfully deleted entry for {target_student_name}.")
                st.rerun()

# ==========================================
# TAB 4: MANAGE ROSTER & DIVISIONS
# ==========================================
with tab_settings:
    st.subheader("➕ Add New Student")
    new_name = st.text_input("Student Name", key="new_s_name")
    new_grade = st.selectbox("Grade", ["Plus One", "Plus Two"], key="new_s_grade")
    
    current_div_options = divisions.get(new_grade, [])
    selected_div = st.selectbox("Division", current_div_options, key="new_s_div")

    if st.button("Register Student", use_container_width=True):
        if not new_name.strip():
            st.error("Please enter a student name.")
        elif not selected_div:
            st.error("Please select a division.")
        else:
            final_name = new_name.strip()
            students.append({"name": final_name, "grade": new_grade, "division": selected_div})
            save_data(DATA_FILE, students)
            st.toast(f"✅ Registered {final_name}!", icon="🎉")
            st.success(f"{final_name} ({selected_div}) added successfully.")
            st.rerun()

    st.write("---")
    st.subheader("🏷️ Add New Division")
    target_div_grade = st.selectbox("For Class", ["Plus One", "Plus Two"], key="new_div_grade")
    new_custom_div = st.text_input("Division Name (e.g. Plus One J3 or Plus Two N3)", key="new_custom_div_box").strip()
    
    if st.button("Save New Division", use_container_width=True):
        if not new_custom_div:
            st.error("Please enter a division name.")
        elif new_custom_div in divisions.get(target_div_grade, []):
            st.warning(f"'{new_custom_div}' already exists.")
        else:
            divisions.setdefault(target_div_grade, []).append(new_custom_div)
            save_data(DIVISIONS_FILE, divisions)
            st.toast(f"✅ Division '{new_custom_div}' added!", icon="🎉")
            st.success(f"Added division '{new_custom_div}' to {target_div_grade}.")
            st.rerun()

    if students:
        st.write("---")
        st.subheader("🗑️ Remove Student from Hostel Roster")
        del_target = st.selectbox("Select student to delete from roster", ["-- Select --"] + [f"{s['name']} ({s['division']})" for s in students])
        if st.button("Delete Student from Roster", use_container_width=True) and del_target != "-- Select --":
            students = [s for s in students if f"{s['name']} ({s['division']})" != del_target]
            save_data(DATA_FILE, students)
            st.toast(f"🗑️ Removed {del_target}", icon="⚠️")
            st.rerun()
    
