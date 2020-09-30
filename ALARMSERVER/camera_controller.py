import cv2
import datetime
import mail_controller
import time
import threading
import numpy as np
import traceback

# Camera object
class TeleopCam:

    # ID name, frame width, frame height, (enforced frame size tuple), rotation angle, points for line overlay
    # Enforced is the size CV tells the webcam to use
    # Frame w and h is the size of the frame that the obj will return after processing
    def __init__(self, id, w, h, rotation):
        self.id = id
        self.w = w
        self.h = h
        self.rotation = rotation

        # Establish CV video caputre
        self.capture = cv2.VideoCapture(self.id)

        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

        self.keepOnlineThread = threading.Thread(target=self.keepOnline, args=())
        self.keepOnlineThread.start()

    def keepOnline(self):

        print('Keep online thread is online')

        while True:
            if self.capture.isOpened() and self.capture.read()[0]:
                #print('Yay, camera is online!', self.capture.read())

                pass

            else:
                print('Camera is not online.')

                #mail_controller.send_mail('Camera will reinitialize',
                #                      'The camera is not online. The camera will be reinitialized',
                #                      [])

                try:
                    self.capture.release()



                    self.capture = cv2.VideoCapture(self.id)

                    print('Successfully reinitialized')
                except:
                    print('Failed to reinitialized, trying again')

            time.sleep(1)


    def drawTextWithBG(self, img, text):
        # Courtesy of https://gist.github.com/aplz/fd34707deffb208f367808aade7e5d5c

        font_scale = 0.5
        font = cv2.FONT_HERSHEY_SIMPLEX

        # set the rectangle background to white
        rectangle_bgr = (255, 255, 255)

        # get the width and height of the text box
        (text_width, text_height) = cv2.getTextSize(text, font, fontScale=font_scale, thickness=1)[0]
        # set the text start position
        text_offset_x = 10
        text_offset_y = img.shape[0] - 25
        # make the coords of the box with a small padding of two pixels
        box_coords = ((text_offset_x, text_offset_y), (text_offset_x + text_width - 2, text_offset_y - text_height - 2))
        cv2.rectangle(img, box_coords[0], box_coords[1], rectangle_bgr, cv2.FILLED)
        cv2.putText(img, text, (text_offset_x, text_offset_y), font, fontScale=font_scale, color=(0, 0, 0), thickness=1)


    def getFrame(self):


        rc, img = self.capture.read()

        if self.rotation == 90:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif self.rotation == 180:
            img = cv2.rotate(img, cv2.ROTATE_180)

        self.drawTextWithBG(img, str(datetime.datetime.now()))

        return [rc, img]
