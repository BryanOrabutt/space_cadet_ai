import cv2

class RewardGate:

    def __init__(self, tier=0, p=[(0,0), (0,0)]):
        self.tier = tier
        self.points = p

    def crossed(self, point, radius):
        x1, x2, x3 = self.points[0][0], self.points[1][0], point[0]
        y1, y2, y3 = self.points[0][1], self.points[1][1], point[1]

        slope = (y2-y1)/(x2-x1)

        on_line = abs(((y3-y1) - slope*(x3-x1))) > radius
        between_points = (min(x1,x2) <= x3 <= max(x1, x2)) and (min(y1, y2) <= y3 <= max(y1, y2))

        return on_line and between_points

    def draw_gate(self, screen, crossed):
        if crossed:
            cv2.line(screen, self.points[0], self.points[1], color=(0,0,255), thickness=2)
        else:
            cv2.line(screen, self.points[0], self.points[1], color=(0,255,0), thickness=2)


