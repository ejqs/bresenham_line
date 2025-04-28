# Processes Points and Generates
class BresenhamPoints:
    def __init__(self):
        self.lines = []  # Store multiple lines as sets of points
    
    def add_line(self, points):
        """Add a new line (list of points) to the collection"""
        self.lines.append(points)
    
    def get_all_points(self):
        """Get all points from all lines"""
        all_points = []
        for line in self.lines:
            all_points.extend(line)
        return all_points

def bresenham_line(x0, y0, x1, y1):
    """
    Implements Bresenham's line algorithm
    Returns a list of points from (x0, y0) to (x1, y1)
    """
    points = []
    
    # Handle vertical lines
    if x0 == x1:
        start_y = min(y0, y1)
        end_y = max(y0, y1)
        for y in range(start_y, end_y + 1):
            points.append((x0, y))
        return points
    
    # Handle horizontal lines
    if y0 == y1:
        start_x = min(x0, x1)
        end_x = max(x0, x1)
        for x in range(start_x, end_x + 1):
            points.append((x, y0))
        return points
    
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            if x0 == x1:
                break
            err -= dy
            x0 += sx
        if e2 < dx:
            if y0 == y1:
                break
            err += dx
            y0 += sy
    
    return points