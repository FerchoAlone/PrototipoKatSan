import cv2


def draw_prediction_overlay(frame, primary_emotion, primary_conf, secondary_emotion, secondary_conf):
    cv2.rectangle(frame, (10, 10), (420, 100), (0, 0, 0), -1)
    cv2.putText(
        frame,
        f"1) {primary_emotion} ({primary_conf:.2f})",
        (20, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2,
    )
    cv2.putText(
        frame,
        f"2) {secondary_emotion} ({secondary_conf:.2f})",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 200, 200),
        2,
    )


def draw_recording_badge(frame):
    cv2.circle(frame, (500, 28), 8, (0, 0, 255), -1)
    cv2.putText(
        frame,
        "REC",
        (520, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2,
    )


def draw_face_bbox(frame, bounds):
    cv2.rectangle(frame, bounds[:2], bounds[2:], (0, 255, 0), 2)
