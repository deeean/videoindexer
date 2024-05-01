import cv2
import torch
import torchvision.models as models
import torchvision.transforms as transforms
import time
import psycopg2
import numpy as np
from PIL import Image
from pgvector.psycopg2 import register_vector

conn = psycopg2.connect(
    host="localhost",
    database="videoindexer2",
    user="postgres",
    password="postgres",
    port="5432"
)

register_vector(conn)

cur = conn.cursor()

cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
conn.commit()

cur.execute("""
CREATE TABLE IF NOT EXISTS embeddings (
    id serial primary key,
    frame integer not null,
    image bytea not null,
    embedding vector(1000) not null,
    created_at timestamp not null default current_timestamp
);
""")
conn.commit()

model = models.resnet50(weights='ResNet50_Weights.DEFAULT')
model.eval()

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def search_embedding():
    img = Image.open("./testdata/images/h.jpg")
    img = transform(img).unsqueeze(0)

    with torch.no_grad():
        embedding = model(img)
    embedding_np = embedding.numpy().flatten()

    now = time.time()
    cur.execute("SELECT id, image, embedding <=> %s as distance FROM embeddings ORDER BY distance ASC LIMIT 10;", (embedding_np,))
    rows = cur.fetchall()
    elapsed = time.time() - now
    print(f"Search took {elapsed:.2f}s")


    for row in rows:
        id, img, similarity = row
        print(f"ID: {id}, Similarity: {1 - similarity}")
        cv2.imshow("result", cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR))
        cv2.waitKey(0)


def insert_embbedings(frame, img):
    buf = cv2.imencode(".jpg", img)[1].tobytes()
    img = Image.fromarray(img)
    img = transform(img).unsqueeze(0)

    with torch.no_grad():
        embedding = model(img)
    embedding_np = embedding.numpy().flatten()

    print(f"Inserting frame {frame}")
    cur.execute("INSERT INTO embeddings (frame, image, embedding) VALUES (%s, %s, %s);", (frame, buf, embedding_np))
    conn.commit()

def insert_embbedings_from_video():
    now = time.time()
    video = cv2.VideoCapture("./testdata/videos/tears_of_steel.mp4")
    fps = int(video.get(cv2.CAP_PROP_FPS))
    frame = 0

    while True:
        ret, img = video.read()
        if not ret:
            break

        if frame % fps == 0:
            insert_embbedings(frame, img)

        frame += 1

    elapsed = time.time() - now
    print(f"Insertion took {elapsed:.2f}s")

insert_embbedings_from_video()
search_embedding()