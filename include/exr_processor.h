#pragma once

#include <string>
#include <vector>
#include <memory>
#include <map>
#include <OpenEXR/ImfHeader.h>
#include <OpenEXR/ImfInputFile.h>
#include <OpenEXR/ImfOutputFile.h>
#include <OpenEXR/ImfChannelList.h>
#include <OpenEXR/ImfFrameBuffer.h>
#include <OpenEXR/ImfRgbaFile.h>
#include <OpenEXR/ImfArray.h>

namespace ImageProcessing {

struct ImageData {
    int width;
    int height;
    int channels;
    std::vector<float> data;
    
    ImageData(int w = 0, int h = 0, int c = 0) 
        : width(w), height(h), channels(c), data(w * h * c) {}
    
    float& operator()(int x, int y, int c) {
        return data[(y * width + x) * channels + c];
    }
    
    const float& operator()(int x, int y, int c) const {
        return data[(y * width + x) * channels + c];
    }
};

struct RenderPass {
    std::string name;
    ImageData image;
    std::string layer_name;
    bool is_alpha;
    
    RenderPass(const std::string& n, int w, int h, int c, bool alpha = false)
        : name(n), image(w, h, c), layer_name(n), is_alpha(alpha) {}
};

class EXRProcessor {
public:
    EXRProcessor();
    ~EXRProcessor();
    
    // EXR file operations
    bool loadEXR(const std::string& filepath, ImageData& image);
    bool saveEXR(const std::string& filepath, const ImageData& image);
    bool loadMultiPlaneEXR(const std::string& filepath, std::vector<RenderPass>& passes);
    bool saveMultiPlaneEXR(const std::string& filepath, const std::vector<RenderPass>& passes);
    
    // Multi-pass rendering
    void addRenderPass(const std::string& name, int width, int height, int channels, bool is_alpha = false);
    RenderPass* getRenderPass(const std::string& name);
    void clearPasses();
    
    // Image filtering
    void applyGaussianBlur(ImageData& image, float sigma, int kernel_size = 0);
    void applySharpen(ImageData& image, float strength);
    void applyEdgeDetection(ImageData& image);
    void applyToneMapping(ImageData& image, float exposure = 1.0f, float gamma = 2.2f);
    
    // Compositing operations
    void compositePasses(const std::vector<std::string>& pass_names, ImageData& output);
    void blendPasses(const RenderPass& pass1, const RenderPass& pass2, 
                    ImageData& output, float blend_factor = 0.5f);
    void addPass(const RenderPass& pass, ImageData& output, float opacity = 1.0f);
    void multiplyPass(const RenderPass& pass, ImageData& output);
    void screenPass(const RenderPass& pass, ImageData& output);
    void overlayPass(const RenderPass& pass, ImageData& output);
    
    // Utility functions
    void resizeImage(const ImageData& input, ImageData& output, int new_width, int new_height);
    void convertToLinear(ImageData& image);
    void convertToSRGB(ImageData& image);
    void normalizeImage(ImageData& image);
    
private:
    std::map<std::string, std::unique_ptr<RenderPass>> render_passes_;
    
    // Helper functions
    void createGaussianKernel(std::vector<float>& kernel, float sigma, int size);
    float gaussian(float x, float sigma);
    void applyKernel(const ImageData& input, ImageData& output, 
                    const std::vector<float>& kernel, int kernel_size);
    void clampPixel(float& value, float min_val = 0.0f, float max_val = 1.0f);
};

// Filtering algorithms
class ImageFilters {
public:
    static void gaussianBlur(ImageData& image, float sigma);
    static void sharpen(ImageData& image, float strength);
    static void sobelEdgeDetection(ImageData& image);
    static void laplacianEdgeDetection(ImageData& image);
    static void unsharpMask(ImageData& image, float radius, float amount, float threshold);
};

// Compositing operations
class Compositor {
public:
    enum BlendMode {
        NORMAL,
        MULTIPLY,
        SCREEN,
        OVERLAY,
        SOFT_LIGHT,
        HARD_LIGHT,
        COLOR_DODGE,
        COLOR_BURN,
        LINEAR_DODGE,
        LINEAR_BURN
    };
    
    static void blend(const ImageData& base, const ImageData& overlay, 
                     ImageData& result, BlendMode mode, float opacity = 1.0f);
    static void premultiplyAlpha(ImageData& image);
    static void unpremultiplyAlpha(ImageData& image);
};

} // namespace ImageProcessing