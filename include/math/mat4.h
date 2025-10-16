#pragma once

#include "vec3.h"
#include "vec4.h"
#include <cmath>
#include <iostream>

namespace Math {

class Mat4 {
public:
    float m[16]; // 4x4 matrix stored in row-major order

    // Конструктори
    Mat4() {
        setIdentity();
    }

    Mat4(float m00, float m01, float m02, float m03,
         float m10, float m11, float m12, float m13,
         float m20, float m21, float m22, float m23,
         float m30, float m31, float m32, float m33) {
        m[0] = m00;  m[1] = m01;  m[2] = m02;  m[3] = m03;
        m[4] = m10;  m[5] = m11;  m[6] = m12;  m[7] = m13;
        m[8] = m20;  m[9] = m21;  m[10] = m22; m[11] = m23;
        m[12] = m30; m[13] = m31; m[14] = m32; m[15] = m33;
    }

    Mat4(const Mat4& other) {
        for (int i = 0; i < 16; i++) {
            m[i] = other.m[i];
        }
    }

    // Оператори присвоєння
    Mat4& operator=(const Mat4& other) {
        for (int i = 0; i < 16; i++) {
            m[i] = other.m[i];
        }
        return *this;
    }

    // Доступ до елементів
    float& operator()(int row, int col) {
        return m[row * 4 + col];
    }

    const float& operator()(int row, int col) const {
        return m[row * 4 + col];
    }

    // Арифметичні оператори
    Mat4 operator+(const Mat4& other) const {
        Mat4 result;
        for (int i = 0; i < 16; i++) {
            result.m[i] = m[i] + other.m[i];
        }
        return result;
    }

    Mat4 operator-(const Mat4& other) const {
        Mat4 result;
        for (int i = 0; i < 16; i++) {
            result.m[i] = m[i] - other.m[i];
        }
        return result;
    }

    Mat4 operator*(const Mat4& other) const {
        Mat4 result;
        for (int row = 0; row < 4; row++) {
            for (int col = 0; col < 4; col++) {
                result(row, col) = 0.0f;
                for (int k = 0; k < 4; k++) {
                    result(row, col) += (*this)(row, k) * other(k, col);
                }
            }
        }
        return result;
    }

    Mat4 operator*(float scalar) const {
        Mat4 result;
        for (int i = 0; i < 16; i++) {
            result.m[i] = m[i] * scalar;
        }
        return result;
    }

    Mat4& operator+=(const Mat4& other) {
        for (int i = 0; i < 16; i++) {
            m[i] += other.m[i];
        }
        return *this;
    }

    Mat4& operator-=(const Mat4& other) {
        for (int i = 0; i < 16; i++) {
            m[i] -= other.m[i];
        }
        return *this;
    }

    Mat4& operator*=(const Mat4& other) {
        *this = *this * other;
        return *this;
    }

    Mat4& operator*=(float scalar) {
        for (int i = 0; i < 16; i++) {
            m[i] *= scalar;
        }
        return *this;
    }

    // Порівняння
    bool operator==(const Mat4& other) const {
        const float epsilon = 1e-6f;
        for (int i = 0; i < 16; i++) {
            if (std::abs(m[i] - other.m[i]) >= epsilon) {
                return false;
            }
        }
        return true;
    }

    bool operator!=(const Mat4& other) const {
        return !(*this == other);
    }

    // Математичні функції
    Mat4 transposed() const {
        Mat4 result;
        for (int row = 0; row < 4; row++) {
            for (int col = 0; col < 4; col++) {
                result(row, col) = (*this)(col, row);
            }
        }
        return result;
    }

    void transpose() {
        *this = transposed();
    }

