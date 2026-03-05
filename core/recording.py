import time
from datetime import datetime

import cv2

from core.config import AppConfig
from core.reporting import write_excel_report, write_non_technical_excel_report


def _camera_fps(cap, default_fps: float) -> float:
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps is None or fps <= 1.0:
        return default_fps
    return float(fps)


def _resolve_recording_fps(cap, default_fps: float, measured_fps: float | None = None) -> float:
    if measured_fps is not None and 1.0 < measured_fps <= 120.0:
        return float(measured_fps)
    return _camera_fps(cap, default_fps)


def start_recording_session(cap, frame_shape, config: AppConfig, measured_fps: float | None = None):
    start_dt = datetime.now()
    session_dir = config.recordings_root / start_dt.strftime("%Y%m%d_%H%M%S")
    session_dir.mkdir(parents=True, exist_ok=True)

    frame_h, frame_w, _ = frame_shape
    fps = _resolve_recording_fps(cap, config.default_camera_fps, measured_fps)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_path = session_dir / config.video_name
    writer = cv2.VideoWriter(str(video_path), fourcc, fps, (frame_w, frame_h))

    if not writer.isOpened():
        raise RuntimeError("No se pudo crear el archivo de video para la grabacion")

    return {
        "dir": session_dir,
        "video_path": video_path,
        "writer": writer,
        "video_fps": fps,
        "recorded_frames": 0,
        "started_at": start_dt,
        "start_monotonic": time.monotonic(),
        "events": [],
    }


def write_recorded_frame(session: dict, frame):
    session["writer"].write(frame)
    session["recorded_frames"] += 1


def register_prediction_event(session: dict, top_emotions):
    video_fps = session.get("video_fps", 0.0)
    recorded_frames = session.get("recorded_frames", 0)
    elapsed_s = (recorded_frames / video_fps) if video_fps > 0 else 0.0
    session["events"].append(
        {
            "elapsed_s": elapsed_s,
            "top_1": top_emotions[0]["emotion"],
            "top_1_conf": top_emotions[0]["confidence"],
            "top_2": top_emotions[1]["emotion"],
            "top_2_conf": top_emotions[1]["confidence"],
        }
    )


def stop_recording_session(session: dict, config: AppConfig):
    session["writer"].release()
    ended_at = datetime.now()
    technical_report_path = write_excel_report(
        session["dir"] / config.technical_report_name,
        session,
        ended_at,
    )
    non_technical_report_path = write_non_technical_excel_report(
        session["dir"] / config.non_technical_report_name,
        session,
        ended_at,
    )
    return session["dir"], session["video_path"], technical_report_path, non_technical_report_path
