import grpc
import pagos_pb2
import pagos_pb2_grpc

def probar_transaccion(stub, solicitud):
    print(f"\n--- Enviando {solicitud.id_transaccion} ---")
    try:
        respuesta = stub.VerificarTransaccion(solicitud)
        if respuesta.aprobado:
            print(f"[APROBADO] Código de autorización: {respuesta.codigo_autorizacion}")
        else:
            print(f"[RECHAZADO] Motivo: {respuesta.motivo_rechazo}")
    except grpc.RpcError as e:
        print(f"[Error gRPC] Código: {e.code()} | Detalle: {e.details()}")

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = pagos_pb2_grpc.ValidadorPagosStub(channel)

        # Caso 1: Pago exitoso
        tx_exitosa = pagos_pb2.SolicitudPago(
            id_transaccion="TX-001",
            numero_tarjeta="4532123456789012",
            monto=250.75,
            codigo_moneda="USD",
            pais_origen="EC"
        )

        # Caso 2: Argumento inválido (monto negativo)
        tx_invalida = pagos_pb2.SolicitudPago(
            id_transaccion="TX-002",
            numero_tarjeta="4532123456789012",
            monto=-50.00,
            codigo_moneda="USD",
            pais_origen="EC"
        )

        # Caso 3: Tarjeta denegada (inicia con 4000)
        tx_fraude = pagos_pb2.SolicitudPago(
            id_transaccion="TX-003",
            numero_tarjeta="4000123456789012",
            monto=120.00,
            codigo_moneda="USD",
            pais_origen="US"
        )

        # Caso 4: Monto > 10,000 desde país distinto a US/MX
        tx_monto_alto = pagos_pb2.SolicitudPago(
            id_transaccion="TX-004",
            numero_tarjeta="4532123456789012",
            monto=15000.00,
            codigo_moneda="USD",
            pais_origen="EC"
        )

        probar_transaccion(stub, tx_exitosa)
        probar_transaccion(stub, tx_invalida)
        probar_transaccion(stub, tx_fraude)
        probar_transaccion(stub, tx_monto_alto)

if __name__ == "__main__":
    run()