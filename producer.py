import pika
import json
import random
import time

def create_tasks():
    """Genera 10 tareas con niveles de complejidad aleatorios (1-5 segundos)"""
    tasks = []
    for i in range(1, 11):
        complexity = random.randint(1, 5)
        task = {
            'task_id': i,
            'complexity': complexity,
            'description': f'Tarea de análisis #{i}'
        }
        tasks.append(task)
    return tasks

def publish_tasks():
    """Publica las tareas en la cola de RabbitMQ"""
    # Conexión a RabbitMQ
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost", port=5672,
                              credentials=pika.PlainCredentials("user", "password"))
    )
    channel = connection.channel()
    
    # Declarar la cola con durabilidad
    channel.queue_declare(queue='tareas_distribuidas', durable=True)
    
    # Generar tareas
    tasks = create_tasks()
    
    print("=== PRODUCTOR INICIADO ===")
    print(f"Generando {len(tasks)} tareas...\n")
    
    # Publicar cada tarea
    for task in tasks:
        message = json.dumps(task)
        
        channel.basic_publish(
            exchange='',
            routing_key='tareas_distribuidas',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Hacer el mensaje persistente
            )
        )
        
        print(f"✓ Tarea #{task['task_id']} publicada - Complejidad: {task['complexity']}s")
        time.sleep(0.1)  # Pequeña pausa para visualización
    
    print(f"\n✓ Todas las tareas han sido enviadas a la cola")
    print(f"✓ Total de tareas: {len(tasks)}")
    
    connection.close()

if __name__ == '__main__':
    try:
        publish_tasks()
    except KeyboardInterrupt:
        print('\n\nProductor interrumpido por el usuario')
    except Exception as e:
        print(f'\nError: {e}')