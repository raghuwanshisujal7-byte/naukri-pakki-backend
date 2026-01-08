from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
import re

app = Flask(__name__)
CORS(app)

# -------------------------
# CONFIG
# -------------------------
SKILLS = [
    "python", "java", "c++", "javascript", "react", "node",
    "machine learning", "deep learning", "data science",
    "sql", "mysql", "postgresql", "mongodb",
    "aws", "docker", "kubernetes", "git", "linux",
    "flask", "django", "fastapi"
]

EXPERIENCE_WORDS = [
    "experience", "internship", "project", "worked", "developed",
    "designed", "implemented", "deployed"
]

EDUCATION_WORDS = [
    "btech", "b.e", "bachelor", "master", "msc", "mtech",
    "engineering", "computer science"
]


# -------------------------
# HELPERS
# -------------------------
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def calculate_score(text: str):
    words = text.split()
    word_count = len(words)

    # Skill matching
    matched_skills = []
    for skill in SKILLS:
        if skill in text:
            matched_skills.append(skill)

    skill_score = min(len(matched_skills) * 4, 40)  # max 40

    # Experience score
    exp_hits = sum(1 for w in EXPERIENCE_WORDS if w in text)
    experience_score = min(exp_hits * 5, 25)  # max 25

    # Education score
    edu_hits = sum(1 for w in EDUCATION_WORDS if w in text)
    education_score = min(edu_hits * 5, 15)  # max 15

    # Length score
    if word_count < 200:
        length_score = 5
    elif word_count < 400:
        length_score = 10
    else:
        length_score = 20  # max 20

    total_score = (
        skill_score +
        experience_score +
        education_score +
        length_score
    )

    total_score = min(total_score, 100)

    return {
        "score": total_score,
        "matched_skills": matched_skills,
        "word_count": word_count,
        "skill_score": skill_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "length_score": length_score
    }


# -------------------------
# ROUTES
# -------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "API is running"})


@app.route("/analyze", methods=["POST"])
def analyze_resume():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "NO_FILE"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"success": False, "error": "EMPTY_FILENAME"}), 400

    # -------- PDF READ --------
    try:
        reader = PdfReader(file)
        raw_text = ""
        for page in reader.pages:
            if page.extract_text():
                raw_text += page.extract_text()
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "PDF_READ_ERROR",
            "details": str(e)
        }), 400

    if not raw_text.strip():
        return jsonify({
            "success": False,
            "error": "NO_TEXT_EXTRACTED"
        }), 400

    clean = clean_text(raw_text)

    result = calculate_score(clean)

    return jsonify({
        "success": True,
        "final_score": result["score"],
        "matched_skills": result["matched_skills"],
        "word_count": result["word_count"],
        "breakdown": {
            "skills": result["skill_score"],
            "experience": result["experience_score"],
            "education": result["education_score"],
            "length": result["length_score"]
        }
    })


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
