import streamlit as st
import io
import tempfile
from pathlib import Path

import numpy as np

# Set page config
st.set_page_config(
    page_title="Multimodal Deepfake Detection",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF6B6B;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #FF5252;
    }
    .result-real {
        background-color: #D1FAE5;
        border-left: 6px solid #047857;
        color: #064E3B;
        padding: 1.25rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 8px rgba(4, 120, 87, 0.2);
    }
    .result-fake {
        background-color: #FEE2E2;
        border-left: 6px solid #B91C1C;
        color: #7F1D1D;
        padding: 1.25rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 8px rgba(185, 28, 28, 0.2);
    }
    .result-real h3,
    .result-real p,
    .result-real strong,
    .result-fake h3,
    .result-fake p,
    .result-fake strong {
        color: inherit !important;
    }
    .result-real h3,
    .result-fake h3 {
        margin-top: 0;
        font-weight: 800;
    }
    </style>
""", unsafe_allow_html=True)

def render_image_analysis(image_bytes: bytes) -> None:
    """Render visual diagnostics for an uploaded image."""
    from PIL import Image

    with Image.open(io.BytesIO(image_bytes)) as source_image:
        image = source_image.convert("RGB")
        pixels = np.asarray(image)

    height, width = pixels.shape[:2]
    channel_means = pixels.mean(axis=(0, 1))
    brightness = float(pixels.mean() / 255 * 100)
    contrast = float(pixels.std())
    histograms = {
        "Red": np.bincount(pixels[:, :, 0].ravel(), minlength=256),
        "Green": np.bincount(pixels[:, :, 1].ravel(), minlength=256),
        "Blue": np.bincount(pixels[:, :, 2].ravel(), minlength=256),
    }

    with st.expander("🖼️ Image Analysis", expanded=True):
        metrics = st.columns(4)
        metrics[0].metric("Dimensions", f"{width} × {height}")
        metrics[1].metric("Brightness", f"{brightness:.1f}%")
        metrics[2].metric("Contrast", f"{contrast:.1f}")
        metrics[3].metric(
            "Average RGB",
            "/".join(str(round(value)) for value in channel_means),
        )

        st.caption("RGB channel distribution — left is darker pixel values; right is lighter.")
        st.line_chart(histograms, height=260, use_container_width=True)


def create_temporary_upload(file_bytes: bytes, filename: str, default_suffix: str) -> Path:
    """Persist an upload briefly when a decoder requires a file path."""
    suffix = Path(filename).suffix or default_suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temporary_file:
        temporary_file.write(file_bytes)
        return Path(temporary_file.name)


def render_audio_analysis(audio_bytes: bytes, filename: str) -> None:
    """Render a waveform and mel spectrogram for an uploaded audio file."""
    import librosa

    temporary_path = create_temporary_upload(audio_bytes, filename, ".wav")
    try:
        samples, sample_rate = librosa.load(str(temporary_path), sr=None, mono=True)
    finally:
        temporary_path.unlink(missing_ok=True)
    if samples.size == 0:
        raise ValueError("The audio file did not contain any samples.")

    duration = len(samples) / sample_rate
    analysis_samples = samples[: min(len(samples), sample_rate * 60)]
    waveform_step = max(1, len(analysis_samples) // 5_000)
    waveform = analysis_samples[::waveform_step]

    mel_spectrogram = librosa.feature.melspectrogram(
        y=analysis_samples,
        sr=sample_rate,
        n_mels=128,
    )
    spectrogram_db = librosa.power_to_db(mel_spectrogram, ref=np.max)
    minimum, maximum = spectrogram_db.min(), spectrogram_db.max()
    if maximum > minimum:
        spectrogram_image = ((spectrogram_db - minimum) / (maximum - minimum) * 255).astype(np.uint8)
    else:
        spectrogram_image = np.zeros_like(spectrogram_db, dtype=np.uint8)

    with st.expander("🎵 Audio Analysis", expanded=True):
        metrics = st.columns(4)
        metrics[0].metric("Duration", f"{duration:.2f} sec")
        metrics[1].metric("Sample Rate", f"{sample_rate:,} Hz")
        metrics[2].metric("Peak Amplitude", f"{np.abs(samples).max():.3f}")
        metrics[3].metric("RMS Level", f"{np.sqrt(np.mean(samples ** 2)):.3f}")

        st.markdown("**Waveform**")
        st.line_chart({"Amplitude": waveform}, height=220, use_container_width=True)

        st.markdown("**Mel Spectrogram**")
        st.image(
            np.flipud(spectrogram_image),
            caption="Frequency content over time",
            clamp=True,
            use_column_width=True,
        )
        if len(analysis_samples) < len(samples):
            st.caption("The waveform and spectrogram show the first 60 seconds of this audio file.")


def render_video_analysis(video_bytes: bytes, filename: str) -> None:
    """Render evenly sampled video frames and simple frame-level diagnostics."""
    import cv2

    temporary_path = create_temporary_upload(video_bytes, filename, ".mp4")

    capture = cv2.VideoCapture(str(temporary_path))
    try:
        frame_count = max(0, int(capture.get(cv2.CAP_PROP_FRAME_COUNT)))
        frames_per_second = capture.get(cv2.CAP_PROP_FPS) or 0.0
        width = max(0, int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)))
        height = max(0, int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        sample_count = min(6, frame_count)
        if sample_count == 0:
            raise ValueError("No readable frames were found in this video file.")

        frame_positions = np.linspace(0, frame_count - 1, sample_count, dtype=int)
        sampled_frames = []
        brightness_values = []
        for position in frame_positions:
            capture.set(cv2.CAP_PROP_POS_FRAMES, int(position))
            success, frame = capture.read()
            if success:
                sampled_frames.append((int(position), cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                brightness_values.append(float(frame.mean()))
    finally:
        capture.release()
        temporary_path.unlink(missing_ok=True)

    if not sampled_frames:
        raise ValueError("Video frames could not be decoded.")

    duration = frame_count / frames_per_second if frames_per_second else 0.0
    with st.expander("🎞️ Video Analysis", expanded=True):
        metrics = st.columns(4)
        metrics[0].metric("Resolution", f"{width} × {height}")
        metrics[1].metric("Frame Rate", f"{frames_per_second:.2f} FPS")
        metrics[2].metric("Duration", f"{duration:.2f} sec")
        metrics[3].metric("Frames Sampled", len(sampled_frames))

        st.markdown("**Sample Frames**")
        frame_columns = st.columns(min(3, len(sampled_frames)))
        for index, (position, frame) in enumerate(sampled_frames):
            timestamp = position / frames_per_second if frames_per_second else 0.0
            with frame_columns[index % len(frame_columns)]:
                st.image(frame, caption=f"Frame {position} · {timestamp:.2f}s", use_column_width=True)

        st.caption("Average brightness across the sampled frames.")
        st.line_chart({"Brightness": brightness_values}, height=180, use_container_width=True)


def render_analysis(analysis_name: str, renderer, *args) -> None:
    """Keep optional visual diagnostics from interrupting a completed prediction."""
    try:
        renderer(*args)
    except Exception as error:
        st.warning(f"{analysis_name} could not be generated: {error}")


# Title
st.title("🎬 Multimodal Deepfake Detection")
st.markdown("Detect deepfakes in images, audio, and videos using advanced neural networks")

# Sidebar
st.sidebar.title("Settings")
st.sidebar.markdown("---")

# Model selection
modality = st.sidebar.radio(
    "Select Detection Type:",
    ["Image", "Audio", "Video"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("💡 Upload a file and click 'Predict' to detect deepfakes")

# Main content
col1, col2 = st.columns([1, 1])

if modality == "Image":
    with col1:
        st.subheader("📸 Image Deepfake Detection")
        uploaded_file = st.file_uploader(
            "Upload an image",
            type=["jpg", "jpeg", "png", "bmp"],
            key="image_uploader"
        )
        
        if uploaded_file:
            st.image(uploaded_file, use_column_width=True, caption="Uploaded Image")
            
            if st.button("🔍 Predict", key="image_predict"):
                with st.spinner("Analyzing image..."):
                    try:
                        from image_model.image_predict import predict_image_bytes
                        
                        image_bytes = uploaded_file.getvalue()
                        result = predict_image_bytes(image_bytes, uploaded_file.name)
                        
                        with col2:
                            st.subheader("📊 Prediction Result")
                            
                            # Extract results
                            is_fake = result.get("is_deepfake", False)
                            confidence = result.get("confidence", 0)
                            probability = result.get("probability_fake", 0)
                            
                            # Display result
                            if is_fake:
                                st.markdown(f"""
                                    <div class="result-fake">
                                    <h3>⚠️ DEEPFAKE DETECTED</h3>
                                    <p><strong>Classification:</strong> Fake</p>
                                    <p><strong>Confidence:</strong> {confidence:.2%}</p>
                                    <p><strong>Fake Probability:</strong> {probability:.4f}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                    <div class="result-real">
                                    <h3>✅ AUTHENTIC IMAGE</h3>
                                    <p><strong>Classification:</strong> Real</p>
                                    <p><strong>Confidence:</strong> {confidence:.2%}</p>
                                    <p><strong>Fake Probability:</strong> {probability:.4f}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            render_analysis("Image analysis", render_image_analysis, image_bytes)

                            # Additional info
                            with st.expander("📋 Details"):
                                st.write(f"**File:** {uploaded_file.name}")
                                st.write(f"**File Size:** {uploaded_file.size / 1024:.2f} KB")
                                st.write(f"**Model Source:** {result.get('model_source', 'N/A')}")
                                if "extra" in result:
                                    st.json(result["extra"])
                                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

