# pip3 install opencv-python
# sudo apt install libopencv-dev python3-opencv
# sudo apt install libopencv-dev python-opencv

# Instructions for installing on pi
# pip3 install opencv-python
# sudo apt-get install libcblas-dev
# sudo apt-get install libhdf5-dev
# sudo apt-get install libhdf5-serial-dev
# sudo apt-get install libatlas-base-dev
# sudo apt-get install libjasper-dev
# sudo apt-get install libqtgui4
# sudo apt-get install libqt4-test

import cv2
import firebase_controller
import mail_controller
import glob
import numpy as np
import camera_controller

from PIL import Image
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from io import BytesIO
import os
import time
import datetime
import traceback
import multiprocessing
import threading
import env
import uuid
import glob

# Check if on the PI for development purposes
try:
    from gpiozero import LED

    ON_PI = True
except:
    ON_PI = False
    print('This is not a pi.')

# Camera location based on v4l address
if ON_PI:
    CAM_PRIMARY = '/dev/v4l/by-path/platform-3f980000.usb-usb-0:1.2:1.0-video-index0'
else:
    CAM_PRIMARY = '/dev/v4l/by-path/pci-0000:00:14.0-usb-0:8:1.0-video-index0'

import subprocess

# If on PI, keep waiting until network is online/connected
while ON_PI and not b'10.8.0.' in subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE).communicate()[0]:
    time.sleep(1)
    print('Waiting for network...')

os.system('echo "nameserver 1.1.1.1">/etc/resolv.conf')

HOST = '0.0.0.0'

e = env.get_env()
privacy_mode = False

rsync_command = 'sudo -u pi rsync -arv goosealert-footage %s:~/&' % e['rsync_remote_user']
upload_command = 'sudo -u pi python video_upload.py --file="%s" --title="%s" --privacyStatus="private"&'

# Default non SSL web port
PORT = 80
COUNTDOWN_DELAY = e['COUNTDOWNDELAY']

watching = {}

