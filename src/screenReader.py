from PIL import ImageGrab
import cv2
from win32gui import FindWindow, GetWindowRect
import numpy as np
import math
import matplotlib.pyplot as pyplot
from collections import deque
import imutils


class ScreenReader:

    def __init__(self):
        window_title = '3D Pinball for Windows - Space Cadet'
        window_handle = FindWindow(None, window_title)
        window_dim = GetWindowRect(window_handle)

        self.screen = np.array(ImageGrab.grab(bbox=window_dim))
        self.screen = cv2.cvtColor(self.screen, cv2.COLOR_BGR2BGRA)
        self.score = 0

        score_x = [430, 585]
        score_y = [234, 274]
        self.score_box = self.screen[score_y[0]:score_y[1], score_x[0]:score_x[1]]

        self.digit_template = []
        for k in range(10):
            self.digit_template.append(cv2.imread(
                r'C:\Users\frien\PycharmProjects\space_cadet_ai\digit_references\dig%d.png' % (k)))
            self.digit_template[k] = cv2.cvtColor(self.digit_template[k], cv2.COLOR_BGR2BGRA)  # convert template to BGRA to match digit color map

        self.ball_pos = deque(maxlen=20)
        self.ball_template = cv2.imread(r'C:\Users\frien\PycharmProjects\space_cadet_ai\digit_references\ball_center.png')
        self.ball_template = cv2.cvtColor(self.ball_template, cv2.COLOR_BGR2BGRA)
        self.update_rate = 25 #milliseconds

    def set_update_rate(self, rate):
        self.update_rate = rate

    def get_update_rate(self):
        return self.update_rate

    def get_window(self):
        window_title = '3D Pinball for Windows - Space Cadet'
        window_handle = FindWindow(None, window_title)
        window_dim = GetWindowRect(window_handle)

        self.screen = np.array(ImageGrab.grab(bbox=window_dim))
        self.screen = cv2.cvtColor(self.screen, cv2.COLOR_BGR2BGRA)
        return self.screen

    def get_score_box(self):
        return self.score_box

    def process_score(self):
        digit_bbox = [5, 8, 140, 32]  # x1,y1,x2,y2
        digit_w = 15  # width of a single digit
        digit_h = digit_bbox[3]-digit_bbox[1] #height of a single digit
        max_digits = int(math.floor((digit_bbox[2] - digit_bbox[0]) / digit_w))  # max digits that can fit in score area

        digits = []  # ROI for each digit in score
        rptr = digit_bbox[2]  # right edge of current ROI

        for i in range(max_digits):
            lptr = rptr - digit_w  # left edge of ROI
            digit = self.score_box[digit_bbox[1]:digit_bbox[3], lptr:rptr]  # get ROI for next digit
            digits.append(digit)
            rptr = lptr  # right ROI edge now becomes left edge for next ROI

        digits = np.array(digits)  # convert list to numpy array
        count = 0
        self.score = 0
        for i in digits:
            err_min = 999999  # minimum error in the convolution between digit and template
            best_match = -1  # best matching numeral for the digit
            for k in range(10):  # loop over template images and convolve with digit, computing MSE
                res = cv2.matchTemplate(i, self.digit_template[k], cv2.TM_SQDIFF_NORMED)  # convolve the images
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # find min error
                if min_val < err_min:  # if error got smaller update min error and best matching numeral
                    err_min = min_val
                    best_match = k
            if err_min < 0.1:  # if there are not 9 digits (max) then exclude the blank digits which have high error
                self.score += best_match * 10 ** count
            count += 1
        return self.score

    def get_ball_velocity(self):
        sx = (self.ball_pos[0][0], self.ball_pos[1][0]) #current and prev x position
        sy = (self.ball_pos[0][1], self.ball_pos[1][1]) #current and prev y position
        v = ((sx[0]-sx[1])/self.update_rate, (sy[0]-sy[1])/self.update_rate)
        return v

    def get_ball_pos(self):
        table = self.screen[44:464, 0:372]
        res = cv2.matchTemplate(table, self.ball_template, cv2.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        pos = self.ball_pos[0] if len(self.ball_pos) > 0 else (0, 0)
        if min_val < 0.05:
            pos = (min_loc[0]+int(self.ball_template.shape[0]/2), min_loc[1]+int(self.ball_template.shape[1]/2))

        self.ball_pos.appendleft(pos)
        return pos