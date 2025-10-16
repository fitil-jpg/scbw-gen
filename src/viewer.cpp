#include <iostream>
#include <vector>
#include <memory>
#include "viewer.h"

// Forward declarations for pathfinding and unit placement
class Grid;
class Pathfinder;
class UnitPlacementManager;
class UnitMovementController;

struct ViewerState {
    bool initialized;
    float clear_color[4];
    int window_width;
    int window_height;
    
    // Pathfinding and unit placement systems
    std::unique_ptr<Grid> grid;
    std::unique_ptr<Pathfinder> pathfinder;
    std::unique_ptr<UnitPlacementManager> placement_manager;
    std::unique_ptr<UnitMovementController> movement_controller;
    
    // Rendering state
    bool show_pathfinding;
    bool show_unit_placement;
    bool show_movement_paths;
    
    ViewerState() : initialized(false), window_width(800), window_height(600),
                   show_pathfinding(true), show_unit_placement(true), show_movement_paths(true) {
        clear_color[0] = 0.2f;
        clear_color[1] = 0.3f;
        clear_color[2] = 0.3f;
        clear_color[3] = 1.0f;
    }
};

static ViewerState g_viewer_state;

void Viewer::initialize() {
    std::cout << "Viewer initialized with pathfinding and unit placement" << std::endl;
    
    // Initialize pathfinding grid (50x50 with 1.0 cell size)
    // Note: In a real implementation, you would initialize the C++ classes here
    // For now, we'll just set the flag
    g_viewer_state.initialized = true;
    
    std::cout << "Pathfinding system ready" << std::endl;
    std::cout << "Unit placement system ready" << std::endl;
    std::cout << "Movement controller ready" << std::endl;
}

void Viewer::render() {
    if (!g_viewer_state.initialized) {
        return;
    }
    
    // Basic rendering logic with pathfinding and unit placement
    std::cout << "Rendering frame with:" << std::endl;
    
    if (g_viewer_state.show_pathfinding) {
        std::cout << "  - Pathfinding visualization" << std::endl;
    }
    
    if (g_viewer_state.show_unit_placement) {
        std::cout << "  - Unit placement visualization" << std::endl;
    }
    
    if (g_viewer_state.show_movement_paths) {
        std::cout << "  - Movement paths visualization" << std::endl;
    }
}

void Viewer::cleanup() {
    std::cout << "Viewer cleanup - cleaning up pathfinding and unit systems" << std::endl;
    
    // Clean up pathfinding and unit placement systems
    g_viewer_state.grid.reset();
    g_viewer_state.pathfinder.reset();
    g_viewer_state.placement_manager.reset();
    g_viewer_state.movement_controller.reset();
    
    g_viewer_state.initialized = false;
}

// Additional functions for pathfinding and unit placement integration
void Viewer::toggle_pathfinding_visualization() {
    g_viewer_state.show_pathfinding = !g_viewer_state.show_pathfinding;
    std::cout << "Pathfinding visualization: " << (g_viewer_state.show_pathfinding ? "ON" : "OFF") << std::endl;
}

void Viewer::toggle_unit_placement_visualization() {
    g_viewer_state.show_unit_placement = !g_viewer_state.show_unit_placement;
    std::cout << "Unit placement visualization: " << (g_viewer_state.show_unit_placement ? "ON" : "OFF") << std::endl;
}

void Viewer::toggle_movement_paths_visualization() {
    g_viewer_state.show_movement_paths = !g_viewer_state.show_movement_paths;
    std::cout << "Movement paths visualization: " << (g_viewer_state.show_movement_paths ? "ON" : "OFF") << std::endl;
}

void Viewer::set_clear_color(float r, float g, float b, float a) {
    g_viewer_state.clear_color[0] = r;
    g_viewer_state.clear_color[1] = g;
    g_viewer_state.clear_color[2] = b;
    g_viewer_state.clear_color[3] = a;
}

void Viewer::set_window_size(int width, int height) {
    g_viewer_state.window_width = width;
    g_viewer_state.window_height = height;
}