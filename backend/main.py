from fastapi import FastAPI
from granian import Granian
from core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from auth.routes import router as auth_router
from my_tasks.routes import router as tasks_router
from resume_ai.routes import router as resume_ai_router
from rooms.routes import router as rooms_router
from ai.routes import router as ai_router
from notifications.routes import router as notifications_router


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.router.include_router(auth_router, tags=['Auth'])
app.router.include_router(tasks_router)
app.router.include_router(resume_ai_router)
app.router.include_router(rooms_router)
app.router.include_router(ai_router)
app.router.include_router(notifications_router)



@app.get('/', tags=['main'])
def main():
    return {'message': 'Hello World'}





if __name__ == "__main__":
    server = Granian(
        "main:app",
        address="127.0.0.1",
        port=8000,
        interface="asgi",
        reload=True  # для разработки
    )
    server.serve()