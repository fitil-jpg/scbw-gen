#include "exr_processor.h"
#include <algorithm>
#include <cmath>

namespace ImageProcessing {

void Compositor::blend(const ImageData& base, const ImageData& overlay, 
                      ImageData& result, BlendMode mode, float opacity) {
    if (base.width != overlay.width || base.height != overlay.height) {
        return; // Dimensions must match
    }
    
    result = ImageData(base.width, base.height, std::max(base.channels, overlay.channels));
    
    for (int y = 0; y < result.height; ++y) {
        for (int x = 0; x < result.width; ++x) {
            for (int c = 0; c < result.channels; ++c) {
                float base_val = (c < base.channels) ? base(x, y, c) : 0.0f;
                float overlay_val = (c < overlay.channels) ? overlay(x, y, c) : 0.0f;
                
                float blended_val = base_val;
                
                switch (mode) {
                    case NORMAL:
                        blended_val = overlay_val;
                        break;
                        
                    case MULTIPLY:
                        blended_val = base_val * overlay_val;
                        break;
                        
                    case SCREEN:
                        blended_val = 1.0f - (1.0f - base_val) * (1.0f - overlay_val);
                        break;
                        
                    case OVERLAY:
                        if (base_val < 0.5f) {
                            blended_val = 2.0f * base_val * overlay_val;
                        } else {
                            blended_val = 1.0f - 2.0f * (1.0f - base_val) * (1.0f - overlay_val);
                        }
                        break;
                        
                    case SOFT_LIGHT:
                        if (overlay_val < 0.5f) {
                            blended_val = 2.0f * base_val * overlay_val + base_val * base_val * (1.0f - 2.0f * overlay_val);
                        } else {
                            blended_val = 2.0f * base_val * (1.0f - overlay_val) + std::sqrt(base_val) * (2.0f * overlay_val - 1.0f);
                        }
                        break;
                        
                    case HARD_LIGHT:
                        if (overlay_val < 0.5f) {
                            blended_val = 2.0f * base_val * overlay_val;
                        } else {
                            blended_val = 1.0f - 2.0f * (1.0f - base_val) * (1.0f - overlay_val);
                        }
                        break;
                        
                    case COLOR_DODGE:
                        if (overlay_val < 1.0f) {
                            blended_val = base_val / (1.0f - overlay_val);
                        } else {
                            blended_val = 1.0f;
                        }
                        break;
                        
                    case COLOR_BURN:
                        if (overlay_val > 0.0f) {
                            blended_val = 1.0f - (1.0f - base_val) / overlay_val;
                        } else {
                            blended_val = 0.0f;
                        }
                        break;
                        
                    case LINEAR_DODGE:
                        blended_val = base_val + overlay_val;
                        break;
                        
                    case LINEAR_BURN:
                        blended_val = base_val + overlay_val - 1.0f;
                        break;
                }
                
                // Apply opacity
                blended_val = base_val * (1.0f - opacity) + blended_val * opacity;
                
                // Clamp result
                result(x, y, c) = std::max(0.0f, std::min(1.0f, blended_val));
            }
        }
    }
}

void Compositor::premultiplyAlpha(ImageData& image) {
    if (image.channels < 4) return; // Need alpha channel
    
    for (int y = 0; y < image.height; ++y) {
        for (int x = 0; x < image.width; ++x) {
            float alpha = image(x, y, 3);
            for (int c = 0; c < 3; ++c) { // RGB channels only
                image(x, y, c) *= alpha;
            }
        }
    }
}

void Compositor::unpremultiplyAlpha(ImageData& image) {
    if (image.channels < 4) return; // Need alpha channel
    
    for (int y = 0; y < image.height; ++y) {
        for (int x = 0; x < image.width; ++x) {
            float alpha = image(x, y, 3);
            if (alpha > 0.0f) {
                for (int c = 0; c < 3; ++c) { // RGB channels only
                    image(x, y, c) /= alpha;
                }
            }
        }
    }
}

} // namespace ImageProcessing