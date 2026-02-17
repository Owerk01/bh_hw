from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from routers import default_router, users_router, quizzes_router, questions_router
from database import DataRepository as dr

@asynccontextmanager # реагирует на  методы __aenter__() и __aexit__()
async def lifespan(app: FastAPI):
    await dr.create_table()
    await dr.add_test_data()
    print("------Bases build-------------")
    
    yield 
    await dr.delete_table()
    print("-------------Bases drooped------------")




app = FastAPI(lifespan=lifespan)

app.include_router(default_router)
app.include_router(users_router)
app.include_router(quizzes_router)
app.include_router(questions_router)



if __name__ == '__main__':    
    uvicorn.run("main:app", reload=True)  
