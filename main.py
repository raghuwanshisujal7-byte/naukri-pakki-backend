from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import re

app = Flask(__name__)
CORS(app)

# -----------------------------
# CONFIG
# -----------------------------
SKILLS_DB = [
    "python", "java", "javascript", "react", "node", "flask",
    "django", "machine learning", "deep learning", "ai",
    "sql", "mysql", "postgresql", "mongodb",
    "aws", "docker", "kubernetes",
    "html", "css", "git"
]

# -----------------------------
# HELPERS
# -----------------------------
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.lower()

def extract_skills(text):
    found = []
    for skill in SKILLS_DB:
        if skill in text:
            found.append(skill)
    return list(set(found))

def estimate_experience(text):
    years = re.findall(r"(\d+)\+?\s*years", text)
    if not years:
        return 0
    return max(int(y) for y in years)

def calculate_score(word_count, skills_count, experience):
    score = 0

    # Resume length (30)
    if word_count > 800:
        score += 30
    elif word_count > 500:
        score += 22
    elif word_count > 300:
        score += 15
    else:
        score += 8

    # Skills (40)
    score += min(skills_count * 4, 40)

    # Experience (30)
    if experience >= 5:
        score += 30
    elif experience >= 3:
        score += 22
    elif experience >= 1:
        score += 15
    else:
        score += 5

    return min(score, 100)

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "backend running"})

@app.route("/analyze", methods=["POST"])
def analyze_resume():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "NO_FILE"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"success": False, "error": "EMPTY_FILENAME"}), 400

    try:
        text = extract_text_from_pdf(file)
        word_count = len(text.split())
        skills = extract_skills(text)
        experience = estimate_experience(text)
        score = calculate_score(word_count, len(skills), experience)

        return jsonify({
            "success": True,
            "score": score,
            "skills": skills,
            "experience_years": experience,
            "word_count": word_count
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "PROCESSING_FAILED",
            "details": str(e)
        }), 500

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
