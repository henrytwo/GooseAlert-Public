import board
import busio
import adafruit_pca9685
from gpiozero import LED
import time
import multiprocessing
import firebase_controller

i2c = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c)

pca.frequency = 50

from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)

SWITCH_CHANNEL = 0
SIREN_CHANNEL = 1
SPEAKER_CHANNEL = 3

class pwm_controller:

    def __init__(self):
        self.pwm_queue = multiprocessing.Queue()
        self.command = None

        self.mute()

        pwm_process = multiprocessing.Process(target=self.listener, args=(self.pwm_queue,))
        pwm_process.start()

    def off(self):
        self.mode_servo()


        kit.servo[SWITCH_CHANNEL].angle = 0
        time.sleep(1)
        kit.servo[SWITCH_CHANNEL].angle = 90


        firebase_controller.log_event('AUXDEVICES', 'Switch Off')


        return 'mute'

    def on(self):
        self.mode_servo()

        for _ in range(2):
            time.sleep(0.5)
            kit.servo[SWITCH_CHANNEL].angle = 170
            time.sleep(1)
            kit.servo[SWITCH_CHANNEL].angle = 90

        firebase_controller.log_event('AUXDEVICES', 'Switch On')

        return 'mute'

    def mode_servo(self):
        pca.frequency = 50

    def mode_change(self):

        for _ in range(2):
            pca.channels[SIREN_CHANNEL].duty_cycle = 0xffff
            pca.frequency = 1200
            time.sleep(0.2)
            self.mute()
            time.sleep(0.2)

        return 'mute'

    def zone_change(self):

        for _ in range(4):
            pca.channels[SPEAKER_CHANNEL].duty_cycle = 0xcaaa
            pca.frequency = 2000
            time.sleep(0.07)
            self.mute()
            time.sleep(0.07)

        return 'mute'

    def error(self):

        pca.channels[SPEAKER_CHANNEL].duty_cycle = 0xcaaa
        pca.frequency = 800
        time.sleep(0.2)
        self.mute()

        return 'mute'

    def alarm(self):
        pca.channels[SIREN_CHANNEL].duty_cycle = 0xffff

        pca.frequency = 1500
        time.sleep(0.5)

        pca.channels[SIREN_CHANNEL].duty_cycle = 0xeeef
        pca.frequency = 1200
        time.sleep(0.5)

    def countdown(self):
        pca.channels[SPEAKER_CHANNEL].duty_cycle = 0xcaaa

        pca.frequency = 1500
        time.sleep(1)
        pca.frequency = 1200
        self.mute()
        time.sleep(1)

    def mute(self):
        pca.channels[SIREN_CHANNEL].duty_cycle = 0
        pca.channels[SPEAKER_CHANNEL].duty_cycle = 0

    def listener(self, pwm_queue):

        self.command = None

        command_list = {
            'mute': self.mute,
            'alarm': self.alarm,
            'on': self.on,
            'off': self.off,
            'error': self.error,
            'mode_change': self.mode_change,
            'zone_change': self.zone_change,
            'countdown': self.countdown
        }

        while True:
            try:
                new_command = pwm_queue.get_nowait()

                if (self.command != 'alarm' or (self.command == 'alarm' and new_command == 'mute')) and (self.command != 'countdown' or (self.command == 'countdown' and new_command != 'zone_change')) and self.command not in ['on', 'off']:
                    self.command = new_command

                #if self.command in ['on', 'off']:
                #    pwm_queue.queue(new_command)
            except:
                pass

            if self.command:

                # Turn off the stuff that isn't the most recent command
                for c in command_list:

                    if c == self.command:
                        new_command = command_list[c]()

                        if new_command:
                            self.command = new_command

                        break

                else:
                    time.sleep(0.1) # So we don't pin the cpu


