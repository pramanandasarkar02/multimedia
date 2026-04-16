from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pymongo import MongoClient
from bson import ObjectId
import gridfs
import io
import os

app = FastAPI()

# =========================
# MongoDB Connection
# =========================
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://USERNAME:PASSWORD@cluster0.mongodb.net/?retryWrites=true&w=majority"
)

client = MongoClient(MONGO_URI)
db = client["media_database"]
fs = gridfs.GridFS(db)


# =========================
# Health Check
# =========================
@app.get("/")
def root():
    return {"status": "API running"}


# =========================
# List all files
# =========================
@app.get("/files/")
def list_all_files():
    files = []

    for f in db.fs.files.find():
        files.append({
            "id": str(f["_id"]),
            "filename": f.get("filename"),
            "content_type": f.get("contentType"),
            "media_type": f.get("metadata", {}).get("media_type")
        })

    return {
        "total_files": len(files),
        "files": files
    }


# =========================
# Upload IMAGE
# =========================
@app.post("/images/")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    content = await file.read()

    file_id = fs.put(
        content,
        filename=file.filename,
        content_type=file.content_type,
        metadata={"media_type": "image"}
    )

    return {"message": "Image uploaded", "id": str(file_id)}


# =========================
# Upload VIDEO
# =========================
@app.post("/videos/")
async def upload_video(file: UploadFile = File(...)):
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Only video files are allowed")

    content = await file.read()

    file_id = fs.put(
        content,
        filename=file.filename,
        content_type=file.content_type,
        metadata={"media_type": "video"}
    )

    return {"message": "Video uploaded", "id": str(file_id)}


# =========================
# Upload AUDIO
# =========================
@app.post("/audio/")
async def upload_audio(file: UploadFile = File(...)):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Only audio files are allowed")

    content = await file.read()

    file_id = fs.put(
        content,
        filename=file.filename,
        content_type=file.content_type,
        metadata={"media_type": "audio"}
    )

    return {"message": "Audio uploaded", "id": str(file_id)}


# =========================
# Get IMAGE
# =========================
@app.get("/images/{file_id}")
def get_image(file_id: str):
    try:
        file = fs.get(ObjectId(file_id))

        if file.metadata.get("media_type") != "image":
            raise HTTPException(status_code=400, detail="Not an image file")

        return StreamingResponse(
            io.BytesIO(file.read()),
            media_type=file.content_type
        )

    except Exception:
        raise HTTPException(status_code=404, detail="Image not found")


# =========================
# Get VIDEO
# =========================
@app.get("/videos/{file_id}")
def get_video(file_id: str):
    try:
        file = fs.get(ObjectId(file_id))

        if file.metadata.get("media_type") != "video":
            raise HTTPException(status_code=400, detail="Not a video file")

        return StreamingResponse(
            io.BytesIO(file.read()),
            media_type=file.content_type
        )

    except Exception:
        raise HTTPException(status_code=404, detail="Video not found")


# =========================
# Get AUDIO
# =========================
@app.get("/audio/{file_id}")
def get_audio(file_id: str):
    try:
        file = fs.get(ObjectId(file_id))

        if file.metadata.get("media_type") != "audio":
            raise HTTPException(status_code=400, detail="Not an audio file")

        return StreamingResponse(
            io.BytesIO(file.read()),
            media_type=file.content_type
        )

    except Exception:
        raise HTTPException(status_code=404, detail="Audio not found")