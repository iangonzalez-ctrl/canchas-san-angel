from servicios import reservar

fecha = "2026-11-10 19:00"

print("Reserva 1:", reservar("Ian", "3001234567", 1, fecha))

try:
    reservar("Pedro", "3009999999", 1, fecha)
except ValueError as e:
    print("Error esperado:", e)

print("Reserva 2:", reservar("Pedro", "3009999999", 2, fecha))