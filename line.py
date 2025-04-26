class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update_point(self):
        pass

class Line:
    """ Create Points
    
    """
    def __init__(self, point1: Point, point2: Point):
        self.x1 = point1.x
        self.y1 = point1.y
        self.x2 = point1.x
        self.y2 = point2.y
