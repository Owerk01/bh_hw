from flask import Flask, redirect, render_template, request, session, url_for, jsonify
import os
from models import db, db_add_new_data, User, Quiz, Question
from random import shuffle

BASE_DIR = os.path.dirname(__file__)
DB_DIR = os.path.join(BASE_DIR, 'db')

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)
    
DB_PATH = os.path.join(DB_DIR, 'db_quiz.db')    


app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

app.config['SECRET_KEY'] = 'secretkeysecretkeysecretkey1212121'

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'


db.init_app(app)

html_config = {
    'admin':True,
    'debug':False
}

# операции с БД перед запуском сервера
with app.app_context():
    db_add_new_data()
    # users = User.query.all()
    # users = User.query.filter(User.id>1).all()
    # print(users)
    # user = db.session.get(User, 1)    
    # print(user)
    # print(user.quizes)
    
    
@app.route('/', methods = ['GET'])
def index():
    users = User.query.order_by(User.name).all()            
    return render_template('users.html', 
                           admin=True, 
                           len=len, 
                           users=users, 
                           html_config = html_config)
    


@app.route("/user_add/", methods=['GET', 'POST'])
def users_():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        if user_name:
            # user = User(user_name)
            db.session.add(User(user_name))
            db.session.commit()
            
    return redirect(url_for('index'))

@app.route('/user_delete/<int:id>/')
def user_delete(id):
    User.query.filter_by(id = id).delete()
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/quiz/', methods = ['GET', 'POST'])
def view_quiz():
    if request.method == 'GET':
        session['quiz_id'] = -1
        quizes = Quiz.query.all()
        # print(quizes)
        return render_template('quizes.html', quizes=quizes, html_config = html_config)
    
    session['quiz_id'] = request.form.get('quiz')
    session['question_n'] = 0
    session['question_id'] = 0
    session['right_answers'] = 0
    return redirect(url_for('view_question'))

@app.route('/quiz_add/', methods=['GET', 'POST'])
def quiz_add():
    if request.method == 'POST':
        name = request.form.get('name')
        user_id = request.form.get('user_id')
        if name and user_id:
            user = db.session.get(User, user_id)
            if user:
                db.session.add(Quiz(name, user))
                db.session.commit()
        return redirect(url_for('view_quiz_edit'))
    users = User.query.all()
    return render_template('quiz_add.html', 
                           users=users, 
                           html_config=html_config)

@app.route('/quiz_edit/<int:id>/', methods=['GET', 'POST'])
def quiz_edit(id):
    quiz = db.session.get(Quiz, id)
    if not quiz:
        return redirect(url_for('view_quiz_edit'))
    if request.method == 'POST':
        quiz.name = request.form.get('name')
        user_id = request.form.get('user_id')
        if user_id:
            quiz.user = db.session.get(User, user_id)
        db.session.commit()
        return redirect(url_for('view_quiz_edit'))
    users = User.query.all()
    return render_template('quiz_edit.html', 
                           quiz=quiz, 
                           users=users, 
                           html_config=html_config)

@app.route('/quiz_delete/<int:id>/')
def quiz_delete(id):
    Quiz.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('view_quiz_edit'))

@app.route('/question/', methods = ['POST', 'GET'])
def view_question():
    
    if not session['quiz_id'] or session['quiz_id'] == -1:
        return redirect(url_for('view_quiz'))

    # если пост значит ответ на вопрос        
    if request.method == 'POST':        
        # question = Question.query.filter_by(id=session['question_id']).all()[0]
        question = db.session.get(Question, session['question_id'])
                
        # если ответ ы сходятся значит +1
        if question.answer == request.form.get('ans_text'):
            session['right_answers'] += 1
        # следующий вопрос
        session['question_n'] += 1


    # quiz = Quiz.query.filter_by(id = session['quiz_id']).all()
    quiz = db.session.get(Quiz, session['quiz_id'])
    if int(session['question_n']) >= len(quiz.question):
        session['quiz_id'] = -1 # чтообы больше не работола страница question
        return redirect(url_for('view_result'))
    
    else:
        question = quiz.question[session['question_n']]
        session['question_id'] = question.id
        answers = [question.answer, question.wrong1, question.wrong2, question.wrong3 ]
        shuffle(answers)

        return render_template('question.html', 
                               answers=answers, 
                               question=question,
                               html_config = html_config
                               )

@app.route('/question_add/', methods=['GET', 'POST'])
def question_add():
    if request.method == 'POST':
        q = request.form.get('question')
        a = request.form.get('answer')
        w1 = request.form.get('wrong1')
        w2 = request.form.get('wrong2')
        w3 = request.form.get('wrong3')
        if all([q, a, w1, w2, w3]):
            db.session.add(Question(q, a, w1, w2, w3))
            db.session.commit()
        return redirect(url_for('view_quiz_edit'))
    return render_template('question_add.html', 
                           html_config=html_config)

@app.route('/question_edit/<int:id>/', methods=['GET', 'POST'])
def question_edit(id):
    q = db.session.get(Question, id)
    if not q:
        return redirect(url_for('view_quiz_edit'))
    if request.method == 'POST':
        q.question = request.form.get('question')
        q.answer = request.form.get('answer')
        q.wrong1 = request.form.get('wrong1')
        q.wrong2 = request.form.get('wrong2')
        q.wrong3 = request.form.get('wrong3')
        db.session.commit()
        return redirect(url_for('view_quiz_edit'))
    return render_template('question_edit.html', 
                           question=q, 
                           html_config=html_config)

@app.route('/question_delete/<int:id>/')
def question_delete(id):
    Question.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('view_quiz_edit'))

@app.route('/result/')
def view_result():
    return render_template('result.html', 
                    right=session['right_answers'], 
                    total = session['question_n'],
                    html_config = html_config)

@app.route('/quizes_view/', methods = ['POST', 'GET'])
def view_quiz_edit():
    quizes = Quiz.query.all()    
    questions = Question.query.all()
    return render_template('quizes_view.html', 
                           html_config = html_config,
                           quizes = quizes,
                           questions = questions,
                           len = len)

@app.route('/quiz_questions_edit/<int:quiz_id>/', methods=['GET', 'POST'])
def quiz_questions_edit(quiz_id):
    quiz = db.session.get(Quiz, quiz_id)
    if not quiz:
        return redirect(url_for('view_quiz_edit'))

    if request.method == 'POST':
        selected_ids = request.form.getlist('question_ids')
        selected_ids = [int(i) for i in selected_ids if i.isdigit()]

        quiz.question.clear()

        for q_id in selected_ids:
            q = db.session.get(Question, q_id)
            if q:
                quiz.question.append(q)
        db.session.commit()
        return redirect(url_for('view_quiz_edit'))

    all_questions = Question.query.all()
    current_ids = {q.id for q in quiz.question}
    return render_template('quiz_questions_edit.html',
                           quiz=quiz,
                           all_questions=all_questions,
                           current_ids=current_ids,
                           html_config=html_config)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', html_config = html_config)
    
    
app.run(debug=True)    