import streamlit as st
import json
from db.models import SessionLocal, PatientComplaint, StaffComplaint, PublicIssue, init_db
from chains.analysis_chain import analyze_complaint
from utils.severity import calculate_severity

# Initialize database
init_db()

# Page config
st.set_page_config(
    page_title="CANDOR - Complaint Intelligence",
    page_icon="🏥",
    layout="centered"
)

# Title
st.title("🏥 CANDOR")
st.subheader("AI-Powered Complaint Intelligence Platform")
st.markdown("---")

# Choose complaint type
complaint_type = st.radio(
    "Who are you?",
    ["Patient", "Staff Member"],
    horizontal=True
)

st.markdown("---")

# ---- PATIENT FORM ----
if complaint_type == "Patient":
    st.markdown("### 📋 Patient Complaint Form")

    department = st.selectbox(
        "Which department?",
        ["General Practice", "Cardiology", "Orthopedics",
         "Neurology", "Physiotherapy", "Gastroenterology",
         "Renal", "Emergency", "None"]
    )

    rating = st.slider(
        "How would you rate your experience?",
        min_value=1, max_value=5, value=3
    )

    wait_time = st.number_input(
        "How long did you wait? (minutes)",
        min_value=0, max_value=300, value=15
    )

    complaint_text = st.text_area(
        "Describe your complaint or feedback",
        placeholder="Tell us what happened...",
        height=150
    )

    is_public = st.checkbox(
        "Allow this complaint to be used for improving hospital services"
    )

    if st.button("🔍 Analyse My Complaint", use_container_width=True):
        if complaint_text.strip() == "":
            st.warning("Please enter your complaint first!")
        else:
            with st.spinner("AI is analysing your complaint..."):
                # Get AI analysis
                result = analyze_complaint(
                    complaint=complaint_text,
                    role="Patient",
                    department=department
                )

                # Calculate severity
                severity = calculate_severity(
                    role="Patient",
                    rating=rating,
                    complaint_text=complaint_text,
                    department=department
                )

            # Store in session state
            st.session_state["analysis"] = result
            st.session_state["severity"] = severity
            st.session_state["complaint_text"] = complaint_text
            st.session_state["department"] = department
            st.session_state["rating"] = rating
            st.session_state["wait_time"] = wait_time
            st.session_state["is_public"] = is_public
            st.session_state["complaint_type"] = "patient"

    # Show results if analysis is done
    if "analysis" in st.session_state and st.session_state.get("complaint_type") == "patient":
        result = st.session_state["analysis"]
        severity = st.session_state["severity"]

        st.markdown("---")
        st.markdown("### 🔎 Analysis Results")

        # Show severity badge
        if severity == "Critical":
            st.error(f"🔴 Severity: **{severity}**")
        elif severity == "High":
            st.warning(f"🟠 Severity: **{severity}**")
        elif severity == "Medium":
            st.info(f"🟡 Severity: **{severity}**")
        else:
            st.success(f"🟢 Severity: **{severity}**")

        st.markdown(f"**Detected Theme:** {result['theme']}")
        st.markdown("---")

        st.markdown("### 💡 Suggested Solutions")
        st.markdown("Please select the most appropriate solution:")

        selected = st.radio(
            "Choose a solution:",
            result["solutions"] + ["Other (I'll describe my own)"]
        )

        custom_solution = ""
        if selected == "Other (I'll describe my own)":
            custom_solution = st.text_area("Describe your solution:")

        if st.button("✅ Submit Complaint", use_container_width=True):
            final_solution = custom_solution if selected == "Other (I'll describe my own)" else selected

            # Save to database
            session = SessionLocal()
            complaint = PatientComplaint(
                department=st.session_state["department"],
                rating=st.session_state["rating"],
                wait_time=st.session_state["wait_time"],
                complaint_text=st.session_state["complaint_text"],
                theme=result["theme"],
                suggestions=json.dumps(result["solutions"]),
                selected_solution=final_solution,
                severity=severity,
                is_public=st.session_state["is_public"]
            )
            session.add(complaint)

            # Update public issues
            if st.session_state["is_public"]:
                existing = session.query(PublicIssue).filter_by(theme=result["theme"]).first()
                if existing:
                    existing.frequency += 1
                else:
                    session.add(PublicIssue(
                        theme=result["theme"],
                        frequency=1,
                        highest_severity=severity
                    ))

            session.commit()
            session.close()

            st.success("✅ Your complaint has been submitted successfully!")
            st.balloons()

            # Clear session
            for key in ["analysis", "severity", "complaint_text",
                        "department", "rating", "wait_time",
                        "is_public", "complaint_type"]:
                st.session_state.pop(key, None)

