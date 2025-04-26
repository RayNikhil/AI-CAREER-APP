from flask import Flask, render_template, request, redirect, url_for, session
import random
import openai

app = Flask(__name__)
openai.api_key = "YOUR_API_KEY"  # replace with your real key
app.secret_key = 'your_secret_key'  # Needed for session management

# Temporary database
users_db = {}

# Career Paths
career_paths = {
    "coding": ["Software Engineer", "Data Scientist", "AI Engineer"],
    "design": ["UI/UX Designer", "Graphic Designer"],
    "talking": ["Public Speaker", "Sales Manager"],
    "teaching": ["Teacher", "Online Tutor"]
}

# Roadmaps
career_roadmaps = {
    "Software Engineer": [
        "Learn Python or Java",
        "Understand Data Structures and Algorithms",
        "Build small projects",
        "Learn Git and GitHub",
        "Apply for internships"
    ],
    "Data Scientist": [
        "Learn Python",
        "Learn Statistics and Math",
        "Learn Machine Learning",
        "Work on real datasets",
        "Build a strong portfolio"
    ],
    "UI/UX Designer": [
        "Learn basics of design (colors, fonts)",
        "Learn Figma or Adobe XD",
        "Create sample designs",
        "Build a portfolio website",
        "Apply for internships"
    ],
    "Teacher": [
        "Master a subject",
        "Improve communication skills",
        "Make online teaching videos",
        "Join online teaching platforms",
        "Build experience and network"
    ]
}

# Skills Tracker
skills = ["Learn Python", "Make a project", "Learn Git", "Apply for Internship"]
completed_skills = []

# ----------------- Routes -----------------

@app.route('/')
def home():
    if 'user' in session:
        return render_template('home.html', user=session['user'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users_db and users_db[email] == password:
            session['user'] = email
            return redirect(url_for('home'))
        else:
            return "Invalid credentials! Try again."
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users_db[email] = password
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/quiz')
def quiz():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('quiz.html')

@app.route('/get_career', methods=['POST'])
def get_career():
    scores = {"coding": 0, "design": 0, "talking": 0, "teaching": 0}
    for i in range(1, 11):
        ans = request.form.get(f'q{i}')
        if ans in scores:
            scores[ans] += 1

    best_fit = max(scores, key=scores.get)
    careers = career_paths.get(best_fit, ["Career not found"])
    chosen_career = random.choice(careers)
    roadmap = career_roadmaps.get(chosen_career, ["No roadmap available"])
    return render_template('career.html', career=chosen_career, roadmap=roadmap)


@app.route('/get_response', methods=['POST'])
def get_response():
    user_question = request.form['question']
    if "data scientist" in user_question.lower():
        answer = "To become a Data Scientist: Learn Python → Statistics → Machine Learning → Build Projects."
    elif "software engineer" in user_question.lower():
        answer = "To become a Software Engineer: Learn a language → Practice DSA → Build Projects → Apply for jobs."
    else:
        answer = "Keep learning and building projects! You'll do great."
    return render_template('chat.html', answer=answer)

@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        skill = request.form['skill']
        completed_skills.append(skill)
    return render_template('tracker.html', skills=skills, completed_skills=completed_skills)

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    # For now, we show a sample career and roadmap
    career = "Software Engineer"
    roadmap = career_roadmaps.get(career, [])
    return render_template('profile.html', user=session['user'], career=career, roadmap=roadmap)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    reply = ""
    if request.method == 'POST':
        question = request.form['question']
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a career expert helping students choose their path."},
                {"role": "user", "content": question}
            ]
        )
        reply = response['choices'][0]['message']['content']
    return render_template('chat.html', reply=reply)

@app.route('/skill-tracker', methods=['GET', 'POST'])
def skill_tracker():
    message = ""
    if request.method == 'POST':
        selected_skills = request.form.getlist('skills')
        message = "Skills saved: " + ", ".join(selected_skills)
    return render_template('skill_tracker.html', message=message)


if __name__ == '__main__':
    app.run(debug=True)
