# Multimodal Deepfake Detection

A simple Docker-based multimodal deepfake detection project for **image**, **audio**, and **video** inputs. The repository includes separate model services for each modality, a small Streamlit frontend, and container orchestration with Docker Compose.

## Overview

This project is organized as a set of independent services:

- **`image_model`**: FastAPI service for image deepfake prediction.
- **`audio_model`**: FastAPI service for audio deepfake prediction.
- **`video_model`**: FastAPI service for video deepfake prediction.
- **`frontend`**: Streamlit UI for uploading a file and viewing predictions.
- **`main.py`**: Combined FastAPI app exposing all three prediction routes from one API.
- **`docker-compose.yml`**: Starts the frontend and the three model services together.

The frontend sends uploaded files to the selected backend service and shows the returned prediction payload.

## Project Structure

```text
.
+-- audio_model/
�   +-- app.py
�   +-- audio_model.py
�   +-- audio_predict.py
�   +-- audio_utils.py
�   +-- Dockerfile
�   +-- requirements.txt
�   +-- model files (.keras, .h5)
+-- image_model/
�   +-- app.py
�   +-- image_model.py
�   +-- image_predict.py
�   +-- image_utils.py
�   +-- Dockerfile
�   +-- requirements.txt
�   +-- model files (.keras)
+-- video_model/
�   +-- app.py
�   +-- video_predict.py
�   +-- video_utils.py
�   +-- Dockerfile
�   +-- requirements.txt
�   +-- model files (.keras)
+-- frontend/
�   +-- app.py
�   +-- Dockerfile
�   +-- requirements.txt
+-- config.py
+-- main.py
+-- docker-compose.yml
```

## Features

- Separate services for image, audio, and video detection.
- Simple web UI built with Streamlit.
- Dockerized setup for easier local deployment.
- Health endpoints for each model service.
- Unified FastAPI application available in `main.py`.
- Configurable thresholds and model-related settings via environment variables.

## How It Works

### 1. Frontend

The Streamlit app in `frontend/app.py` lets you:

- choose a model type: **Image**, **Audio**, or **Video**
- upload a file
- send the file to the matching backend service
- view prediction results, confidence, class index, and raw probabilities

### 2. Backend Services

Each model service exposes:

- `GET /health` � service health check
- `POST /predict` � run prediction on uploaded file

### 3. Combined API

The root-level `main.py` exposes a unified API with:

- `GET /health`
- `POST /image/predict`
- `POST /audio/predict`
- `POST /video/predict`

This can be useful if you want a single entry point instead of separate modality services.

## Ports

By default, Docker Compose maps these ports:

- **Frontend**: `8000` and `8501` ? Streamlit app
- **Image service**: `8001`
- **Audio service**: `8002`
- **Video service**: `8003`

Inside the Docker network:

- `image_model` listens on container port `8000`
- `audio_model` listens on container port `8000`
- `video_model` listens on container port `8000`
- `frontend` communicates with them using service names

## Requirements

Install these before running the project:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

If you want to run services without Docker, you will also need:

- Python 3.10+ recommended
- pip
- system dependencies required by packages such as TensorFlow, OpenCV, librosa, or ffmpeg-compatible tooling if used by your environment

## Run With Docker Compose

From the project root:

```bash
docker compose up --build
```

After startup:

- Open the frontend in your browser at `http://localhost:8501`
- If needed, also try `http://localhost:8000`

To stop the containers:

```bash
docker compose down
```

## API Endpoints

### Individual services

#### Image

- Health: `GET http://localhost:8001/health`
- Predict: `POST http://localhost:8001/predict`

#### Audio

- Health: `GET http://localhost:8002/health`
- Predict: `POST http://localhost:8002/predict`

#### Video

- Health: `GET http://localhost:8003/health`
- Predict: `POST http://localhost:8003/predict`

### Combined API

If you run the root FastAPI app manually, the routes are:

- `GET /health`
- `POST /image/predict`
- `POST /audio/predict`
- `POST /video/predict`

## Example cURL Requests

### Image prediction

```bash
curl -X POST "http://localhost:8001/predict" \
  -F "file=@sample.jpg"
```

### Audio prediction

```bash
curl -X POST "http://localhost:8002/predict" \
  -F "file=@sample.wav"
```

### Video prediction

```bash
curl -X POST "http://localhost:8003/predict" \
  -F "file=@sample.mp4"
```

## Example Response

A typical response may look like this:

```json
{
  "modality": "image",
  "label_mapping": {
    "0": "REAL",
    "1": "FAKE"
  },
  "threshold": 0.5,
  "raw_probabilities": [0.21, 0.79],
  "class_index": 1,
  "label": "FAKE",
  "confidence": 0.79,
  "model_source": "...",
  "filename": "sample.jpg"
}
```

## Environment Variables

The project reads configuration from environment variables, mainly through `config.py` and `docker-compose.yml`.

### Image settings

- `IMAGE_WIDTH` � default `224`
- `IMAGE_HEIGHT` � default `224`
- `IMAGE_THRESHOLD` � default `0.5`
- `IMAGE_COMPLIANT_MODEL` � model filename
- `IMAGE_LEGACY_MODEL` � legacy model filename

### Audio settings

- `AUDIO_SAMPLE_RATE` � default `16000`
- `AUDIO_TARGET_SAMPLES` � default `32000`
- `AUDIO_NUM_MFCC` � default `40`
- `AUDIO_MAX_FRAMES` � default `100`
- `AUDIO_THRESHOLD` � default `0.5`
- `AUDIO_COMPLIANT_MODEL` � model filename
- `AUDIO_LEGACY_MODEL` � legacy model filename
- `AUDIO_LEGACY_WEIGHTS` � weights filename

### Video settings

- `VIDEO_FRAME_COUNT` � default `16`
- `VIDEO_FRAME_STRIDE` � default `2`
- `VIDEO_THRESHOLD` � default `0.5`

## Notes About Models

This repository already contains trained model files such as `.keras` and `.h5` files. The services attempt to load those models during inference.

Depending on which files are present, the code may choose between:

- compliant/full saved Keras models
- legacy model files
- legacy weights files

Make sure the expected model files remain in their current folders, or update the environment variables to match your filenames.

## Running Without Docker

You can also run parts of the project manually.

### Frontend

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

### Single model service example

```bash
cd image_model
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

For audio and video services, run the same command pattern in `audio_model` or `video_model`.

### Combined API example

From the project root:

```bash
pip install fastapi uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Troubleshooting

- If containers fail to build, rebuild with `docker compose up --build`.
- If prediction fails, verify that the required model files exist in the correct folders.
- If the frontend cannot connect, make sure the backend containers are running.
- If audio or video inference fails, verify that the uploaded file format is supported by the preprocessing code.
- If ports are busy, change the host-side port mappings in `docker-compose.yml`.

## Future Improvements

Some useful next steps for this repository could be:

- add sample test files for each modality
- add API documentation screenshots or examples
- add model training instructions
- add `.env` support for easier local configuration
- add request size limits and validation rules

## License

No license file is currently included in this repository. Add one if you plan to distribute the project.
