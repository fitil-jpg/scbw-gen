#pragma once

#include "vec2.h"
#include "vec3.h"
#include "mat4.h"
#include <cmath>
#include <vector>

namespace Math {

// Базові геометричні структури
struct Ray {
    Vec3 origin;
    Vec3 direction;

    Ray() : origin(0, 0, 0), direction(0, 0, 1) {}
    Ray(const Vec3& orig, const Vec3& dir) : origin(orig), direction(dir.normalized()) {}

    Vec3 getPoint(float t) const {
        return origin + direction * t;
    }
};

struct Plane {
    Vec3 normal;
    float distance;

    Plane() : normal(0, 1, 0), distance(0) {}
    Plane(const Vec3& n, float d) : normal(n.normalized()), distance(d) {}
    Plane(const Vec3& point, const Vec3& n) : normal(n.normalized()), distance(normal.dot(point)) {}

    float distanceToPoint(const Vec3& point) const {
        return normal.dot(point) - distance;
    }

    Vec3 projectPoint(const Vec3& point) const {
        return point - normal * distanceToPoint(point);
    }
};

struct Sphere {
    Vec3 center;
    float radius;

    Sphere() : center(0, 0, 0), radius(1) {}
    Sphere(const Vec3& c, float r) : center(c), radius(r) {}

    bool contains(const Vec3& point) const {
        return center.distanceSquared(point) <= radius * radius;
    }

    float distanceToPoint(const Vec3& point) const {
        return std::max(0.0f, center.distance(point) - radius);
    }
};

struct AABB {
    Vec3 min;
    Vec3 max;

    AABB() : min(0, 0, 0), max(1, 1, 1) {}
    AABB(const Vec3& minPoint, const Vec3& maxPoint) : min(minPoint), max(maxPoint) {}

    Vec3 getCenter() const {
        return (min + max) * 0.5f;
    }

    Vec3 getSize() const {
        return max - min;
    }

    Vec3 getExtents() const {
        return getSize() * 0.5f;
    }

    bool contains(const Vec3& point) const {
        return point.x >= min.x && point.x <= max.x &&
               point.y >= min.y && point.y <= max.y &&
               point.z >= min.z && point.z <= max.z;
    }

    bool intersects(const AABB& other) const {
        return min.x <= other.max.x && max.x >= other.min.x &&
               min.y <= other.max.y && max.y >= other.min.y &&
               min.z <= other.max.z && max.z >= other.min.z;
    }

    void expand(const Vec3& point) {
        min.x = std::min(min.x, point.x);
        min.y = std::min(min.y, point.y);
        min.z = std::min(min.z, point.z);
        max.x = std::max(max.x, point.x);
        max.y = std::max(max.y, point.y);
        max.z = std::max(max.z, point.z);
    }

    void expand(const AABB& other) {
        expand(other.min);
        expand(other.max);
    }
};

// Функції для розрахунку відстаней
namespace Distance {
    float pointToPoint(const Vec3& a, const Vec3& b) {
        return a.distance(b);
    }

    float pointToLine(const Vec3& point, const Vec3& lineStart, const Vec3& lineEnd) {
        Vec3 line = lineEnd - lineStart;
        float lineLength = line.length();
        if (lineLength < 1e-6f) {
            return point.distance(lineStart);
        }
        
        Vec3 lineDir = line / lineLength;
        Vec3 pointToStart = point - lineStart;
        float t = pointToStart.dot(lineDir);
        t = std::max(0.0f, std::min(1.0f, t));
        
        Vec3 closestPoint = lineStart + lineDir * t;
        return point.distance(closestPoint);
    }

    float pointToPlane(const Vec3& point, const Plane& plane) {
        return std::abs(plane.distanceToPoint(point));
    }

    float pointToSphere(const Vec3& point, const Sphere& sphere) {
        return std::max(0.0f, point.distance(sphere.center) - sphere.radius);
    }

    float pointToAABB(const Vec3& point, const AABB& aabb) {
        Vec3 closestPoint;
        closestPoint.x = std::max(aabb.min.x, std::min(point.x, aabb.max.x));
        closestPoint.y = std::max(aabb.min.y, std::min(point.y, aabb.max.y));
        closestPoint.z = std::max(aabb.min.z, std::min(point.z, aabb.max.z));
        
        return point.distance(closestPoint);
    }
}

// Функції для перетинів
namespace Intersection {
    bool rayPlane(const Ray& ray, const Plane& plane, float& t) {
        float denom = ray.direction.dot(plane.normal);
        if (std::abs(denom) < 1e-6f) {
            return false; // Паралельно
        }
        
        t = (plane.distance - ray.origin.dot(plane.normal)) / denom;
        return t >= 0;
    }

    bool raySphere(const Ray& ray, const Sphere& sphere, float& t) {
        Vec3 oc = ray.origin - sphere.center;
        float a = ray.direction.dot(ray.direction);
        float b = 2.0f * oc.dot(ray.direction);
        float c = oc.dot(oc) - sphere.radius * sphere.radius;
        
        float discriminant = b * b - 4 * a * c;
        if (discriminant < 0) {
            return false;
        }
        
        float sqrtDisc = std::sqrt(discriminant);
        float t1 = (-b - sqrtDisc) / (2 * a);
        float t2 = (-b + sqrtDisc) / (2 * a);
        
        t = (t1 >= 0) ? t1 : t2;
        return t >= 0;
    }

