import io
import cv2
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from fastapi import UploadFile
from starlette.responses import StreamingResponse
from PIL import Image

from sqlalchemy.orm import Session
from app.database.models import Video, Embedding, VideoStatus

model = models.resnet50(weights='ResNet50_Weights.DEFAULT')
model.eval()

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def search_by_image(db: Session, file: UploadFile):
    img = Image.open(file.file)
    img = transform(img).unsqueeze(0)

    with torch.no_grad():
        embeddings = model(img)
    embeddings = embeddings.numpy().flatten()

    result = db.query(Embedding).order_by(Embedding.embedding.l2_distance(embeddings)).first()
    video = db.query(Video).filter_by(id=result.video_id).first()

    capture = cv2.VideoCapture(video.path)
    capture.set(cv2.CAP_PROP_POS_FRAMES, result.frame)
    ret, img = capture.read()
    jpg = cv2.imencode('.jpg', img)[1].tobytes()

    return StreamingResponse(io.BytesIO(jpg), media_type="image/jpeg")



def indexing(db: Session, video: Video):
    video.status = VideoStatus.INDEXING
    db.commit()

    try:
        capture = cv2.VideoCapture(video.path)
        fps = int(capture.get(cv2.CAP_PROP_FPS))
        frame = 0

        while True:
            ret, img = capture.read()
            if not ret:
                break

            if frame % fps == 0:
                img = Image.fromarray(img)
                img = transform(img).unsqueeze(0)

                with torch.no_grad():
                    embeddings = model(img)
                embedding = Embedding(video_id=video.id, frame=frame, embedding=embeddings.numpy().flatten())
                db.add(embedding)
                db.commit()

            frame += 1
        video.status = VideoStatus.COMPLETED
        db.commit()
    except Exception as e:
        print(e)
        video.status = VideoStatus.FAILED
        db.commit()
        return
