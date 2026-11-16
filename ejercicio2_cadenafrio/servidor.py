from concurrent import futures
from datetime import datetime
import random
import time
import grpc
import telemetria_pb2
import telemetria_pb2_grpc

CAMIONES_REGISTRADOS = {"CAM-001", "CAM-002"}

class MonitorCadenaFrioServicer(telemetria_pb2_grpc.MonitorCadenaFrioServicer):
    def TransmitirTelemetria(self, request, context):
        print(f"[Servidor] Nueva suscripción para {request.id_camion} (cada {request.intervalo_segundos}s)")

        # Regla 1: Validar si el camión existe
        if request.id_camion not in CAMIONES_REGISTRADOS:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"El camión '{request.id_camion}' no está registrado en el sistema.")
            return

        intervalo = max(1, request.intervalo_segundos)
        lat = -0.1807
        lon = -78.4678

        for i in range(1, 11):
            if not context.is_active():
                print(f"[Servidor] Cliente desconectado de {request.id_camion}")
                break

            temperatura = round(random.uniform(1.0, 9.5), 2)
            lat = round(lat + random.uniform(-0.001, 0.001), 6)
            lon = round(lon + random.uniform(-0.001, 0.001), 6)
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Regla 3: Alerta crítica si T < 2.0°C o T > 8.0°C
            es_critica = temperatura < 2.0 or temperatura > 8.0

            print(f"[Servidor] Enviando lectura {i}/10 -> {request.id_camion}: {temperatura}°C | Alerta: {es_critica}")

            # Regla 2: Emitir cada mensaje mediante yield
            yield telemetria_pb2.LecturaSensor(
                id_camion=request.id_camion,
                temperatura_celsius=temperatura,
                latitud=lat,
                longitud=lon,
                timestamp=ahora,
                alerta_critica=es_critica
            )

            time.sleep(intervalo)

        print(f"[Servidor] Transmisión finalizada para {request.id_camion}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    telemetria_pb2_grpc.add_MonitorCadenaFrioServicer_to_server(
        MonitorCadenaFrioServicer(), server
    )
    puerto = "50051"
    server.add_insecure_port(f"[::]:{puerto}")
    server.start()
    print(f"Servidor Monitor Cadena de Frío escuchando en el puerto {puerto}...")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n[Servidor] Apagando servidor gRPC de forma segura...")
        server.stop(0)

if __name__ == "__main__":
    serve()