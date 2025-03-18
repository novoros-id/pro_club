from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging
from app.routes import users, files, llm
from app.config import settings

# Настройка логирования
""" logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("app.log"),
    logging.StreamHandler()
])  """

# Аутентификация (в работе)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth_deps = Annotated[str, Depends(oauth2_scheme)]

app = FastAPI(title=settings.APP_NAME, 
              version=settings.VERSION,
              debug=settings.DEBUG, 
              description=settings.DESCRIPTION,
              openapi_url=f"{settings.API_V1_STR}/openapi.json")


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Разрешенные источники (можно заменить на определенные)
    allow_credentials=settings.ALLOW_CREDENTIALS,  # Разрешение куки
    allow_methods=settings.ALLOW_METHODS,  # Разрешенные методы (GET, POST, PUT и т. д.)
    allow_headers=settings.ALLOW_HEADERS,  # Разрешенные заголовки
)

# Middleware для логирования запросов и ответов
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Логирование запроса
        logging.info(f"Request: {request.method} {request.url}")
        logging.info(f"Headers: {request.headers}")
        logging.info(f"Body: {await request.body()}")

        response = await call_next(request)

        # Логирование ответа
        logging.info(f"Response status: {response.status_code}")
        return response

app.add_middleware(LoggingMiddleware)

# Маршрутизация
api_router = APIRouter(prefix=settings.API_V1_STR)

api_router.include_router(users.router)
api_router.include_router(llm.router)
api_router.include_router(files.router)
app.include_router(api_router)

# Корневой эндпоинт (проверка работы API)
@app.get("/", tags=["root"])
async def read_root():
    return {"message": "Ping!"}