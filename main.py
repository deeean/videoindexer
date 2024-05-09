from fastapi import FastAPI
from app.routers import router

app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=3000,
        log_level="debug",
        reload=True
    )
