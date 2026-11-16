from concurrent import futures
import uuid
import grpc
import pagos_pb2
import pagos_pb2_grpc

class ValidadorPagosServicer(pagos_pb2_grpc.ValidadorPagosServicer):
    def VerificarTransaccion(self, request, context):
        print(f"[Servidor] Evaluando TX: {request.id_transaccion} | Monto: {request.monto} {request.codigo_moneda} | País: {request.pais_origen}")

        # Regla 1: Monto <= 0 o tarjeta no tiene 16 dígitos
        if request.monto <= 0 or len(request.numero_tarjeta) != 16 or not request.numero_tarjeta.isdigit():
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Monto o número de tarjeta inválido")
            return pagos_pb2.ResultadoPago()

        # Regla 2: Tarjeta inicia con "4000" (lista negra)
        if request.numero_tarjeta.startswith("4000"):
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details("Tarjeta bloqueada por fraude")
            return pagos_pb2.ResultadoPago()

        # Regla 3: Monto > 10,000 USD -> solo aprobar si pais_origen es "US" o "MX"
        if request.monto > 10000 and request.pais_origen.upper() not in ("US", "MX"):
            return pagos_pb2.ResultadoPago(
                aprobado=False,
                codigo_autorizacion="",
                motivo_rechazo="Rechazo por política de fraude: monto alto desde país no autorizado"
            )

        # Transacción aprobada
        codigo_auth = f"AUTH-{uuid.uuid4().hex[:8].upper()}"
        return pagos_pb2.ResultadoPago(
            aprobado=True,
            codigo_autorizacion=codigo_auth,
            motivo_rechazo=""
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pagos_pb2_grpc.add_ValidadorPagosServicer_to_server(ValidadorPagosServicer(), server)
    puerto = "50051"
    server.add_insecure_port(f"[::]:{puerto}")
    server.start()
    print(f"Servidor de Validación de Pagos escuchando en el puerto {puerto}...")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n[Servidor] Apagando servidor gRPC de forma segura...")
        server.stop(0)

if __name__ == "__main__":
    serve()