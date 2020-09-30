import time
import os
import mail_controller
import requests

def heartbeat():

    time.sleep(10) # Wait 10 seconds for main server to start

    print('Heartbeat process started')

    while True:

        try:
            requests.post('http://localhost/heartbeat') # Are you still alive?

        except:
            print('Heartbeat failed!')


            mail_controller.send_mail('System will auto reboot',
                                      'The server did not respond to heartbeat. The server will reboot automatically.',
                                      [])

            print('Rebooting!')

            os.system('sudo reboot')

        try:
            requests.get('https://google.com') # Are you still alive?
        except:
            print('Heartbeat failed!')


            mail_controller.send_mail('System will auto reboot',
                                      'The server was unable to connect to the internet.',
                                      []) # idk how this email is supposed o send without the internet

            print('Rebooting!')

            os.system('sudo reboot')


        time.sleep(10)


heartbeat()