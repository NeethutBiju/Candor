import streamlit as st
import pandas as pd
from db.models import SessionLocal, PatientComplaint, StaffComplaint, PublicIssue

st.set_page_config(
    page_title="CANDOR - Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 CANDOR Admin Dashboard")
st.markdown("Real-time complaint intelligence and analytics")
st.markdown("---")

# Load data from database
session = SessionLocal()

patient_complaints = session.query(PatientComplaint).all()
staff_complaints = session.query(StaffComplaint).all()
public_issues = session.query(PublicIssue).all()

session.close()

# Convert to dataframes
patient_df = pd.DataFrame([{
    "department": c.department,
    "rating": c.rating,
    "severity": c.severity,
    "theme": c.theme,
    "complaint": c.complaint_text,
    "wait_time": c.wait_time,
    "timestamp": c.timestamp
} for c in patient_complaints])

staff_df = pd.DataFrame([{
    "name": c.name,
    "role": c.role,
    "department": c.department,
    "rating": c.rating,
    "severity": c.severity,
    "theme": c.theme,
    "complaint": c.complaint_text,
    "timestamp": c.timestamp
} for c in staff_complaints])

# ---- TOP METRICS ----
st.markdown("### 📈 Overview")

col1, col2, col3, col4 = st.columns(4)

total = len(patient_df) + len(staff_df)
critical = len(patient_df[patient_df["severity"] == "Critical"]) + \
           len(staff_df[staff_df["severity"] == "Critical"])
high = len(patient_df[patient_df["severity"] == "High"]) + \
       len(staff_df[staff_df["severity"] == "High"])
public = len(public_issues)

col1.metric("📋 Total Complaints", total)
col2.metric("🔴 Critical", critical)
col3.metric("🟠 High Priority", high)
col4.metric("🔁 Recurring Issues", public)

st.markdown("---")

# ---- SEVERITY BREAKDOWN ----
st.markdown("### 🎯 Severity Breakdown")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Patient Complaints**")
    if not patient_df.empty:
        patient_severity = patient_df["severity"].value_counts()
        st.bar_chart(patient_severity)

with col2:
    st.markdown("**Staff Complaints**")
    if not staff_df.empty:
        staff_severity = staff_df["severity"].value_counts()
        st.bar_chart(staff_severity)

st.markdown("---")

# ---- COMPLAINTS BY DEPARTMENT ----
st.markdown("### 🏥 Complaints by Department")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Patient Departments**")
    if not patient_df.empty:
        patient_dept = patient_df["department"].value_counts()
        st.bar_chart(patient_dept)

with col2:
    st.markdown("**Staff Departments**")
    if not staff_df.empty:
        staff_dept = staff_df["department"].value_counts()
        st.bar_chart(staff_dept)

st.markdown("---")

# ---- CRITICAL COMPLAINTS ----
st.markdown("### 🚨 Critical Complaints Requiring Immediate Attention")

critical_patients = patient_df[patient_df["severity"] == "Critical"] if not patient_df.empty else pd.DataFrame()
critical_staff = staff_df[staff_df["severity"] == "Critical"] if not staff_df.empty else pd.DataFrame()

if not critical_patients.empty:
    st.markdown("**Critical Patient Complaints**")
    st.dataframe(
        critical_patients[["department", "rating", "complaint", "wait_time"]].head(10),
        use_container_width=True
    )

if not critical_staff.empty:
    st.markdown("**Critical Staff Complaints**")
    st.dataframe(
        critical_staff[["name", "role", "department", "rating", "complaint"]].head(10),
        use_container_width=True
    )

st.markdown("---")

# ---- RECURRING PUBLIC ISSUES ----
st.markdown("### 🔁 Recurring Public Issues")

if public_issues:
    issues_df = pd.DataFrame([{
        "Theme": i.theme,
        "Frequency": i.frequency,
        "Highest Severity": i.highest_severity
    } for i in public_issues])

    issues_df = issues_df.sort_values("Frequency", ascending=False)
    st.dataframe(issues_df, use_container_width=True)
else:
    st.info("No public issues recorded yet.")

st.markdown("---")

# ---- STAFF ROLE BREAKDOWN ----
st.markdown("### 👨‍⚕️ Complaints by Staff Role")

if not staff_df.empty:
    role_counts = staff_df["role"].value_counts()
    st.bar_chart(role_counts)

st.markdown("---")

# ---- RECENT COMPLAINTS ----
st.markdown("### 🕐 Recent Complaints")

tab1, tab2 = st.tabs(["Patient", "Staff"])

with tab1:
    if not patient_df.empty:
        st.dataframe(
            patient_df[["department", "rating", "severity", "complaint"]]\
                .tail(20).iloc[::-1],
            use_container_width=True
        )

with tab2:
    if not staff_df.empty:
        st.dataframe(
            staff_df[["name", "role", "department", "rating", "severity", "complaint"]]\
                .tail(20).iloc[::-1],
            use_container_width=True
        )