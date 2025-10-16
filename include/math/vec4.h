#pragma once

#include <cmath>
#include <iostream>

namespace Math {

class Vec4 {
public:
    float x, y, z, w;

    // Конструктори
    Vec4() : x(0.0f), y(0.0f), z(0.0f), w(0.0f) {}
    Vec4(float x, float y, float z, float w) : x(x), y(y), z(z), w(w) {}
    Vec4(const Vec4& other) : x(other.x), y(other.y), z(other.z), w(other.w) {}
    
    // Конструктор з Vec3 та w компонентом
    Vec4(const Vec3& vec3, float w) : x(vec3.x), y(vec3.y), z(vec3.z), w(w) {}

    // Оператори присвоєння
    Vec4& operator=(const Vec4& other) {
        x = other.x;
        y = other.y;
        z = other.z;
        w = other.w;
        return *this;
    }

    // Арифметичні оператори
    Vec4 operator+(const Vec4& other) const {
        return Vec4(x + other.x, y + other.y, z + other.z, w + other.w);
    }

    Vec4 operator-(const Vec4& other) const {
        return Vec4(x - other.x, y - other.y, z - other.z, w - other.w);
    }

    Vec4 operator*(float scalar) const {
        return Vec4(x * scalar, y * scalar, z * scalar, w * scalar);
    }

    Vec4 operator/(float scalar) const {
        return Vec4(x / scalar, y / scalar, z / scalar, w / scalar);
    }

    Vec4& operator+=(const Vec4& other) {
        x += other.x;
        y += other.y;
        z += other.z;
        w += other.w;
        return *this;
    }

    Vec4& operator-=(const Vec4& other) {
        x -= other.x;
        y -= other.y;
        z -= other.z;
        w -= other.w;
        return *this;
    }

    Vec4& operator*=(float scalar) {
        x *= scalar;
        y *= scalar;
        z *= scalar;
        w *= scalar;
        return *this;
    }

    Vec4& operator/=(float scalar) {
        x /= scalar;
        y /= scalar;
        z /= scalar;
        w /= scalar;
        return *this;
    }

    // Порівняння
    bool operator==(const Vec4& other) const {
        const float epsilon = 1e-6f;
        return std::abs(x - other.x) < epsilon && 
               std::abs(y - other.y) < epsilon && 
               std::abs(z - other.z) < epsilon &&
               std::abs(w - other.w) < epsilon;
    }

    bool operator!=(const Vec4& other) const {
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
        return std::sqrt(x * x + y * y + z * z + w * w);
    }

    float lengthSquared() const {
        return x * x + y * y + z * z + w * w;
    }

    Vec4 normalized() const {
        float len = length();
        if (len > 0.0f) {
            return Vec4(x / len, y / len, z / len, w / len);
        }
        return Vec4(0.0f, 0.0f, 0.0f, 0.0f);
    }

    void normalize() {
        float len = length();
        if (len > 0.0f) {
            x /= len;
            y /= len;
            z /= len;
            w /= len;
        }
    }

    float dot(const Vec4& other) const {
        return x * other.x + y * other.y + z * other.z + w * other.w;
    }

    // Статичні функції
    static Vec4 zero() {
        return Vec4(0.0f, 0.0f, 0.0f, 0.0f);
    }

    static Vec4 one() {
        return Vec4(1.0f, 1.0f, 1.0f, 1.0f);
    }

    // Утиліти
    Vec4 lerp(const Vec4& other, float t) const {
        return *this + (other - *this) * t;
    }

    float distance(const Vec4& other) const {
        return (*this - other).length();
    }

    float distanceSquared(const Vec4& other) const {
        return (*this - other).lengthSquared();
    }

    // Конвертація в Vec3 (homogeneous coordinates)
    Vec3 xyz() const {
        if (w != 0.0f) {
            return Vec3(x / w, y / w, z / w);
        }
        return Vec3(x, y, z);
    }

    // Конвертація з Vec3 (homogeneous coordinates)
    static Vec4 fromVec3(const Vec3& vec3, float w = 1.0f) {
        return Vec4(vec3.x, vec3.y, vec3.z, w);
    }
};

// Оператори для скалярного множення
inline Vec4 operator*(float scalar, const Vec4& vec) {
    return vec * scalar;
}

// Оператор виводу
inline std::ostream& operator<<(std::ostream& os, const Vec4& vec) {
    os << "Vec4(" << vec.x << ", " << vec.y << ", " << vec.z << ", " << vec.w << ")";
    return os;
}

} // namespace Math