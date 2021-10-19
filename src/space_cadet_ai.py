from screenReader import ScreenReader
import time
import cv2
from matplotlib import pyplot

screen = ScreenReader()
pyplot.imshow(screen.get_window()[44:464, 0:372])
pyplot.show()

t0 = time.time()
score = screen.process_score()
t1 = time.time()
print(t1-t0)
print(score)

t0 = time.time()
pos = screen.get_ball_pos()
t1 = time.time()
print(t1-t0)
print(pos)

#gates = [[(110, 251), (114, 220)], [(134, 190), (156, 183)], [(116, 156), (123, 146)], [(73, 156), (51, 155)],
#

while True:
    img = screen.get_window()[44:464, 0:372]
    pos = screen.get_ball_pos()
    cv2.circle(img, pos, 6, (0,255,0),2)
    cv2.imshow("Ball tracker", img)
    key = cv2.waitKey(15)
    if key & 0xFF is ord('q'):
            break