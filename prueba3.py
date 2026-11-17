from datetime import datetime, timedelta
from servicios import (
    reservar, cancelar_reserva, unirse_lista_espera, FORMATO
)
from database import conectar

# Limpiar datos de prueba (solo para desarrollo)
con = conectar()
for tabla in ("lista_espera", "reservas", "usuarios", "numeros_baneados"):
    con.execute(f"DELETE FROM {tabla}")
con.commit()

manana = (datetime.now() + timedelta(days=1)).replace(
    hour=19, minute=0, second=0, microsecond=0
)
hora = manana.strftime(FORMATO)

# Ian reserva la cancha 1
id_ian = reservar("Ian", "3001111111", 1, hora)
print("1. Ian reservó:", id_ian)

# Ana y Pedro quieren esa misma hora
unirse_lista_espera("Ana", "3002222222", 1, hora)
unirse_lista_espera("Pedro", "3003333333", 1, hora)
print("2. Ana y Pedro en lista de espera")

# Ana intenta unirse otra vez: debe fallar
try:
    unirse_lista_espera("Ana", "3002222222", 1, hora)
except ValueError as e:
    print("3. Error esperado:", e)

# Unirse a una hora libre: debe fallar
try:
    unirse_lista_espera("Ana", "3002222222", 2, hora)
except ValueError as e:
    print("4. Error esperado:", e)

# Ian cancela: deben salir 2 notificaciones
print("5. Ian cancela...")
cancelar_reserva(id_ian, "3001111111")

# Pedro reserva primero, Ana llega tarde
print("6. Pedro reservó:", reservar("Pedro", "3003333333", 1, hora))
try:
    reservar("Ana", "3002222222", 1, hora)
except ValueError as e:
    print("7. Error esperado (Ana llegó tarde):", e)

# Quién sigue en la lista
quedan = con.execute(
    "SELECT u.nombre FROM lista_espera l JOIN usuarios u ON u.id = l.usuario_id"
).fetchall()
print("8. Siguen esperando:", [f["nombre"] for f in quedan])
con.close()