class WebServer(BaseHTTPRequestHandler):

    def handle_callback(self, callback_id):
        shared_callback_dict[callback_id] = None

        start_time = time.time()

        while True:

            if shared_callback_dict[callback_id]:
                code, message = shared_callback_dict[callback_id]

                self.send_response(code)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                self.wfile.write(str(message).replace('\'', '"').encode(encoding='utf_8'))

                del shared_callback_dict[callback_id]


                break

            if time.time() - start_time > 10:


                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                self.wfile.write(b'{"status": "Server took too long"}')

                del shared_callback_dict[callback_id]


                break

            time.sleep(0.1)

    def do_POST(self):

        global privacy_mode

        path = self.path[1:]

        callback_id = str(uuid.uuid4())

        #print(self.rfile.read(int(self.headers.get('Content-Length'))))

        if path == 'goodnight':

            pwm_queue.put('off')
            command_queue.put(['DESKOFF', callback_id])
            #command_queue.put(['ARM', callback_id])

            pass

        elif path == 'leaving':

            pwm_queue.put('countdown')
            led_queue.put(['countdown', time.time() + COUNTDOWN_DELAY])

            time.sleep(COUNTDOWN_DELAY)


            led_queue.put(['countdown', False])
            pwm_queue.put('off')
            command_queue.put(['DESKOFF', callback_id])

            with open('privacy', 'w') as file:
                file.write('True')
            time.sleep(2)

            command_queue.put(['ARM', callback_id])

            pass

        elif path == 'home':

            now = int(time.strftime('%H:%M:%S').split(':')[0])

            command_queue.put(['DESKON', callback_id])

            if 7 > now or now >= 17:
                pwm_queue.put('on')

                time.sleep(5)

            command_queue.put(['DISARM', callback_id])


            pass

        elif path == 'arm':

            command_queue.put(['ARM', callback_id])

            self.handle_callback(callback_id)

            return

        elif path == 'disarm':

            command_queue.put(['DISARM', callback_id])

            self.handle_callback(callback_id)

            return

        elif path == 'lightON':

            firebase_controller.log_event('AUXDEVICES', 'Flashlight On')

            led_queue.put(['flashlight', True])

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            self.wfile.write(b'{"status": "Command queued"}')

            return

        elif path == 'lightOFF':

            firebase_controller.log_event('AUXDEVICES', 'Flashlight Off')

            led_queue.put(['flashlight', False])

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            self.wfile.write(b'{"status": "Command queued"}')

            return

        elif path == 'popomode':

            firebase_controller.log_event('AUXDEVICES', 'Popo mode')

            led_queue.put(['alarm', True])

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            self.wfile.write(b'{"status": "Command queued"}')

            return

        elif path == 'privacyON':


            enable_privacy()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            self.wfile.write(b'{"status": "Done."}')

            return

        elif path == 'privacyOFF':

            firebase_controller.log_event('SYS', '~ mode disabled')

            led_queue.put(['privacy', False])

            privacy_mode = False

            os.remove('privacy')

            #with open('privacy', 'w') as file:
            #    file.write('False')

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            self.wfile.write(b'{"status": "Done."}')

            return

        elif path == 'discomode':

            firebase_controller.log_event('AUXDEVICES', 'Disco mode')

            command_queue.put(['DESKOFF', callback_id])
            pwm_queue.put('off')
            led_queue.put(['rainbow', True])

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            self.wfile.write(b'{"status": "Command queued"}')

            return


        elif path == 'nodiscomode':

            firebase_controller.log_event('AUXDEVICES', 'No disco mode')

            led_queue.put(['rainbow', False])

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            self.wfile.write(b'{"status": "Command queued"}')

            return



        elif path == 'switchON':

            pwm_queue.put('on')

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            self.wfile.write(b'{"status": "Command queued"}')

            return

        elif path == 'switchOFF':

            pwm_queue.put('off')

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            self.wfile.write(b'{"status": "Command queued"}')

            return

        elif path == 'deskON':

            command_queue.put(['DESKON', callback_id])

            firebase_controller.log_event('AUXDEVICES', 'Desk light On')

            self.handle_callback(callback_id)

            return

        elif path == 'deskOFF':

            command_queue.put(['DESKOFF', callback_id])

            firebase_controller.log_event('AUXDEVICES', 'Desk light Off')

            self.handle_callback(callback_id)

            return

        elif path == 'SILENT':

            command_queue.put(['SILENT', callback_id])

            firebase_controller.log_event('SYSTEM', 'SILENT MODE ENABLED')


            mail_controller.send_mail('Silent Mode Enabled', 'Silent mode has been enabled.', [])


            self.handle_callback(callback_id)

            return

        elif path == 'UNSILENT':

            command_queue.put(['UNSILENT', callback_id])

            firebase_controller.log_event('SYSTEM', 'SILENT MODE DISABLED')

            self.handle_callback(callback_id)

            return

        elif path == 'heartbeat':

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            return

        elif path == 'reboot':

            print('Me Reboot')

            firebase_controller.log_event('SYSTEM', 'Reboot command issued.')
            os.system('sudo reboot')

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            self.wfile.write(b'{"status": "Executed"}')

            return

        elif path == 'pcsuspend':

            firebase_controller.log_event('AUX', 'Suspend PC command issued.')
            os.system('sudo -u pi ssh -oStrictHostKeyChecking=no %s "suspend"' % e['PC_ADDRESS'])

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            self.wfile.write(b'{"status": "Executed"}')

            return


        elif path == 'pclock':

            firebase_controller.log_event('AUX', 'Lock PC command issued.')
            os.system('sudo -u pi ssh -oStrictHostKeyChecking=no %s "lock"' % e['PC_ADDRESS'])

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            self.wfile.write(b'{"status": "Executed"}')

            return

    # Called when GET request is received
    def do_GET(self):

        global active_connections, privacy_mode

        if privacy_mode:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            self.wfile.write(b'{"status": "Unknown Error"}')

            traceback.print_exc()
            print(self.path)

            return

        print('Camera request')

        try:
            path, user = self.path[1:].split('?')

            frame_name = int(path)

            # If frame is in valid domain
            if 0 <= frame_name < len(frames):

                self.send_response(200)
                self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
                self.end_headers()

                if user != 'INTERNAL':
                    firebase_controller.log_event('CAMERA', user + ' is watching the feed')
                    active_connections += 1

                if user not in watching:
                    watching[user] = 0

                watching[user] += 1

                firebase_controller.update_watching(watching)

                if active_connections == 1:
                    command_queue.put(['WATCHING', None])

                # Start frame send loop
                while True:
                    try:

                        if privacy_mode:
                            raise Exception

                        # Get frame
                        img = frames[frame_name]()[1]

                        # Turn greyscale
                        imgRGB = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

                        jpg = Image.fromarray(imgRGB)

                        # Convert frame to jpg byte magic
                        with BytesIO() as output:
                            jpg.save(output, format='JPEG')

                            self.wfile.write(b"--jpgboundary")
                            self.send_header('Content-type', 'image/jpeg')
                            self.send_header('Content-length', str(len(output.getvalue())))
                            self.end_headers()

                            jpg.save(self.wfile, format='JPEG')

                            # Delay to maintain framerate
                            # Too low and frames will buffer
                            # Too high and framerate will suffer

                            time.sleep(0.05)
                    except:
                        print('Ayy it broke')

                        if user != 'INTERNAL':
                            firebase_controller.log_event('CAMERA', user + ' terminated the feed')
                            active_connections -= 1

                        watching[user] -= 1

                        firebase_controller.update_watching(watching)


                        if active_connections == 0:
                            command_queue.put(['NOWATCHING', None])

                        traceback.print_exc()
                        break



        except:

            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            self.wfile.write(b'{"status": "Unknown Error (wtf you broke something)"}')

            traceback.print_exc()
            print(self.path)

            return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


