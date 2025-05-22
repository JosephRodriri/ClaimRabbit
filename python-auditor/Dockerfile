# Usa una imagen base de Python ligera
FROM python:3.9-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY claim_auditor.py .

# Crear directorio para logs de auditoría
RUN mkdir -p /app/audit_logs

# Establecer permisos (chmod +x no es estrictamente necesario para un script python)
# RUN chmod +x claim_auditor.py

# Ejecutar como usuario no root (Buenas prácticas de seguridad, mantenlo)
RUN useradd -m auditor
RUN chown -R auditor:auditor /app
USER auditor

# --- ¡AÑADE ESTAS LÍNEAS! ---
# Define las variables de entorno que el script Python leerá
# Estos valores por defecto serán usados si no se sobrescriben en docker-compose.yml
# Para un entorno de Docker Compose, 'rabbitmq' será el nombre del servicio de RabbitMQ
ENV RABBITMQ_HOST=rabbitmq
ENV RABBITMQ_PORT=5672
ENV RABBITMQ_USER=guest
ENV RABBITMQ_PASS=guest
ENV CLAIMS_QUEUE=claims_created_queue
ENV CLAIMS_UPDATED_QUEUE=claims_updated_queue
ENV AUDIT_DIR=/app/audit_logs
# -----------------------------

# Comando para ejecutar el servicio
CMD ["python", "claim_auditor.py"]