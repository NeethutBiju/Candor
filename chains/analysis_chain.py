import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Load the API key from .env file
load_dotenv()

# Connect to Groq (free and fast!)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY")
)

# This prompt tells the AI exactly what to do with a complaint
analysis_prompt = ChatPromptTemplate.from_template("""
You are a healthcare complaint analyst.

Analyze the following complaint and respond in this EXACT format:
THEME: (one short phrase like "equipment issue" or "long wait time")
SOLUTION1: (first solution)
SOLUTION2: (second solution)
SOLUTION3: (third solution)
SOLUTION4: (fourth solution)
SOLUTION5: (fifth solution)

Complaint: {complaint}
Role: {role}
Department: {department}
""")

# This is the chain that connects the prompt to the AI
chain = analysis_prompt | llm

def analyze_complaint(complaint, role, department):
    # Send the complaint to the AI
    response = chain.invoke({
        "complaint": complaint,
        "role": role,
        "department": department
    })

    # Get the text response
    text = response.content

    # Split the response into lines
    lines = text.strip().split("\n")

    theme = ""
    solutions = []

    for line in lines:
        if line.startswith("THEME:"):
            theme = line.replace("THEME:", "").strip()
        elif line.startswith("SOLUTION"):
            solution = line.split(":", 1)[1].strip()
            solutions.append(solution)

    return {
        "theme": theme,
        "solutions": solutions
    }


# Test when you run this file directly
if __name__ == "__main__":
    result = analyze_complaint(
        complaint="The ICU equipment failed and no nurse responded for 30 minutes",
        role="Doctor",
        department="ICU"
    )
    print("Theme:", result["theme"])
    print("Solutions:")
    for i, s in enumerate(result["solutions"], 1):
        print(f"  {i}. {s}")