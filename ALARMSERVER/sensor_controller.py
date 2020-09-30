import led_controller
import firebase_controller
import multiprocessing
import traceback
from pymongo import MongoClient
import time
import queue
import RPi.GPIO as GPIO
from gpiozero import LED
import uuid
import firebase_admin
import copy
from firebase_admin import firestore
import firebase_controller
import mail_controller
import datetime

class sensor_controller:

    def __init__(self, pwm_queue_in, shared_callback_dict_in):
        self.pwm_queue = pwm_queue_in

        self.led_queue = multiprocessing.Queue()

        self.command_queue = multiprocessing.Queue()

        self.shared_callback_dict = shared_callback_dict_in

        self.alarm_command_queue = multiprocessing.Queue()

        sensor_process = multiprocessing.Process(target=self.sensor_processor, args=())
        sensor_process.start()

        led_process = multiprocessing.Process(target=self.led_processor, args=())
        led_process.start()

        firebase_controller.log_event('SYSTEMSTATE', 'System online')

    # Zone 1 I/O - GPIO 4
    # Zone 2 I/O - GPIO 17

    # Relay - GPIO 27

    # LED processing process
    def led_processor(self):

        while True:

            try:
                command = self.led_queue.get_nowait()

                # [<name>, <enabled>]

                led_controller.command_list[command[0]][1] = command[1]

            except:
                pass

            terminate = led_controller.cycle()

            # If event is supposed to only happen once, disable after it's done
            if terminate:
                led_controller.command_list[terminate][1] = False

    def setup_pins(self, pins):

        #GPIO.cleanup()

        GPIO.setmode(GPIO.BCM)

        for i in pins:
            GPIO.setup(int(i), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def sensor_processor(self):
        # TODO

        # camera feed kill code
        # read/write only sections in db

        # Db schema
        # /users
        #   |- user stuff
        # /logs
        #   |- logs obviously
        # /settings
        #   |- system state
        #   |   |- armed status
        #   |   |- alarm status
        #   |   |- ready status
        #   |   |- grace period
        #   |- sensor data
        #   |   |- sensor x -> x pin, status
        # /instructions
        #   |- armed

        # LED Patterms
        # Startup -
        # Sensor open - Red blink
        # Sensor closed - Blue blink
        # Sensor closed (ready) - Green blink
        # Armed (Action) -
        # Disarmed (Action) - Green blink
        # Armed (status) - Red pulsing
        # Alarm - alarm

        # pin : {'state': True/False, 'name': name}
        try:
            sensors = firebase_admin.firestore.client(app=None).collection('settings').document('sensorConfig').get().to_dict()
        except:
            traceback.print_exc()
            sensors = {
                '4': {'open': False, 'name': 'Zone A', 'time_opened': -1},
                '17': {'open': False, 'name': 'Zone B', 'time_opened': -1}
            }

        desk_light_relay = LED(27)
        desk_light_relay.on()

        print('Sensor Config:', sensors)

        self.setup_pins(sensors)

        # Get current state from db first
        system_state = {
            'silent': False,
            'armed': False,
            'ready': None,
            'alarm': False,
            'deskON': False
        }


        try:
            old_system_state = firebase_admin.firestore.client(app=None).collection('settings').document(
                'systemState').get().to_dict()

            print(old_system_state)

            if old_system_state['armed']:
                self.command_queue.put(['ARM', None])

            if old_system_state['deskON']:
                self.command_queue.put(['DESKON', None])

            if old_system_state['silent']:
                self.command_queue.put(['SILENT', None])

        except:
            traceback.print_exc()

        #sensors_ref.set(sensors)
        #system_state_ref.set(system_state)

        firebase_controller.update_system_state(system_state)
        firebase_controller.update_sensor_state(sensors)

        while True:


            old_system_state = copy.deepcopy(system_state)
            old_sensors = copy.deepcopy(sensors)

            secured = True

            # Check sensors
            for i in sensors:

                try:
                    sensor_open = GPIO.input(int(i)) == GPIO.LOW

                    if sensor_open:
                        secured = False

                    if sensor_open != sensors[i]['open']:
                        sensors[i]['open'] = sensor_open

                        if sensor_open:
                            self.led_queue.put(['sensor_opened', True])

                            sensors[i]['time_opened'] = time.time()

                            firebase_controller.log_event('SENSOR', 'SENSOR OPENED: ' + sensors[i]['name'])


                        else:
                            self.led_queue.put(['sensor_closed', True])

                            firebase_controller.log_event('SENSOR', 'SENSOR CLOSED: ' + sensors[i]['name'])

                        print('Status changed - OPEN: %s, SENSOR: %s' % (sensor_open, sensors[i]['name']))

                        # Update db
                        # Update log

                except:
                    print('Something went wrong')
                    traceback.print_exc()

            # State update
            if system_state['ready'] != secured:
                if system_state['armed'] and not secured and not system_state['alarm']:

                    self.alarm_command_queue.put(sensors)

                    print('ALARM!')

                    self.led_queue.put(['flashlight', True])

                    if system_state['silent']:
                        firebase_controller.log_event('ALARM', 'ALARM TRIGGERED! (SILENT)')

                        self.alarm_command_queue.put('silent')
                    else:
                        firebase_controller.log_event('ALARM', 'ALARM TRIGGERED!')

                    if not system_state['silent']:

                        system_state['alarm'] = True

                        self.led_queue.put(['alarm', True])

                        self.pwm_queue.put('on')

                        time.sleep(1)

                        self.pwm_queue.put('alarm')

                if secured:
                    # led_queue.put(['ready_status', True])
                    self.led_queue.put(['open_status', False])
                else:
                    # led_queue.put(['ready_status', False])
                    self.led_queue.put(['open_status', True])

            system_state['ready'] = secured

            # Check commands
            try:
                command, callback_id = self.command_queue.get_nowait()

                if command == 'ARM':

                    if system_state['ready'] and not system_state['armed']:
                        system_state['armed'] = True

                        self.led_queue.put(['armed', True])
                        self.led_queue.put(['armed_status', True])

                        self.pwm_queue.put('mode_change')

                        firebase_controller.log_event('SYSTEMSTATE', 'SYSTEM ARMED')

                        self.shared_callback_dict[callback_id] = [200, {"status": "System armed"}]
                    else:
                        self.led_queue.put(['error', True])
                        print('System not ready')


                        self.pwm_queue.put('error')

                        if system_state['armed']:
                            self.shared_callback_dict[callback_id] = [500, {"status": "System already armed"}]
                        else:
                            self.shared_callback_dict[callback_id] = [500, {"status": "System not ready"}]


                elif command == 'DISARM':

                    if system_state['armed']:
                        system_state['armed'] = False

                        self.led_queue.put(['armed_status', False])
                        self.led_queue.put(['alarm', False])
                        self.alarm_command_queue.put(False)
                        self.led_queue.put(['flashlight', False])
                        self.led_queue.put(['disarmed', True])

                        self.pwm_queue.put('mute')
                        self.pwm_queue.put('mode_change')

                        firebase_controller.log_event('SYSTEMSTATE', 'SYSTEM DISARMED')

                        #TODO                #Cancel alarm

                        system_state['alarm'] = False

                        self.shared_callback_dict[callback_id] = [200, {"status": "System disarmed"}]

                    else:
                        self.led_queue.put(['error', True])
                        print('System not ready')


                        self.pwm_queue.put('error')

                        self.shared_callback_dict[callback_id] = [500, {"status": "System not armed"}]

                elif command == 'WATCHING':
                    self.led_queue.put(['camera_watched', True])

                elif command == 'NOWATCHING':
                    self.led_queue.put(['camera_watched', False])


                elif command == 'RECORDING':
                    self.led_queue.put(['recording', True])

                elif command == 'NORECORDING':
                    self.led_queue.put(['recording', False])

                elif command == 'DESKON':

                    system_state['deskON'] = True

                    desk_light_relay.off()

                    self.shared_callback_dict[callback_id] = [200, {"status": "Light on!"}]


                elif command == 'DESKOFF':

                    system_state['deskON'] = True

                    desk_light_relay.on()

                    time.sleep(0.5)

                    desk_light_relay.off()

                    self.shared_callback_dict[callback_id] = [200, {"status": "Light off!"}]

                elif command == 'SILENT':
                    system_state['silent'] = True

                    self.led_queue.put(['silent', True])

                    self.shared_callback_dict[callback_id] = [200, {"status": "Silent mode enabled"}]

                elif command == 'UNSILENT':
                    system_state['silent'] = False

                    self.led_queue.put(['silent', False])

                    self.shared_callback_dict[callback_id] = [200, {"status": "Silent mode disabled"}]
                else:
                    print('What is this command? ' + command)

            except queue.Empty:
                pass

            except:
                traceback.print_exc()

            if old_system_state != system_state:
                # Something has changed
                #system_state_ref.set(system_state)

                firebase_controller.update_system_state(system_state)

            if old_sensors != sensors:
                # Something has changed
                #sensors_ref.set(sensors)

                firebase_controller.update_sensor_state(sensors)

                self.pwm_queue.put('zone_change')

            for s in sensors:
                last_time = sensors[s]['time_opened']

                if sensors[s]['open']:
                    if time.time() - last_time > 5 * 60 and last_time != -1: # More than 5 minutes have passed

                        mail_controller.send_mail('Zone open!',
                                                  'Sensor "%s" has been open since %s!' % (sensors[s]['name'], datetime.datetime.fromtimestamp(last_time)), [])

                        print('Reminder email sent!')

                        sensors[s]['time_opened'] = -1 # So we don't get spammed

            # Fixes bounce issues
            time.sleep(0.1)
