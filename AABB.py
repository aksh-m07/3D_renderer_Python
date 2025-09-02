import numpy

print("AABB module imported")

class AABB:
    def __init__(self, min_point, max_point):
        """
        Initialize AABB with min and max points
        min_point: [x, y, z] minimum coordinates
        max_point: [x, y, z] maximum coordinates
        """
        print(f"Creating AABB with min={min_point}, max={max_point}")
        self.min_point = numpy.array(min_point, dtype=float)
        self.max_point = numpy.array(max_point, dtype=float)
        print("AABB created")
    
    def get_center(self):
        """Get the center point of the AABB"""
        return (self.min_point + self.max_point) / 2.0
    
    def get_size(self):
        """Get the size (width, height, depth) of the AABB"""
        return self.max_point - self.min_point
    
    def contains_point(self, point):
        """Check if a point is inside the AABB"""
        point = numpy.array(point)
        return numpy.all(point >= self.min_point) and numpy.all(point <= self.max_point)
    
    def intersects(self, other):
        """Check if this AABB intersects with another AABB"""
        return not (numpy.any(self.max_point < other.min_point) or 
                   numpy.any(self.min_point > other.max_point))
