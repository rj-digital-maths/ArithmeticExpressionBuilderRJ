import streamlit as st
import random
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# =========================================================
# 🏛️ MATHEMATICAL ENGINE & SESSION STATE
# =========================================================
if 'quiz_generated' not in st.session_state:
    st.session_state.quiz_generated = False
    st.session_state.quiz_data = []
    st.session_state.submitted = False
    st.session_state.is_premium = False
    st.session_state.total_qs = 3  # Default fallback count

def generate_quiz(count, level):
    quiz = []
    r_min, r_max = (1, 10) if level == "Easy" else (1, 50) if level == "Hard" else (1, 20)
    for _ in range(count):
        numbers = random.sample(range(r_min, r_max + 1), 3)
        shuffled_display = random.sample(numbers, len(numbers))
        
        pattern = random.randint(0, 5)
        if pattern == 0: target = numbers[0] + numbers[1] - numbers[2]
        elif pattern == 1: target = numbers[0] - numbers[1] + numbers[2]
        elif pattern == 2: target = numbers[0] - (numbers[1] - numbers[2])
        elif pattern == 3: target = (numbers[0] + numbers[1]) - numbers[2]
        elif pattern == 4: target = numbers[0] - (numbers[1] + numbers[2])
        else: target = (numbers[0] - numbers[1]) - numbers[2]
        
        quiz.append({
            "numbers": numbers, 
            "shuffled_display": shuffled_display, 
            "target": target, 
            "pattern": pattern
        })
    return quiz

