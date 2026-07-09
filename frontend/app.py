import requests
import streamlit as st


st.title("Multimodal Deepfake Detection")


def render_prediction(payload):
    label = payload.get("label", "UNKNOWN")
    confidence = payload.get("confidence")
    class_index = payload.get("class_index")
    raw_probabilities = payload.get("raw_probabilities", [])
    threshold = payload.get("threshold", 0.5)

    st.success(f"Prediction: {label}")

    if isinstance(confidence, (int, float)):
        st.write(f"Confidence: {confidence:.2%}")

    if isinstance(class_index, int):
        st.write(f"Class Index: {class_index}")

    if isinstance(raw_probabilities, list) and len(raw_probabilities) == 2:
        st.caption(
            "Raw probabilities "
            f"(REAL={raw_probabilities[0]:.4f}, FAKE={raw_probabilities[1]:.4f}, "
            f"threshold={threshold:.2f})"
        )

    st.json(payload)


option = st.selectbox("Select Model", ["Image", "Audio", "Video"])
file = st.file_uploader("Upload File")

if file and st.button("Predict"):
    if option == "Image":
        url = "http://image_model:8000/predict"
    elif option == "Audio":
        url = "http://audio_model:8000/predict"
    else:
        url = "http://video_model:8000/predict"

    try:
        response = requests.post(
            url,
            files={"file": (file.name, file.getvalue(), file.type or "application/octet-stream")},
            timeout=180,
        )
    except requests.RequestException as exc:
        st.error(f"Request failed: {exc}")
    else:
        try:
            payload = response.json()
        except ValueError:
            payload = {"detail": response.text or "Service returned an empty response."}

        if response.ok:
            render_prediction(payload)
        else:
            st.error(f"{option} service returned HTTP {response.status_code}")
            st.write(payload)
