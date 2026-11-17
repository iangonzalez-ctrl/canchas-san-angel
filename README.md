# Sistema de Reservas de Canchas Sintéticas

Backend para gestionar las reservas de **Canchas San Ángel** (3 canchas de fútbol 5 y 1 de fútbol 8): disponibilidad por hora, cancelaciones con reglas de negocio y lista de espera con notificación cuando se libera una hora.

## Estado del proyecto

En desarrollo. La lógica de negocio y la base de datos ya funcionan; la API web y la interfaz están en construcción.

**Implementado**
- Reserva de horas, con protección a nivel de base de datos contra reservas dobles (índice único parcial en SQLite).
- Cancelación permitida hasta 2 horas antes; si no, se rechaza.
- Marcado de inasistencia por el administrador y bloqueo del número de teléfono.
- Lista de espera por cancha y hora, y notificación a quienes esperan cuando se libera una hora (por ahora la notificación se imprime en consola).

**En desarrollo / planeado**
- API REST con FastAPI
- Pruebas automáticas con pytest
- Interfaz web con calendario de disponibilidad
- Notificaciones reales (correo y WhatsApp)
- Panel de administración, verificación de teléfono y puntos de fidelidad

## Tecnologías

- Python
- SQLite
- FastAPI y Uvicorn

## Estructura

```
├── main.py          # Servidor FastAPI
├── database.py      # Conexión y creación de tablas
├── servicios.py     # Lógica de negocio (reservar, cancelar, lista de espera)
├── prueba*.py       # Scripts de prueba manual
└── requirements.txt
```

## Cómo ejecutarlo (Windows, PowerShell)

```powershell
git clone https://github.com/TU-USUARIO/canchas-san-angel.git
cd canchas-san-angel
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python database.py
uvicorn main:app --reload
```

Luego abre `http://127.0.0.1:8000/docs`.

## Reglas de negocio

- Cada reserva dura 1 hora.
- No se puede reservar una hora pasada ni una cancha ya ocupada en esa hora.
- Se puede cancelar hasta 2 horas antes de la reserva.
- Quien no asiste sin cancelar queda bloqueado por número de teléfono.