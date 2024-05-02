from fastapi import APIRouter
from app.routers import ping, video

router = APIRouter()
router.include_router(ping.router)
router.include_router(video.router)
