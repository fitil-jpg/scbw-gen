#include <iostream>
#include "math/math.h"

using namespace Math;

void testVectors() {
    std::cout << "=== Testing Vectors ===" << std::endl;
    
    // Vec2 tests
    Vec2 v2a(1, 2);
    Vec2 v2b(3, 4);
    Vec2 v2c = v2a + v2b;
    std::cout << "Vec2 addition: " << v2a << " + " << v2b << " = " << v2c << std::endl;
    
    // Vec3 tests
    Vec3 v3a(1, 2, 3);
    Vec3 v3b(4, 5, 6);
    Vec3 v3c = v3a + v3b;
    std::cout << "Vec3 addition: " << v3a << " + " << v3b << " = " << v3c << std::endl;
    
    // Dot product
    float dot = v3a.dot(v3b);
    std::cout << "Dot product: " << v3a << " · " << v3b << " = " << dot << std::endl;
    
    // Cross product
    Vec3 cross = v3a.cross(v3b);
    std::cout << "Cross product: " << v3a << " × " << v3b << " = " << cross << std::endl;
    
    // Length and normalization
    float length = v3a.length();
    Vec3 normalized = v3a.normalized();
    std::cout << "Length of " << v3a << " = " << length << std::endl;
    std::cout << "Normalized: " << normalized << std::endl;
    
    std::cout << std::endl;
}

void testMatrices() {
    std::cout << "=== Testing Matrices ===" << std::endl;
    
    // Mat3 tests
    Mat3 m3a = Mat3::identity();
    Mat3 m3b = Mat3::translation(5, 10);
    Mat3 m3c = m3a * m3b;
    std::cout << "Mat3 translation: " << m3c << std::endl;
    
    // Mat4 tests
    Mat4 m4a = Mat4::identity();
    Mat4 m4b = Mat4::translation(1, 2, 3);
    Mat4 m4c = Mat4::rotationY(degreesToRadians(45));
    Mat4 m4d = m4a * m4b * m4c;
    std::cout << "Mat4 transformation: " << m4d << std::endl;
    
    // Vector transformation
    Vec3 point(1, 0, 0);
    Vec3 transformed = m4d.transformPoint(point);
    std::cout << "Point " << point << " transformed = " << transformed << std::endl;
    
    std::cout << std::endl;
}

void testTransforms() {
    std::cout << "=== Testing Transforms ===" << std::endl;
    
    Transform transform;
    transform.setPosition(5, 10, 15);
    transform.setRotation(0, degreesToRadians(45), 0);
    transform.setScale(2, 2, 2);
    
    std::cout << "Transform position: " << transform.position << std::endl;
    std::cout << "Transform rotation: " << transform.rotation << std::endl;
    std::cout << "Transform scale: " << transform.scale << std::endl;
    
    Vec3 point(1, 0, 0);
    Vec3 transformed = transform.transformPoint(point);
    std::cout << "Point " << point << " transformed = " << transformed << std::endl;
    
    Vec3 forward = transform.getForward();
    std::cout << "Forward direction: " << forward << std::endl;
    
    std::cout << std::endl;
}

void testGeometry() {
    std::cout << "=== Testing Geometry ===" << std::endl;
    
    // Ray tests
    Ray ray(Vec3(0, 0, 0), Vec3(1, 0, 0));
    Vec3 point = ray.getPoint(5);
    std::cout << "Ray point at t=5: " << point << std::endl;
    
    // Sphere tests
    Sphere sphere(Vec3(0, 0, 0), 5);
    bool contains = sphere.contains(Vec3(3, 0, 0));
    std::cout << "Sphere contains (3,0,0): " << (contains ? "true" : "false") << std::endl;
    
    // AABB tests
    AABB aabb(Vec3(-1, -1, -1), Vec3(1, 1, 1));
    bool intersects = aabb.intersects(AABB(Vec3(0, 0, 0), Vec3(2, 2, 2)));
    std::cout << "AABB intersects: " << (intersects ? "true" : "false") << std::endl;
    
    // Distance tests
    float distance = Distance::pointToPoint(Vec3(0, 0, 0), Vec3(3, 4, 0));
    std::cout << "Distance between points: " << distance << std::endl;
    
    // Formation tests
    auto lineFormation = Formation::createLineFormation(Vec3(0, 0, 0), Vec3(10, 0, 0), 5);
    std::cout << "Line formation with 5 units:" << std::endl;
    for (size_t i = 0; i < lineFormation.size(); i++) {
        std::cout << "  Unit " << i << ": " << lineFormation[i] << std::endl;
    }
    
    std::cout << std::endl;
}

void testCamera() {
    std::cout << "=== Testing Camera ===" << std::endl;
    
    Camera camera;
    camera.setPosition(0, 5, 10);
    camera.lookAt(0, 0, 0);
    camera.setPerspective(degreesToRadians(60), 16.0f/9.0f, 0.1f, 1000.0f);
    
    std::cout << "Camera position: " << camera.getPosition() << std::endl;
    std::cout << "Camera forward: " << camera.getForward() << std::endl;
    
    Mat4 viewMatrix = camera.getViewMatrix();
    Mat4 projMatrix = camera.getProjectionMatrix();
    Mat4 viewProjMatrix = camera.getViewProjectionMatrix();
    
    std::cout << "View matrix created" << std::endl;
    std::cout << "Projection matrix created" << std::endl;
    std::cout << "View-projection matrix created" << std::endl;
    
    // Test ray casting
    Ray ray = camera.screenToRay(400, 300, 800, 600);
    std::cout << "Screen ray origin: " << ray.origin << std::endl;
    std::cout << "Screen ray direction: " << ray.direction << std::endl;
    
    std::cout << std::endl;
}

void testFormations() {
    std::cout << "=== Testing Unit Formations ===" << std::endl;
    
    // Line formation
    auto line = Formation::createLineFormation(Vec3(0, 0, 0), Vec3(20, 0, 0), 6);
    std::cout << "Line formation (6 units):" << std::endl;
    for (size_t i = 0; i < line.size(); i++) {
        std::cout << "  " << line[i] << std::endl;
    }
    
    // Arc formation
    auto arc = Formation::createArcFormation(Vec3(0, 0, 0), 10, 0, PI, 5);
    std::cout << "\nArc formation (5 units, 180 degrees):" << std::endl;
    for (size_t i = 0; i < arc.size(); i++) {
        std::cout << "  " << arc[i] << std::endl;
    }
    
    // Circle formation
    auto circle = Formation::createCircleFormation(Vec3(0, 0, 0), 8, 8);
    std::cout << "\nCircle formation (8 units):" << std::endl;
    for (size_t i = 0; i < circle.size(); i++) {
        std::cout << "  " << circle[i] << std::endl;
    }
    
    // Grid formation
    auto grid = Formation::createGridFormation(Vec3(0, 0, 0), 3, 4, 2.0f);
    std::cout << "\nGrid formation (3x4, spacing 2):" << std::endl;
    for (size_t i = 0; i < grid.size(); i++) {
        std::cout << "  " << grid[i] << std::endl;
    }
    
    std::cout << std::endl;
}

int main() {
    std::cout << "Math Engine Test Suite" << std::endl;
    std::cout << "=====================" << std::endl;
    std::cout << std::endl;
    
    testVectors();
    testMatrices();
    testTransforms();
    testGeometry();
    testCamera();
    testFormations();
    
    std::cout << "All tests completed!" << std::endl;
    return 0;
}