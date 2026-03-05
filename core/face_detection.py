import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from core.config import AppConfig


def create_face_detector(config: AppConfig) -> vision.FaceDetector:
    base_options = python.BaseOptions(model_asset_path=config.model_path)
    options = vision.FaceDetectorOptions(base_options=base_options)
    return vision.FaceDetector.create_from_options(options)


def detect_first_face_bbox(frame, detector: vision.FaceDetector):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    results = detector.detect(image)
    if not results.detections:
        return None
    return results.detections[0].bounding_box


def expanded_bbox(frame_shape, bbox, scale: float):
    frame_h, frame_w, _ = frame_shape

    x1 = int(bbox.origin_x)
    y1 = int(bbox.origin_y)
    bw = int(bbox.width)
    bh = int(bbox.height)

    cx = x1 + bw // 2
    cy = y1 + bh // 2
    new_w = int(bw * scale)
    new_h = int(bh * scale)

    x1 = max(0, cx - new_w // 2)
    y1 = max(0, cy - new_h // 2)
    x2 = min(frame_w, x1 + new_w)
    y2 = min(frame_h, y1 + new_h)
    return x1, y1, x2, y2


def extract_face_rgb(frame, bounds, face_size: tuple[int, int]):
    x1, y1, x2, y2 = bounds
    face = frame[y1:y2, x1:x2]
    face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    return cv2.resize(face, face_size)
