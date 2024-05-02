from fastapi import FastAPI
from app.routers import router

app = FastAPI()
app.include_router(router)


@app.on_event("startup")
async def startup():
    print("Starting up...")


@app.on_event("shutdown")
async def shutdown():
    print("Shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=3000,
        log_level="debug",
        reload=True
    )
