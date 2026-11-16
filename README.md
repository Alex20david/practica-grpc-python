# Microservicios Distribuidos con gRPC y Protocol Buffers

Implementación práctica de comunicación remota de alto rendimiento utilizando **gRPC** sobre **HTTP/2** y serialización binaria mediante **Protocol Buffers (`proto3`)** en Python.

Desarrollado para la asignatura de **Sistemas Distribuidos** — *Universidad Politécnica Salesiana*.

## Arquitectura y Estructura del Repositorio

```text
Ejercicios_gRPC/
├── ejercicio1_pagos/           # Patrón Unario (Request / Response)
│   ├── pagos.proto             # Contrato de interfaz del servicio ValidadorPagos
│   ├── pagos_pb2.py            # Clases de mensajes generadas por protoc
│   ├── pagos_pb2_grpc.py       # Stubs y Servicers generados por protoc
│   ├── servidor.py             # Lógica de validación y reglas antifraude
│   └── cliente.py              # Batería de pruebas y manejo de grpc.RpcError
│
├── ejercicio2_cadenafrio/      # Patrón Server Streaming (1 Request -> N Responses)
│   ├── telemetria.proto        # Contrato del servicio MonitorCadenaFrio (stream)
│   ├── telemetria_pb2.py       # Clases de mensajes generadas por protoc
│   ├── telemetria_pb2_grpc.py  # Stubs y Servicers generados por protoc
│   ├── servidor.py             # Emisión continua de sensores mediante yield
│   └── cliente.py              # Suscriptor en tiempo real con alertas visuales
│
├── .gitignore                  # Exclusión de entorno virtual y archivos compilados
└── README.md                   # Documentación del proyecto
```
## Requisitos e Instalación

1. **Clonar el repositorio y entrar al directorio:**
   - `git clone <URL_DE_TU_REPOSITORIO>`
   - `cd Ejercicios_gRPC`

2. **Crear entorno virtual e instalar dependencias:**
   - `python3 -m venv venv`
   - `source venv/bin/activate`
   - `pip install grpcio grpcio-tools`

---

## Descripción de los Servicios

### 1. Validación de Pagos y Detección de Fraude (`ejercicio1_pagos`)
- **Patrón de comunicación:** Unario (`rpc VerificarTransaccion (SolicitudPago) returns (ResultadoPago)`).
- **Reglas implementadas en el servidor:**
  - **Validación de entrada:** Rechaza montos `<= 0` o tarjetas distintas a 16 dígitos numéricos retornando `StatusCode.INVALID_ARGUMENT`.
  - **Lista negra:** Bloquea tarjetas que inicien con `"4000"` retornando `StatusCode.PERMISSION_DENIED`.
  - **Política de montos altos:** Transacciones superiores a `$10,000 USD` fuera de `"US"` o `"MX"` son rechazadas a nivel de negocio (`aprobado = False`).
  - **Autorización:** Si cumple todas las validaciones, genera un identificador único (`AUTH-XXXXXXXX`).
- **Ejecución (en dos terminales con `venv` activo):**
  - Terminal 1: `cd ejercicio1_pagos && python3 servidor.py`
  - Terminal 2: `cd ejercicio1_pagos && python3 cliente.py`

---

### 2. Monitoreo de Telemetría IoT y Cadena de Frío (`ejercicio2_cadenafrio`)
- **Patrón de comunicación:** Server Streaming (`rpc TransmitirTelemetria (SuscripcionCamion) returns (stream LecturaSensor)`).
- **Reglas implementadas en el servidor:**
  - **Validación de flota:** Verifica que el `id_camion` exista en el registro (`CAM-001`, `CAM-002`); de lo contrario aborta con `StatusCode.NOT_FOUND`.
  - **Transmisión continua:** Emite lecturas periódicas de temperatura y coordenadas GPS utilizando generadores (`yield`) sobre una única conexión HTTP/2 persistente.
  - **Detección de anomalías:** Activa `alerta_critica = True` cuando la temperatura sale del rango operativo seguro (`< 2.0 °C` o `> 8.0 °C`).
- **Ejecución (en dos terminales con `venv` activo):**
  - Terminal 1: `cd ejercicio2_cadenafrio && python3 servidor.py`
  - Terminal 2: `cd ejercicio2_cadenafrio && python3 cliente.py`

---

## Recompilación de Contratos `.proto` (Opcional)

En caso de modificar los archivos `.proto`, regenerar el código Python con:
- **Ejercicio 1:** `python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. pagos.proto`
- **Ejercicio 2:** `python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. telemetria.proto`

---

## Autor
- **Alex David Chacha Guashpa** — Ingeniería en Ciencias de la Computación (UPS)
