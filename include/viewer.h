#pragma once

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