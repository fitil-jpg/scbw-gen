#include <iostream>
#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include "exr_processor.h"

void demonstrateEXRProcessing() {
    using namespace ImageProcessing;
    
    std::cout << "\n=== EXR Processing Demonstration ===" << std::endl;
    
    EXRProcessor processor;
    
    // Create a test image
    ImageData testImage(512, 512, 4);
    
    // Generate a simple gradient pattern
    for (int y = 0; y < testImage.height; ++y) {
        for (int x = 0; x < testImage.width; ++x) {
            float r = static_cast<float>(x) / testImage.width;
            float g = static_cast<float>(y) / testImage.height;
            float b = 0.5f;
            float a = 1.0f;
            
            testImage(x, y, 0) = r;
            testImage(x, y, 1) = g;
            testImage(x, y, 2) = b;
            testImage(x, y, 3) = a;
        }
    }
    
    // Save test EXR
    std::cout << "Saving test EXR file..." << std::endl;
    if (processor.saveEXR("test_output.exr", testImage)) {
        std::cout << "✓ Test EXR saved successfully" << std::endl;
    } else {
        std::cout << "✗ Failed to save test EXR" << std::endl;
    }
    
    // Demonstrate multi-pass rendering
    std::cout << "\nCreating multi-pass render..." << std::endl;
    
    // Add different render passes
    processor.addRenderPass("beauty", 512, 512, 4);
    processor.addRenderPass("depth", 512, 512, 1);
    processor.addRenderPass("normal", 512, 512, 3);
    processor.addRenderPass("albedo", 512, 512, 3);
    
    // Fill passes with test data
    RenderPass* beauty = processor.getRenderPass("beauty");
    if (beauty) {
        beauty->image = testImage;
    }
    
    RenderPass* depth = processor.getRenderPass("depth");
    if (depth) {
        for (int y = 0; y < depth->image.height; ++y) {
            for (int x = 0; x < depth->image.width; ++x) {
                float dist = std::sqrt((x - 256) * (x - 256) + (y - 256) * (y - 256));
                depth->image(x, y, 0) = std::min(1.0f, dist / 256.0f);
            }
        }
    }
    
    RenderPass* normal = processor.getRenderPass("normal");
    if (normal) {
        for (int y = 0; y < normal->image.height; ++y) {
            for (int x = 0; x < normal->image.width; ++x) {
                normal->image(x, y, 0) = 0.5f; // R
                normal->image(x, y, 1) = 0.5f; // G
                normal->image(x, y, 2) = 1.0f; // B
            }
        }
    }
    
    RenderPass* albedo = processor.getRenderPass("albedo");
    if (albedo) {
        for (int y = 0; y < albedo->image.height; ++y) {
            for (int x = 0; x < albedo->image.width; ++x) {
                albedo->image(x, y, 0) = 0.8f; // R
                albedo->image(x, y, 1) = 0.6f; // G
                albedo->image(x, y, 2) = 0.4f; // B
            }
        }
    }
    
    // Demonstrate filtering
    std::cout << "\nApplying image filters..." << std::endl;
    
    ImageData filteredImage = testImage;
    processor.applyGaussianBlur(filteredImage, 2.0f);
    processor.saveEXR("test_blurred.exr", filteredImage);
    std::cout << "✓ Applied Gaussian blur" << std::endl;
    
    filteredImage = testImage;
    processor.applySharpen(filteredImage, 0.5f);
    processor.saveEXR("test_sharpened.exr", filteredImage);
    std::cout << "✓ Applied sharpening" << std::endl;
    
    filteredImage = testImage;
    processor.applyEdgeDetection(filteredImage);
    processor.saveEXR("test_edges.exr", filteredImage);
    std::cout << "✓ Applied edge detection" << std::endl;
    
    filteredImage = testImage;
    processor.applyToneMapping(filteredImage, 1.5f, 2.2f);
    processor.saveEXR("test_tonemapped.exr", filteredImage);
    std::cout << "✓ Applied tone mapping" << std::endl;
    
    // Demonstrate compositing
    std::cout << "\nDemonstrating compositing..." << std::endl;
    
    ImageData composite;
    std::vector<std::string> pass_names = {"beauty", "depth", "normal", "albedo"};
    processor.compositePasses(pass_names, composite);
    processor.saveEXR("test_composite.exr", composite);
    std::cout << "✓ Created composite image" << std::endl;
    
    // Demonstrate different blend modes
    if (beauty && albedo) {
        ImageData blend_result;
        processor.blendPasses(*beauty, *albedo, blend_result, 0.5f);
        processor.saveEXR("test_blend.exr", blend_result);
        std::cout << "✓ Applied pass blending" << std::endl;
    }
    
    std::cout << "\n=== EXR Processing Complete ===" << std::endl;
}

