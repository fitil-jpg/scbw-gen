#include <iostream>
#include <fstream>
#include <sstream>
#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include "viewer.h"

Viewer::Viewer() 
    : initialized_(false), shader_program_(0), vao_(0), vbo_(0), ebo_(0), 
      texture_id_(0), exposure_(1.0f), gamma_(2.2f), show_tonemapped_(true) {
    
    // Vertex shader source
    vertex_shader_source_ = R"(
        #version 330 core
        layout (location = 0) in vec3 aPos;
        layout (location = 1) in vec2 aTexCoord;
        
        out vec2 TexCoord;
        
        void main() {
            gl_Position = vec4(aPos, 1.0);
            TexCoord = aTexCoord;
        }
    )";
    
    // Fragment shader source
    fragment_shader_source_ = R"(
        #version 330 core
        out vec4 FragColor;
        
        in vec2 TexCoord;
        
        uniform sampler2D imageTexture;
        uniform float exposure;
        uniform float gamma;
        uniform bool showTonemapped;
        
        vec3 tonemap(vec3 color) {
            // Simple Reinhard tonemapping
            color = color * exposure;
            color = color / (1.0 + color);
            return pow(color, vec3(1.0 / gamma));
        }
        
        void main() {
            vec4 texColor = texture(imageTexture, TexCoord);
            
            if (showTonemapped) {
                vec3 tonemapped = tonemap(texColor.rgb);
                FragColor = vec4(tonemapped, texColor.a);
            } else {
                FragColor = texColor;
            }
        }
    )";
}

Viewer::~Viewer() {
    cleanup();
}

void Viewer::initialize() {
    if (initialized_) return;
    
    // Create shader program
    shader_program_ = createShaderProgram();
    if (shader_program_ == 0) {
        std::cerr << "Failed to create shader program" << std::endl;
        return;
    }
    
    // Setup quad for rendering
    setupQuad();
    
    // Create texture
    glGenTextures(1, &texture_id_);
    
    initialized_ = true;
    std::cout << "Viewer initialized with EXR processing support" << std::endl;
}

void Viewer::render() {
    if (!initialized_) return;
    
    glUseProgram(shader_program_);
    
    // Update uniforms
    updateUniforms();
    
    // Bind texture
    glActiveTexture(GL_TEXTURE0);
    glBindTexture(GL_TEXTURE_2D, texture_id_);
    glUniform1i(glGetUniformLocation(shader_program_, "imageTexture"), 0);
    
    // Draw quad
    glBindVertexArray(vao_);
    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0);
    glBindVertexArray(0);
}

void Viewer::cleanup() {
    if (vao_) {
        glDeleteVertexArrays(1, &vao_);
        vao_ = 0;
    }
    if (vbo_) {
        glDeleteBuffers(1, &vbo_);
        vbo_ = 0;
    }
    if (ebo_) {
        glDeleteBuffers(1, &ebo_);
        ebo_ = 0;
    }
    if (texture_id_) {
        glDeleteTextures(1, &texture_id_);
        texture_id_ = 0;
    }
    if (shader_program_) {
        glDeleteProgram(shader_program_);
        shader_program_ = 0;
    }
    
    initialized_ = false;
    std::cout << "Viewer cleanup completed" << std::endl;
}

bool Viewer::loadEXRImage(const std::string& filepath) {
    using namespace ImageProcessing;
    
    EXRProcessor processor;
    ImageData image;
    
    if (!processor.loadEXR(filepath, image)) {
        std::cerr << "Failed to load EXR image: " << filepath << std::endl;
        return false;
    }
    
    current_image_ = std::move(image);
    loadImageToTexture(current_image_);
    
    std::cout << "Loaded EXR image: " << filepath 
              << " (" << current_image_.width << "x" << current_image_.height << ")" << std::endl;
    return true;
}

void Viewer::setExposure(float exposure) {
    exposure_ = exposure;
}

void Viewer::setGamma(float gamma) {
    gamma_ = gamma;
}

void Viewer::toggleTonemapping() {
    show_tonemapped_ = !show_tonemapped_;
}

