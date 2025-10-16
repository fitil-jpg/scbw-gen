#include "exr_processor.h"
#include <iostream>
#include <fstream>
#include <cmath>
#include <algorithm>
#include <cstring>

namespace ImageProcessing {

EXRProcessor::EXRProcessor() {
}

EXRProcessor::~EXRProcessor() {
    clearPasses();
}

bool EXRProcessor::loadEXR(const std::string& filepath, ImageData& image) {
    try {
        Imf::RgbaInputFile file(filepath.c_str());
        Imath::Box2i dw = file.dataWindow();
        
        int width = dw.max.x - dw.min.x + 1;
        int height = dw.max.y - dw.min.y + 1;
        
        image = ImageData(width, height, 4); // RGBA
        
        Imf::Array2D<Imf::Rgba> pixels;
        pixels.resizeErase(height, width);
        
        file.setFrameBuffer(&pixels[0][0] - dw.min.x - dw.min.y * width, 1, width);
        file.readPixels(dw.min.y, dw.max.y);
        
        // Convert to our format
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                image(x, y, 0) = pixels[y][x].r;
                image(x, y, 1) = pixels[y][x].g;
                image(x, y, 2) = pixels[y][x].b;
                image(x, y, 3) = pixels[y][x].a;
            }
        }
        
        return true;
    } catch (const std::exception& e) {
        std::cerr << "Error loading EXR file: " << e.what() << std::endl;
        return false;
    }
}

bool EXRProcessor::saveEXR(const std::string& filepath, const ImageData& image) {
    try {
        if (image.channels != 4) {
            std::cerr << "EXR save requires RGBA image (4 channels)" << std::endl;
            return false;
        }
        
        Imf::Header header(image.width, image.height);
        header.channels().insert("R", Imf::Channel(Imf::FLOAT));
        header.channels().insert("G", Imf::Channel(Imf::FLOAT));
        header.channels().insert("B", Imf::Channel(Imf::FLOAT));
        header.channels().insert("A", Imf::Channel(Imf::FLOAT));
        
        Imf::OutputFile file(filepath.c_str(), header);
        Imf::FrameBuffer frameBuffer;
        
        frameBuffer.insert("R", Imf::Slice(Imf::FLOAT, 
            (char*)&image.data[0], sizeof(float) * 4, sizeof(float) * image.width * 4));
        frameBuffer.insert("G", Imf::Slice(Imf::FLOAT, 
            (char*)&image.data[1], sizeof(float) * 4, sizeof(float) * image.width * 4));
        frameBuffer.insert("B", Imf::Slice(Imf::FLOAT, 
            (char*)&image.data[2], sizeof(float) * 4, sizeof(float) * image.width * 4));
        frameBuffer.insert("A", Imf::Slice(Imf::FLOAT, 
            (char*)&image.data[3], sizeof(float) * 4, sizeof(float) * image.width * 4));
        
        file.setFrameBuffer(frameBuffer);
        file.writePixels(image.height);
        
        return true;
    } catch (const std::exception& e) {
        std::cerr << "Error saving EXR file: " << e.what() << std::endl;
        return false;
    }
}

