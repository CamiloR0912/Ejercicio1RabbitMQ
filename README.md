# Tareas distribuidas

### Integrantes:
 - Julian Bayona
 - Camilo Ramirez

 ---

 - Creación del servicio
 ![alt text](imagenes/image.png)
 ![alt text](imagenes/image-1.png)
 
 - Creación entorno virtual para instalar pika
 ![alt text](imagenes/venv.png)

 - Creación del worker
 ![alt text](imagenes/image-2.png)

 - Creación del producer
 ![alt text](imagenes/image-3.png)

 - Prueba de funcionamiento:
 Las tareas se reparten de manera equilibrada entre los workers
 ![alt text](imagenes/image-4.png)

 - Tolerancia a fallos:
 Se terminó la ejecución del primer worker y la tarea no se perdió, se completó la tarea y los demas workers que quedaban realizaron las tareas faltantes.
 ![alt text](imagenes/image-5.png)

## FLujo del programa
### 1. producer.py:

 - Genera 10 tareas con un nivel de complejidad aleatorio (1–5 segundos).

 - Publica cada tarea en la cola tareas_distribuidas de RabbitMQ.

 - Las tareas se marcan como persistentes para que no se pierdan si RabbitMQ se reinicia.

### 2. worker.py:

 - Se conectan a la misma cola y quedan a la espera de tareas.

 - Cada worker recibe una tarea, la procesa simulando el tiempo de complejidad con sleep(), y luego envía un ack manual confirmando que terminó.

 - Si un worker falla antes de enviar el ack, RabbitMQ reasigna automáticamente la tarea a otro worker.

### 3. Distribución de tareas:

 - Gracias a basic_qos(prefetch_count=1), cada worker recibe una tarea a la vez y no se sobrecarga.

 - RabbitMQ entrega las tareas de forma equitativa, evitando que un solo worker acapare todo el trabajo.

## Mecanismos de fiabilidad y distribución
 - Persistencia de mensajes: Se usa delivery_mode=2 para que las tareas no se pierdan aunque RabbitMQ se reinicie.

 - ACK manual: Un worker confirma explícitamente la finalización con basic_ack(). Si no lo hace, RabbitMQ reencola la tarea.

 - Prefetch (equidad): Con prefetch_count=1, RabbitMQ asegura que cada worker solo procese una tarea a la vez, balanceando la carga entre todos.

 - Tolerancia a fallos: Si un worker se cae durante el procesamiento, la tarea pendiente se reasigna automáticamente a otro worker disponible.