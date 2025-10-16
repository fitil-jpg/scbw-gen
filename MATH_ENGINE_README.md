# Математичний движок для 3D геометрії

## Огляд

Математичний движок надає повний набір інструментів для роботи з 3D геометрією, включаючи векторну математику, матричні операції, трансформації, геометричні утиліти та систему камери. Движок реалізований як на C++, так і на Python для максимальної сумісності з існуючими системами.

## Структура проекту

```
include/math/           # C++ заголовочні файли
├── vec2.h             # 2D вектори
├── vec3.h             # 3D вектори  
├── vec4.h             # 4D вектори (homogeneous coordinates)
├── mat3.h             # 3x3 матриці
├── mat4.h             # 4x4 матриці
├── transform.h        # 3D трансформації
├── geometry.h         # Геометричні утиліти
├── camera.h           # Система камери
└── math.h             # Головний заголовочний файл

python_math/           # Python модулі
└── math_engine.py     # Python математичний движок

src/                   # C++ вихідний код
├── main.cpp           # Основний C++ файл
├── viewer.cpp         # OpenGL viewer
└── math_test.cpp      # Тести математичного движка

test_math_engine.py    # Python тести
```

## Основні компоненти

### 1. Векторна математика

#### Vec2 (2D вектори)
```cpp
Vec2 v1(1, 2);
Vec2 v2(3, 4);
Vec2 v3 = v1 + v2;           // Додавання
float dot = v1.dot(v2);      // Скалярний добуток
float length = v1.length();  // Довжина вектора
Vec2 normalized = v1.normalized(); // Нормалізація
```

#### Vec3 (3D вектори)
```cpp
Vec3 v1(1, 2, 3);
Vec3 v2(4, 5, 6);
Vec3 cross = v1.cross(v2);   // Векторний добуток
Vec3 lerped = v1.lerp(v2, 0.5f); // Лінійна інтерполяція
```

#### Vec4 (4D вектори)
```cpp
Vec4 v1(1, 2, 3, 1);         // Homogeneous coordinates
Vec3 point = v1.xyz();       // Конвертація в 3D
```

### 2. Матрична математика

#### Mat3 (3x3 матриці)
```cpp
Mat3 identity = Mat3::identity();
Mat3 translation = Mat3::translation(5, 10);
Mat3 rotation = Mat3::rotation(45.0f * DEG_TO_RAD);
Mat3 scale = Mat3::scale(2.0f, 3.0f);
Mat3 combined = translation * rotation * scale;
```

#### Mat4 (4x4 матриці)
```cpp
Mat4 view = Mat4::lookAt(eye, target, up);
Mat4 proj = Mat4::perspective(fov, aspect, near, far);
Mat4 mvp = proj * view * model;
```

### 3. Система трансформацій

```cpp
Transform transform;
transform.setPosition(Vec3(5, 10, 15));
transform.setRotation(Vec3(0, 45 * DEG_TO_RAD, 0));
transform.setScale(Vec3(2, 2, 2));

Vec3 point(1, 0, 0);
Vec3 transformed = transform.transformPoint(point);
Vec3 forward = transform.getForward();
```

### 4. Геометричні утиліти

#### Базові структури
```cpp
Ray ray(Vec3(0, 0, 0), Vec3(1, 0, 0));
Sphere sphere(Vec3(0, 0, 0), 5.0f);
AABB aabb(Vec3(-1, -1, -1), Vec3(1, 1, 1));
Plane plane(Vec3(0, 1, 0), 0.0f);
```

#### Функції перетинів
```cpp
float t;
bool intersects = Intersection::raySphere(ray, sphere, t);
bool contains = sphere.contains(point);
float distance = Distance::pointToPoint(a, b);
```

#### Формації юнітів
```cpp
// Лінійна формація
auto line = Formation::createLineFormation(start, end, count);

// Дугова формація  
auto arc = Formation::createArcFormation(center, radius, startAngle, endAngle, count);

// Кругова формація
auto circle = Formation::createCircleFormation(center, radius, count);

// Сіткова формація
auto grid = Formation::createGridFormation(center, rows, cols, spacing);

// Випадкова формація
auto random = Formation::createRandomFormation(minBounds, maxBounds, count);
```

### 5. Система камери

