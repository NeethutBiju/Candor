import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from db.models import SessionLocal, PatientComplaint, StaffComplaint, PublicIssue, init_db
from utils.severity import calculate_severity

def seed_patient_data():
    print("Loading patient data...")
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "healthcare_analytics_patient_flow_data_rated_1_.csv"))
    session = SessionLocal()
    count = 0

    for _, row in df.iterrows():
        # Skip rows with missing feedback or rating
        if pd.isna(row["Feedback"]) or pd.isna(row["Ratings"]):
            continue

        severity = calculate_severity(
            role="Patient",
            rating=row["Ratings"],
            complaint_text=str(row["Feedback"]),
            department=str(row["Department Referral"])
        )

        complaint = PatientComplaint(
            patient_id=str(row["Patient Id"]),
            department=str(row["Department Referral"]),
            rating=int(row["Ratings"]),
            wait_time=int(row["Patient Waittime"]) if not pd.isna(row["Patient Waittime"]) else 0,
            complaint_text=str(row["Feedback"]),
            severity=severity,
            is_public=True
        )
        session.add(complaint)
        count += 1

    session.commit()
    session.close()
    print(f"✅ Added {count} patient complaints!")

def seed_staff_data():
    print("Loading staff data...")
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "staff_review_5000.csv"))

    session = SessionLocal()
    count = 0

    for _, row in df.iterrows():
        if pd.isna(row["feedback"]) or pd.isna(row["rating"]):
            continue

        severity = calculate_severity(
            role=str(row["role"]),
            rating=row["rating"],
            complaint_text=str(row["feedback"]),
            department=str(row["department"])
        )

        complaint = StaffComplaint(
            name=str(row["name"]),
            role=str(row["role"]),
            department=str(row["department"]),
            rating=int(row["rating"]),
            complaint_text=str(row["feedback"]),
            severity=severity,
            is_public=True
        )
        session.add(complaint)
        count += 1

    session.commit()
    session.close()
    print(f"✅ Added {count} staff complaints!")

if __name__ == "__main__":
    init_db()
    seed_patient_data()
    seed_staff_data()
    print("🎉 All data loaded successfully!")