# =========================================================
# 📄 PDF GENERATOR
# =========================================================
def generate_pdf(name, student_class, difficulty, score, total, quiz_data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=22, textColor=colors.HexColor("#0F4C81"), spaceAfter=15)
    meta_style = ParagraphStyle('Meta', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#444444"), spaceAfter=6)
    q_title = ParagraphStyle('QTitle', fontName='Helvetica-Bold', fontSize=11, spaceBefore=12, spaceAfter=4)
    text_style = ParagraphStyle('Text', fontName='Helvetica', fontSize=10, spaceAfter=4)
    
    story.append(Paragraph("Expression Builder | Performance Report", title_style))
    story.append(Paragraph(f"<b>Student:</b> {name} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Class:</b> {student_class}", meta_style))
    story.append(Paragraph(f"<b>Difficulty:</b> {difficulty} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Final Score:</b> {score} / {total}", meta_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CCCCCC"), spaceAfter=15))
    
    for i, q in enumerate(quiz_data):
        ans = st.session_state.get(f"input_{i}", "").strip()
        is_correct = False
        try:
            clean_expr = ans.replace('−', '-')
            parsed = [int(n) for n in re.findall(r'\d+', clean_expr)]
            if sorted(parsed) == sorted(q['numbers']) and not re.search(r'[^0-9+\-()\s]', clean_expr):
                if eval(clean_expr, {"__builtins__": None}, {}) == q['target']: is_correct = True
        except: pass
        result_str = "correct answer" if is_correct else "wrong answer"
        formulas = [
            f"{q['numbers'][0]} + {q['numbers'][1]} - {q['numbers'][2]}", f"{q['numbers'][0]} - {q['numbers'][1]} + {q['numbers'][2]}",
            f"{q['numbers'][0]} - ({q['numbers'][1]} - {q['numbers'][2]})", f"({q['numbers'][0]} + {q['numbers'][1]}) - {q['numbers'][2]}",
            f"{q['numbers'][0]} - ({q['numbers'][1]} + {q['numbers'][2]})", f"({q['numbers'][0]} - {q['numbers'][1]}) - {q['numbers'][2]}"
        ]
        story.append(Paragraph(f"<b>Question {i+1}:</b> Given Numbers: {q['numbers']} | Target: {q['target']}", q_title))
        story.append(Paragraph(f"<b>Student Answer:</b> {ans if ans else 'No Answer'}", text_style))
        story.append(Paragraph(f"<b>Correct Answer:</b> {formulas[q['pattern']]} = {q['target']}", text_style))
        story.append(Paragraph(f"<b>Result:</b> ({result_str})", text_style))
        story.append(Spacer(1, 5))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#EAEAEA"), spaceAfter=10))
    doc.build(story)
    buffer.seek(0)
    return buffer

# =========================================================
# 🎨 USER INTERFACE DESIGN
# =========================================================
st.set_page_config(page_title="Arithmetic Expression Builder", page_icon="🧮", layout="centered")

with st.sidebar:
    st.header("📖 User Guide")
    st.markdown("""
    Welcome to **Interactive Arithmetic Expression Builder** © RJ Interactive Maths! 
    
    ### 🎯 Objective
    Use the **three provided numbers** along with arithmetic operators (`+`, `-`) or parentheses `()` to construct an expression that equals the **Target Number**.
    
    ### 🛠️ Step-by-Step:
    1️⃣ Enter the **Student Name** and **Class**.
    2️⃣ Select your **Difficulty Level**.
    3️⃣ If you have a **Premium License Key**, type it in to unlock features.
    4️⃣ Click **Start Quiz**!
    """)

st.title("Arithmetic Expression Builder")
st.caption("© RJ Interactive Maths")

# --- CONFIGURATION / START SCREEN ---
if not st.session_state.quiz_generated:
    st.subheader("Arithmetic Sandbox")
    s_name = st.text_input("Student Name", placeholder="Enter student's name")
    s_class = st.text_input("Class", placeholder="Example: VII")
    diff = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"], index=1)
    
    license_key = st.text_input("License Key (Leave blank for Free Trial Mode)", type="password")
    
    valid_keys = st.secrets.get("premium_keys", ["RJ-MASTER-KEY"])
    is_key_valid = license_key.strip() in valid_keys

    if is_key_valid and not st.session_state.is_premium:
        st.session_state.is_premium = True
        st.rerun()
    elif not is_key_valid and st.session_state.is_premium:
        st.session_state.is_premium = False
        st.rerun()

    if st.session_state.is_premium:
        st.success("🔓 Premium Key Verified!")
        q_count = st.select_slider("Number of Questions", options=[5, 10, 15, 20, 25], value=10)
        st.session_state.total_qs = q_count
    else:
        st.info("📝 Free Trial Mode (Fixed to 3 Questions).")
        st.session_state.total_qs = 3

    if st.button("▶ Start Quiz", type="primary"):
        if not s_name or not s_class:
            st.error("Please fill in both Student Name and Class details.")
        else:
            st.session_state.student_name = s_name
            st.session_state.student_class = s_class
            st.session_state.difficulty = diff
            st.session_state.quiz_data = generate_quiz(st.session_state.total_qs, diff)
            st.session_state.quiz_generated = True
            st.session_state.submitted = False
            st.rerun()

# --- ACTIVE QUIZ SCREEN ---
elif st.session_state.quiz_generated and not st.session_state.submitted:
    mode_text = "✨ PREMIUM EDITION" if st.session_state.is_premium else "⏳ FREE TRIAL VERSION"
    st.info(f"**Mode:** {mode_text}  |  👤 **Student:** {st.session_state.student_name}  |  🏫 **Class:** {st.session_state.student_class}  |  📋 **Total:** {st.session_state.total_qs} Qs")
    
    with st.form("quiz_form"):
        for i, q in enumerate(st.session_state.quiz_data):
            st.markdown(f"### Question {i+1}")
            col1, col2 = st.columns([1, 3])
            with col1: 
                st.metric(label="Target", value=q['target'])
            with col2:
                cols = st.columns(3)
                for idx, num in enumerate(q['shuffled_display']):
                    cols[idx].markdown(f"<div style='background:#EDF5FF; border:2px solid #C6DAF8; border-radius:10px; padding:15px; text-align:center; font-size:22px; font-weight:bold; color:#0F4C81;'>{num}</div>", unsafe_allow_html=True)
            
            st.text_input("Your Expression String", key=f"input_{i}", placeholder="e.g. 4 + 2 - 1", label_visibility="collapsed")
            st.write("---")
            
        if st.form_submit_button("✔ Submit Quiz", type="primary"):
            st.session_state.submitted = True
            st.rerun()

# --- SCOREBOARD & REPORT SCREEN ---
elif st.session_state.submitted:
    correct_answers = 0
    for i, q in enumerate(st.session_state.quiz_data):
        ans = st.session_state.get(f"input_{i}", "").strip().replace('−', '-')
        try:
            parsed = [int(n) for n in re.findall(r'\d+', ans)]
            if sorted(parsed) == sorted(q['numbers']) and not re.search(r'[^0-9+\-()\s]', ans):
                if eval(ans, {"__builtins__": None}, {}) == q['target']: 
                    correct_answers += 1
        except: pass

    # 🎈 Trigger balloons instantly for everyone upon submission!
    st.balloons()

    # --- LOCK VS PREMIUM CONDITIONAL LOGIC ---
    if not st.session_state.is_premium:
        # 🛑 FREE TRIAL LOCK SCREEN
        st.markdown("""
        <div style="background:#FFF0F2; border:2px solid #FFC1CC; border-radius:12px; padding:35px; text-align:center; margin-bottom:25px;">
            <h1 style="color:#D32F2F; margin:0; font-size:36px; font-weight:bold;">⚠️ Trial Expired!</h1>
            <p style="color:#555; font-size:16px; margin-top:15px; font-weight:500;">
                Your free trial quiz is complete. Printable PDF reports and unlimited quiz generation are premium features.
            </p>
            <h3 style="color:#C2185B; margin-top:10px; font-size:20px; font-weight:bold;">Please upgrade your application to continue!</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<p style='text-align:center; color:#666;'><b>Trial Performance:</b> {correct_answers} / {st.session_state.total_qs} Correct</p>", unsafe_allow_html=True)
        
    else:
        # 🔓 PREMIUM WIN SCREEN
        st.success("## 🎉 Quiz Completed!")
        percent = (correct_answers / st.session_state.total_qs) * 100
        stars = "⭐⭐⭐⭐⭐" if percent >= 90 else "⭐⭐⭐⭐" if percent >= 75 else "⭐⭐⭐" if percent >= 60 else "⭐⭐" if percent >= 40 else "⭐"
        msg = "Outstanding Masterpiece!" if percent >= 90 else "Excellent Math Skills!" if percent >= 75 else "Very Good Effort!" if percent >= 60 else "Good Work!" if percent >= 40 else "Keep Practising!"
        
        st.markdown(f"""
        <div style="background:#F5F9FF; border:2px solid #D8E7FB; border-radius:12px; padding:30px; text-align:center;">
            <h4 style="margin:0; color:#333;">Your Score</h4>
            <h1 style="font-size:55px; color:#0F4C81; margin:10px 0;">{correct_answers} / {st.session_state.total_qs}</h1>
            <div style="font-size:28px; margin-bottom:10px;">{stars}</div>
            <h3 style="color:#2E7D32; margin:0;">{msg}</h3>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        
        col_dl, col_reset = st.columns(2)
        with col_dl:
            pdf_data = generate_pdf(st.session_state.student_name, st.session_state.student_class, st.session_state.difficulty, correct_answers, st.session_state.total_qs, st.session_state.quiz_data)
            st.download_button(label="📄 Save Result as PDF", data=pdf_data, file_name=f"{st.session_state.student_name.replace(' ', '_')}_Performance_Log.pdf", mime="application/pdf", use_container_width=True)
                    
        with col_reset:
            if st.button("🔄 New Quiz", use_container_width=True):
                for i in range(len(st.session_state.quiz_data)):
                    if f"input_{i}" in st.session_state:
                        del st.session_state[f"input_{i}"]
                st.session_state.quiz_generated = False
                st.session_state.submitted = False
                st.session_state.is_premium = False
                st.rerun()
    # --- NEEDFUL CHANGES END HERE ---