from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "Naukri Pakki backend running"
    })

# -----------------------------
# RESUME ANALYZE (TEMP DEMO)
# -----------------------------
@app.route("/analyze", methods=["POST"])
def analyze_resume():
    if "file" not in request.files:
        return jsonify({
            "success": False,
            "error": "NO_FILE"
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "error": "EMPTY_FILENAME"
        }), 400

    # demo response (stable)
    return jsonify({
        "success": True,
        "score": 35,
        "skills": ["python", "java", "machine learning", "ai"],
        "words": 351
    })

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