elif modality == "Audio":
    with col1:
        st.subheader("🎵 Audio Deepfake Detection")
        uploaded_file = st.file_uploader(
            "Upload an audio file",
            type=["wav", "mp3", "m4a", "flac"],
            key="audio_uploader"
        )
        
        if uploaded_file:
            st.audio(uploaded_file, format="audio/wav")
            
            if st.button("🔍 Predict", key="audio_predict"):
                with st.spinner("Analyzing audio..."):
                    try:
                        from audio_model.audio_predict import predict_audio_bytes
                        
                        audio_bytes = uploaded_file.getvalue()
                        result = predict_audio_bytes(audio_bytes, uploaded_file.name)
                        
                        with col2:
                            st.subheader("📊 Prediction Result")
                            
                            # Extract results
                            is_fake = result.get("is_deepfake", False)
                            confidence = result.get("confidence", 0)
                            probability = result.get("probability_fake", 0)
                            
                            # Display result
                            if is_fake:
                                st.markdown(f"""
                                    <div class="result-fake">
                                    <h3>⚠️ DEEPFAKE DETECTED</h3>
                                    <p><strong>Classification:</strong> Fake Audio</p>
                                    <p><strong>Confidence:</strong> {confidence:.2%}</p>
                                    <p><strong>Fake Probability:</strong> {probability:.4f}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                    <div class="result-real">
                                    <h3>✅ AUTHENTIC AUDIO</h3>
                                    <p><strong>Classification:</strong> Real Audio</p>
                                    <p><strong>Confidence:</strong> {confidence:.2%}</p>
                                    <p><strong>Fake Probability:</strong> {probability:.4f}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            render_analysis(
                                "Audio analysis",
                                render_audio_analysis,
                                audio_bytes,
                                uploaded_file.name,
                            )

                            # Additional info
                            with st.expander("📋 Details"):
                                st.write(f"**File:** {uploaded_file.name}")
                                st.write(f"**File Size:** {uploaded_file.size / 1024:.2f} KB")
                                st.write(f"**Model Source:** {result.get('model_source', 'N/A')}")
                                if "extra" in result:
                                    st.json(result["extra"])
                                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

elif modality == "Video":
    with col1:
        st.subheader("🎥 Video Deepfake Detection")
        uploaded_file = st.file_uploader(
            "Upload a video file",
            type=["mp4", "avi", "mov", "mkv"],
            key="video_uploader"
        )
        
        if uploaded_file:
            st.video(uploaded_file)
            
            if st.button("🔍 Predict", key="video_predict"):
                with st.spinner("Analyzing video (this may take a moment)..."):
                    try:
                        from video_model.video_predict import predict_video_bytes
                        
                        video_bytes = uploaded_file.getvalue()
                        result = predict_video_bytes(video_bytes, uploaded_file.name)
                        
                        with col2:
                            st.subheader("📊 Prediction Result")
                            
                            # Extract results
                            is_fake = result.get("is_deepfake", False)
                            confidence = result.get("confidence", 0)
                            probability = result.get("probability_fake", 0)
                            
                            # Display result
                            if is_fake:
                                st.markdown(f"""
                                    <div class="result-fake">
                                    <h3>⚠️ DEEPFAKE DETECTED</h3>
                                    <p><strong>Classification:</strong> Fake Video</p>
                                    <p><strong>Confidence:</strong> {confidence:.2%}</p>
                                    <p><strong>Fake Probability:</strong> {probability:.4f}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                    <div class="result-real">
                                    <h3>✅ AUTHENTIC VIDEO</h3>
                                    <p><strong>Classification:</strong> Real Video</p>
                                    <p><strong>Confidence:</strong> {confidence:.2%}</p>
                                    <p><strong>Fake Probability:</strong> {probability:.4f}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            render_analysis(
                                "Video analysis",
                                render_video_analysis,
                                video_bytes,
                                uploaded_file.name,
                            )

                            # Additional info
                            with st.expander("📋 Details"):
                                st.write(f"**File:** {uploaded_file.name}")
                                st.write(f"**File Size:** {uploaded_file.size / 1024 / 1024:.2f} MB")
                                st.write(f"**Model Source:** {result.get('model_source', 'N/A')}")
                                if "extra" in result:
                                    extra = result["extra"].copy()
                                    if "frame_probabilities" in extra:
                                        extra["frame_probabilities"] = f"[{len(extra['frame_probabilities'])} frames]"
                                    st.json(extra)
                                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.9rem;">
    <p>🔬 Powered by TensorFlow & Keras</p>
    <p>Multimodal Deepfake Detection System v1.0</p>
</div>
""", unsafe_allow_html=True)