frames = []
pwm_queue = multiprocessing.Queue()
command_queue = multiprocessing.Queue()
shared_callback_dict = None
led_queue = multiprocessing.Queue()
alarm_command_queue = multiprocessing.Queue()
active_connections = 0

def setup(command_queue_in, led_queue_in, alarm_command_queue_in, pwm_queue_in, shared_callback_dict_in):

    global frames, command_queue, led_queue, alarm_command_queue, pwm_queue, camera_command_queue, shared_callback_dict

    primaryCam = camera_controller.TeleopCam(CAM_PRIMARY, int(683), int(384), 0)

    pwm_queue = pwm_queue_in
    alarm_command_queue = alarm_command_queue_in
    command_queue = command_queue_in
    led_queue = led_queue_in
    shared_callback_dict = shared_callback_dict_in

    # List with frame retreval functions
    frames = [primaryCam.getFrame]

    webserver_thread = threading.Thread(target=webserver, args=())
    webserver_thread.start()

    alarm_recorder_thread = threading.Thread(target=alarm_recorder, args=())
    alarm_recorder_thread.start()

    cv_recorder_thread = threading.Thread(target=cv_recorder, args=())
    cv_recorder_thread.start()

    #record_watchdog_thread = threading.Thread(target=record_watchdog, args=())
    #record_watchdog_thread.start()

    '''
    try:
        with open('privacy', 'r') as file:
            if file.read().strip() == 'True':
                print('Ok, i read that privacy mode is on')
                enable_privacy()
    except:
        print('Frick, cant find privacy file')
        traceback.print_exc()
    '''

"""
def record_watchdog():
    last_time = time.time()

    print('Recoder watchdog running')

    while True:

        if 'INTERNAL' in watching and watching['INTERNAL'] > 0:
            last_time = time.time()

        if time.time() - last_time > 30: # Internal recorder hasn't returned to record in 30 seconds
            print('Recorder missed deadline')

            mail_controller.send_mail('System will auto reboot',
                                      'The recorder missed its access deadline. System will reboot automatically.',
                                      [])

            print('Rebooting!')

            os.system('sudo reboot')

        time.sleep(5)
"""

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

