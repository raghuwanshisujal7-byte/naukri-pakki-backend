from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Backend is live"})


@app.route("/analyze", methods=["POST"])
def analyze_resume():
    # 1️⃣ file check
    if "file" not in request.files:
        return jsonify({"success": False, "error": "NO_FILE"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"success": False, "error": "EMPTY_FILENAME"}), 400

    # 2️⃣ PDF text extract
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        return jsonify({"success": False, "error": "PDF_READ_ERROR"}), 400

    if not text.strip():
        return jsonify({
            "success": True,
            "score": 0,
            "words": 0,
            "skills": [],
            "status": "Empty Resume"
        })

    text = text.lower()

    # 3️⃣ word count
    words = text.split()
    word_count = len(words)

    # 4️⃣ skills database
    skills_db = [
        "python", "java", "javascript", "react", "node",
        "sql", "mysql", "mongodb", "flask", "django",
        "html", "css", "bootstrap", "machine learning",
        "data analysis", "ai", "git", "github", "aws"
    ]

    skills_found = []
    for skill in skills_db:
        if skill in text:
            skills_found.append(skill)

    # 5️⃣ scoring logic (REAL, not demo)
    score = 0

    # skills score
    score += len(skills_found) * 8

    # length score
    if word_count > 300:
        score += 20
    elif word_count > 150:
        score += 10

    # cap at 100
    score = min(score, 100)

    # status
    if score < 40:
        status = "Needs Improvement"
    elif score < 70:
        status = "Good"
    else:
        status = "Excellent"

    # 6️⃣ FINAL RESPONSE (IMPORTANT)
    return jsonify({
        "success": True,
        "score": score,
        "words": word_count,
        "skills": skills_found,
        "status": status
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
