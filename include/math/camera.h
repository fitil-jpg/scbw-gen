#pragma once

#include "vec3.h"
#include "mat4.h"
#include "transform.h"
#include <cmath>

namespace Math {

class Camera {
public:
    enum class ProjectionType {
        Perspective,
        Orthographic
    };

private:
    Transform transform;
    ProjectionType projectionType;
    
    // Perspective parameters
    float fov;        // Field of view in radians
    float aspect;     // Aspect ratio (width/height)
    float nearPlane;  // Near clipping plane
    float farPlane;   // Far clipping plane
    
    // Orthographic parameters
    float left, right, bottom, top;
    
    // View parameters
    Vec3 target;
    Vec3 up;

public:
    // Конструктори
    Camera() : projectionType(ProjectionType::Perspective), 
               fov(M_PI / 4.0f), aspect(16.0f / 9.0f), 
               nearPlane(0.1f), farPlane(1000.0f),
               left(-1.0f), right(1.0f), bottom(-1.0f), top(1.0f),
               target(0, 0, 0), up(0, 1, 0) {}

    // Getters
    const Transform& getTransform() const { return transform; }
    ProjectionType getProjectionType() const { return projectionType; }
    float getFOV() const { return fov; }
    float getAspect() const { return aspect; }
    float getNearPlane() const { return nearPlane; }
    float getFarPlane() const { return farPlane; }
    const Vec3& getTarget() const { return target; }
    const Vec3& getUpVector() const { return up; }

    // Setters
    void setTransform(const Transform& t) { transform = t; }
    void setProjectionType(ProjectionType type) { projectionType = type; }
    void setFOV(float f) { fov = f; }
    void setAspect(float a) { aspect = a; }
    void setNearPlane(float n) { nearPlane = n; }
    void setFarPlane(float f) { farPlane = f; }
    void setTarget(const Vec3& t) { target = t; }
    void setUpVector(const Vec3& u) { up = u; }

    // Position and orientation
    void setPosition(const Vec3& position) {
        transform.setPosition(position);
    }

    void setPosition(float x, float y, float z) {
        transform.setPosition(x, y, z);
    }

    void setRotation(const Vec3& rotation) {
        transform.setRotation(rotation);
    }

    void setRotation(float x, float y, float z) {
        transform.setRotation(x, y, z);
    }

    // Look at functions
    void lookAt(const Vec3& target, const Vec3& up = Vec3::up()) {
        this->target = target;
        this->up = up;
        transform.lookAt(target, up);
    }

    void lookAt(float targetX, float targetY, float targetZ, 
                float upX = 0, float upY = 1, float upZ = 0) {
        lookAt(Vec3(targetX, targetY, targetZ), Vec3(upX, upY, upZ));
    }

    // Movement functions
    void move(const Vec3& delta) {
        transform.translate(delta);
    }

    void move(float x, float y, float z) {
        transform.translate(x, y, z);
    }

    void moveForward(float distance) {
        transform.translate(transform.getForward() * distance);
    }

    void moveRight(float distance) {
        transform.translate(transform.getRight() * distance);
    }

    void moveUp(float distance) {
        transform.translate(transform.getUp() * distance);
    }

    // Rotation functions
    void rotate(const Vec3& delta) {
        transform.rotate(delta);
    }

    void rotate(float x, float y, float z) {
        transform.rotate(x, y, z);
    }

    void rotateAround(const Vec3& axis, float angle) {
        transform.rotateAround(axis, angle);
    }

    // Projection setup
    void setPerspective(float fov, float aspect, float near, float far) {
        projectionType = ProjectionType::Perspective;
        this->fov = fov;
        this->aspect = aspect;
        this->nearPlane = near;
        this->farPlane = far;
    }

    void setOrthographic(float left, float right, float bottom, float top, float near, float far) {
        projectionType = ProjectionType::Orthographic;
        this->left = left;
        this->right = right;
        this->bottom = bottom;
        this->top = top;
        this->nearPlane = near;
        this->farPlane = far;
    }

    void setOrthographic(float size, float aspect, float near, float far) {
        float halfHeight = size * 0.5f;
        float halfWidth = halfHeight * aspect;
        setOrthographic(-halfWidth, halfWidth, -halfHeight, halfHeight, near, far);
    }

