# reconocimiento.py
import os
import cv2
import numpy as np
import face_recognition
from datetime import datetime
import database

# URL del stream del ESP32-CAM — editar según tu red
ESP32_STREAM_URL = "http://192.168.18.33:81/stream"

DATA_AUT = os.path.join("data", "autorizados")
DATA_INT = os.path.join("data", "intrusos")

AUTH_TOLERANCE = 0.5
INTRUSO_TOLERANCE = 0.6

known_face_encodings = []
known_face_names = []
intruso_encodings = []

# Flag global para controlar la cámara
camera_active = False

def embedding_to_hex(arr: np.ndarray) -> str:
    return arr.tobytes().hex()

def hex_to_embedding(hexstr: str) -> np.ndarray:
    return np.frombuffer(bytes.fromhex(hexstr), dtype=np.float64)

def load_autorizados_cache():
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = []
    rows = database.list_autorizados()
    for r in rows:
        nombre = r["nombre"]
        filename = r["filename"]
        hx = r["embedding_hex"]
        if hx:
            try:
                emb = hex_to_embedding(hx)
                known_face_encodings.append(emb)
                known_face_names.append(nombre)
                continue
            except Exception:
                pass
        path = os.path.join(DATA_AUT, filename)
        if os.path.exists(path):
            try:
                img = face_recognition.load_image_file(path)
                encs = face_recognition.face_encodings(img)
                if encs:
                    emb = np.array(encs[0], dtype=np.float64)
                    known_face_encodings.append(emb)
                    known_face_names.append(nombre)
                    try:
                        database.update_autorizado_embedding(r["id"], embedding_to_hex(emb))
                    except:
                        pass
            except:
                pass

def load_intrusos_cache():
    global intruso_encodings
    intruso_encodings = []
    rows = database.list_intrusos()
    for r in rows:
        hx = r["embedding_hex"]
        if hx:
            try:
                emb = hex_to_embedding(hx)
                intruso_encodings.append(emb)
            except:
                pass

def initialize_caches():
    os.makedirs(DATA_AUT, exist_ok=True)
    os.makedirs(DATA_INT, exist_ok=True)
    load_autorizados_cache()
    load_intrusos_cache()

def save_intruso_if_new(frame, enc):
    global intruso_encodings
    if intruso_encodings:
        try:
            dists = face_recognition.face_distance(intruso_encodings, enc)
            if any(d <= INTRUSO_TOLERANCE for d in dists):
                return None
        except Exception:
            pass
    fname = f"intruso_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    path = os.path.join(DATA_INT, fname)
    cv2.imwrite(path, frame)
    emb_hex = embedding_to_hex(np.array(enc, dtype=np.float64))
    try:
        database.add_intruso(fname, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), emb_hex)
    except Exception:
        pass
    intruso_encodings.append(np.array(enc, dtype=np.float64))
    return fname

def stop_camera():
    global camera_active
    camera_active = False

def gen_frames():
    global camera_active
    initialize_caches()

    cap = cv2.VideoCapture(ESP32_STREAM_URL)
    if not cap.isOpened():
        print(f"[reconocimiento] No se pudo abrir el stream: {ESP32_STREAM_URL}")
        return

    camera_active = True
    try:
        while camera_active:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("[reconocimiento] No se pudo leer frame del stream.")
                break

            # process
            small = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
            rgb_small = small[:, :, ::-1]
            face_locs = face_recognition.face_locations(rgb_small)
            face_encs = face_recognition.face_encodings(rgb_small, face_locs)

            for enc, loc in zip(face_encs, face_locs):
                name = None
                if known_face_encodings:
                    matches = face_recognition.compare_faces(known_face_encodings, enc, tolerance=AUTH_TOLERANCE)
                    if True in matches:
                        idx = matches.index(True)
                        name = known_face_names[idx]
                if name:
                    color = (0,255,0)
                    label = name
                else:
                    color = (0,0,255)
                    label = "Intruso"
                    save_intruso_if_new(frame, enc)

                top, right, bottom, left = loc
                top *= 2; right *= 2; bottom *= 2; left *= 2
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, label, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            ret2, buffer = cv2.imencode('.jpg', frame)
            if not ret2:
                continue
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        try:
            cap.release()
        except:
            pass
        camera_active = False