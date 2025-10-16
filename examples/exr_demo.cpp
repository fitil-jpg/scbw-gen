#include <iostream>
#include <vector>
#include <functional>
#include <cstdlib>
#include <ctime>
#include <cmath>
#include "../include/exr_processor.h"

using namespace ImageProcessing;

void createTestImage(ImageData& image, int width, int height, const std::string& pattern) {
    image = ImageData(width, height, 4);
    
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            float r, g, b, a = 1.0f;
            
            if (pattern == "gradient") {
                r = static_cast<float>(x) / width;
                g = static_cast<float>(y) / height;
                b = 0.5f;
            } else if (pattern == "checker") {
                int check_size = 32;
                bool check_x = (x / check_size) % 2 == 0;
                bool check_y = (y / check_size) % 2 == 0;
                r = g = b = (check_x ^ check_y) ? 1.0f : 0.0f;
            } else if (pattern == "radial") {
                float center_x = width / 2.0f;
                float center_y = height / 2.0f;
                float dist = std::sqrt((x - center_x) * (x - center_x) + (y - center_y) * (y - center_y));
                float max_dist = std::sqrt(center_x * center_x + center_y * center_y);
                r = g = b = 1.0f - (dist / max_dist);
            } else if (pattern == "noise") {
                r = static_cast<float>(rand()) / RAND_MAX;
                g = static_cast<float>(rand()) / RAND_MAX;
                b = static_cast<float>(rand()) / RAND_MAX;
            }
            
            image(x, y, 0) = r;
            image(x, y, 1) = g;
            image(x, y, 2) = b;
            image(x, y, 3) = a;
        }
    }
}

void demonstrateMultiPassRendering() {
    std::cout << "\n=== Multi-Pass Rendering Demo ===" << std::endl;
    
    EXRProcessor processor;
    const int width = 512;
    const int height = 512;
    
    // Create different render passes
    processor.addRenderPass("beauty", width, height, 4);
    processor.addRenderPass("depth", width, height, 1);
    processor.addRenderPass("normal", width, height, 3);
    processor.addRenderPass("albedo", width, height, 3);
    processor.addRenderPass("specular", width, height, 3);
    processor.addRenderPass("emission", width, height, 3);
    
    // Fill beauty pass with gradient
    RenderPass* beauty = processor.getRenderPass("beauty");
    if (beauty) {
        createTestImage(beauty->image, width, height, "gradient");
    }
    
    // Fill depth pass with radial pattern
    RenderPass* depth = processor.getRenderPass("depth");
    if (depth) {
        createTestImage(depth->image, width, height, "radial");
    }
    
    // Fill normal pass with checker pattern
    RenderPass* normal = processor.getRenderPass("normal");
    if (normal) {
        createTestImage(normal->image, width, height, "checker");
    }
    
    // Fill albedo pass with noise
    RenderPass* albedo = processor.getRenderPass("albedo");
    if (albedo) {
        createTestImage(albedo->image, width, height, "noise");
    }
    
    // Fill specular pass
    RenderPass* specular = processor.getRenderPass("specular");
    if (specular) {
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                specular->image(x, y, 0) = 0.8f; // R
                specular->image(x, y, 1) = 0.8f; // G
                specular->image(x, y, 2) = 0.9f; // B
            }
        }
    }
    
    // Fill emission pass
    RenderPass* emission = processor.getRenderPass("emission");
    if (emission) {
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                float center_x = width / 2.0f;
                float center_y = height / 2.0f;
                float dist = std::sqrt((x - center_x) * (x - center_x) + (y - center_y) * (y - center_y));
                float intensity = std::max(0.0f, 1.0f - dist / 100.0f);
                
                emission->image(x, y, 0) = intensity * 2.0f; // R
                emission->image(x, y, 1) = intensity * 0.5f; // G
                emission->image(x, y, 2) = intensity * 0.1f; // B
            }
        }
    }
    
    // Save individual passes
    std::cout << "Saving individual passes..." << std::endl;
    processor.saveEXR("pass_beauty.exr", beauty->image);
    processor.saveEXR("pass_depth.exr", depth->image);
    processor.saveEXR("pass_normal.exr", normal->image);
    processor.saveEXR("pass_albedo.exr", albedo->image);
    processor.saveEXR("pass_specular.exr", specular->image);
    processor.saveEXR("pass_emission.exr", emission->image);
    
    // Create composite
    std::vector<std::string> pass_names = {"beauty", "depth", "normal", "albedo", "specular", "emission"};
    ImageData composite;
    processor.compositePasses(pass_names, composite);
    processor.saveEXR("composite_all_passes.exr", composite);
    
    std::cout << "✓ Multi-pass rendering complete" << std::endl;
}

