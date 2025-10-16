#pragma once

// Основні математичні типи
#include "vec2.h"
#include "vec3.h"
#include "vec4.h"
#include "mat3.h"
#include "mat4.h"

// Трансформації та геометрія
#include "transform.h"
#include "geometry.h"
#include "camera.h"

// Константи
namespace Math {
    const float PI = 3.14159265358979323846f;
    const float TWO_PI = 2.0f * PI;
    const float HALF_PI = PI / 2.0f;
    const float QUARTER_PI = PI / 4.0f;
    
    const float DEG_TO_RAD = PI / 180.0f;
    const float RAD_TO_DEG = 180.0f / PI;
    
    const float EPSILON = 1e-6f;
    const float EPSILON_SQUARED = EPSILON * EPSILON;
}

// Утилітарні функції
namespace Math {
    // Конвертація кутів
    inline float degreesToRadians(float degrees) {
        return degrees * DEG_TO_RAD;
    }
    
    inline float radiansToDegrees(float radians) {
        return radians * RAD_TO_DEG;
    }
    
    // Обмеження значень
    inline float clamp(float value, float min, float max) {
        return std::max(min, std::min(max, value));
    }
    
    inline int clamp(int value, int min, int max) {
        return std::max(min, std::min(max, value));
    }
    
    // Лінійна інтерполяція
    inline float lerp(float a, float b, float t) {
        return a + (b - a) * t;
    }
    
    // Інтерполяція з обмеженням
    inline float lerpClamped(float a, float b, float t) {
        return lerp(a, b, clamp(t, 0.0f, 1.0f));
    }
    
    // Степенева інтерполяція
    inline float smoothstep(float edge0, float edge1, float x) {
        float t = clamp((x - edge0) / (edge1 - edge0), 0.0f, 1.0f);
        return t * t * (3.0f - 2.0f * t);
    }
    
    // Порівняння з похибкою
    inline bool approximatelyEqual(float a, float b, float epsilon = EPSILON) {
        return std::abs(a - b) < epsilon;
    }
    
    inline bool approximatelyEqual(const Vec3& a, const Vec3& b, float epsilon = EPSILON) {
        return approximatelyEqual(a.x, b.x, epsilon) &&
               approximatelyEqual(a.y, b.y, epsilon) &&
               approximatelyEqual(a.z, b.z, epsilon);
    }
    
    // Знак числа
    inline float sign(float value) {
        return (value > 0.0f) ? 1.0f : ((value < 0.0f) ? -1.0f : 0.0f);
    }
    
    // Абсолютне значення
    inline float abs(float value) {
        return std::abs(value);
    }
    
    // Мінімум та максимум
    inline float min(float a, float b) {
        return std::min(a, b);
    }
    
    inline float max(float a, float b) {
        return std::max(a, b);
    }
    
    inline int min(int a, int b) {
        return std::min(a, b);
    }
    
    inline int max(int a, int b) {
        return std::max(a, b);
    }
    
    // Степінь
    inline float pow(float base, float exponent) {
        return std::pow(base, exponent);
    }
    
    // Квадратний корінь
    inline float sqrt(float value) {
        return std::sqrt(value);
    }
    
    // Синус та косинус
    inline float sin(float angle) {
        return std::sin(angle);
    }
    
    inline float cos(float angle) {
        return std::cos(angle);
    }
    
    inline float tan(float angle) {
        return std::tan(angle);
    }
    
    // Арксинус та арккосинус
    inline float asin(float value) {
        return std::asin(value);
    }
    
    inline float acos(float value) {
        return std::acos(value);
    }
    
    inline float atan(float value) {
        return std::atan(value);
    }
    
    inline float atan2(float y, float x) {
        return std::atan2(y, x);
    }
    
    // Округлення
    inline float floor(float value) {
        return std::floor(value);
    }
    
    inline float ceil(float value) {
        return std::ceil(value);
    }
    
    inline float round(float value) {
        return std::round(value);
    }
    
    // Модуло
    inline float mod(float value, float divisor) {
        return std::fmod(value, divisor);
    }
    
    // Випадкові числа
    inline float random() {
        return (float)rand() / RAND_MAX;
    }
    
    inline float random(float min, float max) {
        return min + random() * (max - min);
    }
    
    inline int randomInt(int min, int max) {
        return min + rand() % (max - min + 1);
    }
    
    // Векторні утиліти
    inline Vec3 randomDirection() {
        float theta = random(0.0f, TWO_PI);
        float phi = random(0.0f, PI);
        return Vec3(
            sin(phi) * cos(theta),
            cos(phi),
            sin(phi) * sin(theta)
        );
    }
    
    inline Vec3 randomPointInSphere(float radius) {
        return randomDirection() * random(0.0f, radius);
    }
    
    inline Vec3 randomPointInAABB(const AABB& aabb) {
        Vec3 size = aabb.getSize();
        return Vec3(
            aabb.min.x + random() * size.x,
            aabb.min.y + random() * size.y,
            aabb.min.z + random() * size.z
        );
    }
}