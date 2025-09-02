from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy
import sys
import random
from collections import defaultdict
import color  # Custom color module
import trackball  # Custom trackball module
import AABB  # Custom AABB module

# Import primitives module
from primitives import init_primitives

# Scene class definition
class Scene(object):
    # the default depth from the camera to place an object at
    PLACE_DEPTH = 15.0
    def __init__(self):
        print("Creating Scene object...")
        self.node_list = list()
        # Keep track of the currently selected node.
        # Actions may depend on whether or not something is selected
        self.selected_node = None
        print("Scene object created")
    
    def add_node(self, node):
        """ Add a new node to the scene """
        print(f"Adding node {type(node).__name__} to scene")
        self.node_list.append(node)
        print(f"Scene now has {len(self.node_list)} nodes")

    def render(self):
        """ Render the scene. """
        for node in self.node_list:
            node.render()
    
    def pick(self, start, direction, mat):
        """ 
        Execute selection.
            
        start, direction describe a Ray. 
        mat is the inverse of the current modelview matrix for the scene.
        """
        print(f"Scene pick called with start={start}, direction={direction}")
        if self.selected_node is not None:
            self.selected_node.select(False)
            self.selected_node = None
        # Keep track of the closest hit.
        mindist = sys.maxsize
        closest_node = None
        for node in self.node_list:
            hit, distance = node.pick(start, direction, mat)
            if hit and distance < mindist:
                mindist, closest_node = distance, node

        # If we hit something, keep track of it.
        if closest_node is not None:
            closest_node.select()
            closest_node.depth = mindist
            closest_node.selected_loc = start + direction * mindist
            self.selected_node = closest_node
            print(f"Selected node: {type(closest_node).__name__}")
        else:
            print("No node selected")

# Node class definition
class Node(object):
    """Base class for scene elements"""
    def __init__(self):
        self.color_index = random.randint(color.MIN_COLOR, color.MAX_COLOR)
        self.aabb = AABB.AABB([0.0, 0.0, 0.0], [0.5, 0.5, 0.5])
        self.translation_matrix = numpy.identity(4)
        self.scaling_matrix = numpy.identity(4)
        self.selected = False
        print(f"Node created with color index {self.color_index}")

    def render(self):
        """Render the item to the screen"""
        
        # Save current matrix
        glPushMatrix()
        
        # Apply transformations
        glMultMatrixf(numpy.transpose(self.translation_matrix))  # Restore transpose - OpenGL needs column-major order
        glMultMatrixf(self.scaling_matrix)
        
        # Debug: Print transformation info
        print(f"Rendering {type(self).__name__} at position: ({self.translation_matrix[0, 3]:.2f}, {self.translation_matrix[1, 3]:.2f}, {self.translation_matrix[2, 3]:.2f})")
        
        # Set color
        cur_color = color.COLORS[self.color_index]
        glColor3f(cur_color[0], cur_color[1], cur_color[2])
        
        # Set material properties for matte appearance
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])  # No specular for matte look
        glMaterialf(GL_FRONT, GL_SHININESS, 0.0)
        
        # Handle selection highlighting
        if self.selected:  # emit light if the node is selected
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.3, 0.3, 0.3])

        # Render the actual object
        self.render_self()

        # Reset emission if selected
        if self.selected:
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0])
        
        # Restore matrix
        glPopMatrix()
    
    def render_self(self):
        """Override this method in subclasses"""
        pass
    
    def pick(self, start, direction, mat):
        """Default pick method - override in subclasses"""
        print(f"Default pick method called for {type(self).__name__}")
        return False, 0
    
    def select(self, select=None):
        """ Toggles or sets selected state """
        if select is not None:
            self.selected = select
        else:
            self.selected = not self.selected
        print(f"Node selected: {self.selected}")
    
    def translate(self, x, y, z):
        """Translate the node"""
        print(f"Translating node by ({x}, {y}, {z})")
        self.translation_matrix[0, 3] += x
        self.translation_matrix[1, 3] += y
        self.translation_matrix[2, 3] += z
        print(f"Translation matrix: {self.translation_matrix[:3, 3]}")
    
    def scale(self, s):
        """Scale the node"""
        self.scaling_matrix = numpy.dot(self.scaling_matrix, scaling([s, s, s]))
    
    def rotate_color(self, forwards):
        """Rotate through colors"""
        print(f"Rotating color {'forward' if forwards else 'backward'}")
        if forwards:
            self.color_index += 1
        else:
            self.color_index -= 1
        
        if self.color_index > color.MAX_COLOR:
            self.color_index = color.MIN_COLOR
        if self.color_index < color.MIN_COLOR:
            self.color_index = color.MAX_COLOR
        print(f"New color index: {self.color_index}")

