import streamlit as st
import html

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Multimodal Deepfake Detection",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    /* =========================
       GLOBAL
       ========================= */

    .main {
        padding: 2rem;
    }

    h1 {
        font-weight: 800 !important;
    }

    h2, h3 {
        font-weight: 700 !important;
    }


    /* =========================
       BUTTON
       ========================= */

    .stButton > button {
        width: 100%;
        background-color: #FF6B6B;
        color: white;
        font-weight: 700;
        padding: 0.75rem;
        border-radius: 0.6rem;
        border: none;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background-color: #FF5252;
        color: white;
        transform: translateY(-1px);
    }


    /* =========================
       RESULT CARD
       ========================= */

    .result-card {
        border-radius: 18px;
        padding: 0;
        margin-top: 10px;
        overflow: hidden;
        background: #171922;
        border: 1px solid #303340;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    }


    /* =========================
       RESULT HEADER
       ========================= */

    .result-header {
        padding: 22px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
    }

    .result-header.real {
        background: linear-gradient(
            135deg,
            #123c2a,
            #195c3e
        );
        border-bottom: 1px solid #287a52;
    }

    .result-header.fake {
        background: linear-gradient(
            135deg,
            #4a171d,
            #721f29
        );
        border-bottom: 1px solid #a83240;
    }


    /* =========================
       STATUS
       ========================= */

    .result-status {
        display: flex;
        align-items: center;
        gap: 14px;
        min-width: 0;
    }

    .result-icon {
        width: 52px;
        height: 52px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255,255,255,0.12);
        font-size: 30px;
        flex-shrink: 0;
    }

    .result-title {
        font-size: 24px;
        font-weight: 800;
        color: white;
        margin: 0;
        line-height: 1.2;
    }

    .result-subtitle {
        color: #c9cdd5;
        font-size: 13px;
        margin-top: 6px;
        line-height: 1.4;
    }


    /* =========================
       CONFIDENCE
       ========================= */

    .confidence-box {
        text-align: right;
        flex-shrink: 0;
    }

    .confidence-value {
        font-size: 29px;
        font-weight: 800;
        color: white;
        line-height: 1;
    }

    .confidence-label {
        font-size: 11px;
        color: #c9cdd5;
        letter-spacing: 1px;
        margin-top: 5px;
    }


    /* =========================
       RESULT BODY
       ========================= */

    .result-body {
        padding: 22px 24px;
    }


    /* =========================
       METRICS
       ========================= */

    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        gap: 15px;
    }

    .metric-label {
        color: #aeb3bf;
        font-size: 14px;
    }

    .metric-value {
        color: white;
        font-weight: 700;
        font-size: 14px;
    }


    /* =========================
       PROGRESS BAR
       ========================= */

    .progress-bg {
        width: 100%;
        height: 9px;
        background: #30333d;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 22px;
    }

    .progress-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.4s ease;
    }

    .fake-progress {
        background: #ff5964;
    }

    .real-progress {
        background: #35c985;
    }


    /* =========================
       RISK BADGE
       ========================= */

    .risk-badge {
        display: inline-block;
        padding: 6px 13px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }

    .risk-low {
        background: #153d2c;
        color: #58dfa0;
        border: 1px solid #236b4a;
    }

    .risk-medium {
        background: #4b3b17;
        color: #ffd35a;
        border: 1px solid #796123;
    }

    .risk-high {
        background: #49191f;
        color: #ff7d87;
        border: 1px solid #85313b;
    }


    /* =========================
       DETAILS CARD
       ========================= */

    .details-card {
        margin-top: 18px;
        padding: 16px 20px;
        background: #1d2029;
        border-radius: 12px;
        border: 1px solid #303340;
    }

    .details-title {
        color: #e7e9ed;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .detail-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 20px;
        padding: 9px 0;
        border-bottom: 1px solid #2b2e38;
    }

    .detail-row:last-child {
        border-bottom: none;
    }

    .detail-label {
        color: #9298a6;
        font-size: 13px;
        flex-shrink: 0;
    }

    .detail-value {
        color: #e7e9ed;
        font-size: 13px;
        font-weight: 600;
        text-align: right;
        max-width: 70%;
        word-break: break-word;
    }


    /* =========================
       ANALYSIS INFO
       ========================= */

    .analysis-summary {
        margin-top: 16px;
        padding: 13px 15px;
        background: #20232d;
        border-radius: 10px;
        border-left: 3px solid #7c83fd;
        color: #c9cdd5;
        font-size: 13px;
        line-height: 1.5;
    }


    /* =========================
       MOBILE
       ========================= */

    @media (max-width: 768px) {

        .result-header {
            flex-direction: column;
            align-items: flex-start;
        }

        .confidence-box {
            text-align: left;
        }

        .detail-row {
            flex-direction: column;
            gap: 3px;
        }

        .detail-value {
            text-align: left;
            max-width: 100%;
        }

    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_risk_level(is_fake, probability):
    """
    Determine risk level from fake probability.
    """

    if not is_fake:
        return {
            "text": "LOW RISK",
            "class": "risk-low"
        }

    if probability >= 0.80:
        return {
            "text": "HIGH RISK",
            "class": "risk-high"
        }

    if probability >= 0.50:
        return {
            "text": "MEDIUM RISK",
            "class": "risk-medium"
        }

    return {
        "text": "LOW RISK",
        "class": "risk-low"
    }


def format_file_size(size_bytes, modality):
    """
    Format file size according to modality.
    """

    if modality == "Video":
        return f"{size_bytes / 1024 / 1024:.2f} MB"

    return f"{size_bytes / 1024:.2f} KB"


def display_prediction_result(result, uploaded_file, modality):
    """
    Display the redesigned prediction result panel.
    """

    # --------------------------------------------------------
    # Extract model results
    # --------------------------------------------------------

    is_fake = bool(result.get("is_deepfake", False))

    confidence = float(
        result.get("confidence", 0)
    )

    probability = float(
        result.get("probability_fake", 0)
    )

    # Prevent invalid values
    confidence = max(0.0, min(confidence, 1.0))
    probability = max(0.0, min(probability, 1.0))

    confidence_pct = confidence * 100
    fake_pct = probability * 100


    # --------------------------------------------------------
    # Escape file/model text for HTML safety
    # --------------------------------------------------------

    file_name = html.escape(
        str(uploaded_file.name)
    )

    model_source = html.escape(
        str(result.get("model_source", "N/A"))
    )


    # --------------------------------------------------------
    # Determine result appearance
    # --------------------------------------------------------

    if is_fake:

        icon = "⚠️"

        title = "DEEPFAKE DETECTED"

        subtitle = (
            f"AI analysis indicates this "
            f"{modality.lower()} is likely manipulated."
        )

        header_class = "fake"

        progress_class = "fake-progress"

    else:

        icon = "✓"

        title = f"AUTHENTIC {modality.upper()}"

        subtitle = (
            f"No significant deepfake indicators "
            f"were detected in this {modality.lower()}."
        )

        header_class = "real"

        progress_class = "real-progress"


    # --------------------------------------------------------
    # Risk
    # --------------------------------------------------------

    risk = get_risk_level(
        is_fake,
        probability
    )


    # --------------------------------------------------------
    # File size
    # --------------------------------------------------------

    size_text = format_file_size(
        uploaded_file.size,
        modality
    )


    # --------------------------------------------------------
    # Result card
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="result-card">

            <!-- HEADER -->

            <div class="result-header {header_class}">

                <div class="result-status">

                    <div class="result-icon">
                        {icon}
                    </div>

                    <div>

                        <div class="result-title">
                            {title}
                        </div>

                        <div class="result-subtitle">
                            {subtitle}
                        </div>

                    </div>

                </div>


                <div class="confidence-box">

                    <div class="confidence-value">
                        {confidence_pct:.1f}%
                    </div>

                    <div class="confidence-label">
                        CONFIDENCE
                    </div>

                </div>

            </div>


            <!-- BODY -->

            <div class="result-body">


                <!-- FAKE PROBABILITY -->

                <div class="metric-row">

                    <span class="metric-label">
                        Fake Probability
                    </span>

                    <span class="metric-value">
                        {fake_pct:.2f}%
                    </span>

                </div>


                <div class="progress-bg">

                    <div
                        class="progress-fill {progress_class}"
                        style="width: {fake_pct:.2f}%;">
                    </div>

                </div>


                <!-- RISK -->

                <div class="metric-row">

                    <span class="metric-label">
                        Risk Assessment
                    </span>

                    <span class="risk-badge {risk['class']}">
                        {risk['text']}
                    </span>

                </div>


                <!-- DETAILS -->

                <div class="details-card">

                    <div class="details-title">
                        📋 File & Model Information
                    </div>


                    <div class="detail-row">

                        <span class="detail-label">
                            File
                        </span>

                        <span class="detail-value">
                            {file_name}
                        </span>

                    </div>


                    <div class="detail-row">

                        <span class="detail-label">
                            File Size
                        </span>

                        <span class="detail-value">
                            {size_text}
                        </span>

                    </div>


                    <div class="detail-row">

                        <span class="detail-label">
                            Detection Type
                        </span>

                        <span class="detail-value">
                            {modality}
                        </span>

                    </div>


                    <div class="detail-row">

                        <span class="detail-label">
                            Model
                        </span>

                        <span class="detail-value">
                            {model_source}
                        </span>

                    </div>

                </div>


                <!-- SUMMARY -->

                <div class="analysis-summary">

                    <strong>Analysis:</strong>

                    {
                        "The model detected a high probability of manipulation."
                        if probability >= 0.80
                        else
                        "The model detected a moderate possibility of manipulation."
                        if probability >= 0.50
                        else
                        "The model found no strong evidence of deepfake manipulation."
                    }

                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # Advanced model information
    # --------------------------------------------------------

    if "extra" in result:

        with st.expander("🔬 Advanced Analysis"):

            extra = result["extra"]

            # Video frame probabilities can be huge,
            # so don't dump every frame into the UI.
            if isinstance(extra, dict):

                extra = extra.copy()

                if "frame_probabilities" in extra:

                    frame_probs = extra["frame_probabilities"]

                    if isinstance(frame_probs, (list, tuple)):

                        extra["frame_probabilities"] = (
                            f"[{len(frame_probs)} frames]"
                        )

            st.json(extra)


# ============================================================
# PAGE HEADER
# ============================================================

st.title("🎬 Multimodal Deepfake Detection")

st.markdown(
    "Detect deepfakes in images, audio, and videos "
    "using advanced neural networks"
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Settings")

st.sidebar.markdown("---")


modality = st.sidebar.radio(
    "Select Detection Type:",
    ["Image", "Audio", "Video"],
    index=0
)


st.sidebar.markdown("---")


st.sidebar.info(
    "💡 Upload a file and click 'Predict' "
    "to detect deepfakes"
)


# ============================================================
# MAIN COLUMNS
# ============================================================

col1, col2 = st.columns(
    [1, 1],
    gap="large"
)


# ============================================================
# IMAGE DETECTION
# ============================================================

if modality == "Image":

    with col1:

        st.subheader(
            "📸 Image Deepfake Detection"
        )


        uploaded_file = st.file_uploader(
            "Upload an image",
            type=[
                "jpg",
                "jpeg",
                "png",
                "bmp"
            ],
            key="image_uploader"
        )


        if uploaded_file:

            st.image(
                uploaded_file,
                use_container_width=True,
                caption="Uploaded Image"
            )


            if st.button(
                "🔍 Predict",
                key="image_predict"
            ):

                with st.spinner(
                    "Analyzing image..."
                ):

                    try:

                        from image_model.image_predict import (
                            predict_image_bytes
                        )


                        image_bytes = (
                            uploaded_file.read()
                        )


                        result = predict_image_bytes(
                            image_bytes,
                            uploaded_file.name
                        )


                        with col2:

                            st.subheader(
                                "📊 Prediction Result"
                            )


                            display_prediction_result(
                                result=result,
                                uploaded_file=uploaded_file,
                                modality="Image"
                            )


                    except Exception as e:

                        st.error(
                            f"❌ Error: {str(e)}"
                        )


# ============================================================
# AUDIO DETECTION
# ============================================================

elif modality == "Audio":

    with col1:

        st.subheader(
            "🎵 Audio Deepfake Detection"
        )


        uploaded_file = st.file_uploader(
            "Upload an audio file",
            type=[
                "wav",
                "mp3",
                "m4a",
                "flac"
            ],
            key="audio_uploader"
        )


        if uploaded_file:

            st.audio(
                uploaded_file
            )


            if st.button(
                "🔍 Predict",
                key="audio_predict"
            ):

                with st.spinner(
                    "Analyzing audio..."
                ):

                    try:

                        from audio_model.audio_predict import (
                            predict_audio_bytes
                        )


                        audio_bytes = (
                            uploaded_file.read()
                        )


                        result = predict_audio_bytes(
                            audio_bytes,
                            uploaded_file.name
                        )


                        with col2:

                            st.subheader(
                                "📊 Prediction Result"
                            )


                            display_prediction_result(
                                result=result,
                                uploaded_file=uploaded_file,
                                modality="Audio"
                            )


                    except Exception as e:

                        st.error(
                            f"❌ Error: {str(e)}"
                        )


# ============================================================
# VIDEO DETECTION
# ============================================================

elif modality == "Video":

    with col1:

        st.subheader(
            "🎥 Video Deepfake Detection"
        )


        uploaded_file = st.file_uploader(
            "Upload a video file",
            type=[
                "mp4",
                "avi",
                "mov",
                "mkv"
            ],
            key="video_uploader"
        )


        if uploaded_file:

            st.video(
                uploaded_file
            )


            if st.button(
                "🔍 Predict",
                key="video_predict"
            ):

                with st.spinner(
                    "Analyzing video "
                    "(this may take a moment)..."
                ):

                    try:

                        from video_model.video_predict import (
                            predict_video_bytes
                        )


                        video_bytes = (
                            uploaded_file.read()
                        )


                        result = predict_video_bytes(
                            video_bytes,
                            uploaded_file.name
                        )


                        with col2:

                            st.subheader(
                                "📊 Prediction Result"
                            )


                            display_prediction_result(
                                result=result,
                                uploaded_file=uploaded_file,
                                modality="Video"
                            )


                    except Exception as e:

                        st.error(
                            f"❌ Error: {str(e)}"
                        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align: center;
        color: #777;
        font-size: 0.85rem;
        padding: 10px;
    ">
        Multimodal Deepfake Detection System
    </div>
    """,
    unsafe_allow_html=True
)
