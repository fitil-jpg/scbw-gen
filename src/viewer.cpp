#include <iostream>
#include "viewer.h"

void Viewer::initialize() {
    std::cout << "Viewer initialized" << std::endl;
}

void Viewer::render() {
    // Basic rendering logic
    std::cout << "Rendering frame" << std::endl;
}

void Viewer::cleanup() {
    std::cout << "Viewer cleanup" << std::endl;
}