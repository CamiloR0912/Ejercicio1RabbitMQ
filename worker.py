import pika
import json
import time
import sys
import random

class Worker:
    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.tasks_processed = 0
        
    def process_task(self, task_data):
        """Simula el procesamiento de una tarea durante el tiempo de complejidad"""
        task_id = task_data['task_id']
        complexity = task_data['complexity']
        description = task_data['description']
        
        print(f"[Worker {self.worker_id}] Procesando tarea #{task_id} - {description}")
        print(f"[Worker {self.worker_id}] Tiempo estimado: {complexity} segundos")
        
        # Simular el trabajo
        time.sleep(complexity)
        
        self.tasks_processed += 1
        print(f"[Worker {self.worker_id}] ✓ Tarea #{task_id} completada")
        print(f"[Worker {self.worker_id}] Tareas procesadas: {self.tasks_processed}\n")
        
    def callback(self, ch, method, properties, body):
        """Callback que se ejecuta al recibir un mensaje"""
        try:
            task_data = json.loads(body)
            
            # Procesar la tarea
            self.process_task(task_data)
            
            # Confirmar manualmente que la tarea fue procesada (ACK)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            print(f"[Worker {self.worker_id}] ✗ Error procesando tarea: {e}")
            # Si hay un error, rechazar el mensaje y reencolarlo
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start(self):
        """Inicia el worker y comienza a consumir tareas"""
        # Conexión a RabbitMQ
        connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", port=5672,
                              credentials=pika.PlainCredentials("user", "password"))
        )
        channel = connection.channel()
        
        # Declarar la cola (debe ser la misma que el productor)
        channel.queue_declare(queue='tareas_distribuidas', durable=True)
        
        # Configurar prefetch_count = 1 para distribución equitativa
        # Esto evita que un worker reciba múltiples tareas si no ha terminado la actual
        channel.basic_qos(prefetch_count=1)
        
        # Configurar el consumidor con ACK manual
        channel.basic_consume(
            queue='tareas_distribuidas',
            on_message_callback=self.callback,
            auto_ack=False  # ACK manual para garantizar procesamiento
        )
        
        print(f"=== WORKER {self.worker_id} INICIADO ===")
        print(f"[Worker {self.worker_id}] Esperando tareas... (Ctrl+C para salir)\n")
        
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            print(f'\n[Worker {self.worker_id}] Detenido por el usuario')
            print(f'[Worker {self.worker_id}] Total de tareas procesadas: {self.tasks_processed}')
            channel.stop_consuming()
        
        connection.close()

if __name__ == '__main__':
    # El ID del worker se puede pasar como argumento o usar un ID aleatorio
    worker_id = sys.argv[1] if len(sys.argv) > 1 else random.randint(1, 100)
    
    worker = Worker(worker_id)
    worker.start()