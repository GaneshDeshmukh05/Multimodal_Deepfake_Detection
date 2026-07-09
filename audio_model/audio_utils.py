from __future__ import annotations

import os
import tempfile

import numpy as np
import soundfile as sf
import tensorflow as tf

from config import AUDIO_CONFIG


def _temp_suffix(filename: str | None) -> str:
    if not filename:
        return ".wav"
    _, extension = os.path.splitext(filename)
    return extension or ".wav"


def load_audio_from_bytes(audio_bytes: bytes, filename: str | None = None) -> np.ndarray:
    with tempfile.NamedTemporaryFile(delete=False, suffix=_temp_suffix(filename)) as temp_file:
        temp_file.write(audio_bytes)
        temp_path = temp_file.name

    try:
        waveform, sample_rate = sf.read(temp_path, dtype="float32")
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    if waveform.size == 0:
        raise ValueError("Could not decode the uploaded audio.")

    if waveform.ndim > 1:
        waveform = np.mean(waveform, axis=1)

    if sample_rate != AUDIO_CONFIG.sample_rate:
        waveform = _resample_waveform(waveform, sample_rate, AUDIO_CONFIG.sample_rate)

    waveform = waveform.astype(np.float32)
    peak = float(np.max(np.abs(waveform)))
    if peak > 0.0:
        waveform = waveform / peak

    return waveform


def pad_or_trim_audio(waveform: np.ndarray) -> np.ndarray:
    if waveform.shape[0] < AUDIO_CONFIG.target_samples:
        pad_width = AUDIO_CONFIG.target_samples - waveform.shape[0]
        waveform = np.pad(waveform, (0, pad_width), mode="constant")
    else:
        waveform = waveform[: AUDIO_CONFIG.target_samples]
    return waveform.astype(np.float32)


def _resample_waveform(waveform: np.ndarray, original_rate: int, target_rate: int) -> np.ndarray:
    if original_rate == target_rate:
        return waveform.astype(np.float32)

    target_length = max(1, int(round(len(waveform) * float(target_rate) / float(original_rate))))
    original_positions = np.linspace(0.0, 1.0, num=len(waveform), endpoint=False)
    target_positions = np.linspace(0.0, 1.0, num=target_length, endpoint=False)
    return np.interp(target_positions, original_positions, waveform).astype(np.float32)


def extract_mfcc_batch(audio_bytes: bytes, filename: str | None = None) -> np.ndarray:
    waveform = pad_or_trim_audio(load_audio_from_bytes(audio_bytes, filename))
    waveform_tensor = tf.convert_to_tensor(waveform, dtype=tf.float32)
    stft = tf.signal.stft(
        waveform_tensor,
        frame_length=400,
        frame_step=160,
        fft_length=512,
        window_fn=tf.signal.hann_window,
    )
    spectrogram = tf.abs(stft) ** 2
    mel_weight_matrix = tf.signal.linear_to_mel_weight_matrix(
        num_mel_bins=64,
        num_spectrogram_bins=int(spectrogram.shape[-1]),
        sample_rate=AUDIO_CONFIG.sample_rate,
        lower_edge_hertz=20.0,
        upper_edge_hertz=AUDIO_CONFIG.sample_rate / 2.0,
    )
    mel_spectrogram = tf.matmul(spectrogram, mel_weight_matrix)
    log_mel_spectrogram = tf.math.log(mel_spectrogram + 1e-6)
    mfcc = tf.signal.mfccs_from_log_mel_spectrograms(log_mel_spectrogram)[..., : AUDIO_CONFIG.num_mfcc]
    mfcc = tf.transpose(mfcc).numpy().astype(np.float32)

    mean = float(np.mean(mfcc))
    std = float(np.std(mfcc))
    mfcc = (mfcc - mean) / (std + 1e-6)

    if mfcc.shape[1] < AUDIO_CONFIG.max_frames:
        pad_width = AUDIO_CONFIG.max_frames - mfcc.shape[1]
        mfcc = np.pad(mfcc, ((0, 0), (0, pad_width)), mode="constant")
    else:
        mfcc = mfcc[:, : AUDIO_CONFIG.max_frames]

    mfcc = mfcc[..., np.newaxis]
    return np.expand_dims(mfcc, axis=0).astype(np.float32)


def extract_legacy_log_mel_batch(audio_bytes: bytes, filename: str | None = None) -> np.ndarray:
    waveform = pad_or_trim_audio(load_audio_from_bytes(audio_bytes, filename))
    waveform_tensor = tf.convert_to_tensor(waveform, dtype=tf.float32)
    stft = tf.signal.stft(
        waveform_tensor,
        frame_length=2048,
        frame_step=512,
        fft_length=2048,
        window_fn=tf.signal.hann_window,
    )
    spectrogram = tf.abs(stft) ** 2
    mel_weight_matrix = tf.signal.linear_to_mel_weight_matrix(
        num_mel_bins=128,
        num_spectrogram_bins=int(spectrogram.shape[-1]),
        sample_rate=AUDIO_CONFIG.sample_rate,
        lower_edge_hertz=20.0,
        upper_edge_hertz=AUDIO_CONFIG.sample_rate / 2.0,
    )
    mel_spectrogram = tf.matmul(spectrogram, mel_weight_matrix)
    log_mel_spectrogram = tf.math.log(mel_spectrogram + 1e-6)
    log_mel = tf.transpose(log_mel_spectrogram).numpy().astype(np.float32)

    target_frames = 63
    if log_mel.shape[1] < target_frames:
        pad_width = target_frames - log_mel.shape[1]
        log_mel = np.pad(log_mel, ((0, 0), (0, pad_width)), mode="constant")
    else:
        log_mel = log_mel[:, :target_frames]

    log_mel = log_mel[..., np.newaxis]
    return np.expand_dims(log_mel, axis=0).astype(np.float32)
