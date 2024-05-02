from fastapi import APIRouter, UploadFile
from fastapi_utilities import repeat_every

router = APIRouter()


@router.get("/videos")
def get_videos():
    return []


@router.post("/video")
def create_video(file: UploadFile):
    print(file)
    return ""


@router.on_event("startup")
@repeat_every(seconds=5)
def indexing_video():
    pass
