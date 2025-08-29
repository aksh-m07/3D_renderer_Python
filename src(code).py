from OpenGL.GLUT import *
from OpenGL.GL import *
import numpy

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




        
if __name__ == "__main__":
    viewer = Viewer()
    viewer.main_loop()]
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
   




    