```cpp
Camera camera(Vec3(0, 5, 10), Vec3(0, 0, 0));
camera.setPerspective(60.0f * DEG_TO_RAD, 16.0f/9.0f, 0.1f, 1000.0f);

Mat4 viewMatrix = camera.getViewMatrix();
Mat4 projMatrix = camera.getProjectionMatrix();
Mat4 viewProjMatrix = camera.getViewProjectionMatrix();

// Ray casting
Ray ray = camera.screenToRay(screenX, screenY, width, height);
```

## Python API

### Базові типи
```python
from math_engine import Vec3, Transform, FormationGenerator, Camera

# Вектори
v1 = Vec3(1, 2, 3)
v2 = Vec3(4, 5, 6)
v3 = v1 + v2
dot = v1.dot(v2)
cross = v1.cross(v2)

# Трансформації
transform = Transform()
transform.position = Vec3(5, 10, 15)
transform.rotation = Vec3(0, math.radians(45), 0)
transform.scale = Vec3(2, 2, 2)

# Формації
line = FormationGenerator.create_line_formation(
    Vec3(0, 0, 0), Vec3(20, 0, 0), 6
)
circle = FormationGenerator.create_circle_formation(
    Vec3(0, 0, 0), 10, 8
)

# Камера
camera = Camera(Vec3(0, 5, 10), Vec3(0, 0, 0))
camera.fov = math.radians(60)
camera.aspect = 16.0 / 9.0
```

## Інтеграція з USD генератором

Математичний движок інтегрований з USD генератором сцен для автоматичного створення формацій юнітів:

```python
# В scene.yaml
units:
  army_1:
    spawn_area: [10, 10, 30, 30]
    units:
      - type: "warrior"
        count: 15
        formation: "line"      # Лінійна формація
        spacing: 2.0
      - type: "archer"
        count: 10
        formation: "arc"       # Дугова формація
        spacing: 1.5
      - type: "mage"
        count: 3
        formation: "grid"      # Сіткова формація
        spacing: 3.0
```

## Збірка та тестування

### C++ збірка
```bash
mkdir build && cd build
cmake ..
make
./math_test
```

### Python тести
```bash
python3 test_math_engine.py
```

### USD генерація
```bash
python3 generate_usd_scene.py --config scene.yaml --out output.usda
```

## Приклади використання

### 1. Створення формації юнітів
```cpp
// C++
Vec3 center(50, 0, 50);
float radius = 20.0f;
int count = 12;

auto positions = Formation::createCircleFormation(center, radius, count);
for (const auto& pos : positions) {
    // Створити юніта в позиції pos
    createUnit(pos);
}
```

### 2. Робота з камерою
```cpp
// C++
Camera camera;
camera.setPosition(Vec3(0, 10, 20));
camera.lookAt(Vec3(0, 0, 0));
camera.setPerspective(60.0f * DEG_TO_RAD, 16.0f/9.0f, 0.1f, 1000.0f);

// Отримати матриці для шейдерів
Mat4 viewMatrix = camera.getViewMatrix();
Mat4 projMatrix = camera.getProjectionMatrix();
```

### 3. Геометричні розрахунки
```cpp
// C++
Vec3 point(5, 0, 5);
Sphere sphere(Vec3(0, 0, 0), 10.0f);

if (sphere.contains(point)) {
    // Точка всередині сфери
}

float distance = Distance::pointToPoint(point, sphere.center);
```

## Складність геометрії

### Поточна складність
- **Проста**: Базові примітиви (куби, сфери, площини)
- **Позиціонування**: 2D/3D координати
- **Трансформації**: Translate, rotate, scale
- **Формації**: Лінійні, дугові, кругові, сіткові, випадкові

### Що робить геометрія
- **Розміщення юнітів** у різних формаціях
- **Позиціонування будівель** та об'єктів
- **Налаштування камери** (позиція, ціль, FOV)
- **Освітлення** (напрямок сонця, ambient)
- **Ефекти** (магічні аури, портали)

## Розширення

Математичний движок легко розширюється для додавання нових функцій:

1. **Нові формації**: Додати в `Formation` namespace
2. **Геометричні примітиви**: Розширити `geometry.h`
3. **Математичні функції**: Додати в `math.h`
4. **Python API**: Розширити `math_engine.py`

## Ліцензія

Проект використовує ті ж ліцензійні умови, що й основний проект SCBW-Gen.