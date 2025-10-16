#pragma once

#include <cmath>
#include <iostream>

namespace Math {

class Vec3 {
public:
    float x, y, z;

    // Конструктори
    Vec3() : x(0.0f), y(0.0f), z(0.0f) {}
    Vec3(float x, float y, float z) : x(x), y(y), z(z) {}
    Vec3(const Vec3& other) : x(other.x), y(other.y), z(other.z) {}

    // Оператори присвоєння
    Vec3& operator=(const Vec3& other) {
        x = other.x;
        y = other.y;
        z = other.z;
        return *this;
    }

    // Арифметичні оператори
    Vec3 operator+(const Vec3& other) const {
        return Vec3(x + other.x, y + other.y, z + other.z);
    }

    Vec3 operator-(const Vec3& other) const {
        return Vec3(x - other.x, y - other.y, z - other.z);
    }

    Vec3 operator*(float scalar) const {
        return Vec3(x * scalar, y * scalar, z * scalar);
    }

    Vec3 operator/(float scalar) const {
        return Vec3(x / scalar, y / scalar, z / scalar);
    }

    Vec3& operator+=(const Vec3& other) {
        x += other.x;
        y += other.y;
        z += other.z;
        return *this;
    }

    Vec3& operator-=(const Vec3& other) {
        x -= other.x;
        y -= other.y;
        z -= other.z;
        return *this;
    }

    Vec3& operator*=(float scalar) {
        x *= scalar;
        y *= scalar;
        z *= scalar;
        return *this;
    }

    Vec3& operator/=(float scalar) {
        x /= scalar;
        y /= scalar;
        z /= scalar;
        return *this;
    }

    // Порівняння
    bool operator==(const Vec3& other) const {
        const float epsilon = 1e-6f;
        return std::abs(x - other.x) < epsilon && 
               std::abs(y - other.y) < epsilon && 
               std::abs(z - other.z) < epsilon;
    }

    bool operator!=(const Vec3& other) const {
        return !(*this == other);
    }

    // Доступ до елементів
    float& operator[](int index) {
        return (&x)[index];
    }

    const float& operator[](int index) const {
        return (&x)[index];
    }

    // Математичні функції
    float length() const {
        return std::sqrt(x * x + y * y + z * z);
    }

    float lengthSquared() const {
        return x * x + y * y + z * z;
    }

    Vec3 normalized() const {
        float len = length();
        if (len > 0.0f) {
            return Vec3(x / len, y / len, z / len);
        }
        return Vec3(0.0f, 0.0f, 0.0f);
    }

    void normalize() {
        float len = length();
        if (len > 0.0f) {
            x /= len;
            y /= len;
            z /= len;
        }
    }

    float dot(const Vec3& other) const {
        return x * other.x + y * other.y + z * other.z;
    }

    Vec3 cross(const Vec3& other) const {
        return Vec3(
            y * other.z - z * other.y,
            z * other.x - x * other.z,
            x * other.y - y * other.x
        );
    }

    // Статичні функції
    static Vec3 zero() {
        return Vec3(0.0f, 0.0f, 0.0f);
    }

    static Vec3 one() {
        return Vec3(1.0f, 1.0f, 1.0f);
    }

    static Vec3 up() {
        return Vec3(0.0f, 1.0f, 0.0f);
    }

    static Vec3 down() {
        return Vec3(0.0f, -1.0f, 0.0f);
    }

    static Vec3 left() {
        return Vec3(-1.0f, 0.0f, 0.0f);
    }

    static Vec3 right() {
        return Vec3(1.0f, 0.0f, 0.0f);
    }

    static Vec3 forward() {
        return Vec3(0.0f, 0.0f, 1.0f);
    }

    static Vec3 back() {
        return Vec3(0.0f, 0.0f, -1.0f);
    }

    // Утиліти
    Vec3 lerp(const Vec3& other, float t) const {
        return *this + (other - *this) * t;
    }

    float distance(const Vec3& other) const {
        return (*this - other).length();
    }

    float distanceSquared(const Vec3& other) const {
        return (*this - other).lengthSquared();
    }

    // Відображення на площину (для 2D проекцій)
    Vec3 project(const Vec3& normal) const {
        return *this - normal * (this->dot(normal));
    }

    // Відбиття від площини
    Vec3 reflect(const Vec3& normal) const {
        return *this - normal * (2.0f * this->dot(normal));
    }
};

// Оператори для скалярного множення
inline Vec3 operator*(float scalar, const Vec3& vec) {
    return vec * scalar;
}

// Оператор виводу
inline std::ostream& operator<<(std::ostream& os, const Vec3& vec) {
    os << "Vec3(" << vec.x << ", " << vec.y << ", " << vec.z << ")";
    return os;
}

} // namespace Math