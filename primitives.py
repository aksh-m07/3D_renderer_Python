from OpenGL.GL import *
import math

print("Primitives module imported")

# Global display list IDs
G_OBJ_PLANE = None
G_OBJ_SPHERE = None
G_OBJ_CUBE = None

def init_primitives():
    """Initialize all primitive display lists"""
    global G_OBJ_PLANE, G_OBJ_SPHERE, G_OBJ_CUBE
    
    print("Creating plane display list...")
    # Create plane display list
    G_OBJ_PLANE = glGenLists(1)
    glNewList(G_OBJ_PLANE, GL_COMPILE)
    draw_plane()
    glEndList()
    print(f"Plane display list created: {G_OBJ_PLANE}")
    
    print("Creating sphere display list...")
    # Create sphere display list
    G_OBJ_SPHERE = glGenLists(1)
    glNewList(G_OBJ_SPHERE, GL_COMPILE)
    draw_sphere()
    glEndList()
    print(f"Sphere display list created: {G_OBJ_SPHERE}")
    
    print("Creating cube display list...")
    # Create cube display list
    G_OBJ_CUBE = glGenLists(1)
    glNewList(G_OBJ_CUBE, GL_COMPILE)
    draw_cube()
    glEndList()
    print(f"Cube display list created: {G_OBJ_CUBE}")
    
    print("All primitives initialized successfully!")

def draw_plane():
    """Draw a grid plane exactly like the reference image"""
    print("Drawing plane...")
    
    # Draw the base plane (dark gray like in the image)
    glColor3f(0.3, 0.3, 0.3)  # Dark gray base
    glBegin(GL_QUADS)
    glVertex3f(-15, -15, 0)
    glVertex3f(15, -15, 0)
    glVertex3f(15, 15, 0)
    glVertex3f(-15, 15, 0)
    glEnd()
    
    # Draw grid lines (black like in the image)
    glColor3f(0.0, 0.0, 0.0)  # Pure black lines
    glLineWidth(1.0)
    glBegin(GL_LINES)
    
    # Draw grid lines every 1 unit to create square cells
    for i in range(-15, 16):
        # Vertical lines
        glVertex3f(i, -15, 0)
        glVertex3f(i, 15, 0)
        # Horizontal lines
        glVertex3f(-15, i, 0)
        glVertex3f(15, i, 0)
    
    glEnd()
    print("Plane drawn")

def draw_sphere():
    """Draw a smooth sphere"""
    print("Drawing sphere...")
    glBegin(GL_TRIANGLES)
    # Higher resolution sphere for smoother appearance
    for i in range(20):
        for j in range(20):
            theta1 = i * math.pi / 20
            theta2 = (i + 1) * math.pi / 20
            phi1 = j * 2 * math.pi / 20
            phi2 = (j + 1) * 2 * math.pi / 20
            
            # Create sphere vertices
            x1 = math.sin(theta1) * math.cos(phi1)
            y1 = math.cos(theta1)
            z1 = math.sin(theta1) * math.sin(phi1)
            
            x2 = math.sin(theta1) * math.cos(phi2)
            y2 = math.cos(theta1)
            z2 = math.sin(theta1) * math.sin(phi2)
            
            x3 = math.sin(theta2) * math.cos(phi1)
            y3 = math.cos(theta2)
            z3 = math.sin(theta2) * math.sin(phi1)
            
            x4 = math.sin(theta2) * math.cos(phi2)
            y4 = math.cos(theta2)
            z4 = math.sin(theta2) * math.sin(phi2)
            
            # Draw triangles
            glVertex3f(x1, y1, z1)
            glVertex3f(x2, y2, z2)
            glVertex3f(x3, y3, z3)
            
            glVertex3f(x2, y2, z2)
            glVertex3f(x4, y4, z4)
            glVertex3f(x3, y3, z3)
    glEnd()
    print("Sphere drawn")

def draw_cube():
    """Draw a solid cube aligned with coordinate axes"""
    print("Drawing cube...")
    glBegin(GL_QUADS)
    # Front face (Z positive)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    
    # Back face (Z negative)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    
    # Top face (Y positive)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, -0.5)
    
    # Bottom face (Y negative)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    
    # Right face (X positive)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    
    # Left face (X negative)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glEnd()
    print("Cube drawn")
