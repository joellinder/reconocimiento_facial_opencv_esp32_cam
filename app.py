# app.py
import os
import base64
import cv2
import numpy as np
import face_recognition
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import database
import reconocimiento as rc

app = Flask(__name__, static_folder="static")
app.secret_key = "CAMBIAR_POR_ALGO_MUY_SEGURO"

# Ensure folders exist
os.makedirs(os.path.join("data","autorizados"), exist_ok=True)
os.makedirs(os.path.join("data","intrusos"), exist_ok=True)

# Init DB and caches
database.init_db()
rc.initialize_caches()

# --- Static file serving for images ---
@app.route("/data/autorizados/<filename>")
def serve_autorizado(filename):
    return send_from_directory(os.path.join("data","autorizados"), filename)

@app.route("/data/intrusos/<filename>")
def serve_intruso(filename):
    return send_from_directory(os.path.join("data","intrusos"), filename)

# --- Auth ---
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        user = database.get_user_by_username(username)
        if user and check_password_hash(user["password"], password):
            session["usuario"] = username
            session["is_admin"] = bool(user["is_admin"])
            session["user_id"] = user["id"]
            return redirect(url_for("index"))
        else:
            flash("Usuario o contraseña incorrectos", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- Dashboard ---
@app.route("/index")
def index():
    if "usuario" not in session:
        return redirect(url_for("login"))
    autorizados = database.list_autorizados()
    logo_exists = os.path.exists(os.path.join("static","logo-unmsm.png"))
    alarm_exists = os.path.exists(os.path.join("static","alarm.mp3"))
    return render_template("index.html", autorizados=autorizados, logo_exists=logo_exists, alarm_exists=alarm_exists)

# --- Transmisión y stream ---
@app.route("/transmision")
def transmision():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("transmision.html")

@app.route("/video_feed")
def video_feed():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return Response(rc.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/stop_video", methods=["POST"])
def stop_video():
    if "usuario" not in session:
        return jsonify({"ok": False, "msg":"No autenticado"}), 401
    rc.stop_camera()
    return jsonify({"ok": True, "msg":"Cámara detenida"})

# --- Captura autorizados ---
@app.route("/captura_autorizado")
def captura_autorizado():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("captura_autorizado.html")

@app.route("/registrar_autorizado", methods=["GET","POST"])
def registrar_autorizado():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        nombre = request.form.get("nombre","").strip()
        file = request.files.get("imagen")
        if not nombre or not file:
            flash("Nombre e imagen requeridos", "warning")
            return redirect(url_for("registrar_autorizado"))
        filename = secure_filename(f"{nombre}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
        path = os.path.join("data","autorizados", filename)
        file.save(path)
        # compute embedding
        emb_hex = None
        try:
            img = face_recognition.load_image_file(path)
            encs = face_recognition.face_encodings(img)
            if encs:
                emb_hex = np.array(encs[0], dtype=np.float64).tobytes().hex()
        except Exception:
            emb_hex = None
        database.add_autorizado(nombre, filename, emb_hex)
        rc.load_autorizados_cache()
        flash("Autorizado registrado", "success")
        return redirect(url_for("index"))
    return render_template("registrar_autorizado.html")

@app.route("/api/registrar_autorizado", methods=["POST"])
def api_registrar_autorizado():
    if "usuario" not in session:
        return jsonify({"ok": False, "msg":"No autenticado"}), 401
    data = request.get_json()
    nombre = data.get("nombre","").strip()
    image_b64 = data.get("image","")
    if not nombre or not image_b64:
        return jsonify({"ok": False, "msg":"Nombre e imagen requeridos"}), 400
    header, b64 = (image_b64.split(",",1) if "," in image_b64 else ("", image_b64))
    try:
        img_bytes = base64.b64decode(b64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception as e:
        return jsonify({"ok": False, "msg": f"Error procesando imagen: {e}"}), 400

    filename = secure_filename(f"{nombre}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
    path = os.path.join("data","autorizados", filename)
    cv2.imwrite(path, img)
    emb_hex = None
    try:
        encs = face_recognition.face_encodings(img[:, :, ::-1])
        if encs:
            emb_hex = np.array(encs[0], dtype=np.float64).tobytes().hex()
    except Exception:
        emb_hex = None

    database.add_autorizado(nombre, filename, emb_hex)
    rc.load_autorizados_cache()
    return jsonify({"ok": True, "msg":"Autorizado registrado"})

# --- Usuarios (admin area) ---
@app.route("/usuarios")
def usuarios():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if not session.get("is_admin"):
        flash("Acceso denegado: administrador requerido", "danger")
        return redirect(url_for("index"))
    users = database.list_users()
    return render_template("usuarios.html", usuarios=users)

@app.route("/usuarios/nuevo", methods=["GET","POST"])
def usuarios_nuevo():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if not session.get("is_admin"):
        flash("Acceso denegado", "danger")
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        is_admin = 1 if request.form.get("is_admin") == "on" else 0
        if not username or not password:
            flash("Usuario y contraseña requerados", "warning"); return redirect(url_for("usuarios_nuevo"))
        if database.get_user_by_username(username):
            flash("Usuario ya existe", "warning"); return redirect(url_for("usuarios_nuevo"))
        password_hash = generate_password_hash(password)
        database.add_user(username, password_hash, is_admin=is_admin)
        flash("Usuario creado", "success")
        return redirect(url_for("usuarios"))
    return render_template("usuarios_nuevo.html")

@app.route("/usuarios/editar/<int:uid>", methods=["GET","POST"])
def usuarios_editar(uid):
    if "usuario" not in session:
        return redirect(url_for("login"))
    if not session.get("is_admin"):
        flash("Acceso denegado", "danger"); return redirect(url_for("index"))
    user = database.get_user_by_id(uid)
    if not user:
        flash("Usuario no encontrado", "warning"); return redirect(url_for("usuarios"))
    if request.method == "POST":
        new_username = request.form.get("username","").strip()
        new_password = request.form.get("password","")
        is_admin = 1 if request.form.get("is_admin") == "on" else 0
        if not new_username:
            flash("El nombre de usuario no puede quedar vacío", "warning"); return redirect(url_for("usuarios_editar", uid=uid))
        # if username changed and already exists, block
        existing = database.get_user_by_username(new_username)
        if existing and existing["id"] != uid:
            flash("El nombre de usuario ya existe", "warning"); return redirect(url_for("usuarios_editar", uid=uid))
        pwd_hash = None
        if new_password:
            pwd_hash = generate_password_hash(new_password)
        # update
        database.update_user(uid, new_username=new_username, new_password_hash=pwd_hash, is_admin=is_admin)
        flash("Usuario actualizado", "success")
        return redirect(url_for("usuarios"))
    return render_template("usuarios_nuevo.html", edit=True, user=user)

@app.route("/usuarios/eliminar/<int:uid>", methods=["POST"])
def usuarios_eliminar(uid):
    if "usuario" not in session:
        return redirect(url_for("login"))
    if not session.get("is_admin"):
        flash("Acceso denegado", "danger"); return redirect(url_for("index"))
    current_user = database.get_user_by_username(session.get("usuario"))
    if current_user and current_user["id"] == uid:
        flash("No puedes eliminarte a ti mismo", "warning"); return redirect(url_for("usuarios"))
    database.delete_user(uid)
    flash("Usuario eliminado", "success")
    return redirect(url_for("usuarios"))

# --- Autorizados & Intrusos pages ---
@app.route("/autorizados")
def autorizados_page():
    if "usuario" not in session:
        return redirect(url_for("login"))
    rows = database.list_autorizados()
    return render_template("autorizados.html", autorizados=rows)

@app.route("/autorizados/eliminar/<int:aid>", methods=["POST"])
def autorizados_eliminar(aid):
    if "usuario" not in session:
        return redirect(url_for("login"))
    database.delete_autorizado(aid)
    rc.load_autorizados_cache()
    flash("Autorizado eliminado", "success")
    return redirect(url_for("autorizados_page"))

@app.route("/intrusos")
def intrusos_page():
    if "usuario" not in session:
        return redirect(url_for("login"))
    rows = database.list_intrusos()
    return render_template("reporte_intrusos.html", intrusos=rows)

@app.route("/intrusos/eliminar/<int:iid>", methods=["POST"])
def intrusos_eliminar(iid):
    if "usuario" not in session:
        return redirect(url_for("login"))
    database.delete_intruso(iid)
    rc.load_intrusos_cache()
    flash("Intruso eliminado", "success")
    return redirect(url_for("intrusos_page"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)