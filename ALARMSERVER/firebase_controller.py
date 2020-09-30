import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth
from datetime import datetime
import time
import traceback
import multiprocessing
import threading

# Setup firebase
# Static functions

def update_system_state(system_state):
    system_state_thread = threading.Thread(target=system_state_worker, args=(system_state,))
    system_state_thread.start()

def system_state_worker(system_state):
    system_state_ref = firebase_admin.firestore.client(app=None).collection('settings').document('systemState')
    system_state_ref.set(system_state)

def update_sensor_state(sensor_state):
    sensor_state_thread = threading.Thread(target=sensor_state_worker, args=(sensor_state,))
    sensor_state_thread.start()

def sensor_state_worker(sensor_state):
    sensors_ref = firebase_admin.firestore.client(app=None).collection('settings').document('sensorData')
    sensors_ref.set(sensor_state)


def log_event(event_type, message):
    # Type - LOG, ALARM, SENSOR

    log_event_thread = threading.Thread(target=log_event_worker, args=(event_type, message))
    log_event_thread.start()

def log_event_worker(event_type, message):
    for _ in range(3):
        print('Trying firebase (round %i)' % _)
        try:

            timestamp = str(datetime.fromtimestamp(time.time()))

            log_data = {
                    'type': event_type,
                    'message': message,
                    'timestamp': timestamp,
                    'unixtime': time.time()
                }


            print('[%s] [%s] %s' % (timestamp, event_type, message))

            firebase_admin.firestore.client(app=None) \
                .collection('logs') \
                .document(timestamp) \
                .set(log_data)

            break
        except:
            traceback.print_exc()
            print('LOGGING FAILED!', event_type, message)

def update_watching(watching):
    update_watching_thread = threading.Thread(target=update_watching_worker, args=(watching,))
    update_watching_thread.start()

def update_watching_worker(watching):

    for _ in range(3):

        print('Trying firebase for watching (round %i)' % _)

        try:

            firebase_admin.firestore.client(app=None)\
                .collection('settings') \
                .document('watching') \
                .set(watching)

            break
        except:
            traceback.print_exc()
            print('Couldn\'t set watch event!', watching)