bool EXRProcessor::loadMultiPlaneEXR(const std::string& filepath, std::vector<RenderPass>& passes) {
    try {
        Imf::InputFile file(filepath.c_str());
        const Imf::Header& header = file.header();
        const Imf::ChannelList& channels = header.channels();
        
        Imath::Box2i dw = header.dataWindow();
        int width = dw.max.x - dw.min.x + 1;
        int height = dw.max.y - dw.min.y + 1;
        
        // Group channels by layer
        std::map<std::string, std::vector<std::string>> layer_channels;
        
        for (Imf::ChannelList::ConstIterator it = channels.begin(); it != channels.end(); ++it) {
            std::string channel_name = it.name();
            std::string layer_name = channel_name.substr(0, channel_name.find_last_of('.'));
            
            if (layer_name.empty()) {
                layer_name = "default";
            }
            
            layer_channels[layer_name].push_back(channel_name);
        }
        
        // Create passes for each layer
        for (const auto& layer : layer_channels) {
            const std::string& layer_name = layer.first;
            const std::vector<std::string>& channel_names = layer.second;
            
            int channel_count = channel_names.size();
            RenderPass pass(layer_name, width, height, channel_count);
            
            // Read channels
            Imf::FrameBuffer frameBuffer;
            for (int i = 0; i < channel_count; ++i) {
                frameBuffer.insert(channel_names[i], Imf::Slice(Imf::FLOAT,
                    (char*)&pass.image.data[i], sizeof(float) * channel_count,
                    sizeof(float) * width * channel_count));
            }
            
            file.setFrameBuffer(frameBuffer);
            file.readPixels(dw.min.y, dw.max.y);
            
            passes.push_back(std::move(pass));
        }
        
        return true;
    } catch (const std::exception& e) {
        std::cerr << "Error loading multi-plane EXR: " << e.what() << std::endl;
        return false;
    }
}

bool EXRProcessor::saveMultiPlaneEXR(const std::string& filepath, const std::vector<RenderPass>& passes) {
    try {
        if (passes.empty()) {
            std::cerr << "No passes to save" << std::endl;
            return false;
        }
        
        int width = passes[0].image.width;
        int height = passes[0].image.height;
        
        Imf::Header header(width, height);
        
        // Add channels for each pass
        for (const auto& pass : passes) {
            for (int c = 0; c < pass.image.channels; ++c) {
                std::string channel_name = pass.layer_name + "." + 
                    (c == 0 ? "R" : c == 1 ? "G" : c == 2 ? "B" : c == 3 ? "A" : 
                     std::to_string(c));
                header.channels().insert(channel_name, Imf::Channel(Imf::FLOAT));
            }
        }
        
        Imf::OutputFile file(filepath.c_str(), header);
        Imf::FrameBuffer frameBuffer;
        
        // Set up frame buffer for each pass
        for (const auto& pass : passes) {
            for (int c = 0; c < pass.image.channels; ++c) {
                std::string channel_name = pass.layer_name + "." + 
                    (c == 0 ? "R" : c == 1 ? "G" : c == 2 ? "B" : c == 3 ? "A" : 
                     std::to_string(c));
                
                frameBuffer.insert(channel_name, Imf::Slice(Imf::FLOAT,
                    (char*)&pass.image.data[c], sizeof(float) * pass.image.channels,
                    sizeof(float) * width * pass.image.channels));
            }
        }
        
        file.setFrameBuffer(frameBuffer);
        file.writePixels(height);
        
        return true;
    } catch (const std::exception& e) {
        std::cerr << "Error saving multi-plane EXR: " << e.what() << std::endl;
        return false;
    }
}

void EXRProcessor::addRenderPass(const std::string& name, int width, int height, int channels, bool is_alpha) {
    render_passes_[name] = std::make_unique<RenderPass>(name, width, height, channels, is_alpha);
}

RenderPass* EXRProcessor::getRenderPass(const std::string& name) {
    auto it = render_passes_.find(name);
    return (it != render_passes_.end()) ? it->second.get() : nullptr;
}

void EXRProcessor::clearPasses() {
    render_passes_.clear();
}

void EXRProcessor::applyGaussianBlur(ImageData& image, float sigma, int kernel_size) {
    if (kernel_size <= 0) {
        kernel_size = static_cast<int>(std::ceil(2.0f * sigma) * 2 + 1);
    }
    
    std::vector<float> kernel;
    createGaussianKernel(kernel, sigma, kernel_size);
    
    ImageData temp(image.width, image.height, image.channels);
    applyKernel(image, temp, kernel, kernel_size);
    image = std::move(temp);
}