# Primitive class definition
class Primitive(Node):
    def __init__(self):
        super(Primitive, self).__init__()
        print(f"Primitive created: {type(self).__name__}")
    
    def render_self(self):
        if hasattr(self, 'call_list') and self.call_list is not None:
            print(f"Rendering {type(self).__name__} with call_list: {self.call_list}")
            glCallList(self.call_list)
        else:
            print(f"Warning: {type(self).__name__} has no valid call_list")

# Sphere class definition
class Sphere(Primitive):
    """Sphere primitive"""
    def __init__(self):
        super(Sphere, self).__init__()
        import primitives
        self.call_list = primitives.G_OBJ_SPHERE
        print(f"Sphere created with call_list: {self.call_list}")

# Cube class definition
class Cube(Primitive):
    """ Cube primitive """
    def __init__(self):
        super(Cube, self).__init__()
        import primitives
        self.call_list = primitives.G_OBJ_CUBE
        print(f"Cube created with call_list: {self.call_list}")

# HierarchicalNode class definition
class HierarchicalNode(Node):
    def __init__(self):
        super(HierarchicalNode, self).__init__()
        self.child_nodes = []
        print(f"HierarchicalNode created: {type(self).__name__}")

    def render_self(self):
        for child in self.child_nodes:
            child.render()

# SnowFigure class definition
class SnowFigure(HierarchicalNode):
    def __init__(self):
        super(SnowFigure, self).__init__()
        print("Creating SnowFigure...")
        self.child_nodes = [Sphere(), Sphere(), Sphere()]
        # Adjust child positions to account for Y=5 base position (so they appear high above grid)
        self.child_nodes[0].translate(0, 4.4, 0)  # Y = 5 - 0.6 = 4.4 (high above grid)
        self.child_nodes[1].translate(0, 5.1, 0)  # Y = 5 + 0.1 = 5.1 (high above grid)
        self.child_nodes[1].scaling_matrix = numpy.dot(
            self.scaling_matrix, scaling([0.8, 0.8, 0.8]))
        self.child_nodes[2].translate(0, 5.75, 0)  # Y = 5 + 0.75 = 5.75 (high above grid)
        self.child_nodes[2].scaling_matrix = numpy.dot(
            self.scaling_matrix, scaling([0.7, 0.7, 0.8]))
        print(f"SnowFigure created with {len(self.child_nodes)} child nodes")

