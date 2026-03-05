from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import joblib
import numpy as np
import tensorflow as tf
from keras.models import load_model

from emotion_map import inv_emotion_map


MODEL_DIR = Path("./model")
MOBNET_V2_PATH = MODEL_DIR / "MobileNetV2LSTM.keras"
MOBNET_V3_PATH = MODEL_DIR / "MobileNetV3LargeLSTM.keras"
META_MODEL_PATH = MODEL_DIR / "meta_model_xgboost.pkl"


class EmotionEnsemblePipeline:
    def __init__(self, mobnetv2_path, mobnetv3_path, meta_model_path, seq_len: int = 10):
        self.seq_len = seq_len

        self.mobnetv2 = load_model(mobnetv2_path, compile=False)
        self.mobnetv3 = load_model(mobnetv3_path, compile=False)
        self.mobnetv2.trainable = False
        self.mobnetv3.trainable = False

        self.mobnetv2_tf = tf.function(lambda x: self.mobnetv2(x, training=False), reduce_retracing=True)
        self.mobnetv3_tf = tf.function(lambda x: self.mobnetv3(x, training=False), reduce_retracing=True)

        self.meta_model = joblib.load(meta_model_path)
        self._warmup_models()

    def _warmup_models(self):
        dummy = tf.zeros((1, self.seq_len, 224, 224, 3), dtype=tf.float32)
        _ = self.mobnetv2_tf(dummy)
        _ = self.mobnetv3_tf(dummy)

    def _force_seq_len(self, frames):
        if not frames:
            raise ValueError("Se requiere al menos 1 frame para predecir emociones")

        normalized = list(frames)
        if len(normalized) < self.seq_len:
            normalized.extend([normalized[-1]] * (self.seq_len - len(normalized)))
        elif len(normalized) > self.seq_len:
            normalized = normalized[: self.seq_len]
        return normalized

    def _prepare_sequence(self, frames):
        sequence = self._force_seq_len(frames)
        sequence = np.asarray(sequence, dtype=np.float32)
        sequence /= 255.0
        return tf.convert_to_tensor(sequence[None, ...], dtype=tf.float32)

    def _extract_meta_features(self, sequence_tensor):
        def predict_v2():
            return self.mobnetv2_tf(sequence_tensor)[0].numpy()

        def predict_v3():
            return self.mobnetv3_tf(sequence_tensor)[0].numpy()

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_v2 = executor.submit(predict_v2)
            future_v3 = executor.submit(predict_v3)
            p_v2 = future_v2.result()
            p_v3 = future_v3.result()

        return np.concatenate([p_v2, p_v3]).reshape(1, -1)

    def predict(self, frames):
        sequence_tensor = self._prepare_sequence(frames)
        meta_features = self._extract_meta_features(sequence_tensor)
        probs = self.meta_model.predict_proba(meta_features)[0]

        top2_idx = np.argsort(probs)[-2:][::-1]
        top2 = [
            {"emotion": inv_emotion_map[i], "confidence": float(probs[i])}
            for i in top2_idx
        ]

        return {
            "top_emotions": top2,
            "predicted_emotion": top2[0]["emotion"],
            "confidence": top2[0]["confidence"],
            "all_probabilities": {inv_emotion_map[i]: float(probs[i]) for i in range(len(probs))},
        }


pipeline = EmotionEnsemblePipeline(
    mobnetv2_path=str(MOBNET_V2_PATH),
    mobnetv3_path=str(MOBNET_V3_PATH),
    meta_model_path=str(META_MODEL_PATH),
)
