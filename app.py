from flask import Flask, request, render_template, redirect, flash, make_response, session
from surveys import surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret_key"
CURRENT_SURVEY_KEY = 'current_survey'
RESPONSES_KEY = 'responses'

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/", methods=["POST"])
def survey_start():
    survey_id = request.form['surveyselection']
    session[CURRENT_SURVEY_KEY] = survey_id
    survey = surveys[survey_id]
    if request.cookies.get(f"completed_{survey_id}"):
        return render_template("survey_completed.html")
    return render_template("survey_start.html", survey=survey)

@app.route("/begin", methods=["POST","GET"])
def begin():
    session[RESPONSES_KEY] = []
    return redirect("/question/0")

@app.route("/question/<int:question_num>", methods=['POST','GET'])
def question(question_num):


    responses = session.get(RESPONSES_KEY)
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]
    
    if(len(responses) is None):
        return redirect("/")
    
    if (len(responses) == len(survey.questions)):
        return redirect("/complete")

    if (len(responses) != question_num):
        flash(f"Invalid question id: {question_num}.")
        return redirect(f"/question/{len(responses)}")

    
    question = survey.questions[question_num]
    return render_template("question.html", question=question, question_num=question_num, survey=survey)

@app.route("/answer", methods=['POST'])
def answer():
    answer = request.form["answer"]
    responses = session.get(RESPONSES_KEY)
    responses.append(answer)
    session[RESPONSES_KEY] = responses

    if (len(responses) == len(surveys[session.get(CURRENT_SURVEY_KEY)].questions)):
       
        return redirect("/complete")

    else:
        return redirect(f"/question/{len(responses)}")
    
@app.route("/complete")
def finished():
    survey = surveys[session[CURRENT_SURVEY_KEY]]
    responses = session.get(RESPONSES_KEY)
    html = render_template("complete.html", survey=survey, responses = responses)
    response = make_response(html)
    survey_id = session.get(CURRENT_SURVEY_KEY)
    response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
    return response
    
    