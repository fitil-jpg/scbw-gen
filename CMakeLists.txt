cmake_minimum_required(VERSION 3.10)
project(DemoProject)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Demo build options
option(DEMO_BUILD_VIEWER "Build viewer component" ON)
option(DEMO_BUILD_TUI "Build TUI component" OFF)
option(DEMO_GL_LOADER "OpenGL loader to use" "GLAD")
option(DEMO_WARNINGS_AS_ERRORS "Treat warnings as errors" OFF)
option(DEMO_INOTIFY_BACKEND "Inotify backend" "raw")

# Find required packages
find_package(Threads REQUIRED)
find_package(glfw3 REQUIRED)
find_package(OpenEXR REQUIRED)

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
        src/main.cpp
        src/viewer.cpp
        src/exr_processor.cpp
        src/image_filters.cpp
        src/compositor.cpp
    )
    
    target_link_libraries(demo_viewer
        glad
        glfw
        OpenEXR::OpenEXR
        Threads::Threads
    )
    
    # Include directories
    target_include_directories(demo_viewer PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
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

# Add EXR examples
add_executable(exr_demo
    examples/exr_demo.cpp
    src/exr_processor.cpp
    src/image_filters.cpp
    src/compositor.cpp
)

target_link_libraries(exr_demo
    OpenEXR::OpenEXR
    Threads::Threads
)

target_include_directories(exr_demo PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

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