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
// REF_PLACE_10: Тут можна додати рефи на структури даних
// Наприклад: typedef struct { float x, y, z; } Vector3;

// REF_PLACE_11: Тут можна додати рефи на константи
// Наприклад: #define MAX_OBJECTS 1000

// REF_PLACE_12: Тут можна додати рефи на енуми
// Наприклад: typedef enum { RENDER_WIREFRAME, RENDER_SOLID } RenderMode;

typedef struct {
    // REF_PLACE_13: Тут можна додати рефи на поля структури
    // Наприклад: int window_width, window_height;
    // Наприклад: RenderMode current_mode;
    int initialized;
    float clear_color[4];
    int window_width;
    int window_height;
    int show_pathfinding;
    int show_unit_placement;
    int show_movement_paths;
} Viewer;

// REF_PLACE_14: Тут можна додати рефи на функції ініціалізації
// Наприклад: int viewer_init_with_config(Viewer* viewer, const char* config_file);
// Наприклад: int viewer_setup_opengl(Viewer* viewer, int major, int minor);

// REF_PLACE_15: Тут можна додати рефи на функції рендерингу
// Наприклад: void viewer_render_scene(Viewer* viewer);
// Наприклад: void viewer_render_ui(Viewer* viewer);

// REF_PLACE_16: Тут можна додати рефи на функції обробки подій
// Наприклад: void viewer_handle_keyboard(Viewer* viewer, int key, int action);
// Наприклад: void viewer_handle_mouse(Viewer* viewer, double x, double y);

// REF_PLACE_17: Тут можна додати рефи на функції утиліт
// Наприклад: void viewer_set_clear_color(Viewer* viewer, float r, float g, float b, float a);
// Наприклад: int viewer_load_shader(const char* vertex_path, const char* fragment_path);

// Основні функції
void viewer_init(Viewer* viewer);
void viewer_render(Viewer* viewer);
void viewer_cleanup(Viewer* viewer);
