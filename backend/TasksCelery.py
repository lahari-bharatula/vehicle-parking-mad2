import time
import csv
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')
celery.conf.update(
    timezone='Asia/Kolkata',
    enable_utc=False,
)

@celery.task
def generate_csv(reservations_data, filename):
    if not reservations_data:
        return
    time.sleep(3)  
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        
        writer = csv.DictWriter(f, fieldnames=[
            'id', 'spot_id', 'lot_id', 'parking_timestamp',
            'leaving_timestamp', 'parking_cost', 'remarks'
        ])
        writer.writeheader()
        writer.writerows(reservations_data)