int main() {
    std::cout << "EXR Processing Demo - OpenGL with GLAD" << std::endl;
    
    // Demonstrate EXR processing first
    demonstrateEXRProcessing();
    
    // Initialize GLFW
    if (!glfwInit()) {
        std::cerr << "Failed to initialize GLFW" << std::endl;
        return -1;
    }
    
    // Create a window
    GLFWwindow* window = glfwCreateWindow(800, 600, "EXR Processing Viewer", nullptr, nullptr);
    if (!window) {
        std::cerr << "Failed to create GLFW window" << std::endl;
        glfwTerminate();
        return -1;
    }
    
    glfwMakeContextCurrent(window);
    
    // Initialize GLAD
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
        std::cerr << "Failed to initialize GLAD" << std::endl;
        glfwTerminate();
        return -1;
    }
    
    std::cout << "OpenGL Version: " << glGetString(GL_VERSION) << std::endl;
    std::cout << "GLAD loaded successfully!" << std::endl;
    
    // Initialize viewer
    Viewer viewer;
    viewer.initialize();
    
    // Load a test EXR if it exists
    viewer.loadEXRImage("test_output.exr");
    
    // Set up input callbacks
    glfwSetKeyCallback(window, [](GLFWwindow* window, int key, int scancode, int action, int mods) {
        if (action == GLFW_PRESS) {
            Viewer* viewer = static_cast<Viewer*>(glfwGetWindowUserPointer(window));
            switch (key) {
                case GLFW_KEY_ESCAPE:
                    glfwSetWindowShouldClose(window, true);
                    break;
                case GLFW_KEY_1:
                    viewer->applyFilter("blur");
                    break;
                case GLFW_KEY_2:
                    viewer->applyFilter("sharpen");
                    break;
                case GLFW_KEY_3:
                    viewer->applyFilter("edges");
                    break;
                case GLFW_KEY_4:
                    viewer->applyFilter("tonemap");
                    break;
                case GLFW_KEY_T:
                    viewer->toggleTonemapping();
                    break;
                case GLFW_KEY_R:
                    viewer->resetImage();
                    break;
                case GLFW_KEY_S:
                    viewer->saveCurrentImage("viewer_output.exr");
                    break;
                case GLFW_KEY_EQUAL:
                case GLFW_KEY_KP_ADD:
                    viewer->setExposure(viewer->exposure_ * 1.1f);
                    break;
                case GLFW_KEY_MINUS:
                case GLFW_KEY_KP_SUBTRACT:
                    viewer->setExposure(viewer->exposure_ / 1.1f);
                    break;
            }
        }
    });
    
    glfwSetWindowUserPointer(window, &viewer);
    
    std::cout << "\n=== Viewer Controls ===" << std::endl;
    std::cout << "1 - Apply Gaussian blur" << std::endl;
    std::cout << "2 - Apply sharpening" << std::endl;
    std::cout << "3 - Apply edge detection" << std::endl;
    std::cout << "4 - Apply tone mapping" << std::endl;
    std::cout << "T - Toggle tonemapping display" << std::endl;
    std::cout << "R - Reset image" << std::endl;
    std::cout << "S - Save current image" << std::endl;
    std::cout << "+/- - Adjust exposure" << std::endl;
    std::cout << "ESC - Exit" << std::endl;
    
    // Main loop
    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();
        
        // Clear the screen
        glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);
        
        // Render the viewer
        viewer.render();
        
        glfwSwapBuffers(window);
    }
    
    glfwTerminate();
    return 0;
}