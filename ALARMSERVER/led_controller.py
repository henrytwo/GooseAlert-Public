import time
import board
import neopixel
import math
import env


e = env.get_env()
COUNTDOWN_DELAY = e['COUNTDOWNDELAY']

# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 20

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB
DEFAULT_BRIGHTNESS = 0.2

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=DEFAULT_BRIGHTNESS, auto_write=False,
                           pixel_order=ORDER)

rainbow_count = 0

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER == neopixel.RGB or ORDER == neopixel.GRB else (r, g, b, 0)


def rainbow_cycle(wait=0.00001):

    global rainbow_count

    for i in range(num_pixels):
        pixel_index = (i * 256 // num_pixels) + rainbow_count
        pixels[i] = wheel(pixel_index & 255)
        #dual(i, wheel(pixel_index & 255))
    pixels.show()

    rainbow_count += 1
    rainbow_count %= 255
    #time.sleep(wait)

def chase(color, direction):

    pixels.fill((0, 0, 0))


    if direction > 0:
        index = int(time.time() * 20) % num_pixels

    else:
        index = num_pixels - int(time.time() * 20) % num_pixels

    for i in range(num_pixels // 2):

        if -1 < (i + index) % num_pixels < num_pixels:

            pixels[(i + index) % num_pixels]  = color

def chase_up():
    chase((0, 0, 255), 1)

def chase_down():
    chase((0, 0, 255), -1)

def error():
    blink(3, (255, 255, 0), 0.1)

def blink(i, color, t):
    for _ in range(i):
        pixels.fill(color)
        pixels.show()

        time.sleep(t)

        pixels.fill((0, 0, 0))
        pixels.show()

        time.sleep(t)

def powered_on():
    blink(3, (0, 0, 255), 0.1)


def sensor_opened():
    blink(3, (255, 0, 0), 0.1)


def sensor_closed():
    blink(3, (0, 255, 0), 0.1)


def alarm():
    pixels.fill((255, 0, 0) if int(time.time() / 0.1) % 2 else (0, 0, 255))

def disarmed():
    blink(1, (0, 255, 0), 0.5)

def armed():
    blink(1, (255, 0, 0), 0.5)

def armed_status():
    pixels.fill((limit(int(128 * math.sin(time.time() * 3) + 128)), 0, 0))

def ready_status():
    pixels.fill((0, limit(int(128 * math.sin(time.time() * 3) + 128)), 0))

def open_status():
    pixels.fill((limit(int(128 * math.sin(time.time() * 3) + 128)), limit(int(128 * math.sin(time.time() * 3) + 128)), 0))

def blank():
    pixels.fill((0, 0, 0))
    pixels.show()

def limit(val):
    return max(min(255, val), 0)

def camera_watched():
    color = (0, 0, 0) if int(time.time()) % 2 == 0 else (255, 0, 255)

    for i in range(num_pixels - 4, num_pixels - 1):
        pixels[i] = color

def countdown():
    #color = (0, 0, 0) if int(time.time()) % 2 == 0 else (255, 0, 255)

    time_left = command_list['countdown'][1] - time.time()

    if time_left / COUNTDOWN_DELAY >= 0.66:
        color = (0, limit(int(128 * math.sin(time.time() * 3) + 128)), 0)
    elif time_left / COUNTDOWN_DELAY >= 0.33:
        color = (limit(int(128 * math.sin(time.time() * 3) + 128)), limit(int(128 * math.sin(time.time() * 3) + 128)), 0)
    else:
        color = (limit(int(128 * math.sin(time.time() * 3) + 128)), 0, 0)

    if command_list['countdown'][1]:
        for i in range(5, num_pixels - 4):

            if i <= ((time_left) / COUNTDOWN_DELAY) * 10 + 5:
                pixels[i] = color
            else:
                pixels[i] = (0, 0, 0)


def recording():
    color = (0, 0, 0) if int(time.time()) % 2 == 0 else (0, 10, 0)

    pixels[0] = color
    pixels[num_pixels - 1] = color

def silent():
    color = (0, 0, 0) if int(time.time()) % 2 == 0 else (0, 0, 50)

    pixels[1] = color
    pixels[num_pixels - 2] = color

def privacy():
    color = (0, 0, 0) if int(time.time()) % 2 == 0 else (50, 0, 0)

    pixels[2] = color
    pixels[num_pixels - 3] = color

def flashlight():

    for i in range(0, 10):
        pixels[i] = (255, 255, 255)

# Higher = higher priority
priority_list = {
    -1000: [
        'camera_watched',
        'recording',
        'silent',
        'privacy',
        'flashlight',
        'countdown'
    ],
    9999 : [
        'alarm',
        'rainbow'
    ],
    10 : [
        'error',
        'armed',
        'disarmed',
        'sensor_closed',
        'sensor_opened',
        'powered_on'
    ],
    0 : [
        'armed_status',
        'ready_status',
        'open_status',
        'blank',

        'chase_down',
        'chase_up'
    ]
}

# [<function>, <activated>]
command_list = {

                # Overlapping
                'countdown': [countdown, False],
                'camera_watched': [camera_watched, False],
                'flashlight': [flashlight, False],
                'recording': [recording, False],
                'silent': [silent, False],
                'privacy': [privacy, False],

                # Alarm
                'alarm': [alarm, False],

                # Current event

                'error': [error, False],

                'armed': [armed, False],
                'disarmed': [disarmed, False],

                'sensor_opened': [sensor_opened, False],
                'sensor_closed': [sensor_closed, False],

                'powered_on' : [powered_on, True],

                # Current status

                'armed_status': [armed_status, False],
                'ready_status': [ready_status, False],
                'open_status': [open_status, False],
                'blank' : [blank, True],

                # Unused
                'rainbow': [rainbow_cycle, False],
                'chase_down': [chase_down, False],
                'chase_up': [chase_up, False]}

def cycle():

    if command_list['flashlight'][1] or command_list['alarm'][1] or command_list['rainbow'][1]:
        pixels.brightness = 1

    else:
        pixels.brightness = DEFAULT_BRIGHTNESS

    pixels.fill((0, 0, 0))

    for p in sorted(list(priority_list.keys()))[::-1]:
        for name in priority_list[p]:
            if command_list[name][1]: # state is activated

                if name != 'blank':
                    command_list[name][0]()  # Run the pattern

                overlay = False

                for l in priority_list[-1000]:

                    if command_list[l][1]:
                        command_list[l][0]()

                        overlay = True



                if not overlay and name == 'blank':
                    command_list[name][0]()  # Run the pattern

                pixels.show()

                if p == 10: # Self terminating:
                    return name

                return None
