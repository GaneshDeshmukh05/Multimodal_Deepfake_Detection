import streamlit as st
import io
from pathlib import Path

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
        background-color: #D4EDDA;
        border-left: 5px solid #28A745;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .result-fake {
        background-color: #F8D7DA;
        border-left: 5px solid #DC3545;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

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
                        
                        image_bytes = uploaded_file.read()
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
                        
                        audio_bytes = uploaded_file.read()
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
                        
                        video_bytes = uploaded_file.read()
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
