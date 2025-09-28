import sqlite3
import os

DB_PATH = "animales.db"
TEMP_DIR = "temp"

def init_db():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS animales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            especie TEXT,
            ruta_imagen TEXT
        )
    ''')
    conn.commit()
    conn.close()

def guardar_animal(usuario_id, especie, ruta_imagen):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO animales (usuario_id, especie, ruta_imagen) VALUES (?, ?, ?)",
              (usuario_id, especie, ruta_imagen))
    conn.commit()
    conn.close()

def obtener_especies(usuario_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT especie FROM animales WHERE usuario_id = ?", (usuario_id,))
    especies = [row[0] for row in c.fetchall()]
    conn.close()
    return especies

def obtener_imagenes_por_especie(usuario_id, especie):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ruta_imagen FROM animales WHERE usuario_id = ? AND especie = ?", (usuario_id, especie))
    imagenes = [row[0] for row in c.fetchall()]
    conn.close()
    return imagenes
