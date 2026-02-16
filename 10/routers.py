from fastapi import APIRouter, HTTPException, Depends, Query

from schemas import *
from database import UserRepository as ur, logger
# pip install fastapi_filter
from fastapi_filter import FilterDepends

default_router = APIRouter()

users_router = APIRouter(
    prefix="/users",
    tags = ["Пользователи"]
)

quizzes_router = APIRouter(
    prefix="/quizzes",
    tags = ["Квизы"]
)

questions_router = APIRouter(
    prefix="/questions",
    tags = ["Вопросы"]
)

@default_router.get('/', tags=['API V1'])
async def index():    
    return {'data':'ok'}



# ответ в виде одиночного списка
@users_router.get('')
async def users_get(
            limit:int = Query(ge=1, lt=10, default=9), 
            offset:int = Query(ge=0, default=0),
            # user_filter: UserFilter = FilterDepends(UserFilter)
        ) -> dict[str, int | list[User]]: 
     
    # users =   await ur.get_users(limit, offset, user_filter)
    users =   await ur.get_users(limit, offset)
    
    # return users
    
    # с развернутым ответом 
    return {"data":users, "limit":limit, "offset":offset}

@quizzes_router.get('')
async def quizzes_get(
    limit:int = Query(ge=1, lt=10, default=9),
    offset:int = Query(ge=0, default = 0)
) -> dict[str, list[Quiz] | int]:
    quizzes_db = await ur.get_quizzes(limit, offset)
    quizzes_pd = [Quiz.model_validate(q) for q in quizzes_db]
    return {"data":quizzes_pd, "limit":limit, "offset":offset}

@questions_router.get('')
async def questions_get(
    limit:int = Query(ge=1, lt=10, default=9),
    offset:int = Query(ge=0, default = 0)
) -> dict[str, list[Question] | int]:
    questions = await ur.get_questions(limit, offset)
    logger.debug(f"questions: {questions}")
    return {"data":questions, "limit":limit, "offset":offset}

# @users_router.get('/u2')
# async def users_get2() -> dict[str, list[User] | int]: 
#     users =   await ur.get_users()
#     return {'status':'ok', 'data':users}

# @quizzes_router.get('/u2')
# async def quizzes_get2() -> dict[str, list[Quiz] | int]:
#     quizzes = await ur.get_quizzes()
#     return {"status": "ok", "data": quizzes}

# @questions_router.get('/u2')
# async def questions_get2() -> dict[str, list[Question] | int]:
#     questions = await ur.get_questions()
#     return {"status": "ok", "data": questions}

@users_router.get('/{id}')
async def user_get(id: int) -> User :  
    user =   await ur.get_user(id)
    if user:
        return user    
    raise HTTPException(status_code=404, detail="User not found")
    # или return {'err':"User not found, ..."} # но тогда get_user(id) -> User | dict[str,str]

@quizzes_router.get('/{id}')
async def quiz_get(id: int) -> Quiz:
    quiz = await ur.get_quiz(id)
    if quiz:
        return quiz
    raise HTTPException(status_code=404, detail="Quiz not found")

@questions_router.get('/{id}')
async def question_get(id: int) -> Question:
    question = await ur.get_question(id)
    if question:
        return question
    raise HTTPException(status_code=404, detail="Question not found")
    
@users_router.post('')
async def add_user(user:UserAdd) -> UserId:
    id = await ur.add_user(user)
    return {'id':id}   
 
@quizzes_router.post('')
async def quiz_add(quiz: QuizAdd) -> QuizId:
    quiz_id = await ur.add_quiz(quiz)
    return {'id':quiz_id}

@questions_router.post('')
async def question_add(question: QuestionAdd) -> QuestionId:
    question_id = await ur.add_question(question)
    return {'id':question_id}



# пример развернутого ответа
#     {
            # "items": [...],
            # "total": 100,
            # "page": 1,
            # "size": 10,
            # "pages": 10
            # }

            # Или с ссылками:

            # {
            # "items": [...],
            # "total": 100,
            # "page": 1,
            # "size": 10,
            # "pages": 10,
            # "links": {
            # "next": "http://api.example.com/items?page=2",
            # "prev": null,
            # "first": "http://api.example.com/items?page=1",
            # "last": "http://api.example.com/items?page=10"
            # }
            # }