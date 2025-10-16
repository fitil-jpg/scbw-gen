#pragma once

#include <cmath>
#include <iostream>

namespace Math {

class Vec2 {
public:
    float x, y;

    // Конструктори
    Vec2() : x(0.0f), y(0.0f) {}
    Vec2(float x, float y) : x(x), y(y) {}
    Vec2(const Vec2& other) : x(other.x), y(other.y) {}

    // Оператори присвоєння
    Vec2& operator=(const Vec2& other) {
        x = other.x;
        y = other.y;
        return *this;
    }

    // Арифметичні оператори
    Vec2 operator+(const Vec2& other) const {
        return Vec2(x + other.x, y + other.y);
    }

    Vec2 operator-(const Vec2& other) const {
        return Vec2(x - other.x, y - other.y);
    }

    Vec2 operator*(float scalar) const {
        return Vec2(x * scalar, y * scalar);
    }

    Vec2 operator/(float scalar) const {
        return Vec2(x / scalar, y / scalar);
    }

    Vec2& operator+=(const Vec2& other) {
        x += other.x;
        y += other.y;
        return *this;
    }

    Vec2& operator-=(const Vec2& other) {
        x -= other.x;
        y -= other.y;
        return *this;
    }

    Vec2& operator*=(float scalar) {
        x *= scalar;
        y *= scalar;
        return *this;
    }

    Vec2& operator/=(float scalar) {
        x /= scalar;
        y /= scalar;
        return *this;
    }

    // Порівняння
    bool operator==(const Vec2& other) const {
        const float epsilon = 1e-6f;
        return std::abs(x - other.x) < epsilon && std::abs(y - other.y) < epsilon;
    }

    bool operator!=(const Vec2& other) const {
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
        return std::sqrt(x * x + y * y);
    }

    float lengthSquared() const {
        return x * x + y * y;
    }

    Vec2 normalized() const {
        float len = length();
        if (len > 0.0f) {
            return Vec2(x / len, y / len);
        }
        return Vec2(0.0f, 0.0f);
    }

    void normalize() {
        float len = length();
        if (len > 0.0f) {
            x /= len;
            y /= len;
        }
    }

    float dot(const Vec2& other) const {
        return x * other.x + y * other.y;
    }

    float cross(const Vec2& other) const {
        return x * other.y - y * other.x;
    }

    // Статичні функції
    static Vec2 zero() {
        return Vec2(0.0f, 0.0f);
    }

    static Vec2 one() {
        return Vec2(1.0f, 1.0f);
    }

    static Vec2 up() {
        return Vec2(0.0f, 1.0f);
    }

    static Vec2 down() {
        return Vec2(0.0f, -1.0f);
    }

    static Vec2 left() {
        return Vec2(-1.0f, 0.0f);
    }

    static Vec2 right() {
        return Vec2(1.0f, 0.0f);
    }

    // Утиліти
    Vec2 lerp(const Vec2& other, float t) const {
        return *this + (other - *this) * t;
    }

    float distance(const Vec2& other) const {
        return (*this - other).length();
    }

    float distanceSquared(const Vec2& other) const {
        return (*this - other).lengthSquared();
    }
};

// Оператори для скалярного множення
inline Vec2 operator*(float scalar, const Vec2& vec) {
    return vec * scalar;
}

// Оператор виводу
inline std::ostream& operator<<(std::ostream& os, const Vec2& vec) {
    os << "Vec2(" << vec.x << ", " << vec.y << ")";
    return os;
}

} // namespace Math