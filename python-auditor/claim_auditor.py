#!/usr/bin/env python3
import json
import os
import time
import logging
from datetime import datetime
import pika

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Envía logs a la consola (visible en logs del contenedor)
    ]
)
logger = logging.getLogger('claim_auditor')

# Configuración de RabbitMQ
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')
CLAIMS_QUEUE = os.getenv('CLAIMS_QUEUE', 'claims_created_queue')
CLAIMS_UPDATED_QUEUE = os.getenv('CLAIMS_UPDATED_QUEUE', 'claims_updated_queue')

# Directorio para archivos de auditoría
AUDIT_DIR = os.getenv('AUDIT_DIR', '/app/audit_logs')
os.makedirs(AUDIT_DIR, exist_ok=True)

def connect_to_rabbitmq():
    """Establece conexión con RabbitMQ con reintentos"""
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    credentials=credentials,
                    heartbeat=600
                )
            )
            logger.info("Conexión establecida con RabbitMQ")
            return connection
        except Exception as e:
            retry_count += 1
            wait_time = 5 * retry_count
            logger.error(f"Error al conectar con RabbitMQ: {e}. Reintentando en {wait_time} segundos...")
            time.sleep(wait_time)
    
    raise Exception("No se pudo establecer conexión con RabbitMQ después de varios intentos")

def save_to_audit_file(claim_data, event_type):
    """Guarda los datos del reclamo en un archivo de auditoría estructurado"""
    try:
        # Crear nombre de archivo con fecha actual
        today = datetime.now().strftime('%Y-%m-%d')
        filename = f"{AUDIT_DIR}/claims_audit_{today}.jsonl"
        
        # Preparar entrada de auditoría
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "claim_id": claim_data.get("id", "unknown"),
            "claim_data": claim_data
        }
        
        # Escribir en archivo (modo append)
        with open(filename, 'a') as f:
            f.write(json.dumps(audit_entry) + '\n')
        
        logger.info(f"Reclamo {claim_data.get('id', 'unknown')} guardado en archivo de auditoría: {filename}")
        return True
    except Exception as e:
        logger.error(f"Error al guardar en archivo de auditoría: {e}")
        return False

def process_claim_message(ch, method, properties, body):
    """Procesa mensajes de reclamos desde RabbitMQ"""
    try:
        # Decodificar mensaje JSON
        claim_data = json.loads(body)
        claim_id = claim_data.get("id", "unknown")
        
        logger.info(f"Recibido reclamo {claim_id} para auditoría")
        
        # Guardar en archivo de auditoría
        if save_to_audit_file(claim_data, "CLAIM_CREATED"):
            # Confirmar procesamiento del mensaje
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Reclamo {claim_id} procesado correctamente")
        else:
            # Rechazar mensaje para reprocesamiento
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            logger.warning(f"Reclamo {claim_id} rechazado para reprocesamiento")
    
    except json.JSONDecodeError as e:
        logger.error(f"Error al decodificar mensaje JSON: {e}")
        # Rechazar mensaje inválido sin reprocesamiento
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    except Exception as e:
        logger.error(f"Error al procesar mensaje: {e}")
        # Rechazar mensaje con error para reprocesamiento
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def process_claim_update_message(ch, method, properties, body):
    """Procesa mensajes de actualización de reclamos desde RabbitMQ"""
    try:
        # Decodificar mensaje JSON
        claim_data = json.loads(body)
        claim_id = claim_data.get("id", "unknown")
        
        logger.info(f"Recibida actualización de reclamo {claim_id} para auditoría")
        
        # Guardar en archivo de auditoría
        if save_to_audit_file(claim_data, "CLAIM_UPDATED"):
            # Confirmar procesamiento del mensaje
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Actualización de reclamo {claim_id} procesada correctamente")
        else:
            # Rechazar mensaje para reprocesamiento
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            logger.warning(f"Actualización de reclamo {claim_id} rechazada para reprocesamiento")
    
    except json.JSONDecodeError as e:
        logger.error(f"Error al decodificar mensaje JSON: {e}")
        # Rechazar mensaje inválido sin reprocesamiento
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    except Exception as e:
        logger.error(f"Error al procesar mensaje de actualización: {e}")
        # Rechazar mensaje con error para reprocesamiento
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    """Función principal del servicio auditor"""
    logger.info("Iniciando servicio de auditoría de reclamos")
    
    while True:
        try:
            # Conectar a RabbitMQ
            connection = connect_to_rabbitmq()
            channel = connection.channel()
            
            # Declarar colas
            channel.queue_declare(queue=CLAIMS_QUEUE, durable=True)
            channel.queue_declare(queue=CLAIMS_UPDATED_QUEUE, durable=True)
            
            # Configurar consumo de mensajes (prefetch_count limita los mensajes procesados simultáneamente)
            channel.basic_qos(prefetch_count=1)
            
            # Configurar callbacks para procesar mensajes
            channel.basic_consume(queue=CLAIMS_QUEUE, on_message_callback=process_claim_message)
            channel.basic_consume(queue=CLAIMS_UPDATED_QUEUE, on_message_callback=process_claim_update_message)
            
            logger.info(f"Esperando mensajes de reclamos. Para salir presione CTRL+C")
            
            # Iniciar consumo de mensajes
            channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Servicio de auditoría detenido por el usuario")
            if 'connection' in locals() and connection.is_open:
                connection.close()
            break
            
        except Exception as e:
            logger.error(f"Error en el servicio de auditoría: {e}")
            logger.info("Reintentando conexión en 10 segundos...")
            time.sleep(10)

if __name__ == "__main__":
    main()
