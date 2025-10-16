#pragma once

#include "vec3.h"
#include "mat4.h"
#include <cmath>

namespace Math {

class Transform {
public:
    Vec3 position;
    Vec3 rotation; // Euler angles in radians (x, y, z)
    Vec3 scale;

    // Конструктори
    Transform() : position(0, 0, 0), rotation(0, 0, 0), scale(1, 1, 1) {}
    
    Transform(const Vec3& pos, const Vec3& rot, const Vec3& scl) 
        : position(pos), rotation(rot), scale(scl) {}

    // Отримати матрицю трансформації
    Mat4 getMatrix() const {
        Mat4 translationMatrix = Mat4::translation(position);
        Mat4 rotationMatrix = getRotationMatrix();
        Mat4 scaleMatrix = Mat4::scale(scale);
        
        return translationMatrix * rotationMatrix * scaleMatrix;
    }

    // Отримати матрицю оберненої трансформації
    Mat4 getInverseMatrix() const {
        Mat4 invScale = Mat4::scale(1.0f / scale.x, 1.0f / scale.y, 1.0f / scale.z);
        Mat4 invRotation = getInverseRotationMatrix();
        Mat4 invTranslation = Mat4::translation(Vec3(-position.x, -position.y, -position.z));
        
        return invScale * invRotation * invTranslation;
    }

    // Трансформувати точку
    Vec3 transformPoint(const Vec3& point) const {
        return getMatrix().transformPoint(point);
    }

    // Трансформувати вектор (без переміщення)
    Vec3 transformVector(const Vec3& vector) const {
        return getMatrix().transformVector(vector);
    }

    // Трансформувати точку в локальні координати
    Vec3 inverseTransformPoint(const Vec3& point) const {
        return getInverseMatrix().transformPoint(point);
    }

    // Трансформувати вектор в локальні координати
    Vec3 inverseTransformVector(const Vec3& vector) const {
        return getInverseMatrix().transformVector(vector);
    }

    // Отримати напрямок вперед (Z+)
    Vec3 getForward() const {
        return transformVector(Vec3::forward());
    }

    // Отримати напрямок вправо (X+)
    Vec3 getRight() const {
        return transformVector(Vec3::right());
    }

    // Отримати напрямок вгору (Y+)
    Vec3 getUp() const {
        return transformVector(Vec3::up());
    }

    // Встановити позицію
    void setPosition(const Vec3& pos) {
        position = pos;
    }

    void setPosition(float x, float y, float z) {
        position = Vec3(x, y, z);
    }

    // Встановити поворот (Euler angles в радіанах)
    void setRotation(const Vec3& rot) {
        rotation = rot;
    }

    void setRotation(float x, float y, float z) {
        rotation = Vec3(x, y, z);
    }

    // Встановити масштаб
    void setScale(const Vec3& scl) {
        scale = scl;
    }

    void setScale(float x, float y, float z) {
        scale = Vec3(x, y, z);
    }

    void setScale(float uniformScale) {
        scale = Vec3(uniformScale, uniformScale, uniformScale);
    }

    // Переміщення
    void translate(const Vec3& translation) {
        position += translation;
    }

    void translate(float x, float y, float z) {
        position += Vec3(x, y, z);
    }

    // Поворот
    void rotate(const Vec3& eulerAngles) {
        rotation += eulerAngles;
    }

    void rotate(float x, float y, float z) {
        rotation += Vec3(x, y, z);
    }

    void rotateAround(const Vec3& axis, float angle) {
        // Конвертуємо в матрицю повороту та застосовуємо
        Mat4 rotationMatrix = Mat4::rotation(axis, angle);
        Vec3 rotatedRotation = rotationMatrix.transformVector(rotation);
        rotation = rotatedRotation;
    }

    // Масштабування
    void scaleBy(const Vec3& scaleFactor) {
        scale.x *= scaleFactor.x;
        scale.y *= scaleFactor.y;
        scale.z *= scaleFactor.z;
    }

