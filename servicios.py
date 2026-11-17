import sqlite3
from datetime import datetime, timedelta
from database import conectar

FORMATO = "%Y-%m-%d %H:%M"
DURACION = timedelta(hours=1)


def esta_baneado(telefono):
    conexion = conectar()
    fila = conexion.execute(
        "SELECT 1 FROM numeros_baneados WHERE telefono = ?", (telefono,)
    ).fetchone()
    conexion.close()
    return fila is not None


def obtener_o_crear_usuario(conexion, nombre, telefono):
    fila = conexion.execute(
        "SELECT id FROM usuarios WHERE telefono = ?", (telefono,)
    ).fetchone()
    if fila:
        return fila["id"]
    cursor = conexion.execute(
        "INSERT INTO usuarios (nombre, telefono) VALUES (?, ?)", (nombre, telefono)
    )
    return cursor.lastrowid


def reservar(nombre, telefono, cancha_id, inicio_texto):
    if esta_baneado(telefono):
        raise ValueError("Este número está bloqueado")

    inicio = datetime.strptime(inicio_texto, FORMATO)
    if inicio <= datetime.now():
        raise ValueError("No se puede reservar en el pasado")
    fin = inicio + DURACION

    conexion = conectar()
    try:
        cancha = conexion.execute(
            "SELECT id FROM canchas WHERE id = ?", (cancha_id,)
        ).fetchone()
        if cancha is None:
            raise ValueError("La cancha no existe")

        usuario_id = obtener_o_crear_usuario(conexion, nombre, telefono)
        cursor = conexion.execute(
            "INSERT INTO reservas (cancha_id, usuario_id, inicio, fin) VALUES (?, ?, ?, ?)",
            (cancha_id, usuario_id, inicio.strftime(FORMATO), fin.strftime(FORMATO)),
        )
        conexion.execute(
            "DELETE FROM lista_espera WHERE usuario_id = ? AND cancha_id = ? AND inicio = ?",
            (usuario_id, cancha_id, inicio.strftime(FORMATO)),
        )
        conexion.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        conexion.rollback()
        raise ValueError("Esa hora ya está reservada")
    finally:
        conexion.close()

LIMITE_CANCELACION = timedelta(hours=2)


def cancelar_reserva(reserva_id, telefono):
    conexion = conectar()
    try:
        reserva = conexion.execute(
            """
            SELECT r.id, r.cancha_id, r.inicio, r.estado
            FROM reservas r
            JOIN usuarios u ON u.id = r.usuario_id
            WHERE r.id = ? AND u.telefono = ?
            """,
            (reserva_id, telefono),
        ).fetchone()

        if reserva is None:
            raise ValueError("Reserva no encontrada")
        if reserva["estado"] != "activa":
            raise ValueError("Esta reserva ya no está activa")

        inicio = datetime.strptime(reserva["inicio"], FORMATO)
        if inicio - datetime.now() < LIMITE_CANCELACION:
            raise ValueError("Solo se puede cancelar hasta 2 horas antes")

        conexion.execute(
            "UPDATE reservas SET estado = 'cancelada' WHERE id = ?", (reserva_id,)
        )
        conexion.commit()
        notificar_lista_espera(reserva["cancha_id"], reserva["inicio"])
        return {"cancha_id": reserva["cancha_id"], "inicio": reserva["inicio"]}
    finally:
        conexion.close()


def marcar_no_asistio(reserva_id):
    conexion = conectar()
    try:
        reserva = conexion.execute(
            """
            SELECT r.estado, r.inicio, u.telefono
            FROM reservas r
            JOIN usuarios u ON u.id = r.usuario_id
            WHERE r.id = ?
            """,
            (reserva_id,),
        ).fetchone()

        if reserva is None:
            raise ValueError("Reserva no encontrada")
        if reserva["estado"] != "activa":
            raise ValueError("Esta reserva ya no está activa")
        if datetime.strptime(reserva["inicio"], FORMATO) > datetime.now():
            raise ValueError("La reserva aún no ha empezado")

        conexion.execute(
            "UPDATE reservas SET estado = 'no_asistio' WHERE id = ?", (reserva_id,)
        )
        conexion.execute(
            "INSERT OR IGNORE INTO numeros_baneados (telefono, motivo, fecha_ban) VALUES (?, ?, ?)",
            (
                reserva["telefono"],
                "No asistió sin cancelar",
                datetime.now().strftime(FORMATO),
            ),
        )
        conexion.commit()
    finally:
        conexion.close()

def enviar_notificacion(telefono, mensaje):
    # Por ahora solo imprime. Más adelante: correo o WhatsApp.
    print(f"[NOTIFICACIÓN a {telefono}] {mensaje}")


def unirse_lista_espera(nombre, telefono, cancha_id, inicio_texto):
    if esta_baneado(telefono):
        raise ValueError("Este número está bloqueado")

    inicio = datetime.strptime(inicio_texto, FORMATO)
    if inicio <= datetime.now():
        raise ValueError("Esa hora ya pasó")
    inicio_texto = inicio.strftime(FORMATO)

    conexion = conectar()
    try:
        ocupada = conexion.execute(
            "SELECT 1 FROM reservas WHERE cancha_id = ? AND inicio = ? AND estado = 'activa'",
            (cancha_id, inicio_texto),
        ).fetchone()
        if ocupada is None:
            raise ValueError("Esa hora está libre, puedes reservarla directamente")

        usuario_id = obtener_o_crear_usuario(conexion, nombre, telefono)

        ya_esta = conexion.execute(
            "SELECT 1 FROM lista_espera WHERE usuario_id = ? AND cancha_id = ? AND inicio = ?",
            (usuario_id, cancha_id, inicio_texto),
        ).fetchone()
        if ya_esta:
            raise ValueError("Ya estás en la lista de espera para esa hora")

        conexion.execute(
            "INSERT INTO lista_espera (usuario_id, cancha_id, inicio) VALUES (?, ?, ?)",
            (usuario_id, cancha_id, inicio_texto),
        )
        conexion.commit()
    finally:
        conexion.close()


def notificar_lista_espera(cancha_id, inicio_texto):
    conexion = conectar()
    esperando = conexion.execute(
        """
        SELECT u.nombre, u.telefono, c.nombre AS cancha
        FROM lista_espera l
        JOIN usuarios u ON u.id = l.usuario_id
        JOIN canchas c ON c.id = l.cancha_id
        WHERE l.cancha_id = ? AND l.inicio = ?
        ORDER BY l.id
        """,
        (cancha_id, inicio_texto),
    ).fetchall()
    conexion.close()

    for persona in esperando:
        enviar_notificacion(
            persona["telefono"],
            f"Hola {persona['nombre']}, se liberó la {persona['cancha']} "
            f"el {inicio_texto}. Reserva ya antes de que te la ganen.",
        )
    return len(esperando)