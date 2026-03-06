from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# This creates the database file called candor.db
engine = create_engine("sqlite:///candor.db", echo=False)

Base = declarative_base()

# This is the table for patient complaints
class PatientComplaint(Base):
    __tablename__ = "patient_complaints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String)
    department = Column(String)
    rating = Column(Integer)
    wait_time = Column(Integer)
    complaint_text = Column(Text)
    theme = Column(String)
    suggestions = Column(Text)       # stored as JSON string
    selected_solution = Column(Text)
    severity = Column(String)        # Critical / High / Medium / Low
    is_public = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# This is the table for staff complaints
class StaffComplaint(Base):
    __tablename__ = "staff_complaints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    role = Column(String)
    department = Column(String)
    rating = Column(Integer)
    complaint_text = Column(Text)
    theme = Column(String)
    suggestions = Column(Text)
    selected_solution = Column(Text)
    severity = Column(String)
    is_public = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# This table tracks recurring public issues
class PublicIssue(Base):
    __tablename__ = "public_issues"

    id = Column(Integer, primary_key=True, autoincrement=True)
    theme = Column(String, unique=True)
    frequency = Column(Integer, default=1)
    highest_severity = Column(String)

# This creates all the tables in the database
def init_db():
    Base.metadata.create_all(engine)
    print("Database tables created!")

# This gives us a session to talk to the database
SessionLocal = sessionmaker(bind=engine)

if __name__ == "__main__":
    init_db()