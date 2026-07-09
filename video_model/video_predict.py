from __future__ import annotations

import numpy as np

from config import VIDEO_CONFIG, build_prediction_result
from image_model.image_model import load_image_model
from image_model.image_utils import preprocess_image_array

from .video_utils import extract_video_frames


def predict_video_bytes(video_bytes: bytes, filename: str | None = None) -> dict:
    loaded_image_model = load_image_model()
    frames = extract_video_frames(video_bytes, filename)
    frame_batches = [
        preprocess_image_array(frame_bgr, mode=loaded_image_model.preprocessing)[0]
        for frame_bgr in frames
    ]
    batch = np.stack(frame_batches, axis=0).astype(np.float32)
    frame_predictions = loaded_image_model.model.predict(batch, verbose=0)
    average_prediction = np.mean(frame_predictions, axis=0)
    
    # DEBUG: Print raw model output
    print(f"[DEBUG VIDEO] Raw frame predictions shape: {frame_predictions.shape}")
    print(f"[DEBUG VIDEO] Average prediction: {average_prediction}")
    print(f"[DEBUG VIDEO] Model preprocessing: {loaded_image_model.preprocessing}")
    print(f"[DEBUG VIDEO] Model legacy_binary_head: {loaded_image_model.legacy_binary_head}")

    return build_prediction_result(
        modality="video",
        raw_prediction=average_prediction,
        threshold=VIDEO_CONFIG.threshold,
        model_source=f"frame_ensemble::{loaded_image_model.source_path}",
        extra={
            "filename": filename,
            "frames_used": int(batch.shape[0]),
            "frame_shape": list(batch.shape[1:]),
            "preprocessing": loaded_image_model.preprocessing,
            "frame_probabilities": np.asarray(frame_predictions, dtype=np.float32).tolist(),
        },
    )
