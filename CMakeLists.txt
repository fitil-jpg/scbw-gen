cmake_minimum_required(VERSION 3.10)
project(DemoProject)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

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
find_package(glfw3)

# Include GLAD
include(FetchContent)
FetchContent_Declare(
    glad
    GIT_REPOSITORY https://github.com/Dav1dde/glad.git
    GIT_TAG v0.1.36
)
FetchContent_MakeAvailable(glad)

# Add executable
if(DEMO_BUILD_VIEWER AND glfw3_FOUND)
    add_executable(demo_viewer
        src/main.cpp
        src/viewer.cpp
    )
    
    target_link_libraries(demo_viewer
        glad
        glfw
        Threads::Threads
    )
    
    # Include directories
    target_include_directories(demo_viewer PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_CURRENT_SOURCE_DIR}/include/math
    )
endif()

if(DEMO_BUILD_TUI)
    add_executable(demo_tui
        src/tui.cpp
    )
    
    target_link_libraries(demo_tui
        Threads::Threads
    )
endif()

# Math engine test
add_executable(math_test
    src/math_test.cpp
)

target_include_directories(math_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math
)

# REF_PLACE_34: Тут можна додати реф на додаткові цілі збірки
# Наприклад: add_library(viewer_lib STATIC src/viewer.c)
# Наприклад: add_executable(demo_test src/test.c)

# Compiler-specific options
if(MSVC)
    target_compile_definitions(demo_viewer PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()

# Warnings as errors
if(DEMO_WARNINGS_AS_ERRORS)
    if(MSVC)
        target_compile_options(demo_viewer PRIVATE /WX)
    else()
        target_compile_options(demo_viewer PRIVATE -Werror)
    endif()
endif()