from fastapi import APIRouter, Depends, UploadFile
from fastapi_utilities import repeat_every
from sqlalchemy.orm import Session
from app.core.indexer import indexing, search_by_image
from app.database.models import Video, VideoStatus
from app.database.connection import get_db

router = APIRouter()


@router.get("/videos")
def get_videos(db: Session = Depends(get_db)):
    return db.query(Video).all()


@router.post("/video")
def create_video(file: UploadFile, db: Session = Depends(get_db)):
    return ""


@router.post("/video/search_by_image")
def search_video_by_image(file: UploadFile, db: Session = Depends(get_db)):
    return search_by_image(db, file)


@router.on_event("startup")
def insert_test_video():
    db = next(get_db())
    if db.query(Video).count() != 0:
        return

    video = Video(name="Big Buck Bunny", description="", path="testdata/videos/big_buck_bunny.mp4")
    db.add(video)
    db.commit()


@router.on_event("startup")
@repeat_every(seconds=5)
def video_indexing_trigger():
    db = next(get_db())
    video = db.query(Video).filter_by(status=VideoStatus.PENDING).first()
    indexing(db, video)
