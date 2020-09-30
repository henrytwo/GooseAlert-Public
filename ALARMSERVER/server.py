# Place into /etc/rc.local
# tmux new-session -d "cd /home/pi/GooseAlert; sudo python3 server.py; read;"

# Add to openvpn cert so that not all traffic is rerouted
# pull-filter ignore "redirect-gateway"

import os
import webserver_controller
import sensor_controller
import mail_controller
import firebase_controller
import pwm_controller
from camera_controller import *
import multiprocessing
import threading
import traceback
import requests

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth
from datetime import datetime
import time

cred = credentials.Certificate('firebase_key.json')
firebase_admin.initialize_app(cred)

manager = multiprocessing.Manager()
shared_callback_dict = manager.dict()

pwmc = pwm_controller.pwm_controller()
sc = sensor_controller.sensor_controller(pwmc.pwm_queue, shared_callback_dict)

webserver_controller.setup(sc.command_queue, sc.led_queue, sc.alarm_command_queue, pwmc.pwm_queue, shared_callback_dict)


print('Server running')

pwmc.pwm_queue.put('zone_change')