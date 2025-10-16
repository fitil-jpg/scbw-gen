#include "exr_processor.h"
#include <cmath>
#include <algorithm>

namespace ImageProcessing {

void ImageFilters::gaussianBlur(ImageData& image, float sigma) {
    if (sigma <= 0.0f) return;
    
    int kernel_size = static_cast<int>(std::ceil(2.0f * sigma) * 2 + 1);
    std::vector<float> kernel(kernel_size);
    int center = kernel_size / 2;
    float sum = 0.0f;
    
    // Create 1D Gaussian kernel
    for (int i = 0; i < kernel_size; ++i) {
        float x = i - center;
        kernel[i] = std::exp(-(x * x) / (2.0f * sigma * sigma));
        sum += kernel[i];
    }
    
    // Normalize kernel
    for (float& val : kernel) {
        val /= sum;
    }
    
    // Apply horizontal blur
    ImageData temp(image.width, image.height, image.channels);
    int half_kernel = kernel_size / 2;
    
    for (int y = 0; y < image.height; ++y) {
        for (int x = 0; x < image.width; ++x) {
            for (int c = 0; c < image.channels; ++c) {
                float sum = 0.0f;
                
                for (int kx = 0; kx < kernel_size; ++kx) {
                    int px = x + kx - half_kernel;
                    if (px >= 0 && px < image.width) {
                        sum += image(px, y, c) * kernel[kx];
                    }
                }
                
                temp(x, y, c) = sum;
            }
        }
    }
    
    // Apply vertical blur
    for (int y = 0; y < image.height; ++y) {
        for (int x = 0; x < image.width; ++x) {
            for (int c = 0; c < image.channels; ++c) {
                float sum = 0.0f;
                
                for (int ky = 0; ky < kernel_size; ++ky) {
                    int py = y + ky - half_kernel;
                    if (py >= 0 && py < image.height) {
                        sum += temp(x, py, c) * kernel[ky];
                    }
                }
                
                image(x, y, c) = sum;
            }
        }
    }
}

void ImageFilters::sharpen(ImageData& image, float strength) {
    if (strength <= 0.0f) return;
    
    // Create sharpening kernel
    std::vector<std::vector<float>> kernel = {
        {0, -strength, 0},
        {-strength, 1 + 4 * strength, -strength},
        {0, -strength, 0}
    };
    
    ImageData temp = image;
    int kernel_size = 3;
    int half_kernel = kernel_size / 2;
    
    for (int y = 0; y < image.height; ++y) {
        for (int x = 0; x < image.width; ++x) {
            for (int c = 0; c < image.channels; ++c) {
                float sum = 0.0f;
                
                for (int ky = 0; ky < kernel_size; ++ky) {
                    for (int kx = 0; kx < kernel_size; ++kx) {
                        int px = x + kx - half_kernel;
                        int py = y + ky - half_kernel;
                        
                        if (px >= 0 && px < image.width && py >= 0 && py < image.height) {
                            sum += temp(px, py, c) * kernel[ky][kx];
                        }
                    }
                }
                
                image(x, y, c) = std::max(0.0f, std::min(1.0f, sum));
            }
        }
    }
}

void ImageFilters::sobelEdgeDetection(ImageData& image) {
    if (image.channels < 3) return;
    
    // Convert to grayscale first
    ImageData grayscale(image.width, image.height, 1);
    for (int y = 0; y < image.height; ++y) {
        for (int x = 0; x < image.width; ++x) {
            float gray = 0.299f * image(x, y, 0) + 0.587f * image(x, y, 1) + 0.114f * image(x, y, 2);
            grayscale(x, y, 0) = gray;
        }
    }
    
    // Sobel kernels
    std::vector<std::vector<int>> sobel_x = {
        {-1, 0, 1},
        {-2, 0, 2},
        {-1, 0, 1}
    };
    
    std::vector<std::vector<int>> sobel_y = {
        {-1, -2, -1},
        {0, 0, 0},
        {1, 2, 1}
    };
    
    ImageData edges(image.width, image.height, 1);
    int kernel_size = 3;
    int half_kernel = kernel_size / 2;
    
    for (int y = 0; y < image.height; ++y) {
        for (int x = 0; x < image.width; ++x) {
            float gx = 0.0f, gy = 0.0f;
            
            for (int ky = 0; ky < kernel_size; ++ky) {
                for (int kx = 0; kx < kernel_size; ++kx) {
                    int px = x + kx - half_kernel;
                    int py = y + ky - half_kernel;
                    
                    if (px >= 0 && px < image.width && py >= 0 && py < image.height) {
                        float pixel = grayscale(px, py, 0);
                        gx += pixel * sobel_x[ky][kx];
                        gy += pixel * sobel_y[ky][kx];
                    }
                }
            }
            
            float magnitude = std::sqrt(gx * gx + gy * gy);
            edges(x, y, 0) = std::min(1.0f, magnitude);
        }
    }
    
    // Copy edges to all channels
    for (int y = 0; y < image.height; ++y) {
        for (int x = 0; x < image.width; ++x) {
            float edge_val = edges(x, y, 0);
            for (int c = 0; c < image.channels; ++c) {
                image(x, y, c) = edge_val;
            }
        }
    }
}

void ImageFilters::laplacianEdgeDetection(ImageData& image) {
    if (image.channels < 3) return;
    
    // Convert to grayscale first
    ImageData grayscale(image.width, image.height, 1);
    for (int y = 0; y < image.height; ++y) {
        for (int x = 0; x < image.width; ++x) {
            float gray = 0.299f * image(x, y, 0) + 0.587f * image(x, y, 1) + 0.114f * image(x, y, 2);
            grayscale(x, y, 0) = gray;
        }
    }
    
    // Laplacian kernel
    std::vector<std::vector<int>> laplacian = {
        {0, -1, 0},
        {-1, 4, -1},
        {0, -1, 0}
    };
    
    ImageData edges(image.width, image.height, 1);
    int kernel_size = 3;
    int half_kernel = kernel_size / 2;
    
    for (int y = 0; y < image.height; ++y) {
        for (int x = 0; x < image.width; ++x) {
            float sum = 0.0f;
            
            for (int ky = 0; ky < kernel_size; ++ky) {
                for (int kx = 0; kx < kernel_size; ++kx) {
                    int px = x + kx - half_kernel;
                    int py = y + ky - half_kernel;
                    
                    if (px >= 0 && px < image.width && py >= 0 && py < image.height) {
                        sum += grayscale(px, py, 0) * laplacian[ky][kx];
                    }
                }
            }
            
            edges(x, y, 0) = std::abs(sum);
        }
    }
    
    // Copy edges to all channels
    for (int y = 0; y < image.height; ++y) {
        for (int x = 0; x < image.width; ++x) {
            float edge_val = edges(x, y, 0);
            for (int c = 0; c < image.channels; ++c) {
                image(x, y, c) = edge_val;
            }
        }
    }
}

void ImageFilters::unsharpMask(ImageData& image, float radius, float amount, float threshold) {
    ImageData blurred = image;
    gaussianBlur(blurred, radius);
    
    for (int y = 0; y < image.height; ++y) {
        for (int x = 0; x < image.width; ++x) {
            for (int c = 0; c < image.channels; ++c) {
                float original = image(x, y, c);
                float blurred_val = blurred(x, y, c);
                float difference = original - blurred_val;
                
                if (std::abs(difference) >= threshold) {
                    image(x, y, c) = original + amount * difference;
                    image(x, y, c) = std::max(0.0f, std::min(1.0f, image(x, y, c)));
                }
            }
        }
    }
}

} // namespace ImageProcessing