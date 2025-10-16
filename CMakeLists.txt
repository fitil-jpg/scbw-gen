cmake_minimum_required(VERSION 3.10)
project(DemoProject)

# Set C standard
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# REF_PLACE_33: Тут можна додати реф на додаткові налаштування компілятора
# Наприклад: set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra")

# Demo build options
option(DEMO_BUILD_VIEWER "Build viewer component" ON)
option(DEMO_BUILD_TUI "Build TUI component" OFF)
option(DEMO_GL_LOADER "OpenGL loader to use" "GLAD")
option(DEMO_WARNINGS_AS_ERRORS "Treat warnings as errors" OFF)
option(DEMO_INOTIFY_BACKEND "Inotify backend" "raw")

# Find required packages
find_package(Threads REQUIRED)
find_package(glfw3 REQUIRED)

# Include GLAD
include(FetchContent)
FetchContent_Declare(
    glad
    GIT_REPOSITORY https://github.com/Dav1dde/glad.git
    GIT_TAG v0.1.36
)
FetchContent_MakeAvailable(glad)

# Add executable
if(DEMO_BUILD_VIEWER)
    add_executable(demo_viewer
        src/main.c
        src/viewer.c
        src/viewer_utils.c
    )
    
    target_link_libraries(demo_viewer
        glad
        glfw
        Threads::Threads
    )
    
    # Include directories
    target_include_directories(demo_viewer PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
    )
endif()

if(DEMO_BUILD_TUI)
    add_executable(demo_tui
        src/tui.c
    )
    
    target_link_libraries(demo_tui
        Threads::Threads
    )
endif()

# REF_PLACE_34: Тут можна додати реф на додаткові цілі збірки
# Наприклад: add_library(viewer_lib STATIC src/viewer.c)
# Наприклад: add_executable(demo_test src/test.c)

# Compiler-specific options
if(MSVC)
    target_compile_definitions(demo_viewer PRIVATE _CRT_SECURE_NO_WARNINGS)
    # REF_PLACE_35: Тут можна додати реф на додаткові MSVC налаштування
    # Наприклад: target_compile_options(demo_viewer PRIVATE /W4)
else()
    # REF_PLACE_36: Тут можна додати реф на GCC/Clang налаштування
    # Наприклад: target_compile_options(demo_viewer PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Warnings as errors
if(DEMO_WARNINGS_AS_ERRORS)
    if(MSVC)
        target_compile_options(demo_viewer PRIVATE /WX)
    else()
        target_compile_options(demo_viewer PRIVATE -Werror)
    endif()
endif()