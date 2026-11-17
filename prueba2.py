from datetime import datetime, timedelta
from servicios import (
    reservar, cancelar_reserva, marcar_no_asistio, esta_baneado, FORMATO
)
from database import conectar

# Limpiar datos de prueba (solo para desarrollo)
con = conectar()
for tabla in ("reservas", "usuarios", "numeros_baneados"):
    con.execute(f"DELETE FROM {tabla}")
con.commit()

ahora = datetime.now()
manana = (ahora + timedelta(days=1)).replace(minute=0, second=0, microsecond=0)
en_una_hora = (ahora + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

# 1. Cancelar con tiempo (mañana): debe funcionar
id1 = reservar("Ian", "3001111111", 1, manana.strftime(FORMATO))
print("1. Cancelada con tiempo:", cancelar_reserva(id1, "3001111111"))

# 2. Cancelar tarde (en menos de 2 horas): debe fallar
id2 = reservar("Ana", "3002222222", 2, en_una_hora.strftime(FORMATO))
try:
    cancelar_reserva(id2, "3002222222")
except ValueError as e:
    print("2. Error esperado:", e)

# 3. Cancelar la reserva de otra persona: debe fallar
try:
    cancelar_reserva(id2, "3009999999")
except ValueError as e:
    print("3. Error esperado:", e)

# 4. No-show: creamos una reserva que ya empezó (directo en la base)
con.execute("INSERT INTO usuarios (nombre, telefono) VALUES ('Luis', '3005555555')")
usuario_id = con.execute(
    "SELECT id FROM usuarios WHERE telefono = '3005555555'"
).fetchone()["id"]
hace_una_hora = (ahora - timedelta(hours=1)).strftime(FORMATO)
cursor = con.execute(
    "INSERT INTO reservas (cancha_id, usuario_id, inicio, fin) VALUES (3, ?, ?, ?)",
    (usuario_id, hace_una_hora, ahora.strftime(FORMATO)),
)
con.commit()
con.close()

marcar_no_asistio(cursor.lastrowid)
print("4. ¿Luis está baneado?", esta_baneado("3005555555"))

# 5. Un número baneado no puede reservar
try:
    reservar("Luis", "3005555555", 1, manana.strftime(FORMATO))
except ValueError as e:
    print("5. Error esperado:", e)