from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    # __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(25))
    
    quizes = db.relationship('Quiz', backref='user', 
                             cascade = "all, delete, delete-orphan",
                             lazy='select')
    
     # lazy - 
            # select (по умолчанию)   Загружает всю коллекцию одним отдельным SELECT-запросом при первом обращении к атрибуту
            # joined  Загружает коллекцию сразу через JOIN с основной таблицей
            # subquery    Загружает коллекцию через подзапрос
            # dynamic Возвращает query-объект, коллекция не загружается сразу, можно строить запросы

    
    def __init__(self, name) -> None:
        super().__init__()
        self.name = name
        
    def __repr__(self):
        return self.name

# отдельная таблица для связи many_to_many
quiz_question = db.Table('quiz_question',
            db.Column('quiz_id', db.Integer, db.ForeignKey('quiz.id'), primary_key=True),
            db.Column('question_id', db.Integer, db.ForeignKey('question.id'), primary_key=True),
            )

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    
    # связь many_to_many прописываем только в одной из 2х таблиц
    # во второй появиться автоматом
    # если надо явно указать имя обратной связи во 2ой таблице тогда 
    # вместо backref - back_populates в обоих таблицах
    # question = db.relationship(
    #             'Question', 
    #             secondary=quiz_question, backref = 'quiz')

    def __init__(self, name: str, user:User) -> None:
        super().__init__()
        self.name = name
        self.user = user

    def __repr__(self) -> str:
        return f'id - {self.id}, name - {self.name}'



class Question(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    question = db.Column(db.String(250), nullable=False)
    answer = db.Column(db.String(100), nullable=False)
    wrong1 = db.Column(db.String(100), nullable=False)
    wrong2 = db.Column(db.String(100), nullable=False)
    wrong3 = db.Column(db.String(100), nullable=False)
    
    quiz = db.relationship(
                'Quiz', 
                secondary=quiz_question, backref = 'question')

    def __init__(self, quesion: str, answer, wrong1, wrong2, wrong3) -> None:
        super().__init__()
        self.question = quesion
        self.answer = answer
        self.wrong1 = wrong1
        self.wrong2 = wrong2
        self.wrong3 = wrong3

    def __repr__(self):
        return f'{self.id}-{self.question}'    
    
def db_add_new_data():
    db.drop_all()
    db.create_all()    
    
    user1 = User('Петя')
    user2 = User('Вася1')    
    user3 = User('user3')    
    
    quizes = [
        Quiz("QUIZ 1", user1),
        Quiz("QUIZ 2", user1),
        Quiz("QUIZ 3", user2),
        Quiz("QUIZ 4", user3),
    ]
    
    
    questions = [        
        Question('Сколько будут 2+2*2', '6', '8', '2', '0'),
        Question('Сколько месяцев в году имеют 28 дней?', 'Все', 'Один', 'Ни одного', 'Два'),
        Question('Каким станет зелёный утёс, если упадет в Красное море?', 'Мокрым?', 'Красным', 'Не изменится', 'Фиолетовым'),
        Question('Какой рукой лучше размешивать чай?', 'Ложкой', 'Правой', 'Левой', 'Любой'),
        Question('Что не имеет длины, глубины, ширины, высоты, а можно измерить?', 'Время', 'Глупость', 'Море', 'Воздух'),
        Question('Когда сетью можно вытянуть воду?', 'Когда вода замерзла', 'Когда нет рыбы', 'Когда уплыла золотая рыбка', 'Когда сеть порвалась'),
        Question('Что больше слона и ничего не весит?', 'Тень слона', 'Воздушный шар', 'Парашют', 'Облако'),
        Question('Что такое у меня в кармашке?', 'Кольцо', 'Кулак', 'Дырка', 'Бублик'),
        
    ]
    
    quizes[0].question.append(questions[0])
    quizes[0].question.append(questions[1])
    quizes[0].question.append(questions[2])
    
    quizes[1].question.append(questions[2])
    quizes[1].question.append(questions[4])
    quizes[1].question.append(questions[5])
    quizes[1].question.append(questions[1])
    
    quizes[2].question.append(questions[7])
    quizes[2].question.append(questions[6])
    quizes[2].question.append(questions[3])
    
    quizes[3].question.append(questions[3])
    quizes[3].question.append(questions[6])
    quizes[3].question.append(questions[5])
    quizes[3].question.append(questions[1])
    quizes[3].question.append(questions[0])
    
    # db.session.add(user1)
    # db.session.add_all([user1, user2, User('_Коля')])
    db.session.add_all(quizes)
    
    
    db.session.commit()
        
    
# CRUD

'''
УПРАВЛЕНИЕ ДАННЫМИ 



# создать объекты
user = User('user1')
quiz = Quiz('QUIZ 1', user1)
question = Question('Сколько будут 2+2*2', '6', '8', '2', '0')

# добавить в квиз вопрос
quiz.question.append(question)

# сохранить КВИЗ в базу
db.session.add(quiz)
db.session.commit()

# взять все  квизы из базы и распечатать с вопросами
quizes = Quiz.query.all() # 
for quiz in quizes:
    print(quiz) # как в __repr__
    print(quiz.question) # -> список
    for question in quiz.question:
        print(question) # как в __repr__
        
        
# взять вопрос по id (так работает только по id) самый быстрый метод
user = db.session.get(User, 1) 
question = db.session.get(Question, 1)

# фильтрация
# user = db.query(User).filter_by(id=2).one()    
# users = db.query(User).filter(User.id>3).all()

# from sqlalchemy import or_
# users = db.query(User).filter(or_(User.name=='Max1', User.fname=='Max2')).all()
# print(users)

# users = db.query(User).filter(User.name.like(r'%Max6%')).all()
# print(users)


# сколько вопросов в квизе
len(quiz.question) 

# Добавить в квиз вопрос с id = 1
quiz.question.append(db.session.query(Question).get(1))
db.session.commit()

# найти вопросы id которых есть в списке или не в списке
questions = Question.query.filter(Question.id.in_([1,2,3])).all()    
questions = Question.query.filter(Question.id.not_in([1,2,3])).all()  

# изменить данные
question = db.session.query(Question).get(id)
question.question = 'измененный вопрос'
question.answer = 'измененный правильный ответ'
user.name = "Vasya"
db.session.commit()
    
# удалить квиз
Quiz.query.filter_by(id = id).delete()
db.session.query(Quiz).get(id).delete()
db.session.commit()

# отвязать вопрос от квиза
question = db.session.query(Question).get(id)
quiz.question.remove(question)
db.session.commit()


# получить связанные данные в обратную сторону
question = db.session.query(Question).get(id)
print(question.quiz) # распечатает все квизы в которые входит вопрос

'''