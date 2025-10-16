#pragma once

// REF_PLACE_53: Тут можна додати рефи на додаткові структури
// Наприклад: typedef struct { float x, y, z; } Vector3;
// Наприклад: typedef struct { Vector3 position; Vector3 rotation; } Transform;

// REF_PLACE_54: Тут можна додати рефи на константи для утиліт
// Наприклад: #define MAX_SHADER_SOURCES 10
// Наприклад: #define CONFIG_BUFFER_SIZE 1024

// REF_PLACE_55: Тут можна додати рефи на функції валідації
// Наприклад: int validate_shader_source(const char* source);
// Наприклад: int validate_config_values(const Viewer* viewer);

// REF_PLACE_56: Тут можна додати рефи на функції завантаження ресурсів
// Наприклад: int load_texture(const char* filename, unsigned int* texture_id);
// Наприклад: int load_model(const char* filename, Model* model);

// REF_PLACE_57: Тут можна додати рефи на функції рендерингу
// Наприклад: void render_mesh(const Mesh* mesh, const Shader* shader);
// Наприклад: void render_text(const char* text, float x, float y);

// REF_PLACE_58: Тут можна додати рефи на функції обробки подій
// Наприклад: void handle_window_resize(Viewer* viewer, int width, int height);
// Наприклад: void handle_scroll_input(Viewer* viewer, double xoffset, double yoffset);

// REF_PLACE_59: Тут можна додати рефи на функції математики
// Наприклад: Vector3 vector3_add(const Vector3* a, const Vector3* b);
// Наприклад: float vector3_length(const Vector3* v);

// Основні функції утиліт
int validate_viewer_params(const Viewer* viewer);
int load_viewer_config(Viewer* viewer, const char* config_file);
int create_default_shaders(Viewer* viewer);
int create_vertex_buffers(Viewer* viewer);
void render_scene_objects(Viewer* viewer);
void render_user_interface(Viewer* viewer);
void handle_keyboard_input(Viewer* viewer, int key, int action);
void handle_mouse_input(Viewer* viewer, double x, double y);