from __future__ import annotations

import os
import tempfile

import cv2
import numpy as np

from config import VIDEO_CONFIG


def _temp_suffix(filename: str | None) -> str:
    if not filename:
        return ".mp4"
    _, extension = os.path.splitext(filename)
    return extension or ".mp4"


def extract_video_frames(video_bytes: bytes, filename: str | None = None) -> np.ndarray:
    with tempfile.NamedTemporaryFile(delete=False, suffix=_temp_suffix(filename)) as temp_file:
        temp_file.write(video_bytes)
        temp_path = temp_file.name

    capture = cv2.VideoCapture(temp_path)
    frames: list[np.ndarray] = []

    try:
        while len(frames) < VIDEO_CONFIG.frame_count:
            grabbed = capture.grab()
            if not grabbed:
                break

            current_frame = int(capture.get(cv2.CAP_PROP_POS_FRAMES)) - 1
            if current_frame % VIDEO_CONFIG.frame_stride != 0:
                continue

            success, frame_bgr = capture.retrieve()
            if not success or frame_bgr is None:
                continue
            frames.append(frame_bgr)
    finally:
        capture.release()
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    if not frames:
        raise ValueError("Could not decode any frames from the uploaded video.")

    if len(frames) < VIDEO_CONFIG.frame_count:
        frames.extend([frames[-1].copy() for _ in range(VIDEO_CONFIG.frame_count - len(frames))])

    return np.asarray(frames, dtype=np.uint8)
