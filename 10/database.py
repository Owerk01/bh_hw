from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from sqlalchemy import select, text

from models import UserOrm, Model, QuizOrm, QuestionOrm, logger
from schemas import *

import os

BASE_DIR = os.path.dirname(__file__)
DB_DIR = os.path.join(BASE_DIR, 'db')

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)
    
DB_PATH = os.path.join(DB_DIR, 'fastapi.db')    

engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}")
# engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}", echo=True) # echo=True - все sql в консоль
# engine = create_async_engine("sqlite+aiosqlite:///example//fastapi//db//fastapi.db")
# engine = create_async_engine("sqlite+aiosqlite:///db//fastapi.db")

new_session = async_sessionmaker(engine, expire_on_commit=False)
# expire_on_commit=False отключает истечение (сброс) атрибутов объектов после commit() в SQLAlchemy сессии.
# если True - после комита обращение к любому полю создаст новый запрос, если False -возмет из памяти



class  DataRepository:
    @classmethod
    async def create_table(cls):
        async with engine.begin() as conn:
            await conn.run_sync(Model.metadata.create_all)
    
    @classmethod            
    async def delete_table(cls):
        async with engine.begin() as conn:
            await conn.run_sync(Model.metadata.drop_all)     

    @classmethod
    async def add_test_data(cls):
        async with new_session() as session:
            user1 = UserOrm(name='user1', age=20)
            user2 = UserOrm(name='user2', age=30, phone='123456789')
            user3 = UserOrm(name='user3', age=41, phone='11')
            session.add_all([user1, user2, user3])
            await session.flush() 

            questions = [
                QuestionOrm(
                    question='Сколько будут 2+2*2',
                    answer='6',
                    wrong1='8', wrong2='2', wrong3='0'
                ),
                QuestionOrm(
                    question='Сколько месяцев в году имеют 28 дней?',
                    answer='Все',
                    wrong1='Один', wrong2='Ни одного', wrong3='Два'
                ),
                QuestionOrm(
                    question='Каким станет зелёный утёс, если упадет в Красное море?',
                    answer='Мокрым?',
                    wrong1='Красным', wrong2='Не изменится', wrong3='Фиолетовым'
                ),
                QuestionOrm(
                    question='Какой рукой лучше размешивать чай?',
                    answer='Ложкой',
                    wrong1='Правой', wrong2='Левой', wrong3='Любой'
                ),
                QuestionOrm(
                    question='Что не имеет длины, глубины, ширины, высоты, а можно измерить?',
                    answer='Время',
                    wrong1='Глупость', wrong2='Море', wrong3='Воздух'
                ),
                QuestionOrm(
                    question='Когда сетью можно вытянуть воду?',
                    answer='Когда вода замерзла',
                    wrong1='Когда нет рыбы', wrong2='Когда уплыла золотая рыбка', wrong3='Когда сеть порвалась'
                ),
                QuestionOrm(
                    question='Что больше слона и ничего не весит?',
                    answer='Тень слона',
                    wrong1='Воздушный шар', wrong2='Парашют', wrong3='Облако'
                ),
                QuestionOrm(
                    question='Что такое у меня в кармашке?',
                    answer='Кольцо',
                    wrong1='Кулак', wrong2='Дырка', wrong3='Бублик'
                ),
            ]
            session.add_all(questions)
            await session.flush() 

            quiz1 = QuizOrm(name="QUIZ 1", user_id=user1.id)
            quiz2 = QuizOrm(name="QUIZ 2", user_id=user1.id)
            quiz3 = QuizOrm(name="QUIZ 3", user_id=user2.id)
            quiz4 = QuizOrm(name="QUIZ 4", user_id=user3.id)

            quiz1.questions = [questions[0], questions[1], questions[2]]
            quiz2.questions = [questions[2], questions[4], questions[5], questions[1]]
            quiz3.questions = [questions[7], questions[6], questions[3]]
            quiz4.questions = [questions[3], questions[6], questions[5], questions[1], questions[0]]

            session.add_all([quiz1, quiz2, quiz3, quiz4])

            await session.commit()


class UserRepository:
    
    @classmethod
    async def add_user(cls, user: UserAdd) -> int:
        async with new_session() as session:
            data = user.model_dump() # -> dict
            user = UserOrm(**data)
            session.add(user) # не производит операций с БД только с памятью поэтому синхронно
            await session.flush()
            await session.commit()
            return user.id
        
    @classmethod
    async def add_quiz(cls, quiz: QuizAdd) -> int:
        async with new_session() as session:
            data = quiz.model_dump()
            new_quiz = QuizOrm(**data)
            session.add(new_quiz)
            await session.flush()
            await session.commit()
            return new_quiz.id
        
    @classmethod
    async def add_question(cls, question: QuestionAdd) -> int:
        async with new_session() as session:
            data = question.model_dump()
            new_question = QuestionOrm(**data)
            session.add(new_question)
            await session.flush()
            await session.commit()
            return new_question.id
            
    @classmethod        
    async def get_users(cls, limit, offset,) -> list[UserOrm]:
        async with new_session() as session:
            
            # query = select(UserOrm)
            query = select(UserOrm).limit(limit).offset(offset)
            
            # query = user_filter.filter(query).limit(limit).offset(offset)
            # query = user_filter.sort(query)
            # query = text(f"SELECT * FROM users WHERE id={id}")
            
            res = await session.execute(query)
            users = res.scalars().all()
            return users
        
    @classmethod
    async def get_quizzes(cls, limit, offset) -> list[QuizOrm]:
        async with new_session() as session:
                query =select(QuizOrm).limit(limit).offset(offset)
                res = await session.execute(query)
                logger.debug(f"res: {res}")
                quizzes = res.scalars().all()
                logger.debug(f"quizzes_db = {quizzes}")
                return quizzes 
        
    @classmethod
    async def get_questions(cls, limit, offset) -> list[QuestionOrm]:
        async with new_session() as session:
                query =select(QuestionOrm).limit(limit).offset(offset)
                res = await session.execute(query)
                questions = res.scalars().all()
                return questions 
        
    @classmethod
    async def get_user(cls, id) -> UserOrm:
        async with new_session() as session:
            query = select(UserOrm).filter(UserOrm.id==id)
            # query = text(f"SELECT * FROM users WHERE id={id}")
            res = await session.execute(query) 
            user = res.scalars().first()
            return user
        
    @classmethod
    async def get_quiz(cls, id) -> QuizOrm:
        async with new_session() as session:
            query = select(QuizOrm).filter(QuizOrm.id==id)
            res = await session.execute(query)
            quiz = res.scalars().first()
            return quiz
        
    @classmethod
    async def get_question(cls, id) -> QuestionOrm:
        async with new_session() as session:
            query = select(QuestionOrm).filter(QuestionOrm.id==id)
            res = await session.execute(query)
            question = res.scalars().first()
            return question