void EXRProcessor::applySharpen(ImageData& image, float strength) {
    // Unsharp mask
    ImageData blurred = image;
    applyGaussianBlur(blurred, 1.0f);
    
    for (int y = 0; y < image.height; ++y) {
        for (int x = 0; x < image.width; ++x) {
            for (int c = 0; c < image.channels; ++c) {
                float original = image(x, y, c);
                float blurred_val = blurred(x, y, c);
                image(x, y, c) = original + strength * (original - blurred_val);
                clampPixel(image(x, y, c));
            }
        }
    }
}

void EXRProcessor::applyEdgeDetection(ImageData& image) {
    ImageFilters::sobelEdgeDetection(image);
}

void EXRProcessor::applyToneMapping(ImageData& image, float exposure, float gamma) {
    for (int y = 0; y < image.height; ++y) {
        for (int x = 0; x < image.width; ++x) {
            for (int c = 0; c < image.channels; ++c) {
                if (c == 3) continue; // Skip alpha channel
                
                float value = image(x, y, c) * exposure;
                value = 1.0f - std::exp(-value);
                value = std::pow(value, 1.0f / gamma);
                image(x, y, c) = value;
            }
        }
    }
}

void EXRProcessor::compositePasses(const std::vector<std::string>& pass_names, ImageData& output) {
    if (pass_names.empty()) return;
    
    // Start with first pass
    RenderPass* first_pass = getRenderPass(pass_names[0]);
    if (!first_pass) return;
    
    output = first_pass->image;
    
    // Composite remaining passes
    for (size_t i = 1; i < pass_names.size(); ++i) {
        RenderPass* pass = getRenderPass(pass_names[i]);
        if (pass) {
            addPass(*pass, output, 1.0f);
        }
    }
}

void EXRProcessor::blendPasses(const RenderPass& pass1, const RenderPass& pass2, 
                               ImageData& output, float blend_factor) {
    if (pass1.image.width != pass2.image.width || 
        pass1.image.height != pass2.image.height) {
        std::cerr << "Pass dimensions don't match for blending" << std::endl;
        return;
    }
    
    output = ImageData(pass1.image.width, pass1.image.height, 
                      std::max(pass1.image.channels, pass2.image.channels));
    
    for (int y = 0; y < output.height; ++y) {
        for (int x = 0; x < output.width; ++x) {
            for (int c = 0; c < output.channels; ++c) {
                float val1 = (c < pass1.image.channels) ? pass1.image(x, y, c) : 0.0f;
                float val2 = (c < pass2.image.channels) ? pass2.image(x, y, c) : 0.0f;
                output(x, y, c) = val1 * (1.0f - blend_factor) + val2 * blend_factor;
            }
        }
    }
}

void EXRProcessor::addPass(const RenderPass& pass, ImageData& output, float opacity) {
    if (output.width == 0 || output.height == 0) {
        output = pass.image;
        return;
    }
    
    for (int y = 0; y < output.height && y < pass.image.height; ++y) {
        for (int x = 0; x < output.width && x < pass.image.width; ++x) {
            for (int c = 0; c < std::min(output.channels, pass.image.channels); ++c) {
                output(x, y, c) += pass.image(x, y, c) * opacity;
                clampPixel(output(x, y, c));
            }
        }
    }
}

void EXRProcessor::multiplyPass(const RenderPass& pass, ImageData& output) {
    Compositor::blend(output, pass.image, output, Compositor::MULTIPLY);
}

void EXRProcessor::screenPass(const RenderPass& pass, ImageData& output) {
    Compositor::blend(output, pass.image, output, Compositor::SCREEN);
}

void EXRProcessor::overlayPass(const RenderPass& pass, ImageData& output) {
    Compositor::blend(output, pass.image, output, Compositor::OVERLAY);
}