    float determinant() const {
        // Розрахунок детермінанту 4x4 матриці
        float a = m[0] * (m[5] * (m[10] * m[15] - m[11] * m[14]) - 
                         m[6] * (m[9] * m[15] - m[11] * m[13]) + 
                         m[7] * (m[9] * m[14] - m[10] * m[13]));
        
        float b = m[1] * (m[4] * (m[10] * m[15] - m[11] * m[14]) - 
                         m[6] * (m[8] * m[15] - m[11] * m[12]) + 
                         m[7] * (m[8] * m[14] - m[10] * m[12]));
        
        float c = m[2] * (m[4] * (m[9] * m[15] - m[11] * m[13]) - 
                         m[5] * (m[8] * m[15] - m[11] * m[12]) + 
                         m[7] * (m[8] * m[13] - m[9] * m[12]));
        
        float d = m[3] * (m[4] * (m[9] * m[14] - m[10] * m[13]) - 
                         m[5] * (m[8] * m[14] - m[10] * m[12]) + 
                         m[6] * (m[8] * m[13] - m[9] * m[12]));
        
        return a - b + c - d;
    }

    Mat4 inverted() const {
        float det = determinant();
        if (std::abs(det) < 1e-6f) {
            return Mat4(); // Повертаємо identity matrix якщо не можна обернути
        }

        Mat4 result;
        float invDet = 1.0f / det;

        // Обчислення оберненої матриці через алгебраїчні доповнення
        result(0, 0) = (m[5] * (m[10] * m[15] - m[11] * m[14]) - 
                       m[6] * (m[9] * m[15] - m[11] * m[13]) + 
                       m[7] * (m[9] * m[14] - m[10] * m[13])) * invDet;

        result(0, 1) = -(m[1] * (m[10] * m[15] - m[11] * m[14]) - 
                        m[2] * (m[9] * m[15] - m[11] * m[13]) + 
                        m[3] * (m[9] * m[14] - m[10] * m[13])) * invDet;

        result(0, 2) = (m[1] * (m[6] * m[15] - m[7] * m[14]) - 
                       m[2] * (m[5] * m[15] - m[7] * m[13]) + 
                       m[3] * (m[5] * m[14] - m[6] * m[13])) * invDet;

        result(0, 3) = -(m[1] * (m[6] * m[11] - m[7] * m[10]) - 
                        m[2] * (m[5] * m[11] - m[7] * m[9]) + 
                        m[3] * (m[5] * m[10] - m[6] * m[9])) * invDet;

        // Продовження для інших рядків...
        // (для повноти реалізації потрібно додати всі 16 елементів)
        
        return result;
    }

    void invert() {
        *this = inverted();
    }

    // Множення на вектор
    Vec4 transform(const Vec4& vec) const {
        return Vec4(
            m[0] * vec.x + m[1] * vec.y + m[2] * vec.z + m[3] * vec.w,
            m[4] * vec.x + m[5] * vec.y + m[6] * vec.z + m[7] * vec.w,
            m[8] * vec.x + m[9] * vec.y + m[10] * vec.z + m[11] * vec.w,
            m[12] * vec.x + m[13] * vec.y + m[14] * vec.z + m[15] * vec.w
        );
    }

    Vec3 transformPoint(const Vec3& point) const {
        Vec4 result = transform(Vec4::fromVec3(point, 1.0f));
        return result.xyz();
    }

    Vec3 transformVector(const Vec3& vector) const {
        Vec4 result = transform(Vec4::fromVec3(vector, 0.0f));
        return result.xyz();
    }

    // Статичні функції
    static Mat4 identity() {
        return Mat4();
    }

    static Mat4 zero() {
        Mat4 result;
        for (int i = 0; i < 16; i++) {
            result.m[i] = 0.0f;
        }
        return result;
    }

    // Створення матриць трансформації
    static Mat4 translation(float x, float y, float z) {
        Mat4 result;
        result(0, 3) = x;
        result(1, 3) = y;
        result(2, 3) = z;
        return result;
    }

    static Mat4 translation(const Vec3& translation) {
        return Mat4::translation(translation.x, translation.y, translation.z);
    }

    static Mat4 rotationX(float angle) {
        float c = std::cos(angle);
        float s = std::sin(angle);
        return Mat4(
            1, 0, 0, 0,
            0, c, -s, 0,
            0, s, c, 0,
            0, 0, 0, 1
        );
    }