    bool rayAABB(const Ray& ray, const AABB& aabb, float& t) {
        float tMin = (aabb.min.x - ray.origin.x) / ray.direction.x;
        float tMax = (aabb.max.x - ray.origin.x) / ray.direction.x;
        
        if (tMin > tMax) std::swap(tMin, tMax);
        
        float tyMin = (aabb.min.y - ray.origin.y) / ray.direction.y;
        float tyMax = (aabb.max.y - ray.origin.y) / ray.direction.y;
        
        if (tyMin > tyMax) std::swap(tyMin, tyMax);
        
        if (tMin > tyMax || tyMin > tMax) return false;
        
        tMin = std::max(tMin, tyMin);
        tMax = std::min(tMax, tyMax);
        
        float tzMin = (aabb.min.z - ray.origin.z) / ray.direction.z;
        float tzMax = (aabb.max.z - ray.origin.z) / ray.direction.z;
        
        if (tzMin > tzMax) std::swap(tzMin, tzMax);
        
        if (tMin > tzMax || tzMin > tMax) return false;
        
        tMin = std::max(tMin, tzMin);
        tMax = std::min(tMax, tzMax);
        
        t = tMin;
        return t >= 0;
    }

    bool sphereSphere(const Sphere& a, const Sphere& b) {
        float distance = a.center.distance(b.center);
        return distance <= (a.radius + b.radius);
    }

    bool sphereAABB(const Sphere& sphere, const AABB& aabb) {
        float distance = Distance::pointToAABB(sphere.center, aabb);
        return distance <= sphere.radius;
    }

    bool AABBAABB(const AABB& a, const AABB& b) {
        return a.intersects(b);
    }
}

// Функції для проекцій
namespace Projection {
    Vec3 projectPointOnPlane(const Vec3& point, const Plane& plane) {
        return plane.projectPoint(point);
    }

    Vec3 projectPointOnLine(const Vec3& point, const Vec3& lineStart, const Vec3& lineEnd) {
        Vec3 line = lineEnd - lineStart;
        float lineLength = line.length();
        if (lineLength < 1e-6f) {
            return lineStart;
        }
        
        Vec3 lineDir = line / lineLength;
        Vec3 pointToStart = point - lineStart;
        float t = pointToStart.dot(lineDir);
        t = std::max(0.0f, std::min(1.0f, t));
        
        return lineStart + lineDir * t;
    }

    Vec2 project3DTo2D(const Vec3& point, const Mat4& viewProjectionMatrix) {
        Vec4 projected = viewProjectionMatrix.transform(Vec4::fromVec3(point, 1.0f));
        
        if (projected.w != 0.0f) {
            projected.x /= projected.w;
            projected.y /= projected.w;
        }
        
        return Vec2(projected.x, projected.y);
    }
}

// Функції для формацій юнітів
namespace Formation {
    // Лінійна формація
    std::vector<Vec3> createLineFormation(const Vec3& start, const Vec3& end, int count) {
        std::vector<Vec3> positions;
        if (count <= 0) return positions;
        
        if (count == 1) {
            positions.push_back(start);
            return positions;
        }
        
        Vec3 direction = (end - start) / (count - 1);
        for (int i = 0; i < count; i++) {
            positions.push_back(start + direction * i);
        }
        
        return positions;
    }

    // Дугова формація
    std::vector<Vec3> createArcFormation(const Vec3& center, float radius, float startAngle, float endAngle, int count) {
        std::vector<Vec3> positions;
        if (count <= 0) return positions;
        
        if (count == 1) {
            positions.push_back(center);
            return positions;
        }
        
        float angleStep = (endAngle - startAngle) / (count - 1);
        for (int i = 0; i < count; i++) {
            float angle = startAngle + angleStep * i;
            Vec3 offset(radius * std::cos(angle), 0, radius * std::sin(angle));
            positions.push_back(center + offset);
        }
        
        return positions;
    }

    // Кругова формація
    std::vector<Vec3> createCircleFormation(const Vec3& center, float radius, int count) {
        return createArcFormation(center, radius, 0, 2 * M_PI, count);
    }

    // Сітка формація
    std::vector<Vec3> createGridFormation(const Vec3& center, int rows, int cols, float spacing) {
        std::vector<Vec3> positions;
        if (rows <= 0 || cols <= 0) return positions;
        
        Vec3 start = center - Vec3((cols - 1) * spacing * 0.5f, 0, (rows - 1) * spacing * 0.5f);
        
        for (int row = 0; row < rows; row++) {
            for (int col = 0; col < cols; col++) {
                Vec3 position = start + Vec3(col * spacing, 0, row * spacing);
                positions.push_back(position);
            }
        }
        
        return positions;
    }

    // Випадкова формація в межах AABB
    std::vector<Vec3> createRandomFormation(const AABB& bounds, int count) {
        std::vector<Vec3> positions;
        if (count <= 0) return positions;
        
        Vec3 size = bounds.getSize();
        for (int i = 0; i < count; i++) {
            Vec3 position(
                bounds.min.x + (float)rand() / RAND_MAX * size.x,
                bounds.min.y + (float)rand() / RAND_MAX * size.y,
                bounds.min.z + (float)rand() / RAND_MAX * size.z
            );
            positions.push_back(position);
        }
        
        return positions;
    }
}

} // namespace Math