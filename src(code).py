from OpenGL.GLUT import *
from OpenGL.GL import *
import numpy
import sys
import random
from collections import defaultdict
import color  # Custom color module
import trackball  # Custom trackball module
import AABB  # Custom AABB module

class Viewer(object):
    def __init__(self):
        """Initialize the viewe"""
        self.init_interface()
        self.init_opengl()
        self.init_scene()
        self.init_interaction()
        init_primitives()

    def init_interface(self):
        """Initialize the the window and register the renderer"""
        glutInit()
        glutInitWindowSize(640, 480)
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        glutDisplayFunc(self.render)
    def init_opengl(self):
        """Initialize the opengl settings to render the scene"""
        self.inverseModelView= numpy.identity(4)
        self.ModelView= numpy.identity(4)

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, GLfloat_4(0.0, 0.0, 1.0, 0.0))
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, GLfloat_3(0, 0, -1))
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)
        glClearColor(0.4, 0.4, 0.4, 0.0)
        
    def init_scene(self):
        """ initialize the scene object and initial scene """
        self.scene = Scene()
        self.create_sample_scene()

    def create_sample_scene(self):
        cube_node = Cube()
        cube_node.translate(2, 0, 2)
        cube_node.color_index = 2
        self.scene.add_node(cube_node)

        sphere_node = Sphere()
        sphere_node.translate(-2, 0, 2)
        sphere_node.color_index = 3
        self.scene.add_node(sphere_node)

        hierarchical_node = SnowFigure()
        hierarchical_node.translate(-2, 0, -2)
        self.scene.add_node(hierarchical_node)

    def init_interaction(self):
        """ init user interaction and callbacks """
        self.interaction = Interaction()
        self.interaction.register_callback('pick', self.pick)
        self.interaction.register_callback('move', self.move)
        self.interaction.register_callback('place', self.place)
        self.interaction.register_callback('rotate_color', self.rotate_color)
        self.interaction.register_callback('scale', self.scale)

    def main_loop(self):
        glutMainLoop()

    def render(self):
        """Render pass for the scene"""
        glEnable(GL_LIGHTING)
        glClear(GL_COLOUR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # Load the modelview matrix from the current state of the trackball
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        loc = self.interaction.get_location()
        glTranslated(loc[0], loc[1], loc[2])
        glMultMatrixf(self.interaction.trackball.matrix)
        # store the inverse of the current modelview.
        currentModelView = numpy.array(glGetFloatv(GL_MODELVIEW_MATRIX))
        self.modelView = numpy.transpose(currentModelView)
        self.inverseModelView = inv(numpy.transpose(currentModelView))

        # render the scene. This will call the render function for each object
        # in the scene
        self.scene.render()
        #draw the grid
        glDisable(GL_LIGHTING)
        glCallList(G_OBJ_PLANE)
        glPopMatrix()
        # flush the buffers so that the scene can be drawn
        glFlush()
    def init_view(self):
        """ initialize the projection matrix """
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        aspect_ratio = float(xSize) / float(ySize)

        # load the projection matrix. Always the same
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glViewport(0, 0, xSize, ySize)
        gluPerspective(70, aspect_ratio, 0.1, 1000.0)
        glTranslated(0, 0, -15)
    
    def get_ray(self, x, y):
        """ 
        Generate a ray beginning at the near plane, in the direction that
        the x, y coordinates are facing 

        Consumes: x, y coordinates of mouse on screen 
        Return: start, direction of the ray 
        """
        self.init_view()

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # get two points on the line.
        start=numpy.array(gluUnProject(x,y,0.001))
        end=numpy.array(gluUnProject(x,y,0.999))

        # convert those points into a ray
        direction = end - start
        direction = direction / numpy.linalg.norm(direction)
        return (start, direction)

    def pick(self, x, y):
        """ Execute pick of an object. Selects an object in the scene. """
        start, direction = self.get_ray(x, y)
        self.scene.pick(start, direction, self.modelView)

    def move(self, x, y):
        """ Execute a move command on the scene. """
        start, direction = self.get_ray(x, y)
        self.scene.move_selected(start, direction, self.inverseModelView)
    def rotate_color(self, forward):
        """ 
        Rotate the color of the selected Node. 
        Boolean 'forward' indicates direction of rotation. 
        """
        self.scene.rotate_selected_color(forward)     
    def scale(self, up):
        """ Scale the selected Node. Boolean up indicates scaling larger."""
        self.scene.scale_selected(up)
    def place(self, shape, x, y):
        """ Execute a placement of a new primitive into the scene. """
        start, direction = self.get_ray(x, y)
        self.scene.place(shape, start, direction, self.inverseModelView)






        
if __name__ == "__main__":
    viewer = Viewer()
    viewer.main_loop()
class Scene(object):
        # the default depth from the camera to place an object at
        PLACE_DEPTH = 15.0
        def __init__(self):
            self.node_list = list()
            # Keep track of the currently selected node.
            # Actions may depend on whether or not something is selected
            self.selected_node = None
            def add_node(self, node):
                """ Add a new node to the scene """
                self.node_list.append(node)

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
        if self.selected_node is not None:
            self.selected_node.select(False)
            self.selected_node = None
        # Keep track of the closest hit.
        mindist=sys.maxint
        closest_node=None
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
        """ 
        Return whether or not the ray hits the object

        Consume:  
        start, direction form the ray to check
        mat is the modelview matrix to transform the ray by 
        """
        newmat=numpy.dot(numpy.dot(mat, self.translation_matrix),numpy.linalg.inv(self.scaling_matrix))
        # transform the modelview matrix by the current translation
        def select(self, select=None):
            """ Toggles or sets selected state """
            if select is not None:
              self.selected = select
            else:
              self.selected = not self.selected
        def rotate_selected_color(self, forwards):
            """ Rotate the color of the currently selected node """
            if self.selected_node is None: return
            self.selected_node.rotate_color(forwards)
        def scale_selected(self, up):
            """ Scale the current selection """
            if self.selected_node is None: return
            self.selected_node.scale(up)
        def move_selected(self, start, direction, inv_modelview):
            """ 
            Move the selected node, if there is one.
                
            Consume: 
            start, direction describes the Ray to move to
            mat is the modelview matrix for the scene 
            """
            if self.selected_node is None: return

            # Find the current depth and location of the selected node
            node = self.selected_node
            depth = node.depth
            oldloc = node.selected_loc

            # The new location of the node is the same depth along the new ray
            newloc = (start + direction * depth)

            # transform the translation with the modelview matrix
            translation = newloc - oldloc
            pre_tran = numpy.array([translation[0], translation[1], translation[2], 0])
            translation = inv_modelview.dot(pre_tran)

            # translate the node and track its location
            node.translate(translation[0], translation[1], translation[2])
            node.selected_loc = newloc
       
        # class Scene
        def place(self, shape, start, direction, inv_modelview):
            """ 
            Place a new node.
                
            Consume:  
            shape the shape to add
            start, direction describes the Ray to move to
            inv_modelview is the inverse modelview matrix for the scene 
            """
            new_node = None
            if shape == 'sphere': new_node = Sphere()
            elif shape == 'cube': new_node = Cube()
            elif shape == 'figure': new_node = SnowFigure()

            self.add_node(new_node)

            # place the node at the cursor in camera-space
            translation = (start + direction * self.PLACE_DEPTH)

            # convert the translation to world-space
            pre_tran = numpy.array([translation[0], translation[1], translation[2], 1])
            translation = inv_modelview.dot(pre_tran)

            new_node.translate(translation[0], translation[1], translation[2])




class Node(object):
    """Base class for scene elements"""
    def __init__(self):
        self.color_index = random.randint(color.MIN_COLOR, color.MAX_COLOR)
        self.aabb= AABB([0.0, 0.0, 0.0], [0.5, 0.5, 0.5])
        self.translation_matrix=numpy.identity(4)
        self.scaling_matrix=numpy.identity(4)
        self.selected = False

    def render(self):
        """Render the item to the screen"""
        glPushMatrix()
        glMultMatrixf(self.transpose(self.translation_matrix))
        glMultMatrixf(self.scaling_matrix)
        cur_color=color.COLORS[self.color_index]
        glColor3f(cur_color[0], cur_color[1], cur_color[2])
        glColor3f(cur_color[0], cur_color[1], cur_color[2])
        if self.selected:  # emit light if the node is selected
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.3, 0.3, 0.3])

        self.render_self()

        if self.selected:
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0])
        glPopMatrix()
    def rotate_color(self, forwards):
        self.color_index += 1 if forwards else -1
        if self.color_index > color.MAX_COLOR:
            self.color_index = color.MIN_COLOR
        if self.color_index < color.MIN_COLOR:
            self.color_index = color.MAX_COLOR

    def scale(self, up):
        s =  1.1 if up else 0.9
        self.scaling_matrix = numpy.dot(self.scaling_matrix, scaling([s, s, s]))
        self.aabb.scale(s)

    def scaling(scale):
        s = numpy.identity(4)
        s[0, 0] = scale[0]
        s[1, 1] = scale[1]
        s[2, 2] = scale[2]
        s[3, 3] = 1
    return s
    def translate(self, x, y, z):
        self.translation_matrix = numpy.dot(
            self.translation_matrix, 
            translation([x, y, z]))
    def translation(displacement):
        t = numpy.identity(4)
        t[0, 3] = displacement[0]
        t[1, 3] = displacement[1]
        t[2, 3] = displacement[2]
        return t


