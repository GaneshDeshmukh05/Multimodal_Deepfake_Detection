from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile

from .video_predict import predict_video_bytes


app = FastAPI(title="Video Deepfake Detection Service", version="2.0.0")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "modality": "video"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> dict:
    try:
        payload = await file.read()
        if not payload:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        return predict_video_bytes(payload, filename=file.filename)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