void Viewer::applyFilter(const std::string& filter_type) {
    using namespace ImageProcessing;
    
    EXRProcessor processor;
    ImageData filtered = current_image_;
    
    if (filter_type == "blur") {
        processor.applyGaussianBlur(filtered, 2.0f);
    } else if (filter_type == "sharpen") {
        processor.applySharpen(filtered, 0.5f);
    } else if (filter_type == "edges") {
        processor.applyEdgeDetection(filtered);
    } else if (filter_type == "tonemap") {
        processor.applyToneMapping(filtered, exposure_, gamma_);
    }
    
    current_image_ = std::move(filtered);
    loadImageToTexture(current_image_);
    
    std::cout << "Applied filter: " << filter_type << std::endl;
}

void Viewer::resetImage() {
    // Reset to original loaded image
    loadImageToTexture(current_image_);
}

void Viewer::saveCurrentImage(const std::string& filepath) {
    using namespace ImageProcessing;
    
    EXRProcessor processor;
    if (processor.saveEXR(filepath, current_image_)) {
        std::cout << "Saved image to: " << filepath << std::endl;
    } else {
        std::cerr << "Failed to save image to: " << filepath << std::endl;
    }
}

unsigned int Viewer::compileShader(unsigned int type, const std::string& source) {
    unsigned int shader = glCreateShader(type);
    const char* src = source.c_str();
    glShaderSource(shader, 1, &src, nullptr);
    glCompileShader(shader);
    
    int success;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
    if (!success) {
        char info_log[512];
        glGetShaderInfoLog(shader, 512, nullptr, info_log);
        std::cerr << "Shader compilation failed: " << info_log << std::endl;
        glDeleteShader(shader);
        return 0;
    }
    
    return shader;
}

unsigned int Viewer::createShaderProgram() {
    unsigned int vertex_shader = compileShader(GL_VERTEX_SHADER, vertex_shader_source_);
    unsigned int fragment_shader = compileShader(GL_FRAGMENT_SHADER, fragment_shader_source_);
    
    if (vertex_shader == 0 || fragment_shader == 0) {
        return 0;
    }
    
    unsigned int program = glCreateProgram();
    glAttachShader(program, vertex_shader);
    glAttachShader(program, fragment_shader);
    glLinkProgram(program);
    
    int success;
    glGetProgramiv(program, GL_LINK_STATUS, &success);
    if (!success) {
        char info_log[512];
        glGetProgramInfoLog(program, 512, nullptr, info_log);
        std::cerr << "Shader program linking failed: " << info_log << std::endl;
        glDeleteProgram(program);
        return 0;
    }
    
    glDeleteShader(vertex_shader);
    glDeleteShader(fragment_shader);
    
    return program;
}

void Viewer::setupQuad() {
    // Quad vertices (position + texture coordinates)
    float vertices[] = {
        // positions   // texture coords
        -1.0f, -1.0f, 0.0f,  0.0f, 0.0f,
         1.0f, -1.0f, 0.0f,  1.0f, 0.0f,
         1.0f,  1.0f, 0.0f,  1.0f, 1.0f,
        -1.0f,  1.0f, 0.0f,  0.0f, 1.0f
    };
    
    unsigned int indices[] = {
        0, 1, 2,
        2, 3, 0
    };
    
    glGenVertexArrays(1, &vao_);
    glGenBuffers(1, &vbo_);
    glGenBuffers(1, &ebo_);
    
    glBindVertexArray(vao_);
    
    glBindBuffer(GL_ARRAY_BUFFER, vbo_);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
    
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo_);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(indices), indices, GL_STATIC_DRAW);
    
    // Position attribute
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
    
    // Texture coordinate attribute
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);
    
    glBindVertexArray(0);
}

void Viewer::loadImageToTexture(const ImageProcessing::ImageData& image) {
    if (image.data.empty()) return;
    
    glBindTexture(GL_TEXTURE_2D, texture_id_);
    
    // Set texture parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    
    // Upload texture data
    GLenum format = (image.channels == 4) ? GL_RGBA : 
                   (image.channels == 3) ? GL_RGB : 
                   (image.channels == 1) ? GL_RED : GL_RGBA;
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, image.width, image.height, 0, format, GL_FLOAT, image.data.data());
    
    glBindTexture(GL_TEXTURE_2D, 0);
}

void Viewer::updateUniforms() {
    glUniform1f(glGetUniformLocation(shader_program_, "exposure"), exposure_);
    glUniform1f(glGetUniformLocation(shader_program_, "gamma"), gamma_);
    glUniform1i(glGetUniformLocation(shader_program_, "showTonemapped"), show_tonemapped_);
}