from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    model_path: str = "./model/detector.tflite"
    face_scale: float = 1.7
    face_size: tuple[int, int] = (224, 224)
    window_name: str = "Emotion Recognition"
    recordings_root: Path = Path("./recordings")
    video_name: str = "grabacion.mp4"
    technical_report_name: str = "informe_emociones_tecnico.xlsx"
    non_technical_report_name: str = "informe_emociones_no_tecnico.xlsx"
    camera_index: int = 0
    default_camera_fps: float = 20.0


DEFAULT_CONFIG = AppConfig()