void demonstrateFiltering() {
    std::cout << "\n=== Image Filtering Demo ===" << std::endl;
    
    EXRProcessor processor;
    ImageData test_image;
    createTestImage(test_image, 256, 256, "noise");
    
    // Apply different filters
    std::vector<std::pair<std::string, std::function<void()>>> filters = {
        {"original", [&]() { processor.saveEXR("filter_original.exr", test_image); }},
        {"gaussian_blur", [&]() {
            ImageData filtered = test_image;
            processor.applyGaussianBlur(filtered, 3.0f);
            processor.saveEXR("filter_gaussian_blur.exr", filtered);
        }},
        {"sharpen", [&]() {
            ImageData filtered = test_image;
            processor.applySharpen(filtered, 1.0f);
            processor.saveEXR("filter_sharpen.exr", filtered);
        }},
        {"edge_detection", [&]() {
            ImageData filtered = test_image;
            processor.applyEdgeDetection(filtered);
            processor.saveEXR("filter_edges.exr", filtered);
        }},
        {"tone_mapping", [&]() {
            ImageData filtered = test_image;
            processor.applyToneMapping(filtered, 2.0f, 2.2f);
            processor.saveEXR("filter_tonemap.exr", filtered);
        }}
    };
    
    for (const auto& filter : filters) {
        std::cout << "Applying " << filter.first << "..." << std::endl;
        filter.second();
    }
    
    std::cout << "✓ Filtering demo complete" << std::endl;
}

void demonstrateCompositing() {
    std::cout << "\n=== Compositing Demo ===" << std::endl;
    
    EXRProcessor processor;
    
    // Create two test images
    ImageData base_image, overlay_image;
    createTestImage(base_image, 256, 256, "gradient");
    createTestImage(overlay_image, 256, 256, "radial");
    
    // Demonstrate different blend modes
    std::vector<Compositor::BlendMode> blend_modes = {
        Compositor::NORMAL,
        Compositor::MULTIPLY,
        Compositor::SCREEN,
        Compositor::OVERLAY,
        Compositor::SOFT_LIGHT,
        Compositor::HARD_LIGHT,
        Compositor::COLOR_DODGE,
        Compositor::COLOR_BURN
    };
    
    std::vector<std::string> mode_names = {
        "normal", "multiply", "screen", "overlay",
        "soft_light", "hard_light", "color_dodge", "color_burn"
    };
    
    for (size_t i = 0; i < blend_modes.size(); ++i) {
        ImageData result;
        Compositor::blend(base_image, overlay_image, result, blend_modes[i], 0.7f);
        
        std::string filename = "composite_" + mode_names[i] + ".exr";
        processor.saveEXR(filename, result);
        std::cout << "Created " << filename << std::endl;
    }
    
    std::cout << "✓ Compositing demo complete" << std::endl;
}

int main() {
    std::cout << "EXR Processing Examples" << std::endl;
    std::cout << "======================" << std::endl;
    
    srand(static_cast<unsigned int>(time(nullptr)));
    
    try {
        demonstrateMultiPassRendering();
        demonstrateFiltering();
        demonstrateCompositing();
        
        std::cout << "\n=== All Examples Complete ===" << std::endl;
        std::cout << "Check the current directory for generated EXR files." << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}