    void scaleBy(float factor) {
        scale *= factor;
    }

    // Look at функція
    void lookAt(const Vec3& target, const Vec3& up = Vec3::up()) {
        Vec3 direction = (target - position).normalized();
        
        // Обчислюємо кути повороту
        float yaw = std::atan2(direction.x, direction.z);
        float pitch = std::asin(-direction.y);
        
        rotation = Vec3(pitch, yaw, 0);
    }

    // Комбінування трансформацій
    Transform combine(const Transform& other) const {
        Transform result;
        result.position = transformPoint(other.position);
        result.rotation = rotation + other.rotation;
        result.scale = Vec3(
            scale.x * other.scale.x,
            scale.y * other.scale.y,
            scale.z * other.scale.z
        );
        return result;
    }

    // Інтерполяція між трансформаціями
    Transform lerp(const Transform& other, float t) const {
        Transform result;
        result.position = position.lerp(other.position, t);
        result.rotation = rotation.lerp(other.rotation, t);
        result.scale = scale.lerp(other.scale, t);
        return result;
    }

    // Отримати дистанцію до іншої трансформації
    float distance(const Transform& other) const {
        return position.distance(other.position);
    }

    // Отримати дистанцію до точки
    float distanceToPoint(const Vec3& point) const {
        return position.distance(point);
    }

private:
    Mat4 getRotationMatrix() const {
        Mat4 rotX = Mat4::rotationX(rotation.x);
        Mat4 rotY = Mat4::rotationY(rotation.y);
        Mat4 rotZ = Mat4::rotationZ(rotation.z);
        
        // Порядок: Z * Y * X (Yaw * Pitch * Roll)
        return rotZ * rotY * rotX;
    }

    Mat4 getInverseRotationMatrix() const {
        Mat4 rotX = Mat4::rotationX(-rotation.x);
        Mat4 rotY = Mat4::rotationY(-rotation.y);
        Mat4 rotZ = Mat4::rotationZ(-rotation.z);
        
        // Обернений порядок: X * Y * Z
        return rotX * rotY * rotZ;
    }
};

// Оператори
inline Transform operator*(const Transform& t1, const Transform& t2) {
    return t1.combine(t2);
}

// Утиліти для роботи з трансформаціями
namespace TransformUtils {
    // Створити трансформацію з матриці
    Transform fromMatrix(const Mat4& matrix) {
        Transform result;
        
        // Витягуємо позицію
        result.position = Vec3(matrix(0, 3), matrix(1, 3), matrix(2, 3));
        
        // Витягуємо масштаб з довжин векторів
        Vec3 scaleX = Vec3(matrix(0, 0), matrix(1, 0), matrix(2, 0));
        Vec3 scaleY = Vec3(matrix(0, 1), matrix(1, 1), matrix(2, 1));
        Vec3 scaleZ = Vec3(matrix(0, 2), matrix(1, 2), matrix(2, 2));
        
        result.scale = Vec3(scaleX.length(), scaleY.length(), scaleZ.length());
        
        // Витягуємо поворот (спрощено)
        // Для повної реалізації потрібен більш складний алгоритм
        float yaw = std::atan2(matrix(0, 2), matrix(2, 2));
        float pitch = std::asin(-matrix(1, 2));
        float roll = std::atan2(matrix(1, 0), matrix(1, 1));
        
        result.rotation = Vec3(pitch, yaw, roll);
        
        return result;
    }

    // Створити трансформацію для камери
    Transform createCameraTransform(const Vec3& position, const Vec3& target, const Vec3& up) {
        Transform result;
        result.position = position;
        result.lookAt(target, up);
        return result;
    }

    // Створити трансформацію для об'єкта що дивиться на ціль
    Transform createLookAtTransform(const Vec3& position, const Vec3& target) {
        Transform result;
        result.position = position;
        result.lookAt(target);
        return result;
    }
}

} // namespace Math