def cv_recorder():

    time.sleep(5)

    print('CV RECORDER RUNNING!')

    CLIP_LENGTH = 300 # 5 minute clips

    failed = 0

    while True:

        last_start = time.time()

        print('Starting new loop')

        command_queue.put(['RECORDING', None])

        try:
            ret, frame = frames[0]()
        except:
            ret = False

        if ret:

            start_time = time.time()

            timestamp = str(datetime.datetime.now()).replace(' ', '_')

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter('goosealert-footage/' + timestamp + '.avi', fourcc, 10.0, (640, 480))

            frame_count = 0

            try:
                while True:
                    ret, frame = frames[0]()

                    if ret == True:
                        # Write the frame into the file 'output.avi'
                        out.write(frame)

                        frame_count += 1

                        if frame_count % 100 == 0:
                            print('On frame count %i on file %s!' % (frame_count, timestamp))

                        #time.sleep(0.05)

                        #print('Got frame')

                    else:
                        break

                    if time.time() - start_time >= CLIP_LENGTH:
                        break

            except:

                print('!!!!!!!!!!!!!!!!!!!!!! Camera failed')
                time.sleep(5)  # Waiting since camera is not ready

                if time.time() - last_start < 30:
                    failed += 1

            # RSYNC IS DISABLED FOR NOW
            #os.system(upload_command % ('goosealert-footage/' + timestamp + '.avi', timestamp))

        else:
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Camera is not ready')
            time.sleep(5) # Waiting since camera is not ready

            if time.time() - last_start < 30:
                failed += 1

        if time.time() - last_start >= 30:
            failed = 0

        command_queue.put(['NORECORDING', None])

        check_capacity_thread = threading.Thread(target=check_capacity, args=())
        check_capacity_thread.start()


        print('-=--------------------------------------------------------------------FAILED', failed)

        if failed == 10:
            mail_controller.send_mail('System will auto reboot', 'The recording loop has failed 10 execution cycles. System will reboot automatically.', [])

            print('Rebooting!')

            os.system('sudo reboot')

        elif failed == 5:
            #os.system(rsync_command)
            mail_controller.send_mail('Recording loop is skipping', 'The recording loop has failed 5 execution cycles. Just thought you should know.', [])

def check_capacity():

    print('Checking capacity')

    MAX_DIR_SIZE = 40

    while get_size('goosealert-footage') / 1000000000 > MAX_DIR_SIZE:

        print('Dir is larger than limit!!!!')

        target_file = sorted(glob.glob('goosealert-footage/*'))[0]

        print('Deleting', target_file)

        os.remove(target_file)




def webserver():

    try:
        # Start HTTP server
        server = ThreadedHTTPServer((HOST, PORT), WebServer)
        print("Server started @ (%s:%i)" % (HOST, PORT))
        server.serve_forever()
    except KeyboardInterrupt:

        server.socket.close()

# This is here so that it shares the same process as the web server
# CV doesn't seem to like it when we access it from different processes
def alarm_recorder():

    command = False
    while True:
        try:
            command = alarm_command_queue.get_nowait()
        except:
            pass

        try:
            if command:

                files = []

                for _ in range(5):
                    filename = 'goosealert-footage/' + str(datetime.datetime.now()).replace(' ', '_') + '.jpg'

                    cv2.imwrite(filename, frames[0]()[1])

                    files.append(filename)

                    time.sleep(1)

                mail_controller.send_mail('Goose detected!!!', 'A goose was detected in your neighbourhood at %s! (Here\'s the system configuration btw %s)' % (datetime.datetime.now(), str(command)), files)

                time.sleep(5)

                if 'silent' in command:
                    command = False

            else:
                time.sleep(1)
        except:
            traceback.print_exc()

def enable_privacy():
    global privacy_mode

    firebase_controller.log_event('SYS', '~ mode enabled')

    led_queue.put(['privacy', True])

    privacy_mode = True

    with open('privacy', 'w') as file:
        file.write('True')

    mail_controller.send_mail('Privacy Mode Enabled', '  has been enabled.', [])

if __name__ == '__main__':
    setup()