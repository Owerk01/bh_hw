from pydantic import BaseModel, ConfigDict

class UserAdd(BaseModel):
    name: str
    age: int
    phone: str | None = None
    
class User(UserAdd):    
    id: int
    
    model_config = ConfigDict(from_attributes=True)    
    # возможность сбора модели из атрибутов объекта (как правило из ORM)
    # Без этого параметра Pydantic ожидал бы словарь, а не объект с атрибутами.
    
       
class UserId(BaseModel):
    id: int

class QuizAdd(BaseModel):
    name: str
    user_id: int

class Quiz(QuizAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)

class QuizId(BaseModel):
    id: int

class QuestionAdd(BaseModel):
    question: str
    answer: str
    wrong1: str
    wrong2: str
    wrong3: str

class Question(QuestionAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)

class QuestionId(BaseModel):
    id: int

class QuizQuestions(Quiz):
    questions: list[Question]

class QuestionLink(BaseModel):
    ids: list[int]