class Primitive(Node):
    def __init__(self):
        super(Primitive, self).__init__()
    def render_self(self):
        glCallList(self.call_list)
class Sphere(Primitive):
    """Sphere primitive"""
    def __init__(self):
        super(Sphere, self).__init__()
        self.call_list=G_OBJ_SPHERE

class Cube(Primitive):
    """ Cube primitive """
    def __init__(self):
        super(Cube, self).__init__()
        self.call_list = G_OBJ_CUBE   

class HierarchicalNode(Node):
    def __init__(self):
        super(HierarchicalNode, self).__init__()
        self.child_nodes = []

    def render_self(self):
        for child in self.child_nodes:
            child.render()
class SnowFigure(HierarchicalNode):
    def __init__(self):
        super(SnowFigure, self).__init__()
        self.child_nodes = [Sphere(), Sphere(), Sphere()]
        self.child_nodes[0].translate(0, -0.6, 0) # scale 1.0
        self.child_nodes[1].translate(0, 0.1, 0)
        self.child_nodes[1].scaling_matrix = numpy.dot(
            self.scaling_matrix, scaling([0.8, 0.8, 0.8]))
        self.child_nodes[2].translate(0, 0.75, 0)
        self.child_nodes[2].scaling_matrix = numpy.dot(
            self.scaling_matrix, scaling([0.7, 0.7, 0.7]))
   
