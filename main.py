from fastapi import FastAPI
from routes import auth, account
from database import engine, Base

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

# Создание приложения FastAPI
app = FastAPI(
    title="Auth Service",
    version="1.0.0",
    description="Сервис авторизации с JWT токенами\n\n"
)

# Подключение роутов аутентификации
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(account.router, prefix="/api/v1/account", tags=["account"])

@app.get("/")
async def root():
    return {"message": "Auth Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
