# 3D Renderer in Python

A real-time 3D rendering application built with Python and OpenGL, featuring interactive camera controls, hierarchical scene graphs, and primitive object rendering.

## About

This project is a 3D graphics renderer that demonstrates fundamental computer graphics concepts including:

- **3D Scene Management**: Hierarchical node-based scene graph system for organizing and rendering 3D objects
- **Interactive Camera Controls**: Trackball-based camera rotation, panning, and zooming
- **Primitive Rendering**: Support for basic 3D primitives (spheres, cubes) with customizable colors and transformations
- **Object Selection**: Ray-casting based object picking and selection system
- **Matrix Transformations**: Full 4x4 matrix transformations for translation, rotation, and scaling
- **OpenGL Integration**: Direct OpenGL rendering with proper lighting, depth testing, and face culling

The renderer uses a modular architecture with separate classes for scene management, nodes, primitives, and user interaction, making it easy to extend with new object types and features.

## Features

- 🎨 **Multiple 3D Primitives**: Spheres, cubes, and custom hierarchical objects (e.g., snowman)
- 🎮 **Interactive Controls**: 
  - Left mouse button: Rotate camera (360° trackball rotation)
  - Right mouse button: Pan camera
  - Middle mouse button: Zoom
  - Trackpad scroll: Zoom in/out
- 🌈 **Color System**: Predefined color palette with color rotation support
- 🔍 **Object Selection**: Click to select objects with visual highlighting
- 📐 **Coordinate System**: Visual grid plane and coordinate axes (X, Y, Z)
- 💡 **Lighting**: Configurable OpenGL lighting with ambient and diffuse components
- 🎯 **Hierarchical Objects**: Support for compound objects with parent-child relationships

## Installation

### Prerequisites

- Python 3.7 or higher
- OpenGL-compatible graphics drivers

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd 3D_renderer_Python
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

The required packages are:
- `PyOpenGL==3.1.7` - OpenGL bindings for Python
- `PyOpenGL-accelerate==3.1.7` - Accelerated OpenGL operations
- `numpy==1.24.3` - Matrix operations and numerical computations

## Usage

Run the renderer:
```bash
python src.py
```

The application will open a window displaying a 3D scene with:
- A red sphere on the left
- A blue cube on the right
- A white snowman (hierarchical object) in the back-left
- A grid plane and coordinate axes

## Controls

| Input | Action |
|-------|--------|
| **Left Mouse Button + Drag** | Rotate camera around scene (trackball) |
| **Right Mouse Button + Drag** | Pan camera (move view) |
| **Middle Mouse Button + Drag** | Zoom in/out |
| **Trackpad Scroll Up** | Zoom in |
| **Trackpad Scroll Down** | Zoom out |
| **Arrow Keys** | Pan camera (up/down/left/right) |

## Project Structure

```
3D_renderer_Python/
├── src.py              # Main renderer application
├── primitives.py       # OpenGL primitive definitions (sphere, cube, plane)
├── color.py            # Color palette definitions
├── trackball.py        # Trackball camera rotation implementation
├── AABB.py             # Axis-Aligned Bounding Box for collision detection
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Architecture

### Core Classes

- **`Viewer`**: Main application class that initializes OpenGL, manages the scene, and handles rendering
- **`Scene`**: Manages the collection of nodes in the 3D scene
- **`Node`**: Base class for all scene objects with transformation matrices
- **`Primitive`**: Base class for renderable 3D primitives (Sphere, Cube)
- **`HierarchicalNode`**: Node that can contain child nodes (e.g., SnowFigure)
- **`Interaction`**: Handles mouse and keyboard input, camera controls

### Matrix System

The renderer uses two matrix stacks:
- **PROJECTION Matrix**: Defines camera perspective and view frustum
- **MODELVIEW Matrix**: Handles object transformations and camera positioning

Transformations are applied using 4x4 homogeneous matrices for translation, rotation, and scaling.

## Technical Details

### Rendering Pipeline

1. **Initialization**: Set up OpenGL context, lighting, and viewport
2. **Projection Setup**: Configure perspective projection matrix
3. **Modelview Setup**: Apply camera transformations (position, rotation)
4. **Object Rendering**: For each node:
   - Push matrix stack
   - Apply object transformations
   - Set material properties
   - Render geometry
   - Pop matrix stack
5. **Grid & Axes**: Render coordinate system visualization
6. **Buffer Swap**: Display rendered frame

### Features Implemented

- **Face Culling**: Back-face culling for performance optimization
- **Depth Testing**: Proper Z-buffer depth sorting
- **Lighting**: Phong-style lighting with ambient and diffuse components
- **Material Properties**: Configurable surface materials (matte appearance)
- **Selection Highlighting**: Visual feedback for selected objects

## Future Enhancements

Potential improvements and extensions:
- Additional primitive types (cylinder, cone, torus)
- Texture mapping support
- Shadow rendering
- Animation system
- Export/import scene files
- More advanced lighting (multiple lights, shadows)
- Shader support (GLSL)

## License

[Add your license information here]

## Author

[Add your name/contact information here]

## Acknowledgments

Built using:
- PyOpenGL for OpenGL bindings
- NumPy for matrix operations
- OpenGL/GLUT for windowing and rendering

