import numpy
import math

print("Trackball module imported")

class Trackball:
    def __init__(self, theta=0, distance=15):
        print(f"Creating Trackball with theta={theta}, distance={distance}")
        self.theta = theta
        self.phi = 0  # Vertical rotation angle
        self.matrix = numpy.identity(4)
        self.last_x = 0
        self.last_y = 0
        self.update_matrix()
        print("Trackball created")
    
    def update_matrix(self):
        """Update the rotation matrix based on theta and phi"""
        print(f"Updating trackball matrix with theta={self.theta}, phi={self.phi}")
        # Convert angles to radians
        theta_rad = math.radians(self.theta)
        phi_rad = math.radians(self.phi)
        
        # Create rotation matrices
        cos_t = math.cos(theta_rad)
        sin_t = math.sin(theta_rad)
        cos_p = math.cos(phi_rad)
        sin_p = math.sin(phi_rad)
        
        # Rotation around Y-axis (theta)
        rot_y = numpy.array([
            [cos_t, 0, sin_t, 0],
            [0, 1, 0, 0],
            [-sin_t, 0, cos_t, 0],
            [0, 0, 0, 1]
        ])
        
        # Rotation around X-axis (phi)
        rot_x = numpy.array([
            [1, 0, 0, 0],
            [0, cos_p, -sin_p, 0],
            [0, sin_p, cos_p, 0],
            [0, 0, 0, 1]
        ])
        
        # Combine rotations: Y rotation first, then X rotation
        self.matrix = numpy.dot(rot_x, rot_y)
        print(f"Trackball matrix updated: {self.matrix}")
    
    def drag_to(self, x, y, dx, dy):
        """Handle mouse drag to rotate the trackball for full 3D rotation"""
        print(f"Trackball drag: ({x}, {y}) -> ({dx}, {dy})")
        
        # Horizontal movement affects Y-rotation (theta)
        self.theta += dx * 0.5
        
        # Vertical movement affects X-rotation (phi)
        self.phi += dy * 0.5
        
        # Clamp phi to prevent gimbal lock (keep between -89 and 89 degrees)
        self.phi = max(-89, min(89, self.phi))
        
        print(f"New theta: {self.theta}, phi: {self.phi}")
        self.update_matrix()