# Interaction class definition
class Interaction(object):
    def __init__(self):
        """ Handles user interaction """
        print("Creating Interaction object...")
        # currently pressed mouse button
        self.pressed = None
        # the current location of the camera
        self.translation = [0.0, 0.0, 0.0]
        # the trackball to calculate rotation
        self.trackball = trackball.Trackball(theta=-25, distance=15)
        # the current mouse location
        self.mouse_loc = None
        # Unsophisticated callback mechanism
        self.callbacks = defaultdict(list)

        self.register()
        print("Interaction object created")
    
    def register(self):
        """ register callbacks with glut """
        print("Registering GLUT callbacks...")
        glutMouseFunc(self.handle_mouse_button)
        glutMotionFunc(self.handle_mouse_motion)
        glutKeyboardFunc(self.handle_keystroke)
        glutSpecialFunc(self.handle_keystroke)
        print("GLUT callbacks registered")

    def translate(self, x, y, z):
        """Translate the camera"""
        print(f"Camera translating by ({x}, {y}, {z})")
        self.translation[0] += x
        self.translation[1] += y
        self.translation[2] += z
        print(f"Camera position: {self.translation}")
    
    def get_location(self):
        """Get the current camera location"""
        print(f"Getting camera location: {self.translation}")
        return self.translation
    
    def zoom_in(self):
        """Zoom in by moving camera closer"""
        print("Zooming in...")
        self.translate(0, 0, -2.0)  # Move camera closer (negative Z)
        print(f"Camera position after zoom in: {self.translation}")
    
    def zoom_out(self):
        """Zoom out by moving camera further away"""
        print("Zooming out...")
        self.translate(0, 0, 2.0)  # Move camera further (positive Z)
        print(f"Camera position after zoom out: {self.translation}")
    
    def handle_mouse_button(self, button, state, x, y):
        """ Called when the mouse button is pressed or released """
        print(f"Mouse button: {button}, state: {state}, position: ({x}, {y})")
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        y = ySize - y
        self.mouse_loc = [x, y]
        print(f"Converted position: ({x}, {y})")

        if state == GLUT_DOWN:
            self.pressed = button
            print(f"Button pressed: {button}")
            if button == GLUT_RIGHT_BUTTON:
                pass
            elif button == GLUT_LEFT_BUTTON:  # pick
                self.trigger('pick', x, y)
            elif button == 3:  # scroll up (trackpad zoom in)
                self.zoom_in()
            elif button == 4:  # scroll down (trackpad zoom out)
                self.zoom_out()
            else:  # mouse button release
                self.pressed = None
            glutPostRedisplay()
    
    def handle_mouse_motion(self, x, y):
        """ Called when the mouse is moved """
        print(f"Mouse motion: ({x}, {y})")
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        y = ySize - y
        print(f"Converted motion: ({x}, {y})")
        
        if self.pressed is not None:
            dx = x - self.mouse_loc[0]
            dy = y - self.mouse_loc[1]
            print(f"Mouse delta: ({dx}, {dy})")
            
            if self.pressed == GLUT_LEFT_BUTTON and self.trackball is not None:
                # Left button for 3D rotation - full 360 degree rotation
                self.trackball.drag_to(self.mouse_loc[0], self.mouse_loc[1], dx, dy)
                glutPostRedisplay()
            elif self.pressed == GLUT_RIGHT_BUTTON:
                # Right button for panning
                self.translate(dx/60.0, -dy/60.0, 0)
                glutPostRedisplay()
            elif self.pressed == GLUT_MIDDLE_BUTTON:
                # Middle button for zooming
                self.translate(0, 0, dy/60.0)
                glutPostRedisplay()
            else:
                pass
        self.mouse_loc = (x, y)
    
    def handle_keystroke(self, key, x, y):
        """ Handle keyboard input """
        print(f"Key pressed: {key}")
        if key == GLUT_KEY_UP:
            self.translate(0, 1, 0)
        elif key == GLUT_KEY_DOWN:
            self.translate(0, -1, 0)
        elif key == GLUT_KEY_LEFT:
            self.translate(-1, 0, 0)
        elif key == GLUT_KEY_RIGHT:
            self.translate(1, 0, 0)
        glutPostRedisplay()
    
    def register_callback(self, name, func):
        print(f"Registering callback: {name} -> {func.__name__}")
        self.callbacks[name].append(func)
    
    def trigger(self, name, *args, **kwargs):
        print(f"Triggering callback: {name} with args: {args}, kwargs: {kwargs}")
        for func in self.callbacks[name]:
            func(*args, **kwargs)

# Utility functions
def scaling(scale):
    """Create a scaling matrix"""
    print(f"Creating scaling matrix: {scale}")
    return numpy.array([
        [scale[0], 0, 0, 0],
        [0, scale[1], 0, 0],
        [0, 0, scale[2], 0],
        [0, 0, 0, 1]
    ])

