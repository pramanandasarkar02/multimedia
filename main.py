from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pymongo import MongoClient
from bson import ObjectId
import gridfs
import io

app = FastAPI()

# MongoDB Atlas connection
MONGO_URI = "mongodb+srv://pramanandasarkar02_db_user:diOxske9Uiao2oPC@cluster0.iefyzqw.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["media_database"]
fs = gridfs.GridFS(db)

# Static folder path
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Serve static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def list_all_files():
    files = []

    for f in db.fs.files.find():
        files.append({
            "id": str(f["_id"]),
            "filename": f.get("filename"),
            "content_type": f.get("contentType"),
            "media_type": f.get("media_type")
        })

    return {
        "total_files": len(files),
        "files": files
    }


@app.post("/images/")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    content = await file.read()

    file_id = fs.put(
        content,
        filename=file.filename,
        content_type=file.content_type,
        media_type="image"
    )

    return {
        "message": "Image uploaded successfully",
        "id": str(file_id)
    }


@app.post("/videos/")
async def upload_video(file: UploadFile = File(...)):
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Only video files are allowed")

    content = await file.read()

    file_id = fs.put(
        content,
        filename=file.filename,
        content_type=file.content_type,
        media_type="video"
    )

    return {
        "message": "Video uploaded successfully",
        "id": str(file_id)
    }


@app.post("/audio/")
async def upload_audio(file: UploadFile = File(...)):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Only audio files are allowed")

    content = await file.read()

    file_id = fs.put(
        content,
        filename=file.filename,
        content_type=file.content_type,
        media_type="audio"
    )

    return {
        "message": "Audio uploaded successfully",
        "id": str(file_id)
    }


@app.get("/images/{file_id}")
def get_image(file_id: str):
    try:
        file = fs.get(ObjectId(file_id))

        if file.media_type != "image":
            raise HTTPException(status_code=400, detail="Not an image file")

        return StreamingResponse(
            io.BytesIO(file.read()),
            media_type=file.content_type
        )

    except Exception:
        raise HTTPException(status_code=404, detail="Image not found")


@app.get("/videos/{file_id}")
def get_video(file_id: str):
    try:
        file = fs.get(ObjectId(file_id))

        if file.media_type != "video":
            raise HTTPException(status_code=400, detail="Not a video file")

        return StreamingResponse(
            io.BytesIO(file.read()),
            media_type=file.content_type
        )

    except Exception:
        raise HTTPException(status_code=404, detail="Video not found")


@app.get("/audio/{file_id}")
def get_audio(file_id: str):
    try:
        file = fs.get(ObjectId(file_id))

        if file.media_type != "audio":
            raise HTTPException(status_code=400, detail="Not an audio file")

        return StreamingResponse(
            io.BytesIO(file.read()),
            media_type=file.content_type
        )

    except Exception:
        raise HTTPException(status_code=404, detail="Audio not found")


@app.get("/articles/{article_id}")
def get_article(article_id: str):
    file_path = STATIC_DIR / f"{article_id}.html"

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Article not found")

    content = file_path.read_text(encoding="utf-8")

    return {
        "id": article_id,
        "filename": file_path.name,
        "content": content
    }

@app.get("/articles/view/{article_id}")
def view_article(article_id: str):
    file_path = STATIC_DIR / f"{article_id}.html"

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Article not found")

    return FileResponse(file_path)