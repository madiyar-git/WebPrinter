from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.printers import router as printers_router
from app.api.v1.print import router as print_router

app = FastAPI(
    title="Print Service API",
    description="REST API для сервиса отправки документов на печать",
    version="0.1.0",
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров v1
app.include_router(printers_router, prefix="/api/v1")
app.include_router(print_router, prefix="/api/v1")


@app.get("/api/v1/health", summary="Проверка состояния API")
async def health_check():
    return {
        "status": "ok",
        "service": "print-service-backend",
    }