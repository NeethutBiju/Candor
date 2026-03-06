# Role weights - higher means more impact on severity score
ROLE_WEIGHTS = {
    "Doctor": 1.5,
    "Nurse": 1.3,
    "Admin": 1.2,
    "Pharmacist": 1.2,
    "Lab Technician": 1.1,
    "Ambulance Staff": 1.3,
    "Janitor": 1.0,
    "Patient": 1.0
}

# These words in a complaint automatically increase severity
RISK_KEYWORDS = [
    "oxygen", "ICU", "emergency", "equipment failure",
    "critical", "death", "died", "unconscious", "bleeding",
    "no doctor", "delay", "ignored", "negligence", "infection",
    "wrong medication", "overdose", "staff absent"
]

# These departments are high risk
HIGH_RISK_DEPARTMENTS = ["ICU", "Emergency", "Surgery"]

def calculate_severity(role, rating, complaint_text, department=""):
    score = 0

    # Add points based on role
    role_weight = ROLE_WEIGHTS.get(role, 1.0)
    score += role_weight * 10

    # Add points based on rating (lower rating = more serious)
    score += (5 - int(rating)) * 15

    # Add points for each risk keyword found in the complaint
    complaint_lower = complaint_text.lower()
    for keyword in RISK_KEYWORDS:
        if keyword.lower() in complaint_lower:
            score += 20

    # Add points if it's a high risk department
    if department in HIGH_RISK_DEPARTMENTS:
        score += 15

    # Convert score to severity level
    if score >= 80:
        return "Critical"
    elif score >= 55:
        return "High"
    elif score >= 30:
        return "Medium"
    else:
        return "Low"


# Test the function when you run this file directly
if __name__ == "__main__":
    test = calculate_severity(
        role="Doctor",
        rating=1,
        complaint_text="Patient in ICU had equipment failure, no doctor responded",
        department="ICU"
    )
    print("Test severity:", test)