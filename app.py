from flask import Flask, render_template, request, session, redirect, url_for
from flask import send_file
import random
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os


app = Flask(__name__)
app.secret_key = "interview_secret_key"

# ---------------- QUESTIONS ----------------
hr_questions = [
    "Tell me about yourself",
    "What are your strengths?",
    "What are your weaknesses?",
    "Why should we hire you?",
    "Where do you see yourself in 5 years?"
]

tech_questions = [
    "What is Python?",
    "Explain OOP concepts",
    "What is Flask?",
    "What is REST API?",
    "What is SQL?"
]

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')

# ---------------- START ----------------
@app.route("/start/<mode>")
def start(mode):
    session["mode"] = mode
    session["used_questions"] = []
    session["score"] = 0
    session["max_score"] = 0   # ✅ ADD THIS
    return redirect("/question")

# ---------------- SIMPLE AI FEEDBACK ----------------
def get_ai_feedback(answer):
    answer = answer.lower()
    words = len(answer.split())

    if words > 40:
        return "🔥 Excellent answer! Well detailed and structured."
    elif words > 20:
        return "👍 Good answer, but you can add more examples."
    else:
        return "📈 Try adding more detail and clarity."

# ---------------- QUESTIONS ----------------
import random
from flask import session, redirect, render_template

@app.route("/question", methods=["GET", "POST"])
def question():

    questions = {
        "hr": [
            "Tell me about yourself",
            "What are your strengths?",
            "What are your weaknesses?",
            "Why should we hire you?",
            "Where do you see yourself in 5 years?"
        ],
        "tech": [
            "What is Python?",
            "Explain OOP concepts",
            "What is SQL?",
            "Difference between list and tuple",
            "What is REST API?"
        ]
    }

    mode = session.get("mode")

    if "used_questions" not in session:
        session["used_questions"] = []

    used = session["used_questions"]

    # ---------------- POST (ANSWER SUBMIT) ----------------
    if request.method == "POST":

        user_answer = request.form.get("answer", "").lower()
        current_question = used[-1]

        correct_answers = {
            "What is Python?": "programming language",
            "Explain OOP concepts": "object",
            "What is SQL?": "database",
            "Difference between list and tuple": "mutable",
            "What is REST API?": "api"
        }

        session["max_score"] = session.get("max_score", 0) + 1

        expected = correct_answers.get(current_question, "")

        if not user_answer.strip():
            feedback = "❌ Please write an answer before submitting."
        
        
        
        
        expected = correct_answers.get(current_question, "").lower()

        if expected in user_answer.lower():
            session["score"] = session.get("score", 0) + 1
            feedback = "🔥 Correct answer!"
        else:
            feedback = "❌ Wrong answer. Try again."

        progress = len(used)
        total = len(questions[mode])
        progress_percent = (progress / total) * 100

        return render_template(
            "questions.html",
            question=current_question,
            feedback=feedback,
            progress=progress,
            total=total,
            progress_percent=progress_percent,
            user_answer=user_answer 
        )

    # ---------------- GET (NEW QUESTION) ----------------
    remaining = [q for q in questions[mode] if q not in used]

    if not remaining:
        return redirect("/result")

    q = random.choice(remaining)
    used.append(q)
    session["used_questions"] = used

    progress = len(used)
    total = len(questions[mode])
    progress_percent = (progress / total) * 100

    return render_template(
        "questions.html",
        question=q,
        progress=progress,
        total=total,
        progress_percent=progress_percent
    )
    
    # ---------------- NEXT ----------------
@app.route("/next")
def next_question():
    return redirect("/question")

# ---------------- RESULT ----------------
@app.route("/result")
def result():

    mode = session.get("mode")
    score = session.get("score", 0)
    max_score = session.get("max_score", 1)  # avoid divide by 0

    percent = int((score / max_score) * 100) if max_score > 0 else 0

    if percent >= 80:
        performance = "🔥 Excellent"
    elif percent >= 50:
        performance = "👍 Good"
    else:
        performance = "📈 Needs Improvement"

    return render_template(
        "result.html",
        mode=mode,
        score=score,
        max_score=max_score,
        percent=percent,
        performance=performance
    )
    
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# ---------------- DOWNLOAD ----------------

@app.route("/download")
def download_report():

    mode = session.get("mode")
    score = session.get("score", 0)
    max_score = session.get("max_score", 0)

    percent = int((score / max_score) * 100) if max_score > 0 else 0

    if percent >= 80:
        performance = "Excellent"
        color = colors.green
    elif percent >= 50:
        performance = "Good"
        color = colors.blue
    else:
        performance = "Needs Improvement"
        color = colors.red

    file_path = "report.pdf"
    doc = SimpleDocTemplate(file_path)

    styles = getSampleStyleSheet()

    # ===== STYLES =====
    title_style = ParagraphStyle(
        "title",
        fontSize=24,
        leading=28,
        alignment=1,
        textColor=colors.HexColor("#1f4e79")
    )

    header_style = ParagraphStyle(
        "header",
        fontSize=12,
        leading=16,
        spaceAfter=10
    )

    section_title = ParagraphStyle(
        "section",
        fontSize=14,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.HexColor("#333333")
    )

    normal = ParagraphStyle(
        "normal",
        fontSize=11,
        spaceAfter=4
    )

    highlight = ParagraphStyle(
        "highlight",
        fontSize=13,
        textColor=color,
        spaceAfter=10
    )

    content = []

    # ===== LOGO =====
    logo_path = os.path.join("static", "logo.png")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.2*inch, height=1.2*inch)
        logo.hAlign = "CENTER"
        content.append(logo)

    # ===== TITLE =====
    content.append(Spacer(1, 10))
    content.append(Paragraph("INTERVIEW ANALYTICS REPORT", title_style))

    content.append(Spacer(1, 10))

    # ===== HEADER INFO =====
    content.append(Paragraph(f"<b>Mode:</b> {mode.upper()}", header_style))
    content.append(Paragraph(f"<b>Score:</b> {score} / {max_score}", header_style))
    content.append(Paragraph(f"<b>Performance:</b> {performance}", highlight))

    content.append(Spacer(1, 12))
    content.append(Paragraph("--------------------------------------------------", normal))

    # ===== STRENGTHS =====
    content.append(Paragraph("STRENGTHS", section_title))
    content.append(Paragraph("✔ Clear communication", normal))
    content.append(Paragraph("✔ Structured thinking", normal))

    content.append(Spacer(1, 8))
    content.append(Paragraph("--------------------------------------------------", normal))

    # ===== IMPROVEMENTS =====
    content.append(Paragraph("AREAS TO IMPROVE", section_title))
    content.append(Paragraph("✘ Add real-world examples", normal))
    content.append(Paragraph("✘ Improve depth of explanation", normal))

    content.append(Spacer(1, 15))

    # ===== FOOTER STYLE LINE =====
    content.append(Paragraph("Generated by AI Interview Coach System", normal))

    doc.build(content)

    return send_file(file_path, as_attachment=True)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)