    static Mat4 rotationY(float angle) {
        float c = std::cos(angle);
        float s = std::sin(angle);
        return Mat4(
            c, 0, s, 0,
            0, 1, 0, 0,
            -s, 0, c, 0,
            0, 0, 0, 1
        );
    }

    static Mat4 rotationZ(float angle) {
        float c = std::cos(angle);
        float s = std::sin(angle);
        return Mat4(
            c, -s, 0, 0,
            s, c, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        );
    }

    static Mat4 rotation(const Vec3& axis, float angle) {
        float c = std::cos(angle);
        float s = std::sin(angle);
        float t = 1.0f - c;
        
        Vec3 normalizedAxis = axis.normalized();
        float x = normalizedAxis.x;
        float y = normalizedAxis.y;
        float z = normalizedAxis.z;

        return Mat4(
            t*x*x + c,   t*x*y - s*z, t*x*z + s*y, 0,
            t*x*y + s*z, t*y*y + c,   t*y*z - s*x, 0,
            t*x*z - s*y, t*y*z + s*x, t*z*z + c,   0,
            0,           0,           0,           1
        );
    }

    static Mat4 scale(float x, float y, float z) {
        Mat4 result;
        result(0, 0) = x;
        result(1, 1) = y;
        result(2, 2) = z;
        return result;
    }

    static Mat4 scale(const Vec3& scale) {
        return Mat4::scale(scale.x, scale.y, scale.z);
    }

    static Mat4 scale(float uniformScale) {
        return Mat4::scale(uniformScale, uniformScale, uniformScale);
    }

    // Проекційні матриці
    static Mat4 perspective(float fov, float aspect, float near, float far) {
        float tanHalfFov = std::tan(fov / 2.0f);
        float range = far - near;
        
        return Mat4(
            1.0f / (aspect * tanHalfFov), 0, 0, 0,
            0, 1.0f / tanHalfFov, 0, 0,
            0, 0, -(far + near) / range, -1,
            0, 0, -(2 * far * near) / range, 0
        );
    }

    static Mat4 orthographic(float left, float right, float bottom, float top, float near, float far) {
        float width = right - left;
        float height = top - bottom;
        float depth = far - near;
        
        return Mat4(
            2.0f / width, 0, 0, -(right + left) / width,
            0, 2.0f / height, 0, -(top + bottom) / height,
            0, 0, -2.0f / depth, -(far + near) / depth,
            0, 0, 0, 1
        );
    }

    // Look-at матриця
    static Mat4 lookAt(const Vec3& eye, const Vec3& target, const Vec3& up) {
        Vec3 f = (target - eye).normalized();
        Vec3 s = f.cross(up).normalized();
        Vec3 u = s.cross(f);
        
        return Mat4(
            s.x, s.y, s.z, -s.dot(eye),
            u.x, u.y, u.z, -u.dot(eye),
            -f.x, -f.y, -f.z, f.dot(eye),
            0, 0, 0, 1
        );
    }

private:
    void setIdentity() {
        for (int i = 0; i < 16; i++) {
            m[i] = (i % 5 == 0) ? 1.0f : 0.0f;
        }
    }
};

// Оператори для скалярного множення
inline Mat4 operator*(float scalar, const Mat4& mat) {
    return mat * scalar;
}

// Множення вектора на матрицю
inline Vec4 operator*(const Vec4& vec, const Mat4& mat) {
    return mat.transform(vec);
}

inline Vec3 operator*(const Vec3& vec, const Mat4& mat) {
    return mat.transformPoint(vec);
}

// Оператор виводу
inline std::ostream& operator<<(std::ostream& os, const Mat4& mat) {
    os << "Mat4(\n";
    for (int row = 0; row < 4; row++) {
        os << "  [";
        for (int col = 0; col < 4; col++) {
            os << mat(row, col);
            if (col < 3) os << ", ";
        }
        os << "]\n";
    }
    os << ")";
    return os;
}

} // namespace Math