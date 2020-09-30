# Not really related to goosealert but it's so that i can remotely manage my pc

import os
import time
import subprocess
import sys

command = sys.argv[1]

commands = {
    'lock' : 'dbus-send --type=method_call --dest=org.gnome.ScreenSaver /org/gnome/ScreenSaver org.gnome.ScreenSaver.Lock',
    'suspend': 'sudo systemctl suspend -i'
}

if command in commands:

    os.system("notify-send 'Remote command issued' 'A remote command has been sent to this machine (%s)'" % command)
    process = subprocess.Popen(commands[command].split(), stdout=subprocess.PIPE)
else:
    os.system("notify-send 'Remote command issued' 'A remote command was sent but we dont know wtf to do with it (%s)'" % command)
