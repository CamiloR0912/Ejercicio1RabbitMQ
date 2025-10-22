import pika
import json
import random
import time
import sys

def create_tasks():
    tasks = []
    priorities = ['low', 'medium', 'high']
    
    for i in range(1, 11):
        complexity = random.randint(1, 5)
        priority = random.choice(priorities)
        
        task = {
            'task_id': i,
            'complexity': complexity,
            'priority': priority,
            'description': f'Tarea de análisis #{i}'
        }
        tasks.append(task)
    return tasks

def publish_tasks(exchange_name='task_router'):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", port=5672,
                                  credentials=pika.PlainCredentials("user", "password"))
    )
    channel = connection.channel()
    
    channel.exchange_declare(exchange=exchange_name, exchange_type='direct', durable=True)
    
    tasks = create_tasks()
    
    print(f"Publicando {len(tasks)} tareas en el exchange '{exchange_name}'...\n")
    
    for task in tasks:
        message = json.dumps(task)
        priority = task['priority']
        
        channel.basic_publish(
            exchange=exchange_name,
            routing_key=priority,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        
        print(f"Tarea #{task['task_id']} - Prioridad: {priority} - Complejidad: {task['complexity']}s")
        time.sleep(0.1)
    
    connection.close()

if __name__ == '__main__':
    try:
        exchange = sys.argv[1] if len(sys.argv) > 1 else 'task_router'
        publish_tasks(exchange)
    except KeyboardInterrupt:
        print('\nProductor interrumpido')
    except Exception as e:
        print(f'Error: {e}')