# ---- STAFF FORM ----
else:
    st.markdown("### 👨‍⚕️ Staff Complaint Form")

    name = st.text_input("Your Name")

    role = st.selectbox(
        "Your Role",
        ["Doctor", "Nurse", "Admin", "Pharmacist",
         "Lab Technician", "Ambulance Staff", "Janitor"]
    )

    department = st.selectbox(
        "Your Department",
        ["OPD", "Emergency", "Surgery", "ICU", "Pharmacy"]
    )

    rating = st.slider(
        "How would you rate the current situation?",
        min_value=1, max_value=5, value=3
    )

    complaint_text = st.text_area(
        "Describe your complaint or concern",
        placeholder="Tell us what happened...",
        height=150
    )

    is_public = st.checkbox(
        "Allow this to be shared for operational improvement"
    )

    if st.button("🔍 Analyse My Complaint", use_container_width=True):
        if complaint_text.strip() == "":
            st.warning("Please enter your complaint first!")
        else:
            with st.spinner("AI is analysing your complaint..."):
                result = analyze_complaint(
                    complaint=complaint_text,
                    role=role,
                    department=department
                )
                severity = calculate_severity(
                    role=role,
                    rating=rating,
                    complaint_text=complaint_text,
                    department=department
                )

            st.session_state["analysis"] = result
            st.session_state["severity"] = severity
            st.session_state["complaint_text"] = complaint_text
            st.session_state["department"] = department
            st.session_state["rating"] = rating
            st.session_state["name"] = name
            st.session_state["role"] = role
            st.session_state["is_public"] = is_public
            st.session_state["complaint_type"] = "staff"

    # Show results
    if "analysis" in st.session_state and st.session_state.get("complaint_type") == "staff":
        result = st.session_state["analysis"]
        severity = st.session_state["severity"]

        st.markdown("---")
        st.markdown("### 🔎 Analysis Results")

        if severity == "Critical":
            st.error(f"🔴 Severity: **{severity}**")
        elif severity == "High":
            st.warning(f"🟠 Severity: **{severity}**")
        elif severity == "Medium":
            st.info(f"🟡 Severity: **{severity}**")
        else:
            st.success(f"🟢 Severity: **{severity}**")

        st.markdown(f"**Detected Theme:** {result['theme']}")
        st.markdown("---")

        st.markdown("### 💡 Suggested Solutions")

        selected = st.radio(
            "Choose a solution:",
            result["solutions"] + ["Other (I'll describe my own)"]
        )

        custom_solution = ""
        if selected == "Other (I'll describe my own)":
            custom_solution = st.text_area("Describe your solution:")

        if st.button("✅ Submit Complaint", use_container_width=True):
            final_solution = custom_solution if selected == "Other (I'll describe my own)" else selected

            session = SessionLocal()
            complaint = StaffComplaint(
                name=st.session_state["name"],
                role=st.session_state["role"],
                department=st.session_state["department"],
                rating=st.session_state["rating"],
                complaint_text=st.session_state["complaint_text"],
                theme=result["theme"],
                suggestions=json.dumps(result["solutions"]),
                selected_solution=final_solution,
                severity=severity,
                is_public=st.session_state["is_public"]
            )
            session.add(complaint)

            if st.session_state["is_public"]:
                existing = session.query(PublicIssue).filter_by(theme=result["theme"]).first()
                if existing:
                    existing.frequency += 1
                else:
                    session.add(PublicIssue(
                        theme=result["theme"],
                        frequency=1,
                        highest_severity=severity
                    ))

            session.commit()
            session.close()

            st.success("✅ Your complaint has been submitted successfully!")
            st.balloons()

            for key in ["analysis", "severity", "complaint_text",
                        "department", "rating", "name", "role",
                        "is_public", "complaint_type"]:
                st.session_state.pop(key, None)