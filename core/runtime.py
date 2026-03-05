import cv2
import time

from core.config import AppConfig, DEFAULT_CONFIG
from core.face_detection import (
    create_face_detector,
    detect_first_face_bbox,
    expanded_bbox,
    extract_face_rgb,
)
from core.recording import (
    register_prediction_event,
    start_recording_session,
    stop_recording_session,
    write_recorded_frame,
)
from core.ui import draw_face_bbox, draw_prediction_overlay, draw_recording_badge


def _update_top_predictions(model_pipeline, frames_buffer, frame_count, seq_len, predict_every):
    # Solo predecimos cuando el buffer temporal esta completo y toca el intervalo.
    if len(frames_buffer) != seq_len or frame_count % predict_every != 0:
        return None
    result = model_pipeline.predict(frames_buffer)
    return result["top_emotions"]


def run_realtime_emotion(model_pipeline, seq_len: int = 10, predict_every: int = 20, config: AppConfig = DEFAULT_CONFIG):
    # Inicializa camara y detector de rostro.
    detector = create_face_detector(config)
    cap = cv2.VideoCapture(config.camera_index)

    frames_buffer = []
    frame_count = 0
    last_face = None

    current_emotion, current_conf = "...", 0.0
    second_emotion, second_conf = "...", 0.0

    is_recording = False
    recording_session = None
    last_loop_t = time.monotonic()
    loop_fps_ema = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # FPS medido del loop  para estimar un FPS real de grabacion mas estable.
        now_t = time.monotonic()
        dt = now_t - last_loop_t
        last_loop_t = now_t
        if dt > 0:
            inst_fps = 1.0 / dt
            loop_fps_ema = inst_fps if loop_fps_ema is None else (0.9 * loop_fps_ema + 0.1 * inst_fps)

        frame_count += 1
        bbox = detect_first_face_bbox(frame, detector)
        face_rgb = None

        if bbox:
            # Si hay rostro, lo recortamos y normalizamos para el modelo.
            bounds = expanded_bbox(frame.shape, bbox, config.face_scale)
            face_rgb = extract_face_rgb(frame, bounds, config.face_size)
            last_face = face_rgb
            draw_face_bbox(frame, bounds)
        elif last_face is not None:
            # Si se pierde un frame, usamos el ultimo rostro valido para mantener continuidad.
            face_rgb = last_face

        if face_rgb is not None:
            # Ventana temporal (secuencia) usada por el modelo.
            frames_buffer.append(face_rgb)
            if len(frames_buffer) > seq_len:
                frames_buffer.pop(0)

        top_emotions = _update_top_predictions(
            model_pipeline=model_pipeline,
            frames_buffer=frames_buffer,
            frame_count=frame_count,
            seq_len=seq_len,
            predict_every=predict_every,
        )

        if top_emotions:
            current_emotion = top_emotions[0]["emotion"]
            current_conf = top_emotions[0]["confidence"]
            second_emotion = top_emotions[1]["emotion"]
            second_conf = top_emotions[1]["confidence"]

        draw_prediction_overlay(frame, current_emotion, current_conf, second_emotion, second_conf)

        if is_recording:
            draw_recording_badge(frame)
            write_recorded_frame(recording_session, frame)
            if top_emotions:
                # Guardamos eventos sincronizados con la linea de tiempo del video.
                register_prediction_event(recording_session, top_emotions)

        cv2.imshow(config.window_name, frame)
        key = cv2.waitKey(1) & 0xFF

        if key in (ord("s"), ord("S")):
            if not is_recording:
                try:
                    # Inicia sesion de grabacion con metadatos para reportes.
                    recording_session = start_recording_session(cap, frame.shape, config, measured_fps=loop_fps_ema)
                    is_recording = True
                    print(f"Grabacion iniciada: {recording_session['dir']}")
                    print(f"FPS de grabacion aplicado: {recording_session['video_fps']:.2f}")
                except RuntimeError as err:
                    print(f"Error al iniciar grabacion: {err}")
            else:
                # Cierra recursos y genera reportes al finalizar.
                session_dir, video_path, technical_report_path, non_technical_report_path = stop_recording_session(
                    recording_session,
                    config,
                )
                is_recording = False
                recording_session = None
                print(f"Grabacion finalizada. Carpeta: {session_dir}")
                print(f"Video: {video_path}")
                print(f"Informe tecnico: {technical_report_path}")
                print(f"Informe no tecnico: {non_technical_report_path}")

        if key == ord("q"):
            break

    if is_recording and recording_session is not None:
        session_dir, video_path, technical_report_path, non_technical_report_path = stop_recording_session(
            recording_session,
            config,
        )
        print(f"Grabacion finalizada por salida. Carpeta: {session_dir}")
        print(f"Video: {video_path}")
        print(f"Informe tecnico: {technical_report_path}")
        print(f"Informe no tecnico: {non_technical_report_path}")

    cap.release()
    cv2.destroyAllWindows()
