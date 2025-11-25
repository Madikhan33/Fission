from fastapi import FastAPI
from granian import Granian
from core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from auth.routes import router as auth_router

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.router.include_router(auth_router)




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