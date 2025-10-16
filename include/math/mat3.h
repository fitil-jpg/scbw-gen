#pragma once

#include "vec3.h"
#include <cmath>
#include <iostream>

namespace Math {

class Mat3 {
public:
    float m[9]; // 3x3 matrix stored in row-major order

    // Конструктори
    Mat3() {
        setIdentity();
    }

    Mat3(float m00, float m01, float m02,
         float m10, float m11, float m12,
         float m20, float m21, float m22) {
        m[0] = m00; m[1] = m01; m[2] = m02;
        m[3] = m10; m[4] = m11; m[5] = m12;
        m[6] = m20; m[7] = m21; m[8] = m22;
    }

    Mat3(const Mat3& other) {
        for (int i = 0; i < 9; i++) {
            m[i] = other.m[i];
        }
    }

    // Оператори присвоєння
    Mat3& operator=(const Mat3& other) {
        for (int i = 0; i < 9; i++) {
            m[i] = other.m[i];
        }
        return *this;
    }

    // Доступ до елементів
    float& operator()(int row, int col) {
        return m[row * 3 + col];
    }

    const float& operator()(int row, int col) const {
        return m[row * 3 + col];
    }

    // Арифметичні оператори
    Mat3 operator+(const Mat3& other) const {
        Mat3 result;
        for (int i = 0; i < 9; i++) {
            result.m[i] = m[i] + other.m[i];
        }
        return result;
    }

    Mat3 operator-(const Mat3& other) const {
        Mat3 result;
        for (int i = 0; i < 9; i++) {
            result.m[i] = m[i] - other.m[i];
        }
        return result;
    }

    Mat3 operator*(const Mat3& other) const {
        Mat3 result;
        for (int row = 0; row < 3; row++) {
            for (int col = 0; col < 3; col++) {
                result(row, col) = 0.0f;
                for (int k = 0; k < 3; k++) {
                    result(row, col) += (*this)(row, k) * other(k, col);
                }
            }
        }
        return result;
    }

    Mat3 operator*(float scalar) const {
        Mat3 result;
        for (int i = 0; i < 9; i++) {
            result.m[i] = m[i] * scalar;
        }
        return result;
    }

    Mat3& operator+=(const Mat3& other) {
        for (int i = 0; i < 9; i++) {
            m[i] += other.m[i];
        }
        return *this;
    }

    Mat3& operator-=(const Mat3& other) {
        for (int i = 0; i < 9; i++) {
            m[i] -= other.m[i];
        }
        return *this;
    }

    Mat3& operator*=(const Mat3& other) {
        *this = *this * other;
        return *this;
    }

    Mat3& operator*=(float scalar) {
        for (int i = 0; i < 9; i++) {
            m[i] *= scalar;
        }
        return *this;
    }

    // Порівняння
    bool operator==(const Mat3& other) const {
        const float epsilon = 1e-6f;
        for (int i = 0; i < 9; i++) {
            if (std::abs(m[i] - other.m[i]) >= epsilon) {
                return false;
            }
        }
        return true;
    }

    bool operator!=(const Mat3& other) const {
        return !(*this == other);
    }

    // Математичні функції
    Mat3 transposed() const {
        Mat3 result;
        for (int row = 0; row < 3; row++) {
            for (int col = 0; col < 3; col++) {
                result(row, col) = (*this)(col, row);
            }
        }
        return result;
    }

    void transpose() {
        *this = transposed();
    }

    float determinant() const {
        return m[0] * (m[4] * m[8] - m[5] * m[7]) -
               m[1] * (m[3] * m[8] - m[5] * m[6]) +
               m[2] * (m[3] * m[7] - m[4] * m[6]);
    }

    Mat3 inverted() const {
        float det = determinant();
        if (std::abs(det) < 1e-6f) {
            return Mat3(); // Повертаємо identity matrix якщо не можна обернути
        }

        Mat3 result;
        float invDet = 1.0f / det;

        result(0, 0) = (m[4] * m[8] - m[5] * m[7]) * invDet;
        result(0, 1) = (m[2] * m[7] - m[1] * m[8]) * invDet;
        result(0, 2) = (m[1] * m[5] - m[2] * m[4]) * invDet;

        result(1, 0) = (m[5] * m[6] - m[3] * m[8]) * invDet;
        result(1, 1) = (m[0] * m[8] - m[2] * m[6]) * invDet;
        result(1, 2) = (m[2] * m[3] - m[0] * m[5]) * invDet;

        result(2, 0) = (m[3] * m[7] - m[4] * m[6]) * invDet;
        result(2, 1) = (m[1] * m[6] - m[0] * m[7]) * invDet;
        result(2, 2) = (m[0] * m[4] - m[1] * m[3]) * invDet;

        return result;
    }

    void invert() {
        *this = inverted();
    }

    // Множення на вектор
    Vec3 transform(const Vec3& vec) const {
        return Vec3(
            m[0] * vec.x + m[1] * vec.y + m[2] * vec.z,
            m[3] * vec.x + m[4] * vec.y + m[5] * vec.z,
            m[6] * vec.x + m[7] * vec.y + m[8] * vec.z
        );
    }

    // Статичні функції
    static Mat3 identity() {
        return Mat3();
    }

    static Mat3 zero() {
        Mat3 result;
        for (int i = 0; i < 9; i++) {
            result.m[i] = 0.0f;
        }
        return result;
    }

    // Створення матриць трансформації
    static Mat3 translation(float x, float y) {
        Mat3 result;
        result(0, 2) = x;
        result(1, 2) = y;
        return result;
    }

    static Mat3 translation(const Vec2& translation) {
        return Mat3::translation(translation.x, translation.y);
    }

    static Mat3 rotation(float angle) {
        float c = std::cos(angle);
        float s = std::sin(angle);
        return Mat3(
            c, -s, 0,
            s,  c, 0,
            0,  0, 1
        );
    }

    static Mat3 scale(float x, float y) {
        Mat3 result;
        result(0, 0) = x;
        result(1, 1) = y;
        return result;
    }

    static Mat3 scale(const Vec2& scale) {
        return Mat3::scale(scale.x, scale.y);
    }

    static Mat3 scale(float uniformScale) {
        return Mat3::scale(uniformScale, uniformScale);
    }

private:
    void setIdentity() {
        for (int i = 0; i < 9; i++) {
            m[i] = (i % 4 == 0) ? 1.0f : 0.0f;
        }
    }
};

// Оператори для скалярного множення
inline Mat3 operator*(float scalar, const Mat3& mat) {
    return mat * scalar;
}

// Множення вектора на матрицю
inline Vec3 operator*(const Vec3& vec, const Mat3& mat) {
    return mat.transform(vec);
}

// Оператор виводу
inline std::ostream& operator<<(std::ostream& os, const Mat3& mat) {
    os << "Mat3(\n";
    for (int row = 0; row < 3; row++) {
        os << "  [";
        for (int col = 0; col < 3; col++) {
            os << mat(row, col);
            if (col < 2) os << ", ";
        }
        os << "]\n";
    }
    os << ")";
    return os;
}

} // namespace Math