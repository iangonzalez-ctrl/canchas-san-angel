import sqlite3

def conectar():
    conexion = sqlite3.connect("canchas.db")
    conexion.row_factory = sqlite3.Row
    return conexion

def crear_tablas():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS canchas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL UNIQUE,
            correo TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cancha_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            inicio TEXT NOT NULL,
            fin TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'activa',
            FOREIGN KEY (cancha_id) REFERENCES canchas(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS una_reserva_activa_por_hora
        ON reservas(cancha_id, inicio)
        WHERE estado = 'activa'
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lista_espera (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            cancha_id INTEGER NOT NULL,
            inicio TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (cancha_id) REFERENCES canchas(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS numeros_baneados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telefono TEXT NOT NULL UNIQUE,
            motivo TEXT,
            fecha_ban TEXT NOT NULL
        )
    """)

    # Cargar las 4 canchas de San Ángel solo si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM canchas")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO canchas (nombre, tipo) VALUES (?, ?)",
            [
                ("Cancha 1", "f5"),
                ("Cancha 2", "f5"),
                ("Cancha 3", "f5"),
                ("Cancha 4", "f8"),
            ],
        )

    conexion.commit()
    conexion.close()

if __name__ == "__main__":
    crear_tablas()
    print("Base de datos creada correctamente")