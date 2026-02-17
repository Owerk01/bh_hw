from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table, Column, func, Integer

from datetime import datetime
import logging
import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',   
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))

logger = colorlog.getLogger('MyApp')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class Model(DeclarativeBase):

    # можно тут добавить тогда эти столбцы будут во всех таблицах
   # т.к. мы наследуемся от этого класса
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # будет вписывать дататайм при создании записи
    dateCreate: Mapped[datetime] = mapped_column(        
                                        server_default=func.now(),
                                        nullable=False)
    
    # будет вписывать дататайм при обновлении записи
    dateUpdate: Mapped[datetime] = mapped_column(        
                                        server_default=func.now(),
                                        server_onupdate=func.now(),
                                        nullable=False)


class UserOrm(Model):
    __tablename__ = 'user'
    
    # уже не нужен так как наследуется
    # id: Mapped[int] = mapped_column(primary_key=True)
    
    name: Mapped[str]
    age: Mapped[int]
    phone: Mapped[str|None]
    quizzes: Mapped[list['QuizOrm']] = relationship(back_populates='user')

quiz_question = Table('quiz_question',
                      Model.metadata,
                      Column('quiz_id', Integer, ForeignKey('quiz.id'), primary_key=True),
                      Column('question_id', Integer, ForeignKey('question.id'), primary_key=True))

class QuizOrm(Model):
    __tablename__ = 'quiz'
    name: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped['UserOrm'] = relationship(back_populates='quizzes')
    questions: Mapped[list['QuestionOrm']] = relationship(secondary='quiz_question',
                                                          back_populates='quizzes')

class QuestionOrm(Model):
    __tablename__ = 'question'
    question: Mapped[str]
    answer: Mapped[str]
    wrong1: Mapped[str]
    wrong2: Mapped[str]
    wrong3: Mapped[str]
    quizzes: Mapped[list['QuizOrm']] = relationship(secondary='quiz_question',
                                                   back_populates='questions',)