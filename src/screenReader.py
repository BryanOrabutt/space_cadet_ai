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

    def get_ball_pos(self):
        table = self.screen[44:464, 0:372]
        lptr = 0
        rptr = lptr + self.ball_template.shape[1]
        ball_bbox = [0, 0, 0, 0]
        err_min = 99999
        pos = (0, 0)
        res = cv2.matchTemplate(table, self.ball_template, cv2.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        pos = (min_loc[0]+int(self.ball_template.shape[0]/2), min_loc[1]+int(self.ball_template.shape[1]/2))
        # for col in range(table.shape[1]): #cols
        #     tptr = 0
        #     bptr = tptr + self.ball_template.shape[0]
        #     for row in range(table.shape[0]): #rows
        #         res = cv2.matchTemplate(table[tptr:bptr, lptr:rptr], self.ball_template, cv2.TM_SQDIFF)
        #         min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # find min error
        #         if min_val < err_min:
        #             # pyplot.imshow(table[tptr:bptr, lptr:rptr])
        #             # pyplot.show()
        #             err_min = min_val
        #             pos = (min_loc[0]+6,min_loc[1]+6)
        #         tptr += 1
        #         bptr += 1
        #     lptr += 1
        #     rptr += 1

        self.ball_pos.append(pos)
        return pos


        # blurred = cv2.GaussianBlur(table, (11,11), 0)
        # pyplot.imshow(table)
        # pyplot.show()
        #
        # rgb = cv2.cvtColor(table, cv2.COLOR_BGR2HSV)
        # pyplot.imshow(rgb)
        # pyplot.show()
        #
        # low_thresh = (0, 0, 0)
        # high_thresh = (255, 10, 255)
        # #low_thresh = (170, 0, 89)
        # #high_thresh = (184, 51, 143)
        # mask = cv2.inRange(rgb, low_thresh, high_thresh)
        # kernel = np.ones((3,3), np.uint8)
        # #mask = cv2.erode(mask, kernel, iterations=1)
        # #mask = cv2.dilate(mask, kernel, iterations=2)
        #
        # pyplot.imshow(mask)
        # pyplot.show()
        #
        # contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # contours = imutils.grab_contours(contours)
        #
        # if len(contours) > 0:
        #     for c in contours:
        #         #c = max(contours, key=cv2.contourArea)
        #         ((x, y), r) = cv2.minEnclosingCircle(c)
        #        # if r >= 3 and r <= 10:
        #         approx = cv2.approxPolyDP(c, 0.001*cv2.arcLength(c, True), True)
        #         if(len(approx) > 8):
        #             circ_img = np.zeros((table.shape[0], table.shape[1]), np.uint8)
        #             circ = cv2.circle(circ_img, (int(x), int(y)), int(r), (255,255,255), 2)
        #             avg_color = cv2.mean(table, mask=circ_img)
        #             #cont = cv2.drawContours(table, c, -1, (0, 255, 255), 2)
        #             cv2.circle(table, (int(x), int(y)), int(r), (255,255,0), 2)
        #             print(x,y,avg_color)
        # pyplot.imshow(table)
        # pyplot.show()
