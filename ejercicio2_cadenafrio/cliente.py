import grpc
import telemetria_pb2
import telemetria_pb2_grpc

ROJO_NEGRITA = "\033[1;31m"
VERDE = "\033[0;32m"
RESET = "\033[0m"

def monitorear_camion(stub, id_camion, intervalo):
    print(f"\n=== Suscribiendo al monitoreo de {id_camion} (cada {intervalo}s) ===")
    peticion = telemetria_pb2.SuscripcionCamion(
        id_camion=id_camion,
        intervalo_segundos=intervalo
    )

    try:
        for lectura in stub.TransmitirTelemetria(peticion):
            info = (
                f"[{lectura.timestamp}] {lectura.id_camion} | "
                f"Temp: {lectura.temperatura_celsius:.2f}°C | "
                f"GPS: ({lectura.latitud}, {lectura.longitud})"
            )

            if lectura.alerta_critica:
                print(f"{ROJO_NEGRITA}🚨 [ALERTA CRÍTICA - FUERA DE RANGO] {info}{RESET}")
            else:
                print(f"{VERDE}✅ [NORMAL]{RESET} {info}")

        print(f"--- Fin de la transmisión de {id_camion} ---")

    except grpc.RpcError as e:
        print(f"[Error gRPC] Código: {e.code()} | Detalle: {e.details()}")

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = telemetria_pb2_grpc.MonitorCadenaFrioStub(channel)

        # Prueba 1: Camión inexistente (StatusCode.NOT_FOUND)
        monitorear_camion(stub, "CAM-999", 1)

        # Prueba 2: Camión válido en streaming cada 1 segundo
        monitorear_camion(stub, "CAM-001", 1)

if __name__ == "__main__":
    run()