void EXRProcessor::resizeImage(const ImageData& input, ImageData& output, int new_width, int new_height) {
    output = ImageData(new_width, new_height, input.channels);
    
    float x_ratio = static_cast<float>(input.width) / new_width;
    float y_ratio = static_cast<float>(input.height) / new_height;
    
    for (int y = 0; y < new_height; ++y) {
        for (int x = 0; x < new_width; ++x) {
            float src_x = x * x_ratio;
            float src_y = y * y_ratio;
            
            int x1 = static_cast<int>(src_x);
            int y1 = static_cast<int>(src_y);
            int x2 = std::min(x1 + 1, input.width - 1);
            int y2 = std::min(y1 + 1, input.height - 1);
            
            float fx = src_x - x1;
            float fy = src_y - y1;
            
            for (int c = 0; c < input.channels; ++c) {
                float val = (1.0f - fx) * (1.0f - fy) * input(x1, y1, c) +
                           fx * (1.0f - fy) * input(x2, y1, c) +
                           (1.0f - fx) * fy * input(x1, y2, c) +
                           fx * fy * input(x2, y2, c);
                output(x, y, c) = val;
            }
        }
    }
}

void EXRProcessor::convertToLinear(ImageData& image) {
    for (int y = 0; y < image.height; ++y) {
        for (int x = 0; x < image.width; ++x) {
            for (int c = 0; c < image.channels; ++c) {
                if (c == 3) continue; // Skip alpha
                float val = image(x, y, c);
                if (val <= 0.04045f) {
                    image(x, y, c) = val / 12.92f;
                } else {
                    image(x, y, c) = std::pow((val + 0.055f) / 1.055f, 2.4f);
                }
            }
        }
    }
}

void EXRProcessor::convertToSRGB(ImageData& image) {
    for (int y = 0; y < image.height; ++y) {
        for (int x = 0; x < image.width; ++x) {
            for (int c = 0; c < image.channels; ++c) {
                if (c == 3) continue; // Skip alpha
                float val = image(x, y, c);
                if (val <= 0.0031308f) {
                    image(x, y, c) = 12.92f * val;
                } else {
                    image(x, y, c) = 1.055f * std::pow(val, 1.0f / 2.4f) - 0.055f;
                }
            }
        }
    }
}

void EXRProcessor::normalizeImage(ImageData& image) {
    float min_val = *std::min_element(image.data.begin(), image.data.end());
    float max_val = *std::max_element(image.data.begin(), image.data.end());
    
    if (max_val > min_val) {
        float range = max_val - min_val;
        for (float& val : image.data) {
            val = (val - min_val) / range;
        }
    }
}

// Helper functions
void EXRProcessor::createGaussianKernel(std::vector<float>& kernel, float sigma, int size) {
    kernel.resize(size);
    int center = size / 2;
    float sum = 0.0f;
    
    for (int i = 0; i < size; ++i) {
        float x = i - center;
        kernel[i] = gaussian(x, sigma);
        sum += kernel[i];
    }
    
    // Normalize
    for (float& val : kernel) {
        val /= sum;
    }
}

float EXRProcessor::gaussian(float x, float sigma) {
    return std::exp(-(x * x) / (2.0f * sigma * sigma));
}

void EXRProcessor::applyKernel(const ImageData& input, ImageData& output, 
                               const std::vector<float>& kernel, int kernel_size) {
    int half_kernel = kernel_size / 2;
    
    for (int y = 0; y < input.height; ++y) {
        for (int x = 0; x < input.width; ++x) {
            for (int c = 0; c < input.channels; ++c) {
                float sum = 0.0f;
                
                for (int ky = 0; ky < kernel_size; ++ky) {
                    for (int kx = 0; kx < kernel_size; ++kx) {
                        int px = x + kx - half_kernel;
                        int py = y + ky - half_kernel;
                        
                        if (px >= 0 && px < input.width && py >= 0 && py < input.height) {
                            sum += input(px, py, c) * kernel[ky * kernel_size + kx];
                        }
                    }
                }
                
                output(x, y, c) = sum;
            }
        }
    }
}

void EXRProcessor::clampPixel(float& value, float min_val, float max_val) {
    value = std::max(min_val, std::min(max_val, value));
}

} // namespace ImageProcessing