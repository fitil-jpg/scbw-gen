#pragma once

#include <string>
#include <memory>
#include "exr_processor.h"

class Viewer {
public:
    float exposure_;
    float gamma_;

private:
    bool initialized_;
    unsigned int shader_program_;
    unsigned int vao_, vbo_, ebo_;
    unsigned int texture_id_;
    ImageProcessing::ImageData current_image_;
    bool show_tonemapped_;
    
    // Shader source code
    std::string vertex_shader_source_;
    std::string fragment_shader_source_;
    
    // OpenGL functions
    unsigned int compileShader(unsigned int type, const std::string& source);
    unsigned int createShaderProgram();
    void setupQuad();
    void loadImageToTexture(const ImageProcessing::ImageData& image);
    void updateUniforms();

public:
    Viewer();
    ~Viewer();
    
    void initialize();
    void render();
    void cleanup();
    
    // EXR processing integration
    bool loadEXRImage(const std::string& filepath);
    void setExposure(float exposure);
    void setGamma(float gamma);
    void toggleTonemapping();
    void applyFilter(const std::string& filter_type);
    
    // Image manipulation
    void resetImage();
    void saveCurrentImage(const std::string& filepath);
};