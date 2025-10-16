#include <stdio.h>
#include <stdlib.h>
#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include "viewer.h"

// REF_PLACE_1: Тут можна додати реф на глобальні змінні або константи
// Наприклад: static const char* WINDOW_TITLE = "Demo Viewer";

int main() {
    printf("Demo Project - OpenGL with GLAD (C version)\n");
    
    // REF_PLACE_2: Тут можна додати реф на функцію ініціалізації GLFW
    // Наприклад: if (!init_glfw()) { ... }
    
    // Initialize GLFW
    if (!glfwInit()) {
        fprintf(stderr, "Failed to initialize GLFW\n");
        return -1;
    }
    
    // REF_PLACE_3: Тут можна додати реф на функцію створення вікна
    // Наприклад: GLFWwindow* window = create_window(800, 600, "Demo Viewer");
    
    // Create a window
    GLFWwindow* window = glfwCreateWindow(800, 600, "Demo Viewer", NULL, NULL);
    if (!window) {
        fprintf(stderr, "Failed to create GLFW window\n");
        glfwTerminate();
        return -1;
    }
    
    glfwMakeContextCurrent(window);
    
    // REF_PLACE_4: Тут можна додати реф на функцію ініціалізації GLAD
    // Наприклад: if (!init_glad()) { ... }
    
    // Initialize GLAD
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
        fprintf(stderr, "Failed to initialize GLAD\n");
        glfwTerminate();
        return -1;
    }
    
    printf("OpenGL Version: %s\n", glGetString(GL_VERSION));
    printf("GLAD loaded successfully!\n");
    
    // REF_PLACE_5: Тут можна додати реф на ініціалізацію viewer
    // Наприклад: viewer_init(&viewer);
    Viewer viewer;
    viewer_init(&viewer);
    
    // REF_PLACE_6: Тут можна додати реф на головний цикл рендерингу
    // Наприклад: run_main_loop(window, &viewer);
    
    // Main loop
    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();
        
        // REF_PLACE_7: Тут можна додати реф на функцію очищення екрану
        // Наприклад: clear_screen(0.2f, 0.3f, 0.3f, 1.0f);
        
        // Clear the screen
        glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);
        
        // REF_PLACE_8: Тут можна додати реф на функцію рендерингу
        // Наприклад: viewer_render(&viewer);
        viewer_render(&viewer);
        
        glfwSwapBuffers(window);
    }
    
    // REF_PLACE_9: Тут можна додати реф на функцію очищення ресурсів
    // Наприклад: cleanup_resources(&viewer);
    viewer_cleanup(&viewer);
    
    glfwTerminate();
    return 0;
}