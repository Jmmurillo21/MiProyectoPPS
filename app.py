from flask import Flask, request, jsonify, session
import mysql.connector
import bcrypt
import os

app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura"

# =======================
# Conexión a MySQL con variables de entorno
# =======================
db_host = os.environ.get("DB_HOST", "localhost")
db_user = os.environ.get("DB_USER", "root")
db_pass = os.environ.get("DB_PASSWORD", "root")
db_name = os.environ.get("DB_NAME", "mi_app_passwords")

# Conectar al servidor MySQL sin base de datos
db = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_pass
)
cursor = db.cursor(dictionary=True)

# Crear base de datos si no existe
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
cursor.execute(f"USE {db_name}")

# Crear tabla usuarios si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    contraseña VARCHAR(255) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
db.commit()

# Reconectar usando la base de datos creada
db = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_pass,
    database=db_name
)
cursor = db.cursor(dictionary=True)

# =======================
# Ruta de registro
# =======================
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    nombre = data.get("name")
    correo = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")

    if password != confirm_password:
        return jsonify({"error": "Las contraseñas no coinciden"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        sql = "INSERT INTO usuarios (nombre_completo, correo, contraseña) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nombre, correo, hashed_password))
        db.commit()
        return jsonify({"message": "Usuario registrado correctamente"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400

# =======================
# Ruta de login
# =======================
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    correo = data.get("username")
    password = data.get("password")

    cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['contraseña'].encode('utf-8')):
        session['user'] = user['nombre_completo']
        return jsonify({"message": f"Bienvenido {user['nombre_completo']}"}), 200
    else:
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

# =======================
# Ruta para ver todos los usuarios
# =======================
@app.route("/api/users", methods=["GET"])
def get_users():
    cursor.execute("SELECT id, nombre_completo, correo, fecha_creacion FROM usuarios")
    users = cursor.fetchall()
    return jsonify(users), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