# Viewer class definition
class Viewer(object):
    def __init__(self):
        """Initialize the viewer"""
        print("Viewer __init__ started")
        self.init_interface()
        self.init_opengl()
        print("Initializing primitives...")
        init_primitives()
        print("Primitives initialized")
        self.init_scene()
        self.init_interaction()
        self.init_view()
        print("View initialized")
        print("Viewer __init__ completed")

    def init_interface(self):
        """Initialize the the window and register the renderer"""
        print("Initializing GLUT interface...")
        glutInit()
        glutInitWindowSize(640, 480)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutCreateWindow("3D Renderer - Left: Rotate, Right: Pan, Middle: Pan, Trackpad: Zoom")
        glutDisplayFunc(self.render)
        print("GLUT interface initialized")
    
    def init_opengl(self):
        """Initialize the opengl settings to render the scene"""
        print("Initializing OpenGL...")
        self.inverseModelView = numpy.identity(4)
        self.ModelView = numpy.identity(4)

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 10.0, 10.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.6, 0.6, 0.6, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)
        glClearColor(0.4, 0.4, 0.4, 0.0)  # Medium gray background like in image
        print("OpenGL initialized")
        
    def init_scene(self):
        """ initialize the scene object and initial scene """
        print("Initializing scene...")
        self.scene = Scene()
        self.create_sample_scene()
        print("Scene initialized")

    def create_sample_scene(self):
        # Red sphere on the left side (negative X) - moved high above grid
        sphere_node = Sphere()
        sphere_node.translate(-3, 5, 0)  # Y=5 to move high above grid
        sphere_node.color_index = 0  # Red color
        self.scene.add_node(sphere_node)
        print(f"Added red sphere at position (-3, 5, 0)")
        print(f"  Final sphere position: ({sphere_node.translation_matrix[0, 3]:.1f}, {sphere_node.translation_matrix[1, 3]:.1f}, {sphere_node.translation_matrix[2, 3]:.1f})")

        # Blue cube on the right side (positive X) - moved high above grid
        cube_node = Cube()
        cube_node.translate(3, 5, 0)  # Y=5 to move high above grid
        cube_node.color_index = 2  # Blue color
        self.scene.add_node(cube_node)
        print(f"Added blue cube at position (3, 5, 0)")
        print(f"  Final cube position: ({cube_node.translation_matrix[0, 3]:.1f}, {cube_node.translation_matrix[1, 3]:.1f}, {cube_node.translation_matrix[2, 3]:.1f})")

        # White snow figure (stacked spheres) on the left-back - moved high above grid
        hierarchical_node = SnowFigure()
        hierarchical_node.translate(-3, 5, -3)  # Y=5 to move high above grid
        hierarchical_node.color_index = 6  # White color
        self.scene.add_node(hierarchical_node)
        print(f"Added white snow figure at position (-3, 5, -3)")
        print(f"  Final snow figure position: ({hierarchical_node.translation_matrix[0, 3]:.1f}, {hierarchical_node.translation_matrix[1, 3]:.1f}, {hierarchical_node.translation_matrix[2, 3]:.1f})")
        
        print(f"Scene created with {len(self.scene.node_list)} objects")

    def init_interaction(self):
        """ init user interaction and callbacks """
        print("Initializing interaction...")
        self.interaction = Interaction()
        self.interaction.register_callback('pick', self.pick)
        self.interaction.register_callback('move', self.move)
        self.interaction.register_callback('place', self.place)
        self.interaction.register_callback('rotate_color', self.rotate_color)
        self.interaction.register_callback('scale', self.scale)
        print("Interaction initialized")

    def main_loop(self):
        print("Starting main loop...")
        glutMainLoop()

    def render(self):
        """Render pass for the scene"""
        glEnable(GL_LIGHTING)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Reset matrix stack to avoid overflow
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Position camera to match the photo exactly: elevated view looking down at the scene
        glTranslated(0, -6, -20)
        
        # Apply trackball rotation for full 360-degree 3D rotation
        if hasattr(self, 'interaction') and hasattr(self.interaction, 'trackball'):
            glMultMatrixf(self.interaction.trackball.matrix)
        
        # Apply camera translation
        if hasattr(self, 'interaction') and hasattr(self.interaction, 'get_location'):
            loc = self.interaction.get_location()
            glTranslated(loc[0], loc[1], loc[2])
        
        # Store the inverse of the current modelview.
        currentModelView = numpy.array(glGetFloatv(GL_MODELVIEW_MATRIX))
        self.modelView = numpy.transpose(currentModelView)
        self.inverseModelView = numpy.linalg.inv(numpy.transpose(currentModelView))

        # Render the scene. This will call the render function for each object
        # in the scene
        if hasattr(self, 'scene'):
            print(f"Rendering scene with {len(self.scene.node_list)} nodes")
            self.scene.render()
            print("Scene rendering completed")
        else:
            print("Warning: No scene to render")
        
        # Draw the grid
        glDisable(GL_LIGHTING)
        import primitives
        print("Drawing grid plane...")
        glCallList(primitives.G_OBJ_PLANE)
        print("Grid plane drawn")
        
        # Draw coordinate axes
        print("Drawing coordinate axes...")
        self.draw_coordinate_axes()
        print("Coordinate axes drawn")
        
        # Swap buffers for double buffering
        glutSwapBuffers()
    
    def draw_coordinate_axes(self):
        """Draw X, Y, Z coordinate axes"""
        import primitives
        
        print("  Drawing Y-axis...")
        glLineWidth(2.0)
        
        # Y-axis (vertical, green) - extends to top of grid
        glBegin(GL_LINES)
        glColor3f(0.0, 1.0, 0.0)  # Green
        glVertex3f(0, 0, 0)
        glVertex3f(0, 15, 0)
        glEnd()
        print("  Y-axis drawn")
        
        # X-axis (horizontal, green) - extends to right edge of grid
        print("  Drawing X-axis...")
        glBegin(GL_LINES)
        glColor3f(0.0, 1.0, 0.0)  # Green
        glVertex3f(0, 0, 0)
        glVertex3f(15, 0, 0)
        glEnd()
        print("  X-axis drawn")
        
        # Z-axis (depth, green) - extends to back edge of grid
        print("  Drawing Z-axis...")
        glBegin(GL_LINES)
        glColor3f(0.0, 1.0, 0.0)  # Green
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 15)
        glEnd()
        print("  Z-axis drawn")
        
        # Draw axis labels with colored cubes and text indicators
        # Y-axis marker (green cube to match Y-axis color)
        print("  Drawing Y-axis marker...")
        glPushMatrix()
        glTranslated(0, 15.2, 0)
        glColor3f(0.0, 1.0, 0.0)  # Green to match Y-axis
        glCallList(primitives.G_OBJ_CUBE)
        glPopMatrix()
        print("  Y-axis marker drawn")
        
        # X-axis marker (green cube to match X-axis color)
        print("  Drawing X-axis marker...")
        glPushMatrix()
        glTranslated(15.2, 0, 0)
        glColor3f(0.0, 1.0, 0.0)  # Green to match X-axis
        glCallList(primitives.G_OBJ_CUBE)
        glPopMatrix()
        print("  X-axis marker drawn")
        
        # Z-axis marker (green cube to match Z-axis color)
        print("  Drawing Z-axis marker...")
        glPushMatrix()
        glTranslated(0, 0, 15.2)
        glColor3f(0.0, 1.0, 0.0)  # Green to match Z-axis
        glCallList(primitives.G_OBJ_CUBE)
        glPopMatrix()
        print("  Z-axis marker drawn")
        
        # Text labels temporarily disabled to fix blank page issue
        # TODO: Re-enable text labels once rendering is working
        
        # Note: The green cubes at the ends of the axes are now labeled with "X", "Y", "Z" text
        # Green cube at (15.2, 0, 0) = X-axis marker with "X" label
        # Green cube at (0, 15.2, 0) = Y-axis marker with "Y" label
        # Green cube at (0, 0, 15.2) = Z-axis marker with "Z" label
        
        glLineWidth(1.0)  # Reset line width
    
    def init_view(self):
        """ initialize the projection matrix """
        print("Initializing view...")
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        aspect_ratio = float(xSize) / float(ySize)
        print(f"Window size: {xSize}x{ySize}, aspect ratio: {aspect_ratio}")

        # load the projection matrix. Always the same
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glViewport(0, 0, xSize, ySize)
        gluPerspective(70, aspect_ratio, 0.1, 1000.0)
        
        # Reset to MODELVIEW mode
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslated(0, -6, -20)
        print("View initialized")
    
    def pick(self, x, y):
        """Handle pick events"""
        print(f"Viewer pick called with ({x}, {y})")
        pass
    
    def move(self, x, y):
        """Handle move events"""
        print(f"Viewer move called with ({x}, {y})")
        pass
    
    def place(self, x, y):
        """Handle place events"""
        print(f"Viewer place called with ({x}, {y})")
        pass
    
    def rotate_color(self, x, y):
        """Handle color rotation events"""
        print(f"Viewer rotate_color called with ({x}, {y})")
        pass
    
    def scale(self, x, y):
        """Handle scale events"""
        print(f"Viewer scale called with ({x}, {y})")
        pass

# Main execution
if __name__ == "__main__":
    print("Starting 3D Renderer...")
    try:
        viewer = Viewer()
        print("Viewer created, starting main loop...")
        viewer.main_loop()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("Program terminated due to error")
    finally:
        print("Program execution completed")
        print("Goodbye!")
        