class Interaction(object):
    def __init__(self):
        """ Handles user interaction """
        # currently pressed mouse button
        self.pressed = None
        # the current location of the camera
        self.translation = [0.0, 0.0, 0.0]
        # the trackball to calculate rotation
        self.trackball = trackball.Trackball(theta = -25, distance=15)
        # the current mouse location
        self.mouse_loc = None
        # Unsophisticated callback mechanism
        self.callbacks = defaultdict(list)

        self.register()
    
    def register(self):
        """ register callbacks with glut """
        glutMouseFunc(self.handle_mouse_button)
        glutMotionFunc(self.handle_mouse_motion)
        glutKeyboardFunc(self.handle_keystroke)
        glutSpecialFunc(self.handle_keystroke)

    def translate(self,x,y,z):
        """Translate the camera"""
        self.translation[0] += x
        self.translation[1] += y
        self.translation[2] += z
    
    def handle_mouse_button(self, button, state, x, y):
                """ Called when the mouse button is pressed or released """
                xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
                y=ySize-y
                self.mouse_loc = [x,y]

                if mode==GLUT_DOWN:
                    self.pressed=button
                    if button==GLUT_RIGHT_BUTTON:
                        pass
                    elif button==GLUT_LEFT_BUTTON:#pick
                        self.trigger('pick',x,y)
                    elif button==3:#scroll up
                        self.translate(0,0,1.0)
                    elif button==4:#scroll down
                        self.translate(0,0,-1.0)
                        
                    else: #mouse button release
                        self,pressed=None
                    glutPostRedisplay()

    def handle_mouse_move(self, x, screen_y):
        """ Called when the mouse is moved """
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        y = ySize - screen_y  # invert the y coordinate because OpenGL is inverted
        if self.pressed is not None:
            dx = x - self.mouse_loc[0]
            dy = y - self.mouse_loc[1]
            if self.pressed == GLUT_RIGHT_BUTTON and self.trackball is not None:
                # ignore the updated camera loc because we want to always
                # rotate around the origin
                self.trackball.drag_to(self.mouse_loc[0], self.mouse_loc[1], dx, dy)
            elif self.pressed == GLUT_LEFT_BUTTON:
                self.trigger('move', x, y)
            elif self.pressed == GLUT_MIDDLE_BUTTON:
                self.translate(dx/60.0, dy/60.0, 0)
            else:
                pass
            glutPostRedisplay()
        self.mouse_loc = (x, y)
    def handle_keystroke(self, key, x, y):
        """ Called on keyboard input from the user """
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        y = ySize - screen_y
        if key == 's':
            self.trigger('place', 'sphere', x, y)
        elif key == 'c':
            self.trigger('place', 'cube', x, y)
        elif key == 'f':
            self.trigger('place', 'figure', x, y)
        elif key == GLUT_KEY_UP:
            self.trigger('scale', up=True)
        elif key == GLUT_KEY_DOWN:
            self.trigger('scale', up=False)
        elif key == GLUT_KEY_LEFT:
            self.trigger('rotate_color', forward=True)
        elif key == GLUT_KEY_RIGHT:
            self.trigger('rotate_color', forward=False)
        glutPostRedisplay()
    def register_callback(self, name, func):
        self.callbacks[name].append(func)
    def trigger(self, name, *args, **kwargs):
        for func in self.callbacks[name]:
            func(*args, **kwargs)