    // Matrix generation
    Mat4 getViewMatrix() const {
        return Mat4::lookAt(transform.position, target, up);
    }

    Mat4 getProjectionMatrix() const {
        if (projectionType == ProjectionType::Perspective) {
            return Mat4::perspective(fov, aspect, nearPlane, farPlane);
        } else {
            return Mat4::orthographic(left, right, bottom, top, nearPlane, farPlane);
        }
    }

    Mat4 getViewProjectionMatrix() const {
        return getProjectionMatrix() * getViewMatrix();
    }

    // Utility functions
    Vec3 getPosition() const {
        return transform.position;
    }

    Vec3 getForward() const {
        return transform.getForward();
    }

    Vec3 getRight() const {
        return transform.getRight();
    }

    Vec3 getUpDirection() const {
        return transform.getUp();
    }

    // Ray casting
    Ray screenToRay(float screenX, float screenY, float screenWidth, float screenHeight) const {
        // Convert screen coordinates to normalized device coordinates
        float ndcX = (2.0f * screenX / screenWidth) - 1.0f;
        float ndcY = 1.0f - (2.0f * screenY / screenHeight);
        
        // Create ray in view space
        Vec3 rayDir;
        if (projectionType == ProjectionType::Perspective) {
            float tanHalfFov = std::tan(fov * 0.5f);
            rayDir = Vec3(ndcX * tanHalfFov * aspect, ndcY * tanHalfFov, -1.0f).normalized();
        } else {
            float halfWidth = (right - left) * 0.5f;
            float halfHeight = (top - bottom) * 0.5f;
            rayDir = Vec3(ndcX * halfWidth, ndcY * halfHeight, -1.0f).normalized();
        }
        
        // Transform to world space
        Mat4 viewMatrix = getViewMatrix();
        Mat4 invViewMatrix = viewMatrix.inverted();
        
        Ray ray;
        ray.origin = transform.position;
        ray.direction = invViewMatrix.transformVector(rayDir);
        
        return ray;
    }

    // Frustum culling helpers
    bool isPointInFrustum(const Vec3& point) const {
        Mat4 viewProj = getViewProjectionMatrix();
        Vec4 clipSpace = viewProj.transform(Vec4::fromVec3(point, 1.0f));
        
        if (clipSpace.w <= 0.0f) return false;
        
        float x = clipSpace.x / clipSpace.w;
        float y = clipSpace.y / clipSpace.w;
        float z = clipSpace.z / clipSpace.w;
        
        return x >= -1.0f && x <= 1.0f && 
               y >= -1.0f && y <= 1.0f && 
               z >= -1.0f && z <= 1.0f;
    }

    // Camera interpolation
    void lerpTo(const Camera& other, float t) {
        transform = transform.lerp(other.transform, t);
        target = target.lerp(other.target, t);
        up = up.lerp(other.up, t);
        
        // Interpolate projection parameters
        fov = fov + (other.fov - fov) * t;
        aspect = aspect + (other.aspect - aspect) * t;
        nearPlane = nearPlane + (other.nearPlane - nearPlane) * t;
        farPlane = farPlane + (other.farPlane - farPlane) * t;
    }

    // Static factory methods
    static Camera createPerspective(const Vec3& position, const Vec3& target, 
                                   float fov, float aspect, float near, float far) {
        Camera camera;
        camera.setPosition(position);
        camera.lookAt(target);
        camera.setPerspective(fov, aspect, near, far);
        return camera;
    }

    static Camera createOrthographic(const Vec3& position, const Vec3& target,
                                    float left, float right, float bottom, float top, 
                                    float near, float far) {
        Camera camera;
        camera.setPosition(position);
        camera.lookAt(target);
        camera.setOrthographic(left, right, bottom, top, near, far);
        return camera;
    }

    static Camera createOrthographic(const Vec3& position, const Vec3& target,
                                    float size, float aspect, float near, float far) {
        Camera camera;
        camera.setPosition(position);
        camera.lookAt(target);
        camera.setOrthographic(size, aspect, near, far);
        return camera;
    }
};

} // namespace Math