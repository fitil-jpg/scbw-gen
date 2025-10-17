# EXR Processing System

A comprehensive C++ library for processing OpenEXR files with multi-pass rendering, filtering, and compositing capabilities.

## Features

### EXR File Operations
- **Load/Save EXR files** - Full support for single and multi-plane EXR files
- **Multi-plane EXR support** - Handle complex render passes with multiple layers
- **High dynamic range** - Native support for HDR data with proper tone mapping

### Multi-Pass Rendering
- **Pass management** - Organize and manage multiple render passes
- **Layer composition** - Combine different passes (beauty, depth, normal, albedo, etc.)
- **Pass blending** - Various blend modes for compositing

### Image Filtering
- **Gaussian blur** - Configurable blur with kernel size and sigma
- **Sharpening** - Unsharp mask and custom sharpening filters
- **Edge detection** - Sobel and Laplacian edge detection algorithms
- **Tone mapping** - Reinhard tone mapping with exposure and gamma control

### Compositing
- **Multiple blend modes** - Normal, Multiply, Screen, Overlay, Soft Light, Hard Light, Color Dodge, Color Burn, Linear Dodge, Linear Burn
- **Alpha handling** - Premultiplied and straight alpha support
- **Opacity control** - Fine-grained control over blend strength

## Dependencies

- **OpenEXR** - For EXR file format support
- **OpenGL/GLAD** - For rendering and display
- **GLFW** - For window management
- **CMake** - For build system

## Building

```bash
mkdir build
cd build
cmake ..
make
```

## Usage

### Basic EXR Operations

```cpp
#include "exr_processor.h"

using namespace ImageProcessing;

EXRProcessor processor;

// Load an EXR file
ImageData image;
if (processor.loadEXR("input.exr", image)) {
    std::cout << "Loaded image: " << image.width << "x" << image.height << std::endl;
}

// Apply filters
processor.applyGaussianBlur(image, 2.0f);
processor.applySharpen(image, 0.5f);
processor.applyToneMapping(image, 1.5f, 2.2f);

// Save the result
processor.saveEXR("output.exr", image);
```

### Multi-Pass Rendering

```cpp
// Create render passes
processor.addRenderPass("beauty", 512, 512, 4);
processor.addRenderPass("depth", 512, 512, 1);
processor.addRenderPass("normal", 512, 512, 3);

// Fill passes with data
RenderPass* beauty = processor.getRenderPass("beauty");
// ... fill beauty pass data ...

// Composite passes
std::vector<std::string> pass_names = {"beauty", "depth", "normal"};
ImageData composite;
processor.compositePasses(pass_names, composite);
```

### Advanced Compositing

```cpp
// Load two images
ImageData base, overlay;
processor.loadEXR("base.exr", base);
processor.loadEXR("overlay.exr", overlay);

// Blend with different modes
ImageData result;
Compositor::blend(base, overlay, result, Compositor::OVERLAY, 0.7f);

// Save result
processor.saveEXR("composite.exr", result);
```

## Viewer Application

The included viewer application provides an interactive interface for:

- Loading and displaying EXR images
- Real-time tone mapping with exposure and gamma controls
- Interactive filtering (blur, sharpen, edge detection)
- Keyboard controls for image manipulation

### Viewer Controls

- **1** - Apply Gaussian blur
- **2** - Apply sharpening
- **3** - Apply edge detection
- **4** - Apply tone mapping
- **T** - Toggle tonemapping display
- **R** - Reset image
- **S** - Save current image
- **+/-** - Adjust exposure
- **ESC** - Exit

## Examples

See `examples/exr_demo.cpp` for comprehensive examples including:

- Multi-pass rendering with different pass types
- Image filtering demonstrations
- Compositing with various blend modes
- Batch processing workflows

## File Structure

```
include/
├── exr_processor.h      # Main EXR processing class
├── viewer.h             # OpenGL viewer for display
└── ...

src/
├── exr_processor.cpp    # EXR file operations
├── image_filters.cpp    # Filtering algorithms
├── compositor.cpp       # Compositing operations
├── viewer.cpp           # OpenGL viewer implementation
└── main.cpp             # Main application

examples/
└── exr_demo.cpp         # Example usage
```

## Performance Notes

- **Memory usage**: Large EXR files are loaded entirely into memory
- **Filtering**: Gaussian blur uses separable kernels for efficiency
- **Compositing**: Optimized for real-time preview applications
- **Multi-threading**: Future versions will include multi-threaded processing

## License

This project is part of the larger rendering pipeline system. See main LICENSE file for details.

## Contributing

When adding new features:

1. Follow the existing code style
2. Add comprehensive error handling
3. Include example usage
4. Update documentation
5. Test with various EXR file formats

## Future Enhancements

- [ ] Multi-threaded processing
- [ ] GPU acceleration with OpenCL/CUDA
- [ ] Additional filter algorithms
- [ ] EXR sequence processing
- [ ] Integration with popular DCC applications
- [ ] Real-time preview in viewer