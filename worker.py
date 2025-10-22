import pika
import json
import time
import sys
import random

class Worker:
    def __init__(self, worker_id, priorities=None):
        self.worker_id = worker_id
        self.tasks_processed = 0
        self.priorities = priorities if priorities else ['low', 'medium', 'high']
        
    def process_task(self, task_data):
        task_id = task_data['task_id']
        complexity = task_data['complexity']
        priority = task_data.get('priority', 'unknown')
        description = task_data['description']
        
        print(f"[Worker {self.worker_id}] Procesando tarea #{task_id} - {description}")
        print(f"[Worker {self.worker_id}] Prioridad: {priority} - Tiempo: {complexity}s")
        
        time.sleep(complexity)
        
        self.tasks_processed += 1
        print(f"[Worker {self.worker_id}] Tarea #{task_id} completada")
        print(f"[Worker {self.worker_id}] Total procesadas: {self.tasks_processed}\n")
        
    def callback(self, ch, method, properties, body):
        try:
            task_data = json.loads(body)
            self.process_task(task_data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"[Worker {self.worker_id}] Error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start(self, exchange_name='task_router'):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost", port=5672,
                                      credentials=pika.PlainCredentials("user", "password"))
        )
        channel = connection.channel()
        
        channel.exchange_declare(exchange=exchange_name, exchange_type='direct', durable=True)
        
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        
        print(f"Worker {self.worker_id} iniciado")
        print(f"Prioridades: {', '.join(self.priorities)}\n")
        
        for priority in self.priorities:
            channel.queue_bind(
                exchange=exchange_name,
                queue=queue_name,
                routing_key=priority
            )
        
        channel.basic_qos(prefetch_count=1)
        
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=self.callback,
            auto_ack=False
        )
        
        print(f"[Worker {self.worker_id}] Esperando tareas...\n")
        
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            print(f'\n[Worker {self.worker_id}] Detenido')
            channel.stop_consuming()
        
        connection.close()


if __name__ == '__main__':
    worker_id = sys.argv[1] if len(sys.argv) > 1 else random.randint(1, 100)
    priorities = sys.argv[2:] if len(sys.argv) > 2 else None
    
    valid_priorities = ['low', 'medium', 'high']
    if priorities:
        priorities = [p for p in priorities if p in valid_priorities]
        if not priorities:
            print("Error: Prioridades inválidas. Use: low, medium, high")
            sys.exit(1)
    
    worker = Worker(worker_